# AquaSanayi AI — Kullanım Kılavuzu ve Veri Toplama Rehberi

## 1. Platformun Amacı ve Kapsamı
**AquaSanayi AI**, Türkiye'nin sanayi kalbi olan **Ege–Marmara–Konya Sanayi Koridoru** (ve WRI Aqueduct 4.0 ulusal tarama katmanındaki 639 alt-havza) için:
1. **Sekme 1 — Yatırım & Yer Seçimi:** Yeni fabrika yatırımı veya yeşil kredi değerlendirmesi için 0–100 şeffaf su kıtlığı risk puanını, 5 fiziksel/regülatif bileşen kırılımını, XGBoost+SHAP yaz pik sürücülerini ve 2026–2050 su dengesi projeksiyonunu sunar.
2. **Sekme 2 — Mevcut Fabrika ROI & 2029 Yeşil Belge Simülatörü:** Mevcut bir fabrikanın su kaynağına (OSB şebekesi, kendi yeraltı kuyusu, karma veya İZSU belediye şebekesi), proses su dağılımına ve yatırım bütçesine göre **0-1 Knapsack** algoritmasıyla en yüksek 5 yıllık NPV'yi sağlayan SYGM/IFC teknik önlemlerini seçer ve **27.12.2029 Su Verimliliği Yönetmeliği (RG 32765)** kriter kontrol listesini değerlendirir.

---

## 2. Veri Gerçeklik ve Şeffaflık Rozetleri
Arayüzdeki her metriğin yanında verinin kaynağını gösteren üç rozetten biri yer alır:
- **🟢 Ölçülmüş / Resmi Veri:** WRI Aqueduct 4.0 (639 alt-havza), İZSU resmi baraj ve üretim serileri, resmi sanayi su tarifeleri (`İZSU 1c: 403,79 TL/m³`, `Bursa BOSB: 122,00 TL/m³`, `Konya KOSKİ: 98,39 TL/m³`, `Kocaeli İSU+GOSB: 80,33 TL/m³`) ve SYGM Gediz Havzası Tahsis Planı (`%100` YAS bağımlılığı, `%62,9` kuraklık kesintisi).
- **🔵 Fizik + ML Modeli:** FAO-56 / Hargreaves-Samani `ET₀`, ERA5 + CMIP6 `Quantile Delta Mapping (QDM)` kalibrasyonu, 5-katlı `GroupKFold` ile doğrulanmış **XGBoost Aylık Yaz Pik Ölçek İndirme (`R² = 0,796`) + SHAP** ve **Isolation Forest** baraj anomali tespiti.
- **🟡 Kalibre Varsayım:** Kamuya açık olmayan fabrika içi parametreler (kuyu pompaj maliyeti `24,80 TL/m³`, üye portalına kapalı OSB tarifeleri için `118,50 TL/m³` referansı, bileşik risk skorundan türetilen `P10/P50/P90` kesinti günü indeksi ve SYGM/IFC katalog CAPEX/tasarruf katsayıları). Tüm kalibre varsayımlar arayüzden kullanıcı tarafından değiştirilebilir.

---

## 3. Beş Hızlı Senaryo ile Anlatım Rehberi (Sekme 2)
Sunumda farklı bölgelerde ve sektörlerde su riskinin **farklı kök nedenlerden** kaynaklandığını ve sistemin her birine **farklı çözüm portföyü** ürettiğini göstermek için Sekme 2'deki 5 senaryo sırasıyla kullanılır:

| Senaryo Butonu | Kök Neden | Su Kaynağı & Tarife | Seçilen Önlemler | Net Tasarruf & Amortisman | 2029 Belge Kademesi |
|---|---|---|---|---|---|
| **1. Kemalpaşa Tekstil** | Boyahane/yıkama proses suyu ağırlığı (`%64 proses`) | OSB Şebeke (`118,50 TL/m³`) | `M01, M03, M04, M06, M10` | `%48,12` (`72.180 m³`) · **2,6 ay** | **Yeşil Belge** |
| **2. Manisa Gıda (Kuyu)** | Kuyu suyu ucuz (`5,46M TL/yıl`) ama SYGM `%62,9` tahsis kesintisi faturanın **3,3 katı (`17,89M TL/yıl`)** duruş zararı yaratır | Kendi Kuyusu (`24,80 TL/m³`) | `M01, M03, M04, M10` | `%38,11` (`83.842 m³`) · **2,4 ay** | **Yeşil Belge** |
| **3. Aliağa Petrokimya** | Reaktör soğutma kulesi buharlaşma yükü (`%62 soğutma`) | Karma (`%55 Şebeke + %45 Kuyu`) | `M01, M03, M04, M05, M10, M11` (`M05` Kapalı Devre + `M11` Dry Cooler) | `%65,48` (`202.988 m³`) · **2,0 ay** | **Turkuaz Belge** |
| **4. Konya Metal KOBİ** | Kapalı havza akifer/obruk çöküşü + kısıtlı KOBİ bütçesi (`1,10M TL`) | KOSKİ Sanayi (`98,39 TL/m³`) | `M01, M02, M10` (`M02` ISO 46001 Dijital Alt-Sayaç Ağı) | `%23,96` (`22.762 m³`) · **3,7 ay** | **Yeşil Belge** |
| **5. İzmir Şehir İçi (İZSU)** | Resmi `403,79 TL/m³` belediye şebeke tarifesi şoku (yıllık `44,4M TL` fatura) | İZSU 1c (`403,79 TL/m³`) | `M01, M03, M04, M05, M06` | `%52,24` (`57.464 m³`) · **1,6 ay** | **Turkuaz Belge** |

---

## 4. Bir Şirket Sahibi Hangi Bilgileri Nereden Bulur?
| Girdi Alanı | Şirket İçinde Kim Bilir? | Hangi Belgeden / Nereden Bulunur? | Şirket Sahibi Değilseniz Ne Kullanılır? |
|---|---|---|---|
| **Yıllık Su Çekimi (`m³/yıl`)** | Tesis / Enerji Yöneticisi veya Muhasebe | 12 aylık OSB / Belediye su faturası toplamı veya kuyu debimetre kaydı | SYGM NACE sektörel referans aralıkları (`95.000 – 310.000 m³/yıl`) |
| **Su Temin Kaynağı** | İdari İşler / Teknik Müdür | OSB su abonelik sözleşmesi veya DSİ *Yeraltı Suyu Kullanım Belgesi* | Seçilen OSB'nin gerçek altyapı profili |
| **Proses Su Dağılımı (`%`)** | Proses Mühendisi | ISO 46001 alt-sayaç kayıtları veya kütle dengesi şeması | Sektör seçildiğinde SYGM NACE varsayılanları otomatik dolar |
| **1 Günlük Duruş Zararı (`TL/gün`)** | Finans (CFO) + Üretim Planlama | `(Yıllık Ciro / 300 iş günü) × Brüt Katkı Marjı` | Sektörel kapasiteye göre `135.000 – 680.000 TL/gün` |
| **Maksimum Yatırım Bütçesi (`TL`)** | Yönetim Kurulu / Finans | Yıllık CAPEX bütçesi veya Yeşil Kredi limiti | `1,1M – 4,65M TL` senaryo şablonları |
| **Çalışan Sayısı** | İnsan Kaynakları | SGK Aylık Prim ve Hizmet Belgesi (`50+` çalışan 2029 Yeşil Belge yükümlüsüdür) | `190 – 410` çalışan örnek profilleri |
