# Turkish Weather Application

Bu uygulama, Türkiye'deki şehirler için hava durumu bilgilerini sağlayan bir MCP (Modular Command Protocol) aracıdır.

## Özellikler

- Türkiye'deki şehirler için güncel hava durumu
- Saatlik hava durumu tahminleri
- Hava kalitesi bilgileri
- Şehirler arası hava karşılaştırması
- Hava durumuna göre aktivite önerileri
- Hava durumu alarmları

## Kurulum

1. Python 3.11 veya üstünü yükleyin
2. Gerekli paketleri yükleyin: `pip install httpx mcp`
3. OpenWeatherMap API anahtarı alın ve `config.py` dosyasında ayarlayın

## Kullanım

Uygulamayı başlatmak için:

```bash
python weather.py
```

## Araçlar

- `hava_durumu_sehir`: Belirli bir şehir için hava durumu bilgisi
- `saatlik_hava_durumu`: Saatlik hava durumu tahminleri
- `hava_kalitesi`: Hava kalitesi endeksi bilgileri
- `sehirler_karsilastir`: İki şehri karşılaştırma
- `havadurumu_aktivite_onerileri`: Hava durumuna göre aktivite önerileri

## Proje Yapısı

- `weather.py`: Ana uygulama ve MCP araçları
- `api.py`: API istekleri için yardımcı fonksiyonlar
- `utils.py`: Yardımcı fonksiyonlar
- `config.py`: Yapılandırma sabitler ve şehir verileri

## Lisans

MIT
