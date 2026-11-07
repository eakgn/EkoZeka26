# AquaSanayi AI — Endüstriyel Su Kıtlığı Risk, Yer Seçimi ve 2029 ROI Karar Platformu

> **EkoZeka26 Hackathonu (İzmir — 7–8 Kasım 2026)** · **Geliştirici:** Ege Akgün (DEÜ Bilgisayar Bilimleri)

**AquaSanayi AI**, sanayi tesisleri, OSB yönetimleri, yatırım ajansları ve yeşil finansman sağlayan bankalar için geliştirilmiş **fizik-öncelikli + makine öğrenmesi destekli** bir karar destek platformudur. İklim projeksiyonlarını (ERA5 + 7 CMIP6 HighResMIP modeli), küresel/yerel hidrolojik verileri (WRI Aqueduct 4.0 Türkiye 639 alt-havza + İZSU baraj/kuyu üretim serileri) ve Bakanlık (SYGM) NACE su verimliliği rehberlerini birleştirerek:
1. **Yeni fabrika yatırımları için** Türkiye'nin **639 alt-havzasında** şeffaf bileşik su kesintisi riskini (`0–100`), P10/P50/P90 beklenen kısıt günlerini ve SHAP sürücülerini hesaplar,
2. **Mevcut fabrikalar için** **27 Aralık 2029 Yeşil Su Verimliliği Belgesi** (RG 27.12.2024, Sayı: 32765) zorunluluğuna uyumu ve 5 yıllık NPV'yi maksimize eden **bütçe kısıtlı optimum önlem portföyünü (0-1 Knapsack + çarpımsal azalan verim)** optimize eder.

---

## 1. Neden Sanayi? (Doğrulanmış Problem Çerçevesi)
- Türkiye'de toplam suyun hacimce **~%79'unu tarım** (DSİ: `48,7 / 61,7 milyar m³`), temin/şebeke tatlı suyunun ise **~%14,7'sini sanayi** (TÜİK 2024: imalat `%7,3` + maden/OSB `%5,8` + termik `%1,6`) çeker. Platformumuz *"suyu en çok sanayi harcıyor"* yanılgısına düşmez; **su kıtlığının m³ başına en pahalıya patladığı, yatırım kapasitesi olan ve yasal zorunluluk altındaki kesime** odaklanır:
  1. **Fiziksel Kesinti Riski (Gediz %100 Yeraltı Bağımlılığı):** Tarım ve Orman Bakanlığı (SYGM) *Gediz Havzası Sektörel Su Tahsis Planı*'na göre havzadaki sanayi su talebinin **%100'ü yeraltı suyundan (kuyulardan)** karşılanmaktadır ve kuraklık senaryosunda sanayi tahsis karşılama oranı **%85,9'dan %37,1'e düşmektedir (%62,9 kesinti / üretim durma riski)**.
  2. **Finansal Maliyet:** İZSU 1 Haziran 2026 tarifesine göre sanayi (1c) su fiyatı 21 m³/ay üzerinde **403,79 TL/m³**'tür (KDV hariç; geri kazanılmış su **11,95 TL/m³**).
  3. **İzmir Barajlarının Gerçek Durumu (6 Kasım 2026):** 5 barajın basit ortalaması `%44,24` iken, kapasitenin **%57,9'unu** tutan Gördes Barajı yalnızca **%27,96** dolu olduğu için **gerçek kapasite-ağırlıklı doluluk %34,01** (`257,17 / 756,19 Mm³`) seviyesindedir.
  4. **Yasal Zorunluluk (Deadline: 27 Aralık 2029):** 27.12.2024 tarihli Resmi Gazete'de (No. 32765) yayımlanan **Su Verimliliği Yönetmeliği** uyarınca OSB'ler ve Ek-2 NACE listesindeki 50+ çalışanlı fabrikalar **27 Aralık 2029'a kadar Yeşil Su Verimliliği Belgesi** almak zorundadır.

---

## 2. Hızlı Başlangıç (Tek Komutla Çalıştırma)

Proje **Python 3.12 (`uv`)** ve **CPU-only (`xgboost-cpu`)** bağımlılıklarıyla sıfır ağ bağımlılığıyla (offline-ready) çalışır:

```bash
# 1. Sunucuyu 127.0.0.1:8000 üzerinde başlat
bash scripts/run.sh

# Veya doğrudan uv ile:
uv run uvicorn ekozeka26.app:app --host 127.0.0.1 --port 8000
```

Tarayıcıda **`http://127.0.0.1:8000`** adresini açın.

```bash
# Tüm birim, doğrulama (V&V), API ve performans testlerini çalıştır:
uv run pytest

# Veri işleme hattını çevrimdışı (data/raw/ üzerinden) yeniden üret:
uv run python -m ekozeka26.data_pipeline --offline

# XGBoost GroupKFold ve Gediz 1984-2025 hidrolojik backtest metriklerini çalıştır:
uv run python -m ekozeka26.ml_engine --backtest
```

---

## 3. Teknik Mimari ve Yapay Zeka Çekirdeği (`src/ekozeka26/`)

| Modül | Metodoloji & Literatür Dayanağı | Doğrulanmış Çıktı / Metrik |
|---|---|---|
| `data_pipeline.py` | WRI Aqueduct 4.0 GDB (`where="gid_0 = 'TUR'"`) + CSV `m:1` (`string_id` ← `pfaf_id`) birleştirme; İZSU Next.js JSON & CSV ayrıştırma | `639` alt-havza poligonu (`116` tekil `pfaf_id`), `<3.8 MB` GeoJSON, `137` aylık İZSU üretim kaydı |
| `climate_engine.py` | **FAO-56 Penman-Monteith** (ERA5) + **Hargreaves-Samani (1985)** (`ET₀` CMIP6); **Quantile Delta Mapping (QDM, Cannon vd. 2015)** dağılımsal kalibrasyon (`YYYY-MM` takvim eşleştirmesi yapılmaz!) | `7` CMIP6 modeli × `3` senaryo (`OPT`, `BAU`, `PES`), `2026–2050` P10/P50/P90 su dengesi ve `%85,7` model mutabakatı |
| `drought_index.py` | **SPI-3/12** (McKee vd. 1993, Gamma) ve **SPEI-3/12** (Vicente-Serrano vd. 2010, 3-parametreli Log-Logistic / Fisk dağılımı) | `1940–2050` aylık seri (`1.332` ay), 2024/2025 rekor kuraklık doğrulaması |
| `risk_index.py` | **Şeffaf Bileşik Endüstriyel Kesinti Risk Skoru (`0–100`)**: Yeraltı düşüşü (`25p`) + Su stresi (`25p`) + SPEI/Kuraklık (`20p`) + Sektörel AWR (`15p`) + Oynaklık (`15p`) + Coğrafi sınır koruması | Her bileşenin puan katkısı ve formülü açık; deniz/sınır dışı tıklamada en yakın kara havzası önerisi |
| `ml_engine.py` | **XGBoost Mevsimsel/Mekânsal Ölçek İndirme (Annual→Monthly Peak Downscaler)** + **5-Katlı `GroupKFold(groups=pfaf_id)`** + **SHAP (`TreeExplainer`)** + **KMeans (`k=5` havza arketipi)** + **ERA5/GloFAS Gediz Backtest** | Naive `MAE=0,4789 (R²=-0,004)` → Ridge `MAE=0,2940 (R²=0,630)` → **XGBoost `MAE=0,1534, RMSE=0,4328, R²=0,7958` (-%68 hata)**; Gediz Backtest `R²=0,6732`; SHAP `<15 ms` |
| `anomaly.py` | **Isolation Forest** (Liu vd. 2008) ile İZSU 2025 aylık üretim serisi (137 kayıt) + 23 günlük baraj kesit deltası (`14.10.2026 → 06.11.2026`) | Kasım 2025 Tahtalı çöküşü (`6,91 → 1,62 Mm³`, `-%76,5`) ve kuyu payı sıçraması (`%69,3`, `Skor=0,5932`); Balçova 23 günde `-%7,43 puan` düşüş |
| `roi_optimizer.py` | **0-1 Knapsack Kesin Çözüm** + Proses bazlı **çarpımsal azalan verim** ($S_p = 1 - \prod(1-r_i) \le \%78$) + Kuyu vs Şebeke ekonomisi + **27.12.2029 Belge Kademesi** | 12 SYGM/IFC önlemi; Kemalpaşa Tekstil örneğinde `%53,28` net tasarruf (`79.920 m³/yıl`), `NPV=128,95M TL`, `Turkuaz Belge` |
| `llm_agent.py` | `google-genai` (`gemini-2.5-flash`) + **Sıfır Halüsinasyon Kilidi (`STRICT_JSON_LOCKED`)** + `<5 ms` çevrimdışı deterministik uzman şablonu | LLM hiçbir çarpma/bölme yapmaz; yalnızca doğrulanmış JSON çıktılarını raporlar |

---

## 4. Veri Soyu (Data Lineage) ve Lisanslar
1. **WRI Aqueduct 4.0 Water Risk Atlas (2023):** CC BY 4.0 — Türkiye `639` alt-havza poligonu (`string_id`) ve `116` hidrolojik havza (`pfaf_id`) baseline/future/monthly serileri (`data/raw/aqueduct_*_tur.csv`, `turkey_gdb_baseline.gpkg`).
2. **Open-Meteo ERA5 (1940–2025), CMIP6 HighResMIP (2020–2050, 7 model) & GloFAS v4 (1984–2025):** CC BY 4.0 (`data/raw/era5.json`, `cmip6.json`, `cm4.json`, `flood.json`).
3. **İZSU Kamuya Açık Baraj Doluluk, Aylık/Günlük Üretim ve Haziran 2026 Sanayi Tarifesi:** Kamu açık verisi (`data/raw/izsu.html`, `izsu_aylik.html`, `baraj.csv`, `gunluk.csv`, `tarife.html`).
4. **T.C. Tarım ve Orman Bakanlığı (SYGM) NACE Rehberleri, Gediz Tahsis Planı & IFC (2017):** Yalnızca atıflı teknik tasarruf/geri ödeme katsayıları kataloglanmıştır (`data/processed/measures_catalog.json`); telifli PDF'ler dağıtılmaz.
5. **Ticari Bağımsızlık:** Hiçbir ticari platformun (CarbonEmit, Blueit, 3pmetrics vb.) verisi veya API'si kullanılmaz. Tesis verisi kendi açık şemamızla (`data/schema/facility.schema.json`) JSON/CSV olarak içe/dışa aktarılır.

---

## 5. Bilinen Sınırlamalar ve Şeffaf Varsayımlar
- **Mekânsal Çözünürlük:** Aqueduct 4.0 gelecek projeksiyonları alt-havza (`pfaf_id`) ölçeğindedir; aynı alt-havzadaki iki farklı kuyu arasındaki mikro-hidrojeolojik farklar yerinde pompaj testi gerektirir.
- **Tarihsel Kesinti Etiketi:** Fabrika bazında tarihsel "su kesintisi günü" kamuya açık olmadığı için geriye dönük doğrulama (backtest) ERA5 + GloFAS Gediz nehir debisi (`1997–2025`, `R² = 0,6732`) ve Aqueduct aylık su stresi (`R² = 0,7958`) üzerinden hidrolojik yeniden üretim olarak gerçekleştirilmiştir.
- **Önlem CAPEX Ölçeklemesi:** Katalogdaki 12 SYGM/IFC önleminin yatırım maliyetleri orta-büyük ölçekli (`100.000 – 300.000 m³/yıl`) standart fabrika kapasitelerine göre kalibre edilmiştir.
