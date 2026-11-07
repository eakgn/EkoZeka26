# SUNUM — EkoZeka26: AquaSanayi AI Sunum ve Savunma Rehberi

> **Durum (`build` oturumu tamamlandı):** Tüm model metrikleri (5-katlı `GroupKFold` XGBoost `R² = 0,7958`, `MAE = 0,1534`; Gediz hidrolojik backtest `R² = 0,6732`; Isolation Forest İZSU anomali skoru `0,5932`), aday OSB karşılaştırma skorları ve 3 gerçek fabrika ROI simülasyonu (Tofaş `%35,8` / `4,4 ay`; Vestel `%24,0` / `2,3 ay`; Petkim `%54,8` / `7,7 ay`) gerçek ve doğrulanmış sayılarla güncellenmiştir.
> **Süre:** 3–5 Dakika (Soru-Cevap dahil) · **Format:** Canlı Sunum + Canlı Demo (`127.0.0.1:8000`)

---

## 1. Altın Sayılar Tablosu (Slaytlarda ve Konuşmada Kullanılacak Doğrulanmış Veriler)

### A) İklim ve İzmir/Ege Su Krizi Verileri
| Gösterge | Sayısal Değer | Kaynak | Sunumda Nasıl Kullanılır? |
|---|---|---|---|
| Küresel ısınma | **2015–2025** kayıtlı en sıcak 11 yıl; 2025 **+1,43°C** | WMO (Mart 2026) | "İklim krizi gelecek tahmini değil, içinde bulunduğumuz gerçek." |
| Türkiye kuraklık rekoru | 2025: **1964'ten beri (61 yılın) en kurak yılı**, yağış normalin **%27,6 altında** | MGM | "Türkiye son 60 yılın en sert kuraklık rejimine girdi." |
| İzmir barajları gerçek doluluk (6 Kas 2026) | Kapasite-ağırlıklı **%34,0** (`257,2 / 756,2 Mm³`) | İZSU Canlı Veri | **Veri okuryazarlığı kancası:** "Medyada %44,2 deniyor çünkü 5 barajın basit ortalamasını alıyorlar. Oysa kapasitenin **%58'ini** tutan Gördes Barajı sadece **%27,96** dolu!" |
| Yıllar arası aşırı oynaklık | Tahtalı Barajı: Geçen yıl (6 Kas 2025) **%1,54** → Bu yıl **%41,39** | İZSU Canlı Veri | "Tek yıllık ortalamayla plan yapılamaz; olasılıksal (P10–P90) yapay zeka şart." |
| İzmir yeraltı suyu baskısı | **~1.600 kuyu**, 2025'te **110 yeni kuyu**, **318 kıyı kuyusu** tuzlanma riskinde | İZSU | "Yüzey suyu yetmeyince yeraltına yükleniyoruz, kuyular tuzlanıyor." |
| Gediz Havzası su stresi projeksiyonu | Baseline: **0,99** (Aşırı Yüksek) → 2030: **1,06** → 2050: **1,72** → 2080: **2,53** (Kötümser: **3,16**) | WRI Aqueduct 4.0 (`pfaf_id=211055`) | "1,0'ın üzeri demek, havzadaki su talebinin doğanın yenileyebildiği suyu aşması demek." |

### B) Neden Sanayi? (Sektörel Gerçekler ve Tuzaktan Kaçınma)
| Gösterge | Sayısal Değer | Kaynak | Sunumda Nasıl Kullanılır? |
|---|---|---|---|
| Türkiye toplam su kullanımı (DSİ) | Toplam **61,7 milyar m³**: Tarım **%79** (`48,7 Mr m³`), İçme+Sanayi **%21** (`13,0 Mr m³`) | DSİ / ÇŞB (2024) | **Asla "en çok suyu sanayi harcıyor" deme!** "Hacim olarak suyun %79'unu tarım harcar; ama 2,2 milyon çiftçiye B2B karar yazılımı satamazsınız." |
| Şebeke/Temin tatlı su çekimi (TÜİK) | Toplam çekim **20,3 Mr m³** (Tatlı su **9,2 Mr m³**): Belediyeler **%81**, Sanayi toplamı **~%14,7** (İmalat %7,3 + Maden/OSB %5,8 + Termik %1,6) | TÜİK (Aralık 2025) | **Veri bilimi jürisine dipnot:** "DSİ barajdan sulamaya verilen suyu, TÜİK temin ağlarını ölçer; aradaki fark kapsam farkıdır." |
| **Gediz Havzası sanayi bağımlılığı (KRİTİK!)** | Sanayi su talebi (**72,2 hm³/yıl → 162,4 hm³/yıl**): **%100'ü yeraltı suyundan** karşılanıyor | Tarım ve Orman Bakanlığı (SYGM) Gediz Tahsis Planı | "İzmir-Manisa sanayisi tamamen yeraltı kuyularına bağımlı." |
| **Kuraklıkta sanayi kesintisi (KRİTİK!)** | Tahsis karşılama: Normalde **%85,9** → Kuraklık senaryosunda **%37,1** (**%62,9 kesinti!**) | SYGM Gediz Sektörel Su Tahsis Planı | **"Kurak bir yılda fabrikanın suyunun üçte ikisi kesiliyor; bu doğrudan üretimin durması demek!"** |
| İzmir sanayi su fiyatı (Haziran 2026) | Sanayi (1c) 21 m³/ay üstü: **403,79 TL/m³** (KDV hariç). Geri kazanılmış su: **11,95 TL/m³** | İZSU Resmi Tarife (01.06.2026) | "Şebeke suyu 404 TL iken geri kazanım 12 TL; su verimliliği artık çevre hayırseverliği değil, doğrudan finansal kârlılık." |
| **Yasal Zorunluluk (Deadline)** | **27 Aralık 2029**: OSB'ler ve Ek-2 NACE listesindeki 50+ çalışanlı fabrikalar **Yeşil Su Verimliliği Belgesi** almak zorunda | Su Verimliliği Yönetmeliği (RG 27.12.2024, No. 32765) | "Şirketlerin önünde 2029'a kadar yasal bir saatli bomba var." |
| Pazar büyüklüğü (Türkiye) | **416 OSB**, **68.000+ fabrika**; sadece **27 Yeşil OSB** ve **3 ISO 46001** belgeli OSB var | OSBÜK / TSE | "Pazarın %93'ü henüz dönüşmedi; hedef kitlemiz net ve ödeme gücüne sahip." |

### C) Önlem ve Yatırım Geri Dönüşü (ROI) Katsayıları
| Önlem / Kategori | Tasarruf Oranı | Tipik Geri Ödeme (Payback) | Kaynak |
|---|---|---|---|
| Tüm sektörel MET'ler (potansiyel tavan) | **%17 – %78** | 1 – 5 yıl | SYGM NACE Rehberleri |
| Kapalı devre soğutma kulesi dönüşümü | Soğutmada **>%95** geri kazanım | **< 2 – 4 yıl** | SYGM / IFC (2017) |
| Basınçlı/otomatik nozullar & sensör kontrolü | Proseste **%20 – %30** (toplamda %4–10) | **< 60 gün – 1 yıl** | SYGM / IFC |
| Durulama / proses suyu kaskad geri kazanımı | **%15 – %35** | **1 – 2,5 yıl** | SYGM NACE Rehberleri |
| Yağmur suyu hasadı + gri su | Toplamda **%5 – %10** | **3 – 3,5 yıl** | IFC (2017) |
| ISO 46001 dijital su izleme & kaçak kontrolü | Toplamda **%3 – %6** | **6 – 12 ay** | SYGM |

### D) Kendi Modelimizin Çıktı Metrikleri (`build` Aşamasında Doldurulacak)
- **Kapsanan Türkiye Alt-Havza Sayısı:** `639` hidrolojik alt-havza (WRI Aqueduct 4.0 GDB + CSV)
- **İklim Modeli Topluluğu:** **7 gerçek CMIP6 HighResMIP modeli** (2020–2050, Open-Meteo) + ERA5 (1940–2025), `3` senaryo (OPT/BAU/PES). Her model ayrı QDM ile kalibre edilir; P10–P90 bandı gerçek model yayılımıdır.
- **Kuraklık İndeksleri:** `SPI-3`, `SPI-12`, `SPEI-3`, `SPEI-12` (log-logistic); kuraklık sınıfları ve trend eğimi (tek referans noktası: İzmir/Gediz).
- **XGBoost Mevsimsel/Mekânsal Ölçek İndirme (5-katlı GroupKFold, 1.392 Aqueduct havza-ay model çıktısı):** Naive (Kaba Yıllık) `MAE = 0,4789, RMSE = 0,9598, R² = -0,0044` → Doğrusal Regresyon (Ridge) `MAE = 0,2940, RMSE = 0,5827, R² = 0,6297` → **XGBoost Downscaler (`max_depth=4`) `MAE = 0,1534, RMSE = 0,4328, R² = 0,7958` (Naive modele göre hatada %68,0 düşüş; SHAP çıkarım gecikmesi `<15 ms`)**. Not: Etiketler yerinde ölçüm değil, WRI Aqueduct aylık model çıktısıdır.
- **Backtest (1984–2025 ERA5 + GloFAS Gediz Debi & 2021/2024/2025 Kurak Yıllar):** `2015–2025` (132 ay) dış-örneklem test dönemi **XGBoost `R² = 0,6732` (`MAE = 0,0269 m³/s`, `RMSE = 0,0545 m³/s`)**; 2024 ve 2025 yaz aylarında gözlenen minimum debi `0,00 m³/s` kuraklık çöküşü doğrulandı.
- **İZSU Gerçek Anomali Bulguları (`izsu_aylik.html` 137 ham satır → 126 tekil tesis-ay + 23 günlük baraj kesiti):** Kasım 2025 kuraklığında Tahtalı aylık üretimi **6,91 Mm³ → 1,62 Mm³ (-%76,5)** çökerken yeraltı kuyuları (Göksu + Halkapınar + Sarıkız + Menemen) arzın **%69,33'ünü (>%62)** üstlendi (**Isolation Forest Anomali Skoru: `0,5932`, `ANOMALİ = TRUE`**); son 23 günde (14 Ekim → 6 Kasım 2026) Balçova Barajı **-%7,43 puan** (`%44,77 → %37,34`) düştü ve Gördes/Balçova günlük üretimi `0 m³/gün` oldu.
- **3 Gerçek Fabrika Vakası ve ROI Çıktıları (2024 kamuya açık rapor verileri):**
  1. **Tofaş — Bursa Tesisi (`430.782 m³/yıl`, %100 yeraltı kuyusu `24,80 TL/m³`, `4.409` çalışan, `6,0M TL` bütçe):** Otomotiv boyahane/proses hattı su yoğun; Bursa Nilüfer Havzası'nda akifer riski yüksek. Seçilen portföy: `M01, M03, M04, M10` → **`%35,8` tasarruf (`154.091 m³/yıl`)**, `NPV = +43,30M TL`, amortisman **`4,4 ay`**, **Yeşil Su Verimliliği Belgesi (Tam Uyum)**.
  2. **Vestel — Manisa Kampüsü (`1.510.208 m³/yıl`, %71,4 şebeke + %28,6 kuyu, `29.000` çalışan, `12,0M TL` bütçe):** Yüksek hacim + Manisa OSB tarifesi + 2029 belgesi. Seçilen portföy: `M01, M02, M10` → **`%24,0` tasarruf (`362.450 m³/yıl`)**, `NPV = +160,59M TL`, amortisman **`2,3 ay`**, **Yeşil Belge**.
  3. **Petkim — Aliağa Kompleksi (`14.230.105 m³/yıl`, %62 soğutma, yüzey suyu `15,00 TL/m³`, `2.433` çalışan, `250M TL` bütçe):** Dev ölçekli yüzey suyu + soğutma kulesi buharlaşması. Seçilen portföy: `M01, M04, M05, M10` (`M05` Kapalı Devre Soğutma) → **`%54,8` tasarruf (`7.793.829 m³/yıl`)**, `NPV = +903,68M TL`, amortisman **`7,7 ay`**, **Turkuaz Su Verimliliği Belgesi (Üstün Uyum)**.

---

## 2. Dakika Dakika Sunum ve Canlı Demo Senaryosu (Toplam: 4 Dakika)

### 0:00 – 0:45 | 1. Perde: Kanca ve Doğru Problem Çerçevesi
- **Açılış cümlesi:** *"Bugün İzmir'de haberleri açarsanız barajlarımız %44 dolu diyorlar. Ama bu 5 barajın basit ortalaması. İzmir'in su kapasitesinin %58'ini tek başına tutan Gördes Barajı bugün %28 dolu; yani gerçek ağırlıklı doluluğumuz sadece **%34**."*
- **Pivot (Neden Sanayi?):** *"Peki su kıtlığını nasıl çözeriz? Türkiye'de suyun %79'unu tarım harcar ama 2 milyon çiftçiye kurumsal karar yazılımı satamazsınız. Sanayi ise tatlı su şebekesinin ~%15'ini çeker ama Gediz Havzası'nda sanayi suyunun **%100'ü yeraltı kuyularından** gelir ve Bakanlığın tahsis planına göre kurak bir yılda sanayiye verilen su **%37'ye düşer — yani %63 kesinti ve üretimin durması!** Üstelik İZSU sanayi su fiyatı **404 TL/m³** oldu ve 2024 sonunda çıkan yönetmelikle fabrikalar **27 Aralık 2029'a kadar Yeşil Su Verimliliği Belgesi** almak zorunda. Biz su kıtlığını, bu krizden milyonlarca lira zarar edecek olan fabrikaya, kendi kârıyla çözdürüyoruz."*

### 0:45 – 1:50 | 2. Perde: Canlı Demo — Sekme 1 (Yer Seçimi, Şeffaf Risk & SHAP)
- Ekranda **AquaSanayi AI — Sekme 1 (Yatırım & Yer Seçimi)** açıktır.
- **Göster:** Türkiye'nin **639 gerçek hidrolojik alt-havzasını** içeren haritada 2050 Kötümser/Normal su stresi katmanı. Sağ üstte İZSU canlı baraj kartları.
- **Aksiyon:** *"Diyelim ki otomotiv, elektronik veya petrokimya sektöründe yeni bir fabrika kuracağız veya bir banka olarak kredi vereceğiz. Bursa, Manisa ve Aliağa OSB'lerini karşılaştırıyoruz."*
- **Yapay Zeka Vurgusu:**
  1. **Şeffaf Bileşik Risk İndeksi:** Tek bir kara kutu sayısı değil; skorun **her bileşeni ve ağırlığı** ekranda. *"Kemalpaşa OSB'de 2050 (BAU) risk skoru **82,8 / 100** çıktı çünkü gelecek/yaz pik su stresi +25,0, yeraltı suyu düşüşü ve kuyu bağımlılığı +22,4, SPEI-12 kuraklık trendi +18,0 ve sektörel tahsis baskısı +13,4 puan ekledi (Bursa OSB 57,8, Gebze OSB 55,0)."*
  2. **Belirsizlik (P10–P90):** **7 gerçek CMIP6 modelinin** dağılımından **P10 (İyimser: 17,4 gün) / P50 (Beklenen: 33,5 gün) / P90 (Kötümser: 60,7 gün)** yıllık kesinti günü aralığı + "Kemalpaşa'da 6/7 model (%85,7) kuraklaşma yönünde" mutabakat oranı. *(Kesinti günü aralığı risk indeksinden türetilen sezgisel göstergedir; tarihsel kesinti etiketi değildir.)*
  3. **XGBoost + SHAP (dürüst rolü):** *"XGBoost'u iklimi taklit etsin diye değil, kaba yıllık projeksiyonları **yaz pik su stresine ölçek indirsin (downscaling)** diye kullandık; 7 CMIP6 modelini ise ayrı ayrı ERA5'e **QDM** ile kalibre ettik. SHAP grafiği (`<15 ms`) bu havzada yaz pik stresini en çok hangi fiziksel sürücülerin (`summer_x_bws`, `month`, `bws_raw`, `sev_raw`) artırdığını gösteriyor."*

### 1:50 – 3:10 | 3. Perde: Canlı Demo — Sekme 2 (Mevcut Fabrika ROI Optimizasyonu & 2029 Belgesi)
- **Aksiyon:** *"Peki fabrikamız zaten buradaysa? İkinci sekmeye geçiyoruz."*
- **"Gerçek Fabrika Vakası"** butonlarından **Tofaş — Bursa**'ya tıkla: *"Kendi açık şemamıza uyan, kamuya açık 2024 entegre raporundan doğrulanmış bir tesisi tek tıkla yüklüyoruz: Tofaş Bursa, yılda 430.782 m³ suyun tamamını yeraltı kuyularından çekiyor. Bu şema herhangi bir ayak izi platformunun dışa aktarımıyla eşlenebilir; ama biz hiçbir ticari platforma bağımlı değiliz."*
- **Kritik Mühendislik Detayı:** Su kaynağını **"Kendi Kuyusu (24,80 TL/m³)"**, **"OSB Şebekesi (118,50 TL/m³)"** ve **"Yüzey Suyu (15,00 TL/m³)"** arasında değiştirerek göster: *"Fabrika 'benim kendi kuyum var, şebekeye para ödemiyorum' diyebilir. Ama kuyu seçtiğinizde motorumuz havza tahsis kesintisi ve akifer riski yüzünden fabrikanın kaç gün duracağını ve **günlük üretim kaybı zararını** hesaplıyor. Petkim gibi yüzey suyu kullanan dev tesislerde ise asıl risk soğutma kulesi buharlaşması."*
- **Optimizasyon Çıktısı:** Tofaş için bütçeyi `6.000.000 TL` olarak gir → **0-1 Knapsack / MILP Optimizasyon Motoru** Bakanlığın NACE rehberindeki 12 önlem arasından bütçeye sığan en kârlı kombinasyonu seçer (proses bazında azalan verim kuralıyla, asla %100 üstü hatalı toplama yapmadan; CAPEX tesis kapasitesine göre ölçeklenir).
- Ekranda **Geri Ödeme Süresi (Payback)**, **5 Yıllık NPV**, **2029 Yeşil Su Verimliliği Belgesi kademesi**, **JSON/CSV indir** ve **Gemini AI Yönetim Kurulu Özeti** görünür.

### 3:10 – 4:00 | 4. Perde: İş Modeli, Ölçeklenebilirlik ve Kapanış
- **Kim öder?** Türkiye'deki **416 OSB ve 68.000 fabrika**, Yeşil OSB olmak isteyen yönetimler ve yeşil kredi/leasing veren bankalar.
- **Gelir modeli:** Tesis başı yıllık SaaS aboneliği + yatırım bankaları/leasing için portföy risk analizi lisansı. Veri dışa aktarımı açık şema (JSON/CSV) ile yapılır; ticari platforma bağımlılık yoktur.
- **Kapanış:** *"Su krizini durdurmanın en hızlı yolu, su tasarrufunu fabrikalar için en kârlı yatırım haline getirmektir. Teşekkür ederim."*

---

## 3. Jüri Soru-Cevap (Q&A) Cephaneliği

1. **[Musa Can Minaz — CarbonEmit] "Biz zaten ISO 14046 su ayak izi raporu veriyoruz, müşterimiz neden sizi de alsın?"**
   - **Cevap:** *"ISO 14046 geçmiş yılın doğrulanmış muhasebesidir ve denetim/raporlama bütçesinden çıkar. Biz doğrulanmış ayak izi raporu üretmiyoruz ve sizin verinize/API'nize de ihtiyaç duymuyoruz. Bizim sorumuz şu: 'Önümüzdeki 10–25 yılda bu tesisin suyu kesilir mi, bu kesinti kaç TL üretim kaybı demek, ve 27 Aralık 2029 Yeşil Su Verimliliği Belgesi'ni en düşük CAPEX ile almak için hangi önlemleri seçmeliyim?' Yani sizin raporunuz geçmişi belgeler; bizim platformumuz o belgenin üzerine ileriye dönük yatırım kararı koyar. Birbirini tamamlayan iki katmanız — ve tesis verisini kendi açık şemamızla JSON/CSV alıp verebildiğimiz için entegrasyon iddiamız yok, bağımlılığımız da yok."*
2. **[Veri Topluluğu Jürisi] "Aqueduct ve CMIP6 zaten açık veri. Sizin XGBoost modeliniz tam olarak neyi öğreniyor ve aşırı öğrenmeyi (overfitting) nasıl engellediniz?"**
   - **Cevap:** *"İki kritik boşluğu dolduruyoruz: Birincisi, CMIP6 serbest-koşulu bir iklim simülasyonu olduğu için ERA5 ile takvim günü bazında eşleştirilemez; bu yüzden her CMIP6 modelinin olasılık dağılımını ayrı ayrı ERA5'e **Quantile Delta Mapping (QDM)** ile kalibre ediyoruz ve eksik olan `ET₀` buharlaşmasını FAO-56/Hargreaves ile hesaplıyoruz. İkincisi, gelecek projeksiyonları yalnızca **kaba yıllık ortalama** su stresini verir; oysa fabrikaların suyu **Temmuz–Ekim yaz pikinde** kesilir. **XGBoost modelimiz**, Türkiye'nin 116 havzasındaki 1.392 Aqueduct havza-ay model çıktısı üzerinde kaba yıllık hidrolojik göstergelerden (`bws`, `gtd`, `sev`, `iav`, `drr`) **aylık/yaz pik su stresine ölçek indirmeyi (downscaling)** öğreniyor. Overfitting'i **5-katlı `GroupKFold` (havza bazlı)** çapraz doğrulamayla engelledik: hiçbir havza aynı anda hem eğitim hem test setine girmedi. Sonuçta kaba yıllık baseline `MAE = 0,4789`, doğrusal regresyon `MAE = 0,2940 (R² = 0,63)` verirken, XGBoost hatayı **%68 düşürerek `MAE = 0,1534` ve `R² = 0,7958`** başarı sağladı. Etiketler yerinde ölçüm değil, WRI Aqueduct'in yayımlanmış aylık model çıktısıdır; bunu da açıkça belirtiyoruz."*
3. **[Veri Bilimi Jürisi] "Neden doğrudan XGBoost ile 2050 riskini tahmin etmediniz?"**
   - **Cevap:** *"Çünkü o kurgu **döngüsel** olurdu: Aqueduct zaten 2050 su stresini veriyor; biz XGBoost'a 'Aqueduct'in verdiği sayıyı tahmin et' dersek model yeni bilgi üretmez, sadece onu taklit eder. Üstelik Türkiye için elimizde 639 satır var — bu, denetimli öğrenme için çok az. Bu yüzden mimariyi **fizik-öncelikli** kurduk: su dengesi (`P − ET₀`), SPEI/SPI, Aqueduct göstergeleri ve yeraltı bağımlılığı şeffaf bir indekste birleşiyor. XGBoost'u ise gerçekten etiketli olan yere koyduk: iklim modeli yanlılık düzeltmesi. Ayrıca KMeans ile havza arketipleri, Isolation Forest ile İZSU canlı veri anomalileri üretiyoruz. Yani 'yapay zeka süs değil' diyorsak, onu doğru işe koyduk."*
4. **[DEÜ Bilgisayar Bilimleri Jürisi] "LLM (Gemini) burada sayı uydurursa (halüsinasyon) fabrika yanlış yatırım yapmaz mı?"**
   - **Cevap:** *"Kesinlikle haklısınız, bu yüzden mimarimizde **LLM hiçbir matematiksel işlem yapmaz.** Tüm risk skorları şeffaf indeksten, tüm TL ve m³ hesapları ise deterministik Knapsack optimizasyon motorumuzdan kesin JSON şemasıyla çıkar. Gemini yalnızca bu doğrulanmış JSON tablosunu yönetim kurulu diline tercüme eder; API kesilirse veya saparsa deterministik şablon motorumuz (offline fallback) devreye girer."*
5. **[Genel Jüri] "Fabrika iki önlem aldığında ikisi de %50 tasarruf sağlıyorsa %100 mü tasarruf ediyor?"**
   - **Cevap:** *"Hayır, bu en sık yapılan mühendislik hatasıdır. Motorumuzda fabrikayı 4 alt prosese (soğutma, yıkama/proses, kazan, evsel) ayırdık. Aynı prosese uygulanan önlemler çarpımsal azalan verim formülüyle ($1 - (1-r_1)(1-r_2)$) hesaplanır ve Bakanlığın NACE rehberindeki teknik üst sınırla (%78) sınırlandırılır."*
6. **[Genel Jüri] "Bu sistemi tek başına 22 saatte nasıl yaptın, sürdürülebilir mi?"**
   - **Cevap:** *"Mimariyi baştan modüler ayırdım: veri hattı, iklim motoru, kuraklık indeksi, risk indeksi, ML, ROI optimizasyonu, API ve arayüz birbirinden bağımsız test edilebilir. Her modülün otomatik testi var; biri çökerse diğeri çalışmaya devam ediyor. Veri katmanı tamamen önbellekli, internet giderse çevrimdışı rozetle aynı demo çalışıyor. Yani bu bir 'demo hack'i değil, ürünün ilk sürümü."*
