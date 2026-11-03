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

## 🌟 v3 PRO Sürümündeki Yenilikler

* ⚡ **Ultra Hızlı ONNX Motoru:** Ağır PyTorch kütüphanesi yerine doğrudan C++ seviyesinde çalışan **ONNX Runtime (CPU)** motoruna geçildi. Açılış süresi 10 saniyeden **0.3 saniyeye** indirildi, kütüphane çakışmaları sıfırlandı.
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
1. Bilgisayarınızda Python 3.10+ kurulu olduğundan emin olun.
2. Gerekli kütüphaneleri yükleyin:
   ```bash
   pip install -r distance/code/yolo5/requirements.txt
   pip install pystray pyinstaller
   ```
3. Uygulamayı başlatın:
   * **`run.bat`** dosyasına çift tıklayın.

### Yöntem 2: Bağımsız `.exe` Dosyası Oluşturma
Programı Python olmadan çalışacak tek bir `.exe` haline getirmek için:
1. **`build_exe.bat`** dosyasına çift tıklayın.
2. Derleme tamamlandığında dosyanız şurada hazır olacaktır:
   ```
   dist/WarThunderRangefinder_v3.exe
   ```

---

## 🎮 Savaşta Nasıl Kullanılır?

1. Oyuna girmeden önce programı açın (Windows saatinin yanına simge olarak yerleşecektir).
2. Savaşta düşmana veya vurmak istediğiniz konuma nişangah veya dürbünden bakın.
3. Belirlediğiniz tuşa (varsayılan: **`T`**) basarak hedefe sarı işaret koyun.
4. Taktiksel HUD ekranında anında şu bilgiler görünecektir:
   * 🎯 **Mesafe (Range):** Metre cinsinden tam uzaklık
   * 🧭 **Azimut (Azimuth):** Pusula derecesi
   * 📐 **Ölçek (Scale):** Harita kare büyüklüğü (`[OTO]` veya `[MAN]`)

---

## ⌨️ Varsayılan Kısayol Tuşları

| Eylem | Varsayılan Tuş | Ayarlardan Değiştirilebilir mi? |
| :--- | :--- | :--- |
| **Mesafe Ölçümü** | `T` | Evet (Klavye veya Fare) |
| **Manuel Ölçek Penceresi** | `Ctrl + N` | Evet |
| **Dil Değiştirme** | Arayüz / Tepsi Menüsü | `English` / `Türkçe` |

---

## 👥 Teşekkür ve Atıflar

* **Orijinal Geliştirici & Model:** [Yonisen](https://github.com/Yonisen) — [WarThunder_Yellow_Mark_Rangefinder](https://github.com/Yonisen/WarThunder_Yellow_Mark_Rangefinder) projesinin yaratıcısı.
* **Ultralytics YOLOv5:** Nesne tespit mimarisi için [Ultralytics](https://github.com/ultralytics/yolov5).
* **War Thunder Telemetri API:** Yerel harita ve telemetri yayını için Gaijin Entertainment.

---

## 📜 Lisans

Bu proje MIT Lisansı altında sunulmaktadır.
