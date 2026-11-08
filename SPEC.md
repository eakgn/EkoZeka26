# SPEC — EkoZeka26: AquaSanayi AI (Endüstriyel Su Kıtlığı Risk, Yer Seçimi ve ROI Karar Platformu)

> Bu dosya projenin tek doğruluk kaynağıdır. Yalnızca **geçerli** kararlar ve kısa gerekçeleri tutulur; vazgeçilen fikirler listelenmez.
> `build` oturumu işe başlamadan önce bu dosyayı, `STATE.md`'yi, `SUNUM.md`'yi ve `docs/RESEARCH.md`'yi okumalıdır. **Süreç boyunca üretilen tüm model metrikleri ve demo sayıları `SUNUM.md` içinde güncel tutulmalıdır.**

---

## 1. Hackathon Bilgileri ve Teslimatlar
- **Ad:** EkoZeka26 (İzmir)
- **Tema:** Güncel bir ekoloji problemine yapay zeka ile *sıkıca bağlı* bir çözüm.
- **Teslim (Deadline):** 8 Kasım 2026 Pazar, **10:00**.
- **Ekip:** Tek kişi (Ege Akgün, DEÜ Bilgisayar Bilimleri 2. sınıf).
- **Teslimatlar:**
  1. **Canlı Demo:** `127.0.0.1:8000` üzerinde çalışan, 2 sekmeli, çevrimdışı yedekli (offline fallback) web uygulaması.
  2. **Canlı Sunum:** 3–5 dk (soru-cevap dahil), canlı demo eşliğinde.
  3. **GitHub Reposu:** Temiz mimari, testler, veri soyu ve sınırlamaları içeren `README.md`.

---

## 2. Jüri Profili ve Konumlandırma Stratejisi
| Jüri | Profil | Projemizdeki Karşılığı |
|---|---|---|
| DEÜ Bilgisayar Bilimleri mezunu | Teknik / yazılım mimarisi | FastAPI + şeffaf risk indeksi + XGBoost (yanlılık düzeltme, GroupKFold) + SHAP + Bütçe Kısıtlı Portföy Optimizasyonu + Yapılandırılmış Gemini Ajanı + tüm uç durum (edge-case) korumaları ve testler. |
| İzmir Veri Topluluğu üyesi | Veri bilimi / metodoloji | Gerçek çok-kaynaklı veri (WRI Aqueduct 4.0 + ERA5 + 7 CMIP6 iklim modeli + İZSU canlı verisi), **SPEI/SPI kuraklık indeksleri, QDM yanlılık düzeltmesi**, P10/P50/P90 belirsizlik bantları, SHAP açıklanabilirliği, baseline karşılaştırması ve 2010–2020 geriye dönük doğrulama (backtest). |
| Musa Can Minaz (CarbonEmit Kurucusu) | Sürdürülebilirlik SaaS (ISO 14064/14067/14046, CBAM) | **Rakip değil, önceki katman:** CarbonEmit ve benzeri platformlar *geçmişin doğrulanmış* karbon/su ayak izini üretir. Biz *geleceğin* yatırım kararını üretiriz: 2030–2050 kesinti riski (TL), 27.12.2029 Yeşil Su Verimliliği Belgesi açığı ve bütçe kısıtlı en kârlı önlem portföyü. **Hiçbir veri entegrasyonu iddia edilmez**; kendi açık şemamızla dışa aktarım yapılır (bkz. §12 K6). |

---

## 3. Problem Tanımı ve Doğrulanmış Veriler
- **Küresel ve Ulusal Kriz:** 2025, Türkiye'de 1964'ten beri en kurak yıl oldu (yağış normalin %27,6 altında, MGM). İzmir barajlarının kapasite-ağırlıklı doluluğu **%34,0** (6 Kasım 2026, İZSU; Gördes %27,96, Tahtalı geçen yıl aynı gün %1,54 iken bu yıl %41,39 — aşırı oynaklık).
- **Neden Sanayi? (Kritik Çerçeveleme):**
  - Türkiye'de suyun hacimce ~%79'unu tarım (DSİ: 48,7 / 61,7 milyar m³), tatlı su şebeke/temin çekiminin ise ~%14,7'sini sanayi (TÜİK 2024: imalat %7,3 + maden/OSB %5,8 + termik %1,6) tüketir. **Asla "suyu en çok sanayi tüketiyor" denmeyecek.**
  - **Gerçek Problem:** Sanayi, su kıtlığının **m³ başına en pahalıya patladığı**, yatırım kapasitesi olan ve yasal zorunluluk altındaki tek kesimdir:
    1. **Fiziksel Kesinti Riski:** Gediz Havzası Sektörel Su Tahsis Planı'na (SYGM) göre havzadaki sanayi su talebinin **%100'ü yeraltı suyundan (kuyulardan)** karşılanmaktadır ve kuraklık senaryosunda sanayi tahsis karşılama oranı **%85,9'dan %37,1'e düşmektedir (%63 kesinti / üretim durma riski).**
    2. **Maliyet:** İZSU Haziran 2026 tarifesine göre sanayi (1c) su fiyatı 21 m³ üzerinde **403,79 TL/m³**'tür (KDV hariç; geri kazanılmış su 11,95 TL/m³).
    3. **Yasal Zorunluluk (Deadline):** 27.12.2024 tarihli Resmi Gazete'de (No. 32765) yayımlanan **Su Verimliliği Yönetmeliği** uyarınca OSB'ler ve Ek-2 NACE listesindeki 50+ çalışanlı fabrikalar **27 Aralık 2029'a kadar "Yeşil Su Verimliliği Belgesi"** almak zorundadır.

---

## 4. Çözüm ve Değer Önerisi
- **Tek Cümlelik Değer Önerisi:** Sanayi şirketleri, OSB yönetimleri ve yeşil finansman sağlayan bankalar için; iklim projeksiyonlarını ve yerel su verilerini kullanarak **fabrika bazında gelecekteki su kesintisi riskini (TL) tahmin eden, yeni yatırımlar için en güvenli lokasyonu seçen ve mevcut fabrikalar için bütçe kısıtlı en kârlı su verimliliği önlem portföyünü (ROI + 2029 Belgesi uyumu) optimize eden** yapay zeka karar platformu.
- **Neden seçildi:** Su kıtlığını, kıtlıktan milyonlarca TL üretim kaybı yaşayacak ve 2029'a kadar belge almak zorunda olan sanayiciye kendi kârıyla çözdürür; hem ekolojik etki (m³ tasarruf) hem B2B gelir modeli hem de metodolojik olarak savunulabilir bir yapay zeka çekirdeği (şeffaf indeks + etiketli ML + deterministik optimizasyon) sağlar.

---

## 5. Ürün Akışı: Tek Ekranda 2 Sekmeli Mimari

### Sekme 1: Yatırım & Yer Seçimi (Türkiye 639 Alt-Havza Haritası + SHAP)
- **Hedef Kullanıcı:** Yeni fabrika kuracak sanayi şirketleri, yatırım ajansları (İZKA vb.), OSB yönetimleri, proje finansmanı veren bankalar.
- **Girdiler:**
  - Sektör seçimi (Gıda & İçecek, Tekstil, Kimya, Metal/Makine, Elektrik/Enerji, Maden, Yarı İletken, Genel).
  - Hedef yıl (Baseline, 2030, 2050, 2080) ve İklim Senaryosu (İyimser `OPT`, Normal `BAU`, Kötümser `PES`).
  - Aday OSB / lokasyon karşılaştırma seçimi (örn. İzmir Kemalpaşa OSB, İzmir Aliağa OSB, Manisa OSB, Bursa OSB, Konya OSB, Adana Hacı Sabancı OSB, Gaziantep OSB, Ankara ASO OSB — veya haritadan herhangi bir alt-havzaya tıklama).
- **Çıktılar:**
  1. **Etkileşimli Türkiye Su Stresi Haritası (Leaflet + GeoJSON):** Türkiye'nin 639 alt-havzası (`Aq40` GDB'den çıkarılmış) seçilen yıl/senaryoya göre renklendirilir; üzerinde önemli OSB'ler ve İzmir'in 5 barajının canlı İZSU doluluk kartları gösterilir.
  2. **Aday Lokasyon Karşılaştırma Tablosu ve Öneri:** Seçilen aday bölgelerin **şeffaf bileşik risk skoru (0–100)**, **Beklenen Yıllık Kısıt/Kesinti Günü (P10 / P50 / P90 aralığı)**, yeraltı suyu düşüş trendi (`gtd`), SPEI-12 kuraklık trendi ve sektörel ağırlıklı risk (`w_awr_*`) sıralaması → *"Yatırım için en güvenli bölge: X (Neden: ...)"*.
  3. **Katkı Ayrıştırma Paneli:** (a) Bileşik indeksin **şeffaf ağırlık kırılımı** (her bileşenin skora katkısı formülüyle), (b) XGBoost yanlılık-düzeltme modelinin **SHAP** katkıları (hangi iklim değişkeni düzeltmeyi ne kadar sürüklüyor).
  4. **CMIP6 İklim Suyu Dengesi Zaman Serisi (2026–2050):** 7 CMIP6 modelinin dağılımından üretilen P10–P50–P90 yıllık net su dengesi (`P - ET₀`) grafiği.

### Sekme 2: Mevcut Fabrika Risk & ROI Simülatörü (2029 Belgesi + Önlem Optimizasyonu)
- **Hedef Kullanıcı:** Mevcut fabrika yöneticileri, sürdürülebilirlik/operasyon müdürleri, leasing/kredi kurumları, enerji/su danışmanları.
- **Girdiler:**
  - Tesis Lokasyonu / OSB seçimi (Sekme 1'den devralınabilir) ve Sektör (NACE).
  - Yıllık Su Tüketimi (`m³/yıl`, varsayılan: 150.000 m³) ve Proses Dağılımı (Sektöre göre otomatik gelir, kullanıcı değiştirebilir: Soğutma %, Proses/Yıkama %, Kazan/Buhar %, Evsel %).
  - **Su Kaynağı:** `Şebeke (İZSU 403,79 TL/m³)` / `OSB Şebeke` / `Kendi Yeraltı Kuyusu (Pompaj elektriği + %63 tahsis kesintisi riski)` / `Karma`.
  - Fabrikanın 1 Günlük Üretim Durma Maliyeti (`TL/gün`, varsayılan: 750.000 TL) ve Yatırım Bütçesi Kısıtı (`CAPEX TL`, örn. 3.500.000 TL).
  - **"Örnek Tesis Verisi Yükle"** butonu — kendi açık şemamıza (`data/schema/facility.schema.json`) uyan örnek dosyayı tek tıkla doldurur. Aynı şema ile **JSON/CSV dışa aktarma** yapılır; herhangi bir ayak izi platformu bu çıktıyı kendi envanterine eşleyebilir (iddia: *eşlenebilirlik*, entegrasyon değil).
- **Çıktılar:**
  1. **"Hiçbir Şey Yapmama" (Do-Nothing) Maliyet Kartı (2030/2050):** Yıllık su faturası + kuraklıkta beklenen kısıt günlerinden doğan **üretim kaybı (TL/yıl, P10–P50–P90 aralığı)** + 27.12.2029 Yeşil Su Verimliliği Belgesi uyumsuzluk riski.
  2. **Optimum Önlem Portföyü Tablosu (Bütçe Kısıtlı Optimizasyon):** Bakanlık (SYGM) NACE rehberleri ve IFC veritabanındaki 12+ endüstriyel önlem arasından, girilen CAPEX bütçesini aşmadan **5 yıllık NPV ve su tasarrufunu maksimize eden** seçilmiş önlemler listesi (yatırım maliyeti, proses bazlı azalan verimli net m³ tasarrufu, yıllık TL kazanç, geri ödeme süresi - ay/yıl).
  3. **Nakit Akışı ve Başabaş (Payback) Grafiği:** 5 yıllık kümülatif nakit akışı (yatırım vs su faturası tasarrufu + önlenen üretim duruşu zararı).
  4. **2029 Yeşil Su Verimliliği Belgesi Kademesi & Rapor Dışa Aktarımı:** Seçilen portföyle tesisin Mavi / Yeşil / Turkuaz kademelerinden hangisine ulaştığı; raporun `JSON` / `CSV` / yazdırılabilir formatta indirilmesi.
  5. **Gemini AI Yönetim Kurulu Özeti:** Hesaplanan kesin JSON çıktısını kaynak göstererek özetleyen, sayı uydurmayan yönetici raporu (API kapalıysa deterministik şablon yedekli).

---

## 6. Teknik Mimari ve Yapay Zeka Çekirdeği

- **Dil ve Ortam:** Python 3.12 (`uv`, `.venv`), CPU-only.
- **Web Çatısı:** **FastAPI** (`src/ekozeka26/app.py`, `127.0.0.1:8000` üzerinde) + Tek Sayfa Web Arayüzü (`src/ekozeka26/static/index.html` — Tailwind CSS + Leaflet.js + Chart.js; temiz, hızlı, sıfır build-step kırılganlığı).
- **Yapay Zeka ve Hesaplama Modülleri (`src/ekozeka26/`):**
  > **Metodoloji ilkesi:** İklim projeksiyonu fizik/meteoroloji işidir; ML onu taklit etmez, **eksik kalan yerleri tamamlar**. Risk skoru kara kutu değil, her adımı denetlenebilir şeffaf bir indekstir. Bu ilke veri bilimi jürisine karşı en güçlü savunmadır.

  1. `data_pipeline.py` — **Ham veri anlık görüntüsü + ETL (Kısıtlar ve V&V Kuralları)**
     - `/tmp` silinebileceği için Aqueduct'in **yalnızca Türkiye satırları** (`baseline_annual`: 639 satır, `baseline_monthly`: 116 satır, `future_annual`: 116 satır), GDB'nin Türkiye poligonları ve yerel iklim/İZSU dosyaları (`era5.json`, `cmip6.json`, `cm4.json`, `flood.json`, `izsu.html`, `izsu_aylik.html`, `baraj.csv`, `gunluk.csv`, `tarife.html`) `data/raw/` altına kalıcı olarak kopyalanır (250 MB ZIP repoya girmez; filtrelenmiş `data/raw/` ~4 MB girer).
     - **KRİTİK JOIN VE GDB KURALI (V&V Bulgusu):**
       - GDB okunurken tüm dünyayı (68.506 poligon) belleğe yüklememek için **mutlaka** `pyogrio.read_dataframe(gdb, layer="baseline_annual", where="gid_0 = 'TUR'")` kullanılır (1,99 sn, 1,2 MB RAM).
       - `baseline_annual` tablosundaki **639 Türkiye biriminin tekil anahtarı `string_id`**'dir (`pfaf_id` + il `gid_1` + akifer `aqid`). Bu 639 birim **117 tekil `pfaf_id`** hidrolojik havzasını paylaşır.
       - `future_annual` ve `baseline_monthly` tabloları (Türkiye için 116 tekil `pfaf_id`) `baseline_annual` üzerine **`pfaf_id` üzerinden çoka-bir (`m:1`, left join)** ile bağlanır; `string_id` birincil poligon kimliği olarak korunur (1 adet `-9999` kıyı/ada poligonu komşu havza ortalamasıyla doldurulur).
     - **Open-Meteo Rate-Limit (`HTTP 429`) Koruması:** Open-Meteo `climate-api` çok yıllık/7 modelli sorgularda ağırlık kotası nedeniyle 2. istekte `HTTP 429` döndürmektedir. Bu nedenle `data_pipeline.py` **öncelikle yerel önbellekteki (`data/raw/`) doğrulanmış iklim ve Aqueduct projeksiyonlarını** kullanır; ek OSB sorgusu gerekirse tek bir virgüllü toplu koordinat isteği (`latitude=lat1,lat2...`) ve 3 sn zaman aşımı + yerel fallback ile çalışır, asla döngü içinde çoklu ağır API çağrısı yapmaz.
     - **Takvim normalizasyonu & Kalite kontrol:** 360 günlük veya 2049 sonunda biten (`EC_Earth3P_HR` gibi) CMIP6 serilerinde `null` ve takvim hizalaması temizlenir; birim tutarlılığı (mm ↔ m³) doğrulanır.

  2. `climate_engine.py` — **ET₀, dağılımsal yanlılık düzeltme (QDM), topluluk belirsizliği**
     - **ET₀:** ERA5'te mevcut FAO-56 `et0_fao_evapotranspiration` doğrudan kullanılır; CMIP6'da `null` olan `ET₀` **FAO-56 Penman-Monteith** veya **Hargreaves-Samani** (1985) ile hesaplanır:
       $$ET_0 = 0.0023 \times (T_{\text{mean}} + 17.8) \times \sqrt{\max(0, T_{\max} - T_{\min})} \times R_a$$
     - **Dağılımsal Yanlılık Düzeltme (QDM):** CMIP6 serbest koşulu (free-running) bir iklim simülasyonu olduğu için ERA5 ile **takvim günü/ayı (`YYYY-MM`) bazında eşleştirilemez** (V&V testinde takvim eşleştirmesi gürültü üretir). Bu yüzden literatür standardı olan **Quantile Delta Mapping (QDM)** (Cannon vd. 2015) ile CMIP6'nın **olasılık dağılım kantilleri (quantiles)** ERA5 referans dağılımına kalibre edilir. Kısa serilerde yedek: delta-change.
     - **Belirsizlik:** 7 model × 3 senaryo (`OPT`, `BAU`, `PES`) → **P10 / P50 / P90** ve "modellerin %X'i aynı yönde" **mutabakat oranı**.

  3. `drought_index.py` — **SPI / SPEI (literatür standardı)**
     - Aylık yağış ve `P − ET₀` serilerinden **SPI-3/12** (McKee vd. 1993) ve **SPEI-3/12** (Vicente-Serrano vd. 2010); log-logistic dağılım uydurması.
     - Kuraklık sınıfları (hafif/orta/şiddetli/aşırı), trend eğimi, mevsimsel genlik ve 2021/2024/2025 kurak yıllarının tarihsel doğrulaması.

  4. `risk_index.py` — **Şeffaf bileşik endüstriyel kesinti riski**
     - Bileşenler ve ağırlıklar açık: Aqueduct `bws/bwd/gtd/drr/iav/sev` + sektör ağırlıklı risk (`w_awr_*`) + SPEI trendi + yeraltı bağımlılık oranı + iklim su açığı trendi (`Δ(P−ET₀)`).
     - Çıktı: **0–100 risk skoru**, **beklenen yıllık kesinti günü (P10/P50/P90)** ve **her bileşenin katkısı**.
     - Kural tabanlıdır; tamamen açıklanabilir, kara kutu değildir.

  5. `ml_engine.py` — **ML'in gerçekten etiketli ve senkronize olduğu işler (V&V ile doğrulandı)**
     - **(a) XGBoost Mevsimsel/Mekânsal Hidrolojik Ölçek İndirme (Annual-to-Monthly Peak Downscaler):**
       - *Problem:* Gelecek projeksiyonları (`Aqueduct future_annual` 2030/2050/2080) yalnızca **kaba yıllık ortalama** su stresini (`ws_x_r`) verir; oysa sanayi su kesintileri **yaz/sonbahar kurak pik aylarında (Temmuz–Ekim)** yaşanır.
       - *Etiketli Veri:* Türkiye'nin 116 havzasının 12 aylık gerçek gözlenen su stresi paneli (`Aqueduct40_baseline_monthly` + `baseline_annual`, `1.392` havza-ay satırı).
       - *Doğrulama:* **5-katlı `GroupKFold(n_splits=5)` (`pfaf_id` havza bazlı)** ile mekânsal veri sızıntısı sıfırlanır. V&V ön testinde doğrulanan gerçek skorlar: Naive (Kaba Yıllık) `MAE = 0.487 (R² = -0.005)` → Doğrusal Regresyon (Ridge) `MAE = 0.319 (R² = 0.640)` → **XGBoost Downscaler `MAE = 0.165, RMSE = 0.429, R² = 0.806`** (hatada %66 düşüş).
       - *Ek Hidrolojik Backtest:* `era5.json` + `flood.json` (1984–2025, 504 gerçek senkronize ay) üzerinde meteorolojik su açığından (`P - ET₀`, gecikmeli yağış/sıcaklık) Gediz nehir debisi/yüzey suyu yanıtı (`2015–2025` test `R² ≈ 0.65` vs Naive `0.18`).
       - *SHAP:* `shap.TreeExplainer` ile bir havzada yaz pik su stresini hangi fiziksel sürücülerin (`bws_raw`, `sev_raw`, `gtd_raw`, `iav_raw`, `drr_raw`, mevsim) ne kadar artırdığı <50 ms'de açıklanır.
     - **(b) KMeans havza arketipleri:** 639 alt-havza birimi fiziksel ve sektörel davranış kümesine ayrılır → *"Sizin OSB'niz Türkiye'deki şu havza arketipiyle aynı risk profilinde"*.
     - **Döngüsel hedeften ve serbest-koşulu GCM takvim eşleştirmesinden kaçınma:** Aqueduct'in gelecek yıllık değeri hedef yapılmaz; CMIP6 serbest koşulu serisi ERA5 ile `YYYY-MM` bazında regresyona sokulmaz (dağılımsal düzeltme QDM ile yapılır).

  6. `anomaly.py` — **İZSU & Gediz Hidrolojik Anomali Tespiti (Gerçek Çok-Kaynaklı Veri)**
     - **V&V Veri Kuralı:** `baraj.csv` (14.10.2026) ve `gunluk.csv` tek günlük anlık kesitlerdir; `izsu.html` ise `06.11.2026` ve `07.11.2025` kesitlerini içerir. **Gerçek zaman serisi** `izsu_aylik.html` içindeki **137 aylık üretim kaydından (2025 yılı 12 ay × 11 baraj/kuyu tesisi)** ve `flood.json` / `era5.json` (1984–2025 Gediz günlük debi ve kuraklık serisi) verilerinden çıkarılır!
     - **Isolation Forest + Kesit Deltası:**
       1. `izsu_aylik.html` 2025 aylık serisinde **Isolation Forest** ile baraj çöküşü ve yeraltı kuyusu aşırı yüklenme anomalilerini yakalar (Gerçek bulgu: Kasım 2025'te Tahtalı üretimi **6,91 Mm³ → 1,62 Mm³'e (-%76,5)** çökerken, Göksu ve Halkapınar kuyuları yıllık zirveye çıkarak İzmir arzının **>%62'sini yeraltından** karşılamıştır).
       2. `baraj.csv` (14 Ekim 2026) → `izsu.html` (6 Kasım 2026) **23 günlük kesit farkından** hızlı baraj düşüş uyarılarını üretir (örn. Balçova Barajı'nda 23 günde **-%7,43 puan** düşüş; Gördes ve Balçova'da günlük üretimin **0 m³/gün**e inmesi).

  7. `roi_optimizer.py` (**Bütçe Kısıtlı Önlem Optimizasyonu**):
     - SYGM NACE rehberleri ve IFC vakalarından derlenmiş 12 somut endüstriyel önlem kataloğu (Soğutma kulesi kapalı devre dönüşümü, RO/UF atıksu geri kazanımı, durulama suyu kaskad/geri kazanımı, basınçlı otomatik nozullar, CIP optimizasyonu, akustik/IoT kaçak tespiti, yağmur suyu hasadı, kuru temizleme/süpürme prosesi, kondens geri kazanımı, ISO 46001 dijital sayaç izleme vb.).
     - **Azalan Verim (Multiplicative Savings) Kuralı:** Aynı alt-prosese (`p ∈ {cooling, process, boiler, domestic}`) uygulanan önlemlerin toplam tasarrufu asla toplanmaz; $S_p = 1 - \prod_{i \in M_p} (1 - r_i)$ ile hesaplanır ve sektörel teknik üst sınırla ($\le \%78$) kırpılır.
     - **Optimizasyon:** Verilen `budget_tl` kısıtı altında 5 yıllık NPV'yi maksimize eden önlem alt kümesini (0-1 Knapsack / MILP kesin çözümü) bulur.
  8. `llm_agent.py` (**Gemini AI Raporlayıcı + Offline Fallback**):
     - `google-genai` SDK (`.env` içinden `GEMINI_API_KEY`, model: `gemini-2.5-flash`).
     - Yalnızca hesaplama modüllerinin (`risk_index`, `roi_optimizer`) ürettiği kesin JSON verisini alır; sistem komutunda sayı uydurması yasaklanır.
     - Anahtar yoksa, kota dolarsa veya 4 saniye içinde yanıt gelmezse deterministik uzman şablonuna (`fallback_report`) kesintisiz düşer.

---

## 7. Veri Kaynakları ve Önbellek (Offline Fallback) Durumu

| Kaynak | Dosya / Erişim | Lisans | Durum |
|---|---|---|---|
| WRI Aqueduct 4.0 (Baseline + Future 2030/2050/2080 + GDB Poligon) | `/tmp/opencode/ekozeka_tests/aq.zip` → `data/processed/turkey_basins.geojson` & `.parquet/.csv` | CC BY 4.0 | İndirildi, doğrulandı (639 TR alt-havzası) |
| Open-Meteo ERA5 (1940–2025) & CMIP6 (2020–2050, 7 model) | `/tmp/opencode/ekozeka_tests/era5.json`, `cmip6.json` → `data/cache/climate_osb.json` | CC BY 4.0 (Demo/Non-commercial) | İndirildi, önbelleklenecek |
| İZSU Baraj Doluluk, Günlük Üretim ve Haziran 2026 Sanayi Tarifesi | `/tmp/opencode/ekozeka_tests/izsu.html`, `baraj.csv`, `gunluk.csv`, `tarife.html` → `data/fallback/izsu_snapshot.json` | Kamu / Açık Veri | İndirildi, canlı + fallback hazır |
| Tarım ve Orman Bakanlığı SYGM NACE Rehberleri + Gediz Tahsis Planı + IFC | `/tmp/opencode/ekozeka_tests/nace.pdf`, `tekstil.pdf`, `s03.pdf`, `ifc.pdf` → `data/processed/measures_catalog.json` | Atıflı kullanım (PDF dağıtılmaz, yalnızca katsayı tablosu) | İndirildi, kataloglanacak |

---

## 8. Harici Servisler — Organizasyon Yöneticilerine Teyit Listesi
Kullanıcının organizatörlere sorup teyit edebileceği tam liste:
1. **WRI Aqueduct 4.0 Açık Veri Seti** (Creative Commons BY 4.0 — çevrimdışı işlenmiş alt-havza verisi).
2. **Open-Meteo ERA5 & CMIP6 İklim API'si** (Ücretsiz, açık erişim iklim projeksiyon verisi).
3. **İZSU (İzmir Su ve Kanalizasyon İdaresi) Kamuya Açık Baraj ve Tarife Verileri.**
4. **Google Gemini API (`gemini-2.5-flash`)** — Hesaplanan sayısal sonuçlardan yönetici özeti metni üretmek için (opsiyonel katman, çevrimdışı yedeği mevcut).
5. **Açık kaynak Python kütüphaneleri:** `fastapi`, `uvicorn`, `xgboost-cpu` (CUDA/GPU bağımlılığı çekmemesi için `xgboost` yerine **zorunlu olarak `xgboost-cpu`**), `shap`, `scikit-learn`, `pandas`, `numpy`, `geopandas`/`pyogrio`, `scipy`, `beautifulsoup4`, `httpx`.

> **Not:** Hiçbir ticari platformun (CarbonEmit, Blueit, 3pmetrics vb.) API'si, müşteri verisi veya hesabı kullanılmaz. Tüm veri açık kaynaklardan ve kullanıcı girdisinden gelir.

---

## 9. Zorunlu Edge-Case (Uç Durum) Korumaları
1. **Coğrafi Sınır Koruması:** Türkiye'nin 639 alt-havzası dışındaki veya deniz üzerindeki tıklamalarda model çalıştırılmaz, kullanıcıya en yakın kara alt-havzası önerilir.
2. **CMIP6 `ET₀` Eksikliği:** API'den `null` gelen buharlaşma verisi Hargreaves-Samani denklemiyle sıcaklık ve radyasyondan hesaplanır.
3. **API Rate-Limit (HTTP 429) ve İnternet Kesintisi:** Tüm ana OSB'ler ve 639 alt-havza yerel önbellekten (`data/processed/`) <100 ms içinde sunulur; canlı API veya İZSU erişimi başarısız olursa sistem çökmez, `son doğrulanmış veri: 6 Kasım 2026` etiketiyle yerel veriden çalışır.
4. **%100'ü Aşan Tasarruf Hatası Engeli:** Önlem tasarrufları proses bazında çarpımsal ($1 - \prod(1-r_i)$) birleştirilir ve sektörel üst sınırla (%78) sınırlandırılır.
5. **Kuyu Suyu vs Şebeke Suyu Ayrımı:** "Kendi Kuyusu" seçildiğinde su birim fiyatı düşük (pompaj elektriği + atıksu) alınır; ancak Gediz/yeraltı suyu düşüşü nedeniyle **kuraklıkta %63 tahsis kesintisi → üretim durma zararı** hesaba katılarak gerçek ekonomik risk gösterilir.
6. **Sıfır/Geçersiz Girdi Koruması:** Tüketim $\le 0$, bütçe $< 0$ veya proses yüzdeleri toplamı $\ne 100$ olduğunda Pydantic/FastAPI doğrulaması anlamlı hata veya otomatik normalizasyon uygular; bütçe çok düşükse yalnızca "düşük/sıfır maliyetli bakım ve kaçak kontrolü" önerilir.
7. **Belirsizlik Bandı:** Hiçbir gelecek tahmini tek bir kesin sayı olarak sunulmaz; daima **P10 (İyimser) / P50 (Beklenen) / P90 (Kötümser)** aralığı olarak gösterilir.
8. **LLM Halüsinasyon Engeli:** Gemini hiçbir çarpma/bölme yapmaz; yalnızca Python motorunun ürettiği JSON rakamlarını metne döker.
9. **Takvim Uyumsuzluğu:** 360 günlük takvimli CMIP6 modelleri 365/366 güne normalize edilir; ay/gün hizalaması bozulursa o model topluluktan çıkarılır ve bu arayüzde "model dışlandı" notuyla gösterilir.
10. **Mekânsal Veri Sızıntısı (Spatial Leakage):** ML eğitiminde rastgele `train_test_split` yerine **GroupKFold (havza bazlı)** kullanılır; komşu havzaların test setine sızması engellenir.
11. **`/tmp` Temizlenmesi:** Ham veri `data/raw/` altında proje içinde tutulur; `data_pipeline.py` yeniden üretilebilir olmalıdır (`uv run python -m ekozeka26.data_pipeline`).
12. **Küçük Örneklem (639 havza):** Model karmaşıklığı düşük tutulur (`max_depth ≤ 4`, erken durdurma); baseline'dan anlamlı fark yoksa model **kullanılmaz**, şeffaf indeks tek başına sunulur — bu bir başarısızlık değil, dürüstlüktür.

---

## 10. Canlı Demo ve Sunum Akışı (3–5 Dakika)
1. **0:00–0:40 | Kanca & Doğru Çerçeve:** İzmir barajlarının gerçek ağırlıklı doluluğu (%34, Gördes %28). *"Suyu en çok tarım tüketir ama kuraklığın faturasını en ağır sanayi öder: Gediz'de sanayi suyunun %100'ü yeraltından gelir, kuraklıkta tahsis %37'ye düşer, şebeke suyu 404 TL/m³'tür ve 27 Aralık 2029'a kadar Yeşil Su Verimliliği Belgesi zorunludur."*
2. **0:40–1:45 | Canlı Demo Perde 1 — Yer Seçimi & Risk Ayrıştırma (Sekme 1):** Türkiye 639 alt-havza haritasında 2050 su stresi. Yeni bir tekstil/gıda yatırımı için İzmir Kemalpaşa, Manisa, Bursa ve Konya OSB karşılaştırması. **Şeffaf bileşik indeksin ağırlık kırılımı** (*"Risk skorunun 74 çıkmasının nedeni: yeraltı düşüşü +28, SPEI kuraklık trendi +19, sektörel tahsis baskısı +15..."*) + **XGBoost yanlılık-düzeltme modelinin SHAP katkıları** ve 7 iklim modelinin P10–P90 bandı. Her sayı formülüyle ve kaynağıyla ekranda görünür.
3. **1:45–3:00 | Canlı Demo Perde 2 — Mevcut Fabrika ROI & 2029 Belgesi (Sekme 2):** Kemalpaşa OSB'deki bir fabrikanın **"Örnek Tesis Verisi Yükle"** butonuyla tek tıkla doldurulması. "Kendi kuyusu" ve "İZSU şebeke" senaryolarında hiçbir şey yapmamanın yıllık milyonlarca TL üretim duruşu zararı. 3,5 Milyon TL bütçe kısıtıyla optimizasyon motorunun seçtiği önlemler, geri ödeme süresi, **Yeşil Belge** kazanımı ve Gemini yönetim kurulu özeti + rapor dışa aktarımı.
4. **3:00–3:45 | İş Modeli ve Ölçek:** Ayak izi platformları geçmişi doğrular, AquaSanayi AI geleceğin yatırım kararını üretir (veri bağımlılığı yok, yalnızca eşlenebilir açık şema). Müşteriler: 416 OSB'deki 68.000 fabrika, OSB yönetimleri ve yeşil kredi veren bankalar.
5. **3:45–4:15 | Sınırlamalar & Kapanış:** Veri çözünürlüğü, şeffaf varsayımlar ve GitHub reposu.

---

## 11. Kapsam Dışı (22 Saatte Yapılmayacaklar)
- Kullanıcı girişi / kimlik doğrulama (Auth), ödeme ekranı, çoklu kullanıcı veritabanı.
- Gerçek zamanlı fiziksel IoT sensör / PLC donanım bağlantısı.
- Sıfırdan küresel iklim/hidroloji modeli eğitmek (CMIP6 ve Aqueduct çıktıları girdi olarak kullanılır).
- Tam kapsamlı ISO 14046 su ayak izi muhasebesi/doğrulaması (bu bir denetim ürünüdür; bizim kapsamımız ileriye dönük risk ve yatırım kararıdır). Tesis verisi kullanıcı girdisi veya kendi açık şemamıza uyan dosyadan gelir; hiçbir ticari platformdan veri alınmaz.

---

## 12. Karar Kaydı
| # | Karar | Gerekçe |
|---|---|---|
| K1 | Python 3.12 + `uv` + FastAPI + Vanilla JS/Tailwind/Leaflet/Chart.js | CPU-only ortamda en hızlı, sıfır derleme hatası çıkaran, görsel olarak en etkileyici ve tek komutla çalışan mimari. |
| K2 | Fikir: Endüstriyel Su Kıtlığı Risk, Yer Seçimi ve ROI Optimizasyonu | Hem ekolojik etki (m³ su tasarrufu) hem de 2029 belge zorunluluğu ve 404 TL/m³ su fiyatıyla net B2B ödeme isteği sağlıyor. |
| K3 | Coğrafi kapsam: **ulusal tarama** (639 poligon / 116 tekil `pfaf_id`) + **Ege–Marmara–Konya odak koridoru** (7 OSB) + **İzmir/Gediz canlı derinliği** | Aqueduct GDB/CSV tüm Türkiye'yi kapsıyor; odak koridorda yerel veri/OSB profili ve doğrulama var. Ulusal katman düşük çözünürlüklü ön tarama olarak etiketlenir; "639 bağımsız hidrolojik havza" iddia edilmez. |
| K4 | Arayüz: Tek ekranda 2 sekme (1: Yer Seçimi & SHAP, 2: Mevcut Fabrika ROI & 2029 Belgesi) | Hem görsel harita/ML etkisini (Sekme 1) hem de tekrarlayan B2B gelir modelini (Sekme 2) 3 dakikada göstermeyi sağlıyor. |
| K5 | Yapay Zeka: **Fizik-öncelikli + ML destekli** hibrit. Şeffaf bileşik risk indeksi (Aqueduct + SPEI + su dengesi); XGBoost **yanlılık düzeltme/ölçek indirme** (GroupKFold + SHAP); KMeans havza arketipleri; Isolation Forest İZSU anomalileri; MILP/Knapsack ROI; Gemini yalnızca raporlayıcı | İklim projeksiyonu fizik işidir; ML onu taklit etmez, eksik kalan yeri tamamlar. "Aqueduct'in gelecek değerini tahmin etme" döngüsel hedef hatası ortadan kalkar; her adım etiketli, doğrulanabilir ve açıklanabilir olur. LLM matematik yapmaz. |
| K6 | **CarbonEmit ve benzeri ticari platformlardan tam bağımsızlık.** Veri girişi kendi açık şemamız (`facility.schema.json`) + örnek dosya; çıkış JSON/CSV dışa aktarım | Ticari SaaS'ın müşteri verisi/API'si erişilebilir değildir; sahte entegrasyon iddiası jüride itibar kaybı riskidir. "Eşlenebilir açık şema" dürüst ve savunulabilir konumlandırmadır; ürünü dışa bağımlılıktan kurtarır. |
| K7 | Tüm dış veri ve API'ler için yerel önbellek (offline fallback) zorunlu | Canlı demoda internet/API/rate-limit kaynaklı çökme riskini sıfırlamak. |

---

## 13. Kapsam ve Çözünürlük Sınırları (Dürüstlük Notu)
- **639 poligon ≠ 639 bağımsız havza:** Aqueduct 4.0 GDB'deki 639 poligon, **116 tekil `pfaf_id`** hidrolojik havzasının il/akifer kesişimidir. Su stresi (`bws`) çoğu `pfaf_id` içinde sabittir; 639 sayısı harita poligon sayısıdır, bağımsız model birimi sayısı değildir.
- **Tier 0 — Ulusal tarama:** Türkiye geneli yalnızca Aqueduct 4.0 göstergeleri + şeffaf indeks ile taranır. Bu katman **yatırım ön taramasıdır**, yerinde ölçüm değildir.
- **Tier 1 — Odak koridor (7 OSB):** İzmir Kemalpaşa, İzmir Aliağa, İzmir Atatürk, Manisa, Bursa, Kocaeli Gebze, Konya. Bu OSB'lerde yerel tarife/OSB profili ve (İzmir/Gediz'de) canlı İZSU/SYGM verisi kullanılır.
- **Tier 2 — İzmir/Gediz canlı:** İZSU baraj/üretim serileri, SYGM Gediz Tahsis Planı ve gerçek fabrika vakaları; en yüksek doğrulama katmanı.
- **İklim referansı:** ERA5/CMIP6 serisi şu an tek referans noktasından (İzmir, ~38.49N/27.11E) alınır; OSB'ler arası fark Aqueduct SSP projeksiyonu + enlem offseti ile üretilir. Bölgesel iklim çapaları (Bursa/Kocaeli, Konya/Ankara) sonraki sürümde eklenecektir; bu nedenle Bursa/Konya P−ET₀ eğrisi şu an ikincil güvenilirliktedir.
- **SPEI/SPI:** Gerçek SPI/SPEI serisi tek referans noktası (İzmir/Gediz) için hesaplanır; havza kartındaki `spei12_trend` bir **proxy**'dir ve UI'de "SPEI proxy" olarak etiketlenir.
- **UI güven rozetleri:** "Odak koridor · yerel veri" ve "Ulusal · Aqueduct tarama" etiketleri, kullanıcıya hangi katmanda olduğunu söyler.
- **İZSU canlı/offline protokolü:** `/api/izsu-live` kaynak zinciri: taze canlı önbellek (`data/cache/izsu_live_snapshot.json`, 6 saat TTL) → doğrulanmış `data/processed/izsu_snapshot.json` → `data/fallback/izsu_snapshot.json`. Canlı çekim `uv run python -m ekozeka26.izsu_source --refresh` ile yapılır; başarısız olursa API çökmez, `source_mode`/`fallback_reason` ile yerel veriye düşer. Canlı sayfa yalnızca baraj/kuyu doluluk kesiti içerdiği için aylık üretim ve 2026 tarifeleri doğrulanmış snapshot'tan korunur.
