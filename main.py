from contextlib import asynccontextmanager
from fastapi import FastAPI, Depends, HTTPException, Request
from fastapi.responses import FileResponse

from pydantic import BaseModel
from sqlalchemy.orm import Session
from apscheduler.schedulers.background import BackgroundScheduler

from app.database import SessionLocal, TrackedProduct, PriceHistory, init_db
from app.scraper import scrape_product, validate_url
from app.notifier import send_telegram_alert



def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def check_all_products():
    print("[SCHEDULER] Otonom fiyat ve stok taraması başlatıldı...")
    db = SessionLocal()
    try:
        products = db.query(TrackedProduct).filter(TrackedProduct.is_active == True).all()
        for product in products:
            try:
                data = scrape_product(product.url)
                if data.get("status") != "success" or data.get("price") is None:
                    continue

                new_price = data["price"]
                new_stock = data["in_stock"]
                title = data["title"] or product.title or "Bilinmeyen Ürün"

                if product.last_price is None:
                    product.title = title
                    product.last_price = new_price
                    product.last_in_stock = new_stock
                else:
                    if new_price < product.last_price:
                        diff = product.last_price - new_price
                        msg = (
                            f"📉 <b>FİYAT DÜŞÜŞÜ YAKALANDI!</b>\n\n"
                            f"📦 <b>Ürün:</b> {title}\n"
                            f"💰 <b>Eski Fiyat:</b> {product.last_price:.2f} TL\n"
                            f"🔥 <b>Yeni Fiyat:</b> {new_price:.2f} TL (-{diff:.2f} TL)\n"
                            f"🔗 <a href='{product.url}'>Ürüne Git</a>"
                        )
                        send_telegram_alert(msg)

                    elif product.target_price and new_price <= product.target_price and product.last_price > product.target_price:
                        msg = (
                            f"🎯 <b>HEDEF FİYATA ULAŞILDI!</b>\n\n"
                            f"📦 <b>Ürün:</b> {title}\n"
                            f"🔥 <b>Güncel Fiyat:</b> {new_price:.2f} TL (Hedef: {product.target_price:.2f} TL)\n"
                            f"🔗 <a href='{product.url}'>Ürüne Git</a>"
                        )
                        send_telegram_alert(msg)

                    if product.last_in_stock and not new_stock:
                        msg = (
                            f"🚨 <b>RAKİP STOĞU TÜKENDİ! (Fırsat)</b>\n\n"
                            f"📦 <b>Ürün:</b> {title}\n"
                            f"💡 Rakibin stoğu bitti, kendi fiyatını/kampanyanı optimize edebilirsin.\n"
                            f"🔗 <a href='{product.url}'>Ürüne Git</a>"
                        )
                        send_telegram_alert(msg)

                    product.title = title
                    product.last_price = new_price
                    product.last_in_stock = new_stock

                db.add(PriceHistory(
                    product_id=product.id,
                    price=new_price,
                    in_stock=new_stock
                ))
                db.commit()
            except Exception as e:
                print(f"[HATA] Ürün tarama hatası ({product.url}): {e}")
    finally:
        db.close()

scheduler = BackgroundScheduler()

@asynccontextmanager
async def lifespan(app: FastAPI):
    init_db()
    scheduler.add_job(check_all_products, "interval", minutes=15, id="price_radar_job")
    scheduler.start()
    yield
    scheduler.shutdown()

app = FastAPI(
    title="FiyatRadar B2B İstihbarat API",
    version="1.0.0",
    lifespan=lifespan
)

class ProductCreate(BaseModel):
    url: str
    target_price: float | None = None

@app.get("/", include_in_schema=False)
def dashboard():
    return FileResponse("templates/index.html")

@app.post("/products/")
def add_product(item: ProductCreate, db: Session = Depends(get_db)):
    if not validate_url(item.url):
        raise HTTPException(status_code=400, detail="Sadece geçerli HTTPS Trendyol veya Hepsiburada linkleri kabul edilir.")

    existing = db.query(TrackedProduct).filter(TrackedProduct.url == item.url).first()
    if existing:
        raise HTTPException(status_code=409, detail="Bu ürün zaten takip listesinde mevcut.")

    try:
        initial_data = scrape_product(item.url)
    except Exception as e:
        raise HTTPException(status_code=502, detail=f"Hedef siteden veri çekilemedi: {str(e)}")

    if initial_data.get("status") != "success":
        raise HTTPException(status_code=502, detail="Hedef site isteği reddetti.")

    new_product = TrackedProduct(
        url=item.url,
        title=initial_data.get("title"),
        target_price=item.target_price,
        last_price=initial_data.get("price"),
        last_in_stock=initial_data.get("in_stock", True)
    )
    db.add(new_product)
    db.commit()
    db.refresh(new_product)

    db.add(PriceHistory(
        product_id=new_product.id,
        price=new_product.last_price,
        in_stock=new_product.last_in_stock
    ))
    db.commit()
    return {"message": "Ürün takibe alındı", "product": new_product}

@app.get("/products/")
def list_products(db: Session = Depends(get_db)):
    return db.query(TrackedProduct).order_by(TrackedProduct.id.desc()).all()

@app.delete("/products/{product_id}")
def delete_product(product_id: int, db: Session = Depends(get_db)):
    product = db.query(TrackedProduct).filter(TrackedProduct.id == product_id).first()
    if not product:
        raise HTTPException(status_code=404, detail="Ürün bulunamadı.")
    db.delete(product)
    db.commit()
    return {"message": "Ürün silindi."}

@app.post("/scan-now/")
def trigger_manual_scan():
    check_all_products()
    return {"message": "Manuel tarama tamamlandı."}
