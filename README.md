# AquaSanayi AI — Endüstriyel Su Kıtlığı Risk, Yer Seçimi ve 2029 ROI Karar Platformu

> **EkoZeka26 Hackathonu (İzmir — 7–8 Kasım 2026)** · **Geliştirici:** Ege Akgün (DEÜ Bilgisayar Bilimleri)

**AquaSanayi AI**, sanayi tesisleri, OSB yönetimleri, yatırım ajansları ve yeşil finansman sağlayan bankalar için geliştirilmiş **fizik-öncelikli + makine öğrenmesi destekli** bir karar destek platformudur. İklim projeksiyonlarını (ERA5 + 7 CMIP6 HighResMIP modeli), küresel/yerel hidrolojik verileri (WRI Aqueduct 4.0 Türkiye 639 poligon / 116 tekil hidrolojik havza + İZSU baraj/kuyu üretim serileri) ve Bakanlık (SYGM) NACE su verimliliği rehberlerini birleştirerek:
1. **Yeni fabrika yatırımları için** Türkiye'nin **639 poligonunda (116 tekil `pfaf_id` havzası)** şeffaf bileşik su kesintisi riskini (`0–100`), P10/P50/P90 beklenen kısıt günlerini ve SHAP sürücülerini hesaplar,
2. **Mevcut fabrikalar için** **27 Aralık 2029 Yeşil Su Verimliliği Belgesi** (RG 27.12.2024, Sayı: 32765) zorunluluğuna uyumu ve 5 yıllık **finansal** NPV'yi maksimize eden **bütçe kısıtlı optimum önlem portföyünü (0-1 Knapsack + çarpımsal azalan verim)** optimize eder; önlenen duruş riski ayrı gösterilir.

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
| `data_pipeline.py` | WRI Aqueduct 4.0 GDB (`where="gid_0 = 'TUR'"`) + CSV `m:1` (`string_id` ← `pfaf_id`) birleştirme; İZSU Next.js JSON & CSV ayrıştırma; `9999` "veri yok" temizliği | `639` alt-havza poligonu (`116` tekil `pfaf_id`), `<3.8 MB` GeoJSON, `137` ham İZSU satırı → `126` tekil tesis-ay |
| `climate_engine.py` | **FAO-56 Penman-Monteith** (ERA5) + **Hargreaves-Samani (1985)** (`ET₀` CMIP6); **Quantile Delta Mapping (QDM, Cannon vd. 2015)** her model için ayrı | **7 gerçek CMIP6 HighResMIP modeli** × `3` senaryo (`OPT`, `BAU`, `PES`), `2026–2050` P10/P50/P90 su dengesi; model mutabakatı `%71–86` (gerçek model yayılımı) |
| `drought_index.py` | **SPI-3/12** (McKee vd. 1993, Gamma) ve **SPEI-3/12** (Vicente-Serrano vd. 2010, 3-parametreli Log-Logistic / Fisk dağılımı) | `1940–2050` aylık seri (`1.332` ay), 2024/2025 rekor kuraklık doğrulaması |
| `risk_index.py` | **Şeffaf Bileşik Endüstriyel Kesinti Risk Skoru (`0–100`)**: Yeraltı düşüşü (`25p`) + Su stresi (`25p`) + SPEI/Kuraklık (`20p`) + Sektörel AWR (`15p`) + Oynaklık (`15p`) + Coğrafi sınır koruması | Her bileşenin puan katkısı ve formülü açık; Aqueduct "ölçüm" değil **resmî model** olarak etiketli; deniz/sınır dışı tıklamada en yakın kara havzası önerisi |
| `ml_engine.py` | **XGBoost Mevsimsel/Mekânsal Ölçek İndirme (Annual→Monthly Peak Downscaler)** + **5-Katlı `GroupKFold(groups=pfaf_id)`** + **SHAP (`TreeExplainer`)** + **KMeans (`k=5` havza arketipi)** + **ERA5/GloFAS Gediz Backtest** | Naive `MAE=0,4789 (R²=-0,004)` → Ridge `MAE=0,2940 (R²=0,630)` → **XGBoost `MAE=0,1534, RMSE=0,4328, R²=0,7958` (-%68 hata)**; Gediz Backtest `R²=0,6732`; SHAP `<15 ms` |
| `anomaly.py` | **Isolation Forest** (Liu vd. 2008) ile İZSU 2025 aylık üretim serisi (137 ham → 126 tekil tesis-ay) + 23 günlük baraj kesit deltası (`14.10.2026 → 06.11.2026`) | Kasım 2025 Tahtalı çöküşü (`6,91 → 1,62 Mm³`, `-%76,5`) ve kuyu payı sıçraması (`%69,3`, `Skor=0,5932`); Balçova 23 günde `-%7,43 puan` düşüş |
| `roi_optimizer.py` | **0-1 Knapsack Kesin Çözüm** + Proses bazlı **çarpımsal azalan verim** ($S_p = 1 - \prod(1-r_i) \le \%78$) + Kuyu/Şebeke/Yüzey suyu ekonomisi + **CAPEX ölçek kalibrasyonu** + **finansal NPV/geri ödeme** + ayrı **risk azaltımı** + **27.12.2029 Belge Kademesi** | 12 SYGM/IFC önlemi; **Tofaş**: `%35,8` tasarruf, **17,3 ay finansal**, Yeşil; **Vestel**: `%24,0`, **3,9 ay finansal**, Yeşil; **Petkim**: `%48,0`, **20,8 ay finansal**, Yeşil |
| `llm_agent.py` | `google-genai` (`gemini-2.5-flash`) + **Sıfır Halüsinasyon Kilidi (`STRICT_JSON_LOCKED`)** + `<5 ms` çevrimdışı deterministik uzman şablonu | LLM hiçbir çarpma/bölme yapmaz; yalnızca doğrulanmış JSON çıktılarını raporlar |

---

## 4. Veri Soyu (Data Lineage) ve Lisanslar
1. **WRI Aqueduct 4.0 Water Risk Atlas (2023):** CC BY 4.0 — Türkiye `639` alt-havza poligonu (`string_id`) ve `116` hidrolojik havza (`pfaf_id`) baseline/future/monthly serileri (`data/raw/aqueduct_*_tur.csv`, `turkey_gdb_baseline.gpkg`).
2. **Open-Meteo ERA5 (1940–2025), CMIP6 HighResMIP (2020–2050, 7 gerçek model) & GloFAS v4 (1984–2025):** CC BY 4.0 (`data/raw/era5.json`, `cmip6_7models.json`, `cmip6.json`, `cm4.json`, `flood.json`).
3. **İZSU Kamuya Açık Baraj Doluluk, Aylık/Günlük Üretim ve Haziran 2026 Sanayi Tarifesi:** Kamu açık verisi (`data/raw/izsu.html`, `izsu_aylik.html`, `baraj.csv`, `gunluk.csv`, `tarife.html`).
4. **T.C. Tarım ve Orman Bakanlığı (SYGM) NACE Rehberleri, Gediz Tahsis Planı & IFC (2017):** Yalnızca atıflı teknik tasarruf/geri ödeme katsayıları kataloglanmıştır (`data/processed/measures_catalog.json`); telifli PDF'ler dağıtılmaz.
5. **Gerçek Tesis Verileri (2024):** Tofaş 2024 Entegre Raporu (`430.782 m³` yeraltı suyu, `4.409` çalışan), Vestel 2024 Sürdürülebilirlik Raporu (`1.510.208 m³`), Petkim 2024 Entegre Faaliyet Raporu (`14.230.105 m³`, `2.433` çalışan). Yalnızca kamuya açık özet göstergeler kullanılır; proses payları/bütçe kalibre varsayımdır.
6. **Ticari Bağımsızlık:** Hiçbir ticari platformun (CarbonEmit, Blueit, 3pmetrics vb.) verisi veya API'si kullanılmaz. Tesis verisi kendi açık şemamızla (`data/schema/facility.schema.json`) JSON/CSV olarak içe/dışa aktarılır.

---

## 5. Bilinen Sınırlamalar ve Şeffaf Varsayımlar
- **Mekânsal Çözünürlük:** Aqueduct 4.0 gelecek projeksiyonları alt-havza (`pfaf_id`) ölçeğindedir; aynı alt-havzadaki iki farklı kuyu arasındaki mikro-hidrojeolojik farklar yerinde pompaj testi gerektirir.
- **Tarihsel Kesinti Etiketi:** Fabrika bazında tarihsel "su kesinti günü" kamuya açık olmadığı için geriye dönük doğrulama (backtest) ERA5 + GloFAS Gediz nehir debisi (`1997–2025`, `R² = 0,6732`) ve Aqueduct aylık su stresi (`R² = 0,7958`) üzerinden hidrolojik yeniden üretim olarak gerçekleştirilmiştir.
- **Önlem CAPEX Ölçeklemesi:** Katalogdaki 12 SYGM/IFC önleminin yatırım maliyetleri `150.000 m³/yıl` referans tesise göre kalibre edilmiştir. Farklı kapasitelerde CAPEX doğrusal ölçeklenir (`0,5–100×`), böylece katalogdaki tipik geri ödeme oranı korunur; bu bir mühendislik yaklaşımıdır, yerinde keşif/teklif yerine geçmez.
- **7 CMIP6 Modeli:** Open-Meteo HighResMIP serisi yüksek emisyon (RCP8.5 benzeri) yolundadır. `OPT/BAU/PES` ayrımı, model anomalisinin `0,70/0,85/1,00` ölçeklenmesi ve Aqueduct SSP projeksiyonlarıyla yapılır; bu bir senaryo haritalamasıdır, üç ayrı emisyon simülasyonu değildir.
- **Örnek Tesis Verileri:** Tofaş/Vestel/Petkim su çekimi ve çalışan sayıları kamuya açık 2024 raporlarından alınmıştır; proses payları, duruş maliyeti ve bütçe şeffaf kalibre varsayımdır.

### 5.1 Kapsam ve Çözünürlük (Dürüstlük Notu)
- **Tier 0 — Ulusal tarama:** 639 poligon, **116 tekil `pfaf_id`** hidrolojik havzasının il/akifer kesişimidir; `bws` çoğu `pfaf_id` içinde sabittir. "639 bağımsız havza" değildir; bu katman yatırım **ön taramasıdır**, yerinde ölçüm değildir.
- **Tier 1 — Odak koridor (7 OSB):** İzmir Kemalpaşa, İzmir Aliağa, İzmir Atatürk, Manisa, Bursa, Kocaeli Gebze, Konya. Bu OSB'lerde yerel tarife/OSB profili kullanılır.
- **Tier 2 — İzmir/Gediz canlı:** İZSU baraj/üretim serileri + SYGM Gediz Tahsis Planı + gerçek fabrika vakaları; en yüksek doğrulama katmanı.
- **İklim referansı:** ERA5/CMIP6 serisi şu an tek noktadan (İzmir, ~38.49N/27.11E) alınır; OSB farkı Aqueduct SSP projeksiyonu + enlem offseti ile üretilir. 1991–2020 ERA5 kontrolünde Bursa P−ET₀ ≈ −174 mm iken model ≈ −601 mm, Konya ≈ −1029 mm iken model ≈ −687 mm verir. Bölgesel iklim çapaları sonraki sürümde eklenecektir.
- **SPEI/SPI:** Gerçek seri tek referans noktası (İzmir/Gediz) için hesaplanır; havza kartındaki `spei12_trend` bir proxy'dir ve UI'de "SPEI proxy" olarak etiketlenir.
- **UI güven rozetleri:** "Odak koridor · yerel veri" ve "Ulusal · Aqueduct tarama" etiketleri hangi katmanda olduğunuzu söyler.

### 5.2 İZSU Canlı Veri ve Offline Fallback Protokolü
`/api/izsu-live` çalışma anında doğrudan İZSU'ya bağımlı değildir. Kaynak zinciri:

1. **Taze canlı önbellek:** `data/cache/izsu_live_snapshot.json` (varsayılan TTL 6 saat).
2. **Doğrulanmış snapshot:** `data/processed/izsu_snapshot.json` (6 Kasım 2026, tam aylık üretim + tarife katmanı).
3. **Fallback:** `data/fallback/izsu_snapshot.json` (processed yoksa/bozuksa).

Canlı çekim isteğe bağlıdır:

```bash
# Mevcut kaynak modunu ve önbellek yaşını göster
uv run python -m ekozeka26.izsu_source --status

# İZSU baraj sayfasını canlı çek; başarısız olursa doğrulanmış snapshot'a düş
uv run python -m ekozeka26.izsu_source --refresh

# API üzerinden canlı deneme (başarısız olursa fallback_reason döner)
curl -s "http://127.0.0.1:8000/api/izsu-live?refresh=true"
```

`/api/izsu-live` yanıtı `source_mode` (`live_fetch` / `live_cache` / `verified_snapshot` / `fallback_snapshot`), `snapshot_date`, `age_days` ve `fallback_reason` alanlarını taşır. Canlı sayfa yalnızca baraj/kuyu doluluk kesitini içerdiği için aylık üretim serisi, 23 günlük kesit ve 2026 tarifeleri doğrulanmış snapshot'tan korunur; böylece canlı fetch başarısız olsa bile demo eksik veriyle çalışmaz.

### 5.3 ROI Finansal Modeli (Dürüstlük Notu)
- **Headline NPV/geri ödeme yalnızca sert nakit:** su faturası tasarrufu + OPEX tasarrufu − CAPEX. Önlenen üretim duruşu zararı **finansal NPV'ye dahil edilmez**; ayrı "risk azaltımı (beklenen)" kartında gösterilir.
- **Neden:** Duruş zararı, kesinti günü tahminine ve `1.15 × tasarruf oranı` varsayımına dayanır; tarihsel fabrika kesinti verisi yoktur. Bu kalemi NPV'ye katmak geri ödemeyi 2–8 aya düşürüyordu; sektör benchmark'ları (EPA ~5 yıl, PNNL ~6 yıl, yerinde su geri kazanımı 3–7 yıl) ve katalog tipik süreleri (3,5–24 ay) ile çelişiyordu.
- **Yeni finansal sonuçlar:** Tofaş **17,3 ay**, Vestel **3,9 ay**, Petkim **20,8 ay**. Risk azaltımı ayrı: Tofaş 12,77M TL/yıl, Vestel 22,77M TL/yıl, Petkim 231,89M TL/yıl.
- **Tarife duyarlılığı:** Manisa OSB (118,50 TL/m³), Tofaş kuyu (24,80 TL/m³) ve Petkim yüzey suyu (15,00 TL/m³) kalibre varsayımdır. Tarife ±%40 değişirse Tofaş 12,4–28,9 ay, Vestel 2,8–6,4 ay, Petkim 17,1–39,9 ay aralığına kayar; Petkim'de %40 düşük tarifede NPV negatif olur.
- **CAPEX ölçeklemesi:** 150.000 m³/yıl referans tesise göre doğrusal (0,5–100×). Bu bir mühendislik yaklaşımıdır; izleme/kaçak önlemleri su hacmiyle doğrusal ölçeklenmez.
- **Petkim kademesi:** Finansal optimizasyon `M01, M05, M10` seçtiği için `%48,0` tasarruf ve **Yeşil** belge; risk-dahil eski portföy `M01, M04, M05, M10` ile **Turkuaz**'a ulaşıyordu. Turkuaz gönüllü üst kademedir; 2029 zorunlu Yeşil hedefi karşılanır.

---

## 6. Bilinen Zararsız Log Gürültüsü: `GET /v1/models → 404`

**Belirti:** Sunucu logunda `GET /health 200 OK` hemen ardından `GET /v1/models 404 Not Found` satırları ~30 saniyede bir tekrar eder.

**Sebep:** Bu istekleri **AquaSanayi AI değil, OpenCode CLI (`user-agent: opencode/latest/2.1.4/cli`) kendisi** gönderir. OpenCode, desteklediği yerel/OpenAI-uyumlu LLM sunucularını keşfetmek için `127.0.0.1:8000` adresini yoklar:
1. `GET /health` → "Bu portta bir servis var mı?" (bizim eklediğimiz sağlık kısayolu `200` döner),
2. `GET /v1/models` → "Hangi modeller yüklü?" (OpenAI API standardı; vLLM'in varsayılan portu da 8000'dir).

Bizim uygulamamız bir **LLM sunucusu değil**, bir REST karar platformudur; uç noktaları `/api/...` altındadır. Dolayısıyla `/v1/models` için `404` dönmesi **doğru ve beklenen** davranıştır.

**Etkisi: Sıfır.** 404 yalnızca OpenCode'un keşif isteğine verilen cevaptır; uygulamanın hiçbir uç noktasını, haritayı, ROI motorunu veya testleri etkilemez. Doğrulandı: `/`, `/api/health`, `/api/basins`, `/api/izsu-live`, `/api/osb-compare`, `/api/simulate-roi` → tümü `HTTP 200`. Ayrıca uygulama `8012` portunda 35 saniye çalıştırıldığında **tek bir yoklama isteği bile gelmedi**; yoklama yalnızca 8000 portuna özgüdür.

**Ne yapmalı?** Hiçbir şey. `404` satırını görünce sunucunun bozuk olduğunu düşünmeyin; `Application startup complete` + `Uvicorn running on http://127.0.0.1:8000` satırları sunucunun ayakta olduğunu gösterir ve tarayıcıda `http://127.0.0.1:8000` açılır.

**Log gürültüsünü tamamen gizlemek isterseniz (isteğe bağlı):**

```bash
ACCESS_LOG=off bash scripts/run.sh
```

Bu mod yalnızca erişim loglarını kapatır; uygulama davranışı ve tüm uç noktalar aynı kalır. Varsayılan (`on`) modda jüriye `200 OK` isteklerini göstermek için erişim logları açık kalır.
