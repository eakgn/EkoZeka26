# AquaSanayi AI — Kullanım Kılavuzu ve Veri Toplama Rehberi

## 1. Platformun Amacı ve Kapsamı
**AquaSanayi AI**, Türkiye'nin sanayi kalbi olan **Ege–Marmara–Konya Sanayi Koridoru** (ve WRI Aqueduct 4.0 ulusal tarama katmanındaki 639 alt-havza) için:
1. **Sekme 1 — Yatırım & Yer Seçimi:** Yeni fabrika yatırımı veya yeşil kredi değerlendirmesi için 0–100 şeffaf su kıtlığı risk puanını, 5 fiziksel/regülatif bileşen kırılımını, XGBoost+SHAP yaz pik sürücülerini ve 2026–2050 su dengesi projeksiyonunu sunar.
2. **Sekme 2 — Mevcut Fabrika ROI & 2029 Yeşil Belge Simülatörü:** Mevcut bir fabrikanın su kaynağına (OSB şebekesi, kendi yeraltı kuyusu, yüzey suyu/baraj, karma veya İZSU belediye şebekesi), proses su dağılımına ve yatırım bütçesine göre **0-1 Knapsack** algoritmasıyla en yüksek 5 yıllık NPV'yi sağlayan SYGM/IFC teknik önlemlerini seçer ve **27.12.2029 Su Verimliliği Yönetmeliği (RG 32765)** kriter kontrol listesini değerlendirir.

---

## 2. Veri Gerçeklik ve Şeffaflık Rozetleri
Arayüzdeki her metriğin yanında verinin kaynağını gösteren üç rozetten biri yer alır:
- **🟢 Ölçülmüş / Resmî Kayıt:** İZSU resmi baraj ve üretim serileri, resmi sanayi su tarifeleri (`İZSU 1c: 403,79 TL/m³`, `Bursa BOSB: 122,00 TL/m³`, `Konya KOSKİ: 98,39 TL/m³`, `Kocaeli İSU+GOSB: 80,33 TL/m³`), SYGM Gediz Tahsis Planı ve şirketlerin kamuya açık 2024 sürdürülebilirlik/entegre raporlarındaki tesis su çekimleri (Tofaş, Vestel, Petkim).
- **🔵 Resmî Model / Fizik + ML:** WRI Aqueduct 4.0 (639 alt-havza; ölçüm değil, yayımlanmış küresel model), ERA5 yeniden analizi, **7 gerçek CMIP6 HighResMIP modeli**, FAO-56 / Hargreaves-Samani `ET₀`, `Quantile Delta Mapping (QDM)`, 5-katlı `GroupKFold` ile doğrulanmış **XGBoost Aylık Yaz Pik Ölçek İndirme (`R² = 0,796`) + SHAP** ve **Isolation Forest** baraj anomali tespiti.
- **🟡 Kalibre Varsayım:** Kamuya açık olmayan fabrika içi parametreler (kuyu pompaj maliyeti `24,80 TL/m³`, yüzey suyu/arıtma `15,00 TL/m³`, üye portalına kapalı OSB tarifeleri için `118,50 TL/m³` referansı, proses payları, SYGM/IFC katalog CAPEX/tasarruf katsayıları, duruş maliyeti ve bileşik risk skorundan türetilen `P10/P50/P90` kesinti günü indeksi). Tüm kalibre varsayımlar arayüzden kullanıcı tarafından değiştirilebilir.

---

## 3. Üç Gerçek Fabrika Vakası ile Anlatım Rehberi (Sekme 2)
Sunumda farklı bölgelerde ve sektörlerde su riskinin **farklı kök nedenlerden** kaynaklandığını ve sistemin her birine **farklı çözüm portföyü** ürettiğini göstermek için Sekme 2'deki 3 gerçek vaka kullanılır. Su çekimi, çalışan sayısı ve kaynak dağılımı şirketlerin 2024 raporlarından; proses payları ve bütçe sektör kalibrasyonundan gelir.

| Vaka | Kök Neden | Su Kaynağı & Tarife | Seçilen Önlemler | Net Tasarruf & Amortisman | 2029 Belge Kademesi |
|---|---|---|---|---|---|
| **1. Tofaş — Bursa** (`430.782 m³/yıl`, 4.409 çalışan) | Suyun **%100'ü yeraltı kuyularından**; otomotiv boyahane/proses hattı + Nilüfer Havzası akifer riski | Kendi Kuyusu (`24,80 TL/m³`) | `M01, M03, M04, M10` | `%35,8` (`154.091 m³`) · **4,4 ay** | **Yeşil Belge** |
| **2. Vestel — Manisa** (`1.510.208 m³/yıl`, 29.000 çalışan) | Yüksek hacimli **şebeke + kuyu karması** (%71,4 şebeke); Manisa OSB tarifesi ve 2029 belgesi maliyet baskısı | Karma (`91,70 TL/m³`) | `M01, M02, M10` | `%24,0` (`362.450 m³`) · **2,3 ay** | **Yeşil Belge** |
| **3. Petkim — Aliağa** (`14.230.105 m³/yıl`, 2.433 çalışan) | Dev ölçekli **yüzey suyu** (Güzelhisar) ve **%62 soğutma** buharlaşma yükü | Yüzey Suyu (`15,00 TL/m³`) | `M01, M04, M05, M10` (`M05` Kapalı Devre Soğutma) | `%54,8` (`7.793.829 m³`) · **7,7 ay** | **Turkuaz Belge** |

> **Dürüstlük notu:** Bu üç tesisin su çekimi/çalışan sayısı raporlardan doğrulanmıştır; ancak proses payları, günlük duruş maliyeti ve yatırım bütçesi kamuya açık olmadığı için kalibre varsayımdır. Arayüzde bu ayrım 🟢/🟡 rozetleriyle gösterilir.


---

## 4. Bir Şirket Sahibi Hangi Bilgileri Nereden Bulur?
| Girdi Alanı | Şirket İçinde Kim Bilir? | Hangi Belgeden / Nereden Bulunur? | Şirket Sahibi Değilseniz Ne Kullanılır? |
|---|---|---|---|
| **Yıllık Su Çekimi (`m³/yıl`)** | Tesis / Enerji Yöneticisi veya Muhasebe | 12 aylık OSB / Belediye su faturası toplamı veya kuyu debimetre kaydı | Şirket sürdürülebilirlik raporu; yoksa SYGM NACE sektörel referans aralıkları (`430.782 – 14.230.105 m³/yıl` gerçek vakalar) |
| **Su Temin Kaynağı** | İdari İşler / Teknik Müdür | OSB su abonelik sözleşmesi veya DSİ *Yeraltı Suyu Kullanım Belgesi* | Seçilen OSB'nin gerçek altyapı profili |
| **Proses Su Dağılımı (`%`)** | Proses Mühendisi | ISO 46001 alt-sayaç kayıtları veya kütle dengesi şeması | Sektör seçildiğinde SYGM NACE varsayılanları otomatik dolar |
| **1 Günlük Duruş Zararı (`TL/gün`)** | Finans (CFO) + Üretim Planlama | `(Yıllık Ciro / 300 iş günü) × Brüt Katkı Marjı` | Sektörel kapasiteye göre `1,5M – 15M TL/gün` |
| **Maksimum Yatırım Bütçesi (`TL`)** | Yönetim Kurulu / Finans | Yıllık CAPEX bütçesi veya Yeşil Kredi limiti | `6M – 250M TL` gerçek vaka şablonları |
| **Çalışan Sayısı** | İnsan Kaynakları | SGK Aylık Prim ve Hizmet Belgesi (`50+` çalışan 2029 Yeşil Belge yükümlüsüdür) | `2.433 – 29.000` çalışan gerçek vakalar |
