# STATE

## Mimari Özeti
- **Proje:** AquaSanayi AI — Sanayi tesisleri ve yatırımcılar için İklim-Tabanlı Su Kıtlığı Risk Tahmini, Yer Seçimi ve Yatırım (ROI / 2029 Yeşil Su Verimliliği Belgesi) Optimizasyon Platformu.
- **Yığın:** Python 3.12 (`uv` + `.venv`, CPU-only), FastAPI (`127.0.0.1:8000`), Tek Sayfa Arayüz (Tailwind CSS + Leaflet.js Türkiye 639 alt-havza haritası + Chart.js, 2 sekme).
- **AI & Hesaplama Çekirdeği (Fizik-öncelikli + ML destekli, 8 modül):**
  1. `data_pipeline.py`: Ham veri snapshot'ı (`data/raw/`) + WRI Aqueduct 4.0 (CSV + GDB 639 TR alt-havzası) + Open-Meteo ERA5/CMIP6 + İZSU canlı/fallback; takvim normalizasyonu ve kalite kontrolü.
  2. `climate_engine.py`: FAO-56 Penman-Monteith / Hargreaves-Samani `ET₀`, **QDM** yanlılık düzeltmesi, 7 model × 3 senaryo topluluk belirsizliği (P10/P50/P90 + mutabakat oranı).
  3. `drought_index.py`: **SPI-3/12** ve **SPEI-3/12** (log-logistic), kuraklık sınıfları ve trend eğimi.
  4. `risk_index.py`: Şeffaf **bileşik endüstriyel kesinti risk skoru (0–100)** + bileşen katkıları (kara kutu değil).
  5. `ml_engine.py`: XGBoost **yanlılık düzeltme/ölçek indirme** (GroupKFold, MAE/RMSE/R², SHAP) + **KMeans havza arketipleri**. Aqueduct'in gelecek değeri hedef yapılmaz (döngüsel hedef yok).
  6. `anomaly.py`: **Isolation Forest** ile İZSU baraj/üretim anomalileri (gerçek canlı veri).
  7. `roi_optimizer.py`: SYGM/IFC kataloglu 12 önlem üzerinde proses bazlı azalan verimli ($1-\prod(1-r_i)$) ve bütçe kısıtlı (0-1 Knapsack) NPV/ROI optimizasyonu + kuyu/şebeke ayrımı + 2029 Belgesi puanlaması. **Ticari platform entegrasyonu yoktur.**
  8. `llm_agent.py`: Gemini (`gemini-2.5-flash`) yapılandırılmış yönetici özeti + deterministik çevrimdışı yedek (offline fallback).

## Aktif Görev
- **Faz: WBS-0 → WBS-8 tüm iş paketleri tamamlandı ve doğrulandı.**
- Uygulama `bash scripts/run.sh` (veya `uv run uvicorn ekozeka26.app:app --host 127.0.0.1 --port 8000`) ile canlı sunuma hazırdır.

## Tamamlanan Adımlar
- [x] Proje iskeleti (`uv`, `pyproject.toml`, `src/ekozeka26/`, `.gitignore`)
- [x] Hackathon bilgileri, jüri profili ve çalışma modeli belirlendi
- [x] Araştırma: güncel ekoloji problemleri + kazanan hackathon projeleri (`RESEARCH.md`)
- [x] Su kıtlığı veri kaynakları canlı `curl` ile doğrulandı ve `/tmp/opencode/ekozeka_tests/` altına indirildi (`aq.zip`, `era5.json`, `cmip6.json`, `izsu.html`, `baraj.csv`, `gunluk.csv`, `tarife.html`, `nace.pdf`, `tekstil.pdf`, `ifc.pdf`)
- [x] Kırmızı takım (red-team) pazar/varsayım testi yapıldı ve tüm edge-case kuralları `SPEC.md`'ye işlendi
- [x] Fikir, kapsam ve 2 sekmeli mimari kullanıcı onayıyla `SPEC.md` içinde kilitlendi
- [x] Sunum sayıları, 4 dakikalık demo akışı ve jüri soru-cevap cephaneliği `SUNUM.md` içinde oluşturuldu
- [x] CarbonEmit bağımlılığı kaldırıldı; kendi açık tesis şeması + örnek dosya + JSON/CSV dışa aktarım kararı alındı
- [x] Yapay zeka çekirdeği **fizik-öncelikli + ML destekli** hibrite geçirildi (şeffaf indeks + XGBoost yanlılık düzeltme + KMeans + Isolation Forest)
- [x] WBS 9 iş paketine genişletildi (veri snapshot, backtest, `run.sh`/`.env.example`, prova + yedek video eklendi)

## Proje Yönetimi İlerleme Şablonu (WBS & Definition of Done)
> `build` oturumunda her görev tamamlandığında `Durum` sütunu `[x]` yapılacak, `git commit` atılacak ve yeni sayılar `SUNUM.md`'ye işlenecektir.

| ID | Faz / Görev | Çıktı Dosyaları | Kabul Kriteri (Definition of Done - DoD) | Doğrulama Komutu | Durum |
|---|---|---|---|---|---|
| **WBS-0** | Kurulum & Dosya Senkronizasyonu (~15 dk) | `SPEC.md`, `STATE.md`, `SUNUM.md`, `docs/RESEARCH.md`, `data/schema/facility.schema.json`, `pyproject.toml`, `.env.example` | Plan dosyaları proje köküne kopyalandı; paketler (`uv add fastapi uvicorn pandas numpy scikit-learn xgboost-cpu shap geopandas pyogrio shapely scipy httpx beautifulsoup4 google-genai python-dotenv pytest` — **CUDA çekmemesi için mutlaka `xgboost-cpu`**) hatasız kuruldu; `.env.example` oluşturuldu. | `uv run python -c "import fastapi, xgboost, shap, geopandas, sklearn"` | `[x]` |
| **WBS-1** | Veri Snapshot & ETL (~1,5 saat) | `src/ekozeka26/data_pipeline.py`, `data/raw/` (TR filtresi, ~4 MB), `data/processed/turkey_basins.geojson`, `turkey_basins.parquet`, `osb_profiles.json`, `measures_catalog.json`, `izsu_snapshot.json` | GDB `pyogrio.read_dataframe(..., where="gid_0 = 'TUR'")` ile 2 sn'de okundu; 639 poligon (`string_id` anahtarlı) üzerine `future_annual` ve `baseline_monthly` (116 `pfaf_id`) çoka-bir (`m:1`) birleştirildi (<5 MB GeoJSON); `era5.json`, `cmip6.json`, `cm4.json`, `flood.json`, `izsu.html`, `izsu_aylik.html`, `baraj.csv`, `gunluk.csv` `data/raw/` altına alındı; 12 SYGM/IFC önlemi kataloglandı; Open-Meteo `HTTP 429`'a karşı sıfır ağ bağımlılığıyla `data/raw/` üzerinden yeniden üretilebilir. | `uv run pytest tests/test_data_pipeline.py` + `rm -rf data/processed && uv run python -m ekozeka26.data_pipeline --offline` | `[x]` |
| **WBS-2** | İklim & Kuraklık Motoru (~1,5 saat) | `src/ekozeka26/climate_engine.py`, `src/ekozeka26/drought_index.py`, `data/processed/climate_osb.json`, `drought_indices.parquet` | FAO-56/Hargreaves `ET₀` hesaplanıyor; QDM **dağılımsal kantil düzeltmesi** ERA5 referansına uygulanıyor (`YYYY-MM` takvim eşleştirmesi yapılmaz); 7 modelden P10/P50/P90 + mutabakat oranı çıkıyor; SPI-3/12 ve SPEI-3/12 sınıfları üretiliyor. | `uv run pytest tests/test_climate_engine.py tests/test_drought_index.py` | `[x]` |
| **WBS-3** | Risk İndeksi, ML & Backtest (~2,5 saat) | `src/ekozeka26/risk_index.py`, `src/ekozeka26/ml_engine.py`, `src/ekozeka26/anomaly.py`, `data/processed/xgb_downscaler.json`, `data/processed/model_metrics.json` | Şeffaf bileşik skor (0–100) her bileşen katkısıyla dönüyor; **XGBoost Mevsimsel/Mekânsal Ölçek İndirme (Annual→Monthly Peak Downscaler, 1.392 havza-ay)** `GroupKFold(n_splits=5, groups=pfaf_id)` ile eğitildi (`R² ≈ 0.806`, `MAE ≈ 0.165` vs Lineer `0.319` vs Naive `0.487`) + ERA5/GloFAS (`flood.json`) hidrolojik backtest (`R² ≈ 0.65`); SHAP <50 ms; KMeans arketipleri; `anomaly.py` içinde `izsu_aylik.html` (137 aylık kayıt) + `flood.json` üzerinde Isolation Forest ve 23 günlük baraj deltası çalışıyor. Metrikler `SUNUM.md`'ye yazıldı. | `uv run pytest tests/test_risk_index.py tests/test_ml_engine.py tests/test_anomaly.py` + `uv run python -m ekozeka26.ml_engine --backtest` | `[x]` |
| **WBS-4** | ROI & Portföy Optimizasyon Motoru (~1,5 saat) | `src/ekozeka26/roi_optimizer.py` | Azalan verim ($1-\prod(1-r_i) \le 0.78$) çalışıyor; 0-1 Knapsack bütçeyi aşmadan maksimum NPV'li önlemleri seçiyor; kuyu vs şebeke farkını ve 2029 Yeşil Belge kademesini hesaplıyor; tüm edge-case testleri geçiyor. | `uv run pytest tests/test_roi_optimizer.py` | `[x]` |
| **WBS-5** | FastAPI Backend & Gemini/Fallback Ajanı (~1,5 saat) | `src/ekozeka26/app.py`, `src/ekozeka26/llm_agent.py`, `scripts/run.sh`, `.env.example` | Tüm REST uç noktaları (`/api/basins`, `/api/osb-compare`, `/api/predict-location`, `/api/simulate-roi`, `/api/executive-summary`, `/api/izsu-live`, `/api/facility-sample`, `/api/export/{json,csv}`) 200 OK dönüyor; `.env` yokken veya internet kapalıyken zengin deterministik fallback <100 ms'de çalışıyor; `scripts/run.sh` tek komutla uygulamayı `127.0.0.1:8000`'de ayağa kaldırıyor. | `uv run pytest tests/test_api.py` + `timeout 5 bash scripts/run.sh` | `[x]` |
| **WBS-6** | 2 Sekmeli Web Arayüzü (UI) (~2,5 saat) | `src/ekozeka26/static/index.html` | Sekme 1 (639 alt-havza haritası + OSB tablosu + şeffaf risk kırılımı + SHAP + CMIP6 P10–P90 + İZSU kartları & anomali rozetleri) ve Sekme 2 (Sektör Şablonu / Örnek Tesis Verisi Yükle + Fabrika ROI + Kuyu/Şebeke + Nakit akışı + 2029 Belgesi + Yönetici Özeti + JSON/CSV indir) hatasız çalışıyor. | `uv run uvicorn ekozeka26.app:app --host 127.0.0.1 --port 8000` + tarayıcı/curl kontrolü | `[x]` |
| **WBS-7** | Uçtan Uca Test & Performans Cilası (~1 saat) | `tests/`, `README.md` (taslak) | Tüm birim/entegrasyon testleri yeşil; harita yükleme <2 s; API yanıtları <200 ms; boş/geçersiz girdi, deniz tıklaması, çok düşük bütçe senaryoları doğrulandı. | `uv run pytest` + `curl -s -o /dev/null -w "%{http_code}" http://127.0.0.1:8000/api/basins` | `[x]` |
| **WBS-8** | Otomatik Ekran Görüntüleri, `README.md` & `SUNUM.md` (~1 saat) | `README.md`, `SUNUM.md`, `docs/demo/` (ekran görüntüleri + demo doğrulama çıktısı) | `SUNUM.md` içindeki tüm `[BUILD'DE GÜNCELLENECEK]` alanları gerçek çıktılarla dolduruldu; `google-chrome --headless` / `grim` / `wf-recorder` ile `docs/demo/` ekran görüntüleri alındı; temiz git durumu. (4 dk sözlü prova kullanıcı tarafından yapılacak.) | `uv run pytest` && `git status` && `ls docs/demo/` | `[x]` |

## Bilinen Sorunlar / Fallback Notları
- **Alt ajan kotası:** Claude tabanlı alt ajan kotası doldu → `build` oturumunda yalnızca Gemini/ücretsiz alt ajanlar (`explore`, `general`, `fast-check-free`, `rescue-free`) veya doğrudan ana model kullanılmalı.
- **Google Search aracı:** `execute` içindeki `google_search` 401 veriyor → gerekirse yerleşik `websearch` veya `webfetch` kullanılmalı.
- **İzmir Açık Veri API:** `openapi.izmir.bel.tr/api/izsu/barajdurum` HTTP 500 veriyor → İZSU resmi web sayfası (`izsu.gov.tr/bilgi-merkezi/barajlar/su-durumu`) + yerel önbellek (`/tmp/opencode/ekozeka_tests/izsu.html` ve `baraj.csv`) kullanılacak.
- **CMIP6 `ET₀`:** Open-Meteo CMIP6 API'sinde `et0` alanı `null` dönüyor → Hargreaves-Samani formülüyle kod içinde hesaplanacak.
- **QDM veri yetersizliği:** Bir havzada ERA5/CMIP6 örtüşme serisi çok kısaysa (ör. model 2050'de başlıyorsa) QDM yerine **delta-change** yedeğine düşülecek; bu durum arayüzde "basitleştirilmiş düzeltme" notuyla gösterilecek.
- **Backtest etiketi:** Gerçek "kesinti günü" tarihsel etiketi elimizde yok → 2010–2020 backtest, **SPEI/`P−ET₀` ve Aqueduct `bws` yeniden üretimi** üzerinden yapılacak; sunumda "hidrolojik yeniden üretim doğrulaması" olarak dürüstçe adlandırılacak (sahte kesinti etiketi üretilmeyecek).
- **Ticari platform bağımlılığı:** CarbonEmit ve benzeri platformların API'si/verisi **kullanılmayacak**; tesis verisi yalnızca kullanıcı girdisi veya `data/schema/facility.schema.json` uyumlu dosyadan gelecek.
- **Zararsız log gürültüsü (`GET /v1/models → 404`):** İstekler uygulamadan değil **OpenCode CLI**'den (`user-agent: opencode/latest/2.1.4/cli`) gelir; OpenCode 8000 portunda OpenAI-uyumlu yerel LLM sunucusu arar (`/health` → `/v1/models`). Uygulamamız LLM sunucusu olmadığı için `/v1/models` doğru şekilde 404 döner. **İşlevsel etkisi yoktur** (tüm `/api/*` uç noktaları 200; 8012 portunda hiç yoklama gelmiyor). İsteğe bağlı gizleme: `ACCESS_LOG=off bash scripts/run.sh`. Ayrıntı: `README.md §6`.
