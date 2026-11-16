# FiyatRadar — B2B E-Ticaret Rakip Fiyat & Stok İstihbarat Motoru

**FiyatRadar**, e-ticaret satıcılarının rakip ürün fiyatlarını ve stok durumlarını otonom olarak takip etmesini sağlayan, kritik değişimlerde (fiyat kırımı, hedef fiyata ulaşma, rakip stoğunun tükenmesi) **Telegram Bot API** üzerinden anlık aksiyon bildirimleri üreten bir B2B otomasyon ve istihbarat sistemidir.

---

## Mimari ve Teknik Özellikler

* **Anti-Bot & TLS Parmak İzi Taklidi:** Standart HTTP istemcilerinin WAF (Web Application Firewall) engellerine takılmasını önlemek için curl_cffi kullanılarak gerçek tarayıcı TLS/JA3 imzaları taklit edilir ve istek aralıklarına rastgele gecikmeler (Jitter) uygulanır.
* **Yapısal Veri Ayrıştırma (JSON-LD):** HTML sınıf isimlerindeki sık değişikliklerden etkilenmemek için sayfa içi Schema.org (pplication/ld+json) standart meta verileri hedeflenir.
* **Otonom Zamanlayıcı & Geçmiş Kaydı:** APScheduler ve SQLAlchemy ORM ile arka planda periyodik tarama yapılır; her fiyat değişimi zaman damgasıyla (price_history) veritabanına işlenir.
* **Hafif & Modern Kontrol Paneli:** FastAPI üzerinde çalışan, ek derleme adımı gerektirmeyen Tailwind CSS & Alpine.js tabanlı yönetim arayüzü.

## Güvenlik Tasarımı (Security by Design)

1. **SSRF (Server-Side Request Forgery) Koruması:** Kullanıcıdan alınan URL'ler yalnızca HTTPS protokolü ve izin verilen pazaryeri alan adları (Allowlist) ile sınırlandırılarak iç ağ tarama riskleri engellenmiştir.
2. **XSS (Cross-Site Scripting) Önlemi:** Hedef sitelerden çekilen dinamik ürün başlıkları arayüzde ham HTML yerine güvenli metin bağlama (x-text) ile işlenir.
3. **Gizli Anahtar Yönetimi (Secret Management):** API anahtarları ve Telegram token bilgileri kod tabanından tamamen izole edilerek .env ortam değişkenleri üzerinden yönetilir.

## Kurulum ve Çalıştırma

1. Depoyu klonlayın ve klasöre girin:
   git clone https://github.com/KULLANICI_ADIN/fiyatradar.git
   cd fiyatradar

2. Sanal ortam oluşturun ve aktif edin:
   python -m venv .venv
   .venv\Scripts\activate

3. Bağımlılıkları yükleyin:
   pip install -r requirements.txt

4. Ortam değişkenlerini ayarlayın:
   .env.example dosyasının adını .env olarak kopyalayıp TELEGRAM_BOT_TOKEN ve TELEGRAM_CHAT_ID bilgilerinizi girin.

5. Sunucuyu başlatın:
   uvicorn main:app --reload

Tarayıcınızdan http://127.0.0.1:8000 adresine giderek kontrol paneline, http://127.0.0.1:8000/docs adresinden ise OpenAPI dokümantasyonuna erişebilirsiniz.

---

## Geliştirme Metodolojisi & Şeffaflık Beyanı

> **AI-Assisted Engineering:** Bu proje; sistem mimarisi tasarımı, siber güvenlik kontrolleri (SSRF/XSS/Secret Management), modüler kod organizasyonu ve dokümantasyon süreçlerinde **yapay zeka ile eşli programlama (AI Pair Programming)** yaklaşımı benimsenerek geliştirilmiştir. Tüm kodlar yerel ortamda test edilmiş, doğrulanmış ve uçtan uca entegre edilmiştir.
<img width="1241" height="654" alt="ekran" src="https://github.com/user-attachments/assets/7ce934be-e62a-4547-aa28-1f2eb5a85f48" />
