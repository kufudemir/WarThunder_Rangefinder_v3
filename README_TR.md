# War Thunder Taktiksel Mesafe Bulucu v3 PRO 🎯

[![License: MIT](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)
[![Python 3.10+](https://img.shields.io/badge/Python-3.10%2B-blue.svg)](https://www.python.org/)
[![Platform](https://img.shields.io/badge/Platform-Windows%2010%20%2F%2011-lightgrey.svg)](https://www.microsoft.com/windows)
[![Original Project](https://img.shields.io/badge/Original%20Repo-Yonisen-orange.svg)](https://github.com/Yonisen/WarThunder_Yellow_Mark_Rangefinder)

> [!NOTE]  
> 🇬🇧 **For English documentation, please refer to [README.md](README.md).**

**War Thunder Kara Gerçekçi ve Simülatör Savaşları** için geliştirilmiş, yapay zeka (YOLOv5 ONNX) destekli ultra hızlı bir optik telemetre (mesafe ölçer) programıdır.  
Mini harita üzerindeki sarı manga hedef işaretinizi bilgisayarlı görü ile tespit eder ve War Thunder'ın yerel telemetri API'sini kullanarak hedef mesafesini ve azimut açısını anında hesaplar.

Bu proje, **@Yonisen** tarafından geliştirilen [WarThunder_Yellow_Mark_Rangefinder](https://github.com/Yonisen/WarThunder_Yellow_Mark_Rangefinder) açık kaynak projesi temel alınarak yüksek performanslı, iki dilli ve bağımsız çalışabilir mimariyle sıfırdan yeniden modernize edilmiştir.

---

## 🌟 v3.0.1 Sürümündeki Yenilikler

* ⏱️ **Ayarlanabilir Algılama Gecikmesi & Otomatik Yeniden Deneme:** `T` tuşuna basıldığında sarı işaret animasyonu tamamlanmadan ekran görüntüsü alma sorununu çözer. Kullanıcılar kontrol panelinden gecikmeyi milisaniye cinsinden (varsayılan 350 ms) ayarlayabilir; işaret geç render edilirse 150 ms mikro deneme ile otomatik kurtarma yapılır.
* 🎯 **Nişangah Yanı Taktiksel HUD Modu:** HUD konumu için **Nişangah Yanı** (`Ekran-X / 2 + 55, Ekran-Y / 2 - 25`), klasik **Sol Üst** veya özel koordinat seçimi. Mesafe bilgisi doğrudan nişan aldığınız alanın hemen yanında, görüşü kapatmadan gösterilir.
* ⚡ **Ultra Hızlı ONNX Motoru:** Doğrudan C++ seviyesinde çalışan **ONNX Runtime (CPU)** motoru. Anlık açılış ve sıfır PyTorch yükü.
* 🚀 **Sıfır Disk Gecikmesi (Bellekten Doğrudan İşleme):** Harita ekran görüntüleri sabit diske PNG olarak yazılmadan doğrudan RAM üzerinden işlenir. Bu sayede sıfır gecikmeyle anlık sonuç üretilir.
* 🌐 **War Thunder Canlı Telemetri API (8111) Entegrasyonu:** Maç esnasında haritanın kare ölçeğini (250m, 350m vb.) War Thunder'ın yerel ağından **otomatik** çeker. **Artık her haritada `Ctrl+N` ile elle ölçek girme zahmeti ortadan kalktı!**
* 🎛️ **Modern Kontrol Paneli & Sistem Tepsisi (Tray):** Konsol ekranları yerine modern koyu temalı bir arayüz ve Windows saatinin yanında sessizce arka planda çalışma özelliği.
* 🌍 **İki Dilli Destek (English / Türkçe):** Arayüzden veya sistem tepsisi menüsünden tek tıkla canlı dil değiştirme imkanı. Tüm ekran uyarıları ve HUD seçilen dilde görüntülenir.
* 📦 **Tek Tıkla `.exe` Derleme:** `build_exe.bat` ile bağımsız, bilgisayarda Python kurulu olmasına dahi gerek kalmayan tek bir `WarThunderRangefinder_v3.exe` oluşturabilme.
* 🖥️ **Tıklama Geçirgen HUD (Click-Through Overlay):** Oyunu ve fare hareketlerini hiçbir şekilde engellemeyen saydam taktiksel ekran göstergesi.

---

## ⚙️ War Thunder Oyun İçi Ayarları

Programın mini haritayı doğru okuyabilmesi için oyunda şu ayarları yapmanız gereklidir:

1. **Görüntü Modu:**
   * **Seçenekler** -> **Grafik** -> Ekran Modunu **Pencereli Tam Ekran (Fullscreen Window)** yapın.
2. **Mini Harita Boyutu:**
   * **Seçenekler** -> **Ana Parametreler** -> **Kara Araçları Savaşı Ayarları** -> **Taktiksel Harita Ölçeği**'ni **%133 (en büyük)** yapın.
3. **Manga Hedef İşaretleme Tuşu:**
   * **Kontroller** -> **Ortak** -> **"Manga için hedef belirle"** seçeneğine bir tuş atayın (Varsayılan: `T`).

---

## 🚀 Kurulum ve Başlatma

### Yöntem 1: Kaynak Koddan Çalıştırma
1. Bilgisayarınızda Python 3.10+ (Python 3.11 önerilir) kurulu olduğundan emin olun.
2. Gerekli kütüphaneleri yükleyin:
   ```bash
   pip install -r requirements.txt
   ```
3. Uygulamayı başlatın:
   * **`run.bat`** dosyasına çift tıklayın (veya `python app.pyw` çalıştırın).

### Yöntem 2: Bağımsız `.exe` Dosyası Oluşturma
Programı Python olmadan çalışacak tek bir `.exe` haline getirmek için:
1. **`build_exe.bat`** dosyasına çift tıklayın.
2. Derleme tamamlandığında dosyanız şurada hazır olacaktır:
   ```
   dist/WarThunderRangefinder_v3.exe
   ```

---

## 🕹️ Kısayollar ve Kullanım

* **`T`** (Varsayılan): Oyunda manga hedefini işaretler. Program gecikme süresince bekleyip mini haritayı okur, mesafeyi ve yön açısını anında HUD üzerinde görüntüler.
* **`Ctrl + N`**: Elle harita ölçeği girme penceresi (özel lobilerde telemetri kapalıysa kullanılır).
* **`Alt + Q`**: Acil durum anında çıkış.

---

## 📁 Proje Dosya Yapısı

```
WarThunder_Rangefinder_v3/
├── app.pyw                  # Ana GUI arayüzü ve HUD kontrolcüsü
├── requirements.txt         # Gereksinim listesi
├── run.bat                  # Hata bildirimli başlatıcı betiği
├── build_exe.bat            # Tek dosya .exe derleme betiği
├── data/                    # ONNX modelleri ve görsel şablonlar
├── distance/                # Bilgisayarlı görü ve telemetri motoru
│   └── code/
│       ├── buttons.ini      # Kullanıcı ayarları ve tuş yapılandırması
│       ├── locales.py       # İngilizce ve Türkçe dil çevirileri
│       ├── distance_onnx.py # ONNX tespit ve mesafe hesaplayıcı
│       └── web.py           # War Thunder 8111 yerel API istemcisi
└── dist/                    # Derlenen bağımsız exe klasörü
```

---

## ⚖️ Lisans ve Adil Oyun (Fair Play)

Bu yazılım **MIT Lisansı** ile dağıtılmaktadır.  
Gaijin Entertainment tarafından sağlanan yerel telemetri portunu (8111) ve kendi ekran görüntünüzü analiz eden harici bir erişilebilirlik katmanıdır. Oyun dosyalarını değiştirmez, oyun belleğine müdahale etmez (hook/inject yapmaz). Bununla birlikte kullanım sorumluluğu oyuncuya aittir.
