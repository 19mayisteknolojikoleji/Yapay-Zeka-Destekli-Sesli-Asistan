# Yapay Zeka Destekli Sesli Asistan

Bu proje, donanım seviyesinde ses kaydı yapan bir **ESP32** ile bu sesi işleyerek yapay zeka yanıtları üreten bir **Python (Flask)** sunucusunun birleşimidir. Sistem; sesi metne dönüştürür, bir yerel dil modeli (LLM) ile yanıt üretir ve bu yanıtı tekrar sese dönüştürerek kullanıcıya geri gönderir.

---

## ✨ Özellikler

* 🎙️ **Sesli Etkileşim:** ESP32 üzerindeki I2S mikrofon ve hoparlör ile sesli komut alıp verme.
* 🤖 **Yerel Yapay Zeka:** Tüm işlemler yerel sunucuda döner (Whisper & Ollama).
* ⚡ **Hızlı Çeviri (STT):** `faster-whisper` kütüphanesi ile yüksek doğrulukta ses-metin dönüşümü.
* 🧠 **Akıllı Yanıtlar:** Ollama üzerinden `mistral` veya `phi3` modelleri ile kısa ve öz cevaplar.
* 🗣️ **Doğal Seslendirme (TTS):** `Piper` motoru ile Türkçe karakter destekli doğal ses çıkışı.
* 📺 **OLED Bilgilendirme:** Cihaz durumu (kayıt, gönderim, çalma) OLED ekran üzerinden takip edilebilir.

---

## 🛠️ Sistem Mimarisi

1. **Donanım (ESP32):** Kullanıcı butona bastığında sesi kaydeder ve HTTP üzerinden Python sunucusuna gönderir.
2. **Backend (Flask):** - **Whisper:** Gelen sesi metne çevirir.
   - **LLM (Ollama):** Metni analiz edip cevap üretir.
   - **Piper:** Cevabı `reply.wav` olarak seslendirir.
3. **Geri Bildirim:** Oluşturulan ses dosyası ESP32'ye geri gönderilir ve I2S üzerinden hoparlörden çalınır.

---

## 🔌 Donanım Bileşenleri

* **ESP32 DevKitV1**
* **I2S Mikrofon** (Örn: INMP441)
* **I2S DAC & Hoparlör** (Örn: MAX98357A)
* **OLED Ekran** (SSD1306 - I2C)
* **Buton** (Kayıt tetikleyici)

---

## 🚀 Kurulum ve Yapılandırma

### 1. Python Sunucusu (Backend)
Gerekli Python kütüphanelerini kurun:
```bash
pip install flask faster-whisper soundfile sounddevice requests numpy
```

## 📸 Ekran Görüntüleri
<img width="1200" height="1600" alt="image" src="https://github.com/user-attachments/assets/dfd56c33-e1fd-4727-a21b-3fbbb6425778" />
