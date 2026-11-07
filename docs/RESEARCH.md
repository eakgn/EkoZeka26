# RESEARCH — EkoZeka26 Araştırma Özeti

> Fikir seçimi ve sunum için başvuru notu. Rakamlar sunuma girmeden önce kaynağından tekrar doğrulanmalı (⚠️ = ikincil/tahmini kaynak).
> Araştırma tarihi: 7 Kasım 2026.

## 1. Güncel Ekoloji Problemleri — Öne Çıkan Veriler

| Konu | Veri | Kaynak |
|---|---|---|
| Küresel sıcaklık | 2015–2025 kayıtlı en sıcak 11 yıl; 2025 ≈ +1,43°C | WMO State of the Global Climate 2025 |
| Türkiye | 2024 en sıcak yıl (15,6°C); 2025, 1964'ten beri en kurak yıl (yağış normalin %27,6 altı) | MGM |
| İzmir barajları | 6 Kas 2026: kapasite-ağırlıklı doluluk **%34,0** (257,2 / 756,2 Mm³). Basit ortalama %44,2 (yanıltıcı; Gördes kapasitenin ~%58'i ve %27,96 dolu) | https://izsu.gov.tr/bilgi-merkezi/barajlar/su-durumu |
| Orman yangını | 2025 Türkiye: 3.224 yangın, 81.473 ha (OGM). En çok yangın İzmir orman bölgesinde (321 yangın / 15.203 ha) | OGM (Evrensel) |
| İzmir Körfezi | Ağu–Eyl 2025 balık ölümleri, alg patlaması, oksijen düşüşü; ÇŞB acil eylem planı | ÇŞB, basın |
| Kentsel ısı | İzmir 2025'te 41,8°C rekor | İzmir BB StoryMap |
| Hava kalitesi | 2024'te İzmir'de PM2.5 kaynaklı ~4.803 erken ölüm | Kara Rapor 2025 |
| CBAM | AB SKDM kesin dönemi 1 Ocak 2026'da başladı; sertifika satışı Şubat 2027; 2026 beyanı 30 Eyl 2027'ye kadar; 50 t/yıl muafiyet | AB Komisyonu |
| TR ETS | 7552 sayılı İklim Kanunu (9 Tem 2025); >50.000 tCO2e tesisler; 2026 yalnızca raporlama | iklim.gov.tr |
| Türkiye CBAM ihracatı | ⚠️ ~€10,83 milyar (2025, doğrulanmalı) | ikincil |
| Veri merkezleri | 2025'te ~485 TWh, yıllık +%17 | IEA |
| Biyoçeşitlilik | 1970–2020 izlenen popülasyonlarda ortalama %73 düşüş | WWF LPR 2024 |

### Yapılabilirlik × Etki Sıralaması (22 saat, tek kişi)
1. İzmir baraj & kuraklık erken uyarı (F5/E5)
2. CBAM / TR ETS uyum (F4/E5) — jüri (CarbonEmit) alanı
3. İzmir Körfezi hipoksi/alg erken uyarı (F4/E5) — doğrulama zor
4. Orman yangını riski (F4/E5) — rekabet yoğun
5. Kentsel ısı adası yeşillendirme optimizasyonu (F4/E4)

## 2. Benzer Hackathonlarda Kazanan Projelerden Dersler
Örnekler: WaterWise (NASA Space Apps 2024 — ET verisi → "bu gece kaç saat sula"), QUEÑARIS (NASA 2025 — tek şehir/tek ekosistem), BugBit/Yolanda (CASSINI — Sentinel-2 ile böcek salgını erken uyarı → şirketleşti), GeoGemma (Google Solution Challenge 2025), ClimateHack.AI (küçük model, en iyi MAE), TRACE (AI x City 2026 — "kim eksik?" sorusu), Pina (orman karbon MRV).

**Kazandıran örüntüler:**
1. Dashboard değil **tek bir karar** satmak ("ne yapmalıyım?" sorusuna cevap).
2. Tek yer + tek ekosistem + tek nedensel zincir.
3. Ölçülebilir teknik iddia (metrik, baseline karşılaştırması).
4. Veri soyu görünür: hangi veri, hangi model, hangi varsayım, sınırlamalar.
5. AI ürünün içinde; LLM/chatbot ek katman, çekirdek değil.
6. Küçük/verimli model > büyük model.
7. Gerçek kullanıcı/pilot ve "kim öder" cevabı.
8. Teslim paketi bütünlüğü: çalışan demo + README + veri kaynakları + sınırlamalar.

**Klişeler (kaçınılacak):** kişisel karbon hesaplayıcı + chatbot, genel sürdürülebilirlik dashboard'u, atık sınıflandırıcı, "iklim ChatGPT" (RAG), AQI panosu, blockchain karbon kredisi. Klişenin içindeki **kararı** al ve kanıtlanabilir yap.

**Jüriye özel:**
- CarbonEmit: tedarikçi verisi, emisyon faktörü, denetim izi, CBAM/ISO 14067. Onların ürününü kopyalama; tamamlayıcı katman ol.
- Veri topluluğu: baseline, segment bazlı hata, eksik veri yönetimi, tekrarlanabilirlik, açık/yerel veri (acikveri.bizizmir.com, İZSU).
- CS mezunu: mimari şema, test, structured output, fallback, maliyet.

**3–5 dk sunum akışı:** yerel sayı ve etkilenen kişi (30 sn) → kararı kim veriyor, bugün nasıl veriliyor (30 sn) → tek senaryo canlı demo (90 sn) → AI: model, veri, metrik (45 sn) → etki, kim öder, ölçek (45 sn) → sınırlamalar ve kapanış (30 sn).

## 3. Doğrulanmış Veri Erişimi (İzmir Açık Veri — CKAN API)
Lisans: İzmir BB Açık Veri Lisansı (portal içeriği CC BY 4.0). Doküman: https://openfiles.izmir.bel.tr/309436/docs/izsu-WebServisKullanimDokumani_1.0.pdf
| Veri seti | Erişim | Güncelleme | Not |
|---|---|---|---|
| Barajların güncel doluluk oranları | API `https://openapi.izmir.bel.tr/api/izsu/barajdurum`, CSV `https://openfiles.izmir.bel.tr/309436/docs/izsu-baraj-doluluk-oranlari.csv` | Günlük | **Yalnızca güncel değer**; geçmiş seri yok → zaman serisi için kendi arşivimiz/başka kaynak gerekir |
| Su üretiminin aylara ve kaynaklara göre dağılımı | API `.../api/izsu/suuretiminindagilimi`, CSV/XLSX (~62 KB) | Aylık | Geçmişe dönük aylık seri (baraj/kuyu bazında) → tahmin modeli için ana aday |
| Günlük su üretimi | API `.../api/izsu/gunluksuuretimi`, CSV | Günlük | Tek günlük değer |
| Baraj su kalite raporları | API `.../api/izsu/barajsukaliteraporlari` | Haftalık | Su kalitesi analizleri |
| Baraj ve kuyu listesi | API `.../api/izsu/barajvekuyular` | Sabit | Konumlar (harita için) |

⚠️ 7 Kas 2026 ~12:00 testinde `barajdurum` API'si **HTTP 500**, aylık üretim CSV'si "Unexpected error" döndü → İzmir açık veri servisleri kararsız olabilir. Bu yol seçilirse: veri hemen çekilip repoya önbelleklenmeli; yedek kaynak olarak İZSU sayfası (https://izsu.gov.tr/bilgi-merkezi/barajlar/su-durumu, HTML) kullanılmalı.

## 4. Su Kıtlığı + Sanayi Fikri — Veri Doğrulama (curl ile test edildi, dosyalar `/tmp/opencode/ekozeka_tests/` altında hazır)

**Çalışan, anahtarsız kaynaklar:**
1. **WRI Aqueduct 4.0:** `files.wri.org/aqueduct/aqueduct-4-0-water-risk-data.zip` (249 MB, CC BY 4.0, indirildi). Türkiye için **639 alt-havza satırı**; baseline (13 gösterge: `bws`, `bwd`, `gtd` yeraltı düşüşü, `drr` kuraklık riski vb.) + **2030/2050/2080** (BAU/iyimser/kötümser) projeksiyonları. `pfaf_id` ile join ediliyor. Gediz alt-havzası (`211055`): baseline `0,989` (>%80, Extremely High), 2030 BAU `1,06`, 2050 BAU `1,72`, 2080 BAU `2,53` (kötümser `3,16`).
2. **Open-Meteo Climate API (CMIP6 HighResMIP):** `climate-api.open-meteo.com/v1/climate` (1950–2050, 10 km, 7 model, CC BY 4.0; ücretsiz katman ticari değil; dakikalık rate limit var → toplu istek + cache şart). `et0` alanı null dönüyor → Tmax/Tmin/radyasyon ile Hargreaves/Penman-Monteith biz hesaplayacağız.
3. **Open-Meteo Archive (ERA5):** `archive-api.open-meteo.com/v1/archive` (1940–günümüz, günlük P, T, ET₀; indirildi).
4. **Open-Meteo Flood (GloFAS):** 1984–günümüz + 92 gün nehir debisi tahmini (Gediz test edildi).
5. **İZSU canlı HTML + CSV:** `izsu.gov.tr/bilgi-merkezi/barajlar/su-durumu` (Next.js JSON gömülü: 5 baraj doluluk + geçen yıl aynı gün — örn. Tahtalı bugün %41,39, geçen yıl aynı gün **%1,54**); `izsu-gunluk-su-uretimi.csv` (baraj vs kuyu üretimi); `izsu.gov.tr/su-ve-atik-su-tarifesi` (01.06.2026 sanayi 1c tarifesi: 0–10 m³ **143,66 TL**, 11–20 m³ **199,65 TL**, 21+ m³ **403,79 TL/m³** KDV hariç; geri kazanılmış su 11,95 TL/m³).
6. **Önlem & ROI katalogları (indirildi):** Tarım ve Orman Bakanlığı SYGM "NACE Kodlarına Göre Endüstriyel Su Kullanım Verimliliği" rehber PDF'leri (152 NACE, MET listeleri, %17–78 tasarruf, geri ödeme süreleri; lisans: her hakkı saklı → yalnızca atıflı sayı kullan, PDF dağıtma) + IFC *Cash Flows with Water* (gerçek sanayi vakaları: kapalı devre soğutma <2 yıl geri ödeme, sensör/basınç <60 gün, yağmur suyu 3,5 yıl).
7. **Gediz Havzası Sektörel Su Tahsis Planı & Eylem Planı (SYGM PDF):** Gediz'de sanayi talebinin **%100'ü yeraltı suyundan** karşılanıyor; tahsis karşılama oranı normal senaryoda %85,9 → %80,4 (2040), **kuraklık senaryosunda %37,1** (~üçte iki kesinti riski).

**Çalışmayan / kullanılmayacak kaynaklar:** DSİ baraj API (WAF engeli), TÜİK API (403/503), İzmir OpenAPI `barajdurum` ve aylık üretim CSV (HTTP 500 / bozuk dosya), OSB web sitelerindeki su tarifeleri (yayınlanmamış), NASA GRACE (login + 300 km çözünürlük), WWF Water Risk Filter (veri indirme kapalı).

## 5. Kırmızı Takım (Red-Team) ve Pazar Bulguları
- **Sektörel gerçek:** Türkiye'de suyun ~%79'unu tarım tüketir (DSİ: 48,7 / 61,7 milyar m³). TÜİK şebeke/temin çekiminde (20,3 milyar m³, tatlı su 9,2 milyar m³) sanayi toplamı (imalat %7,3 + maden/OSB %5,8 + termik %1,6) **~%14,7**. Yani "sanayi en büyük tüketici" demek **yanlış**; doğru cümle: *"Sanayi su kıtlığının m³ başına en pahalıya patladığı, Gediz'de %100 yeraltı suyuna bağımlı olan, kuraklıkta tahsisi %37'ye düşen ve ödeme/yatırım kapasitesi olan kesim."*
- **Regülasyon tetikleyicisi:** **Su Verimliliği Yönetmeliği (RG 27.12.2024, No. 32765)** → OSB'ler ve Ek-2 NACE listesindeki 50+ çalışanlı tesisler **27.12.2029**'a kadar Yeşil Su Verimliliği Belgesi almak zorunda. Ayrıca **TSRS** (~400 büyük şirket) ve **Yeşil OSB** (TSE) sertifikası. (Dikkat: CBAM suyu **kapsamaz**, sadece karbon.)
- **Rakipler:** Küreselde Aqueduct, WWF, Ecolab, Waterplan. Türkiye'de **Blueit** (İzmir, 40+ tesis, gerçek zamanlı IoT + finansman ortaklığı), **Suversis** (2029 belgesi), **CarbonEmit** (500+ şirket, ISO 14046 su ayak izi, tek tesis ücretsiz), **Mizanera**, **3pmetrics**. Ayak izi/rapor bacağı dolu; boşluk **ileriye dönük havza/iklim senaryosu + kuraklıkta TL üretim durma riski + bütçe kısıtlı önlem portföyü optimizasyonu + 2029 belge açığı** kesişiminde. CarbonEmit ile rekabet değil **tamamlayıcılık** (onlar geçmiş muhasebe/ISO 14046, biz gelecek senaryo ve yatırım kararı).
- **Yer seçimi vs mevcut fabrika:** Yer seçimi bir firmada 5–10 yılda bir verilir (ancak OSB yönetimleri, yatırım ajansları, bankalar/leasing için tekrarlayan karar). Mevcut fabrika ise 2029 zorunluluğu ve su faturası nedeniyle acil. İkisi aynı hesaplama motorunun iki modu olarak sunulmalı.

## 6. Literatür Yöntemleri (Metodolojik Dayanaklar — Jüri Savunması İçin)

> Bu bölüm, "hangi yöntemi neden seçtik" sorusunun kaynaklı cevabıdır. Kodda kullanılan her yöntemin arkasında hakemli literatür vardır.

| Yöntem | Ne için | Kaynak |
|---|---|---|
| **FAO-56 Penman-Monteith** | Referans buharlaşma (`ET₀`); tam meteoroloji varsa birinci tercih | Allen, Pereira, Raes & Smith (1998), *FAO Irrigation and Drainage Paper 56* |
| **Hargreaves-Samani** | Radyasyon/nem eksikse `ET₀` tahmini (CMIP6 API'sinde `et0` null olduğu için zorunlu yedek) | Hargreaves & Samani (1985), *Applied Engineering in Agriculture* 1(2) |
| **SPI (Standartlaştırılmış Yağış İndeksi)** | Kuraklık şiddeti/süresi; yalnızca yağışla | McKee, Doesken & Kleist (1993), *8th Conf. on Applied Climatology* |
| **SPEI (Standartlaştırılmış Yağış-Evapotranspirasyon İndeksi)** | Sıcaklık artışını da içeren kuraklık indeksi; iklim değişimi altında SPI'dan üstün | Vicente-Serrano, Beguería & López-Moreno (2010), *Journal of Climate* 23(7) |
| **Quantile Delta Mapping (QDM)** | CMIP6 ham çıktısının ERA5 yerel dağılımına yanlılık düzeltmesi (kantil eşleştirme + trend koruma) | Cannon, Sobie & Murdock (2015), *Journal of Climate* 28(17) |
| **Delta-change (yedek)** | QDM için yeterli örtüşme yoksa ortalama fark ekleme | Klasik yanlılık düzeltme yaklaşımı (Tebaldi & Knutti 2007 derlemesi) |
| **GroupKFold çapraz doğrulama** | Mekânsal sızıntıyı engellemek (komşu havzaların test setine düşmemesi) | Roberts vd. (2017), *Ecography* 40(8) — mekânsal çapraz doğrulama |
| **XGBoost** | Doğrusal olmayan yanlılık düzeltmesi / ölçek indirme (etiket: ERA5 gözlemi) | Chen & Guestrin (2016), *KDD* |
| **SHAP (TreeExplainer)** | Ağaç modellerinde tutarlı özellik katkısı | Lundberg & Lee (2017), *NeurIPS* |
| **KMeans (havza arketipleri)** | Benzer davranışlı havzaları gruplama; "sizin havzanız şu 14 havza gibi" anlatısı | MacQueen (1967); kullanım: hidrolojik sınıflandırma |
| **Isolation Forest** | İZSU baraj/üretim serilerinde anomali tespiti | Liu, Ting & Zhou (2008), *ICDM* |
| **0-1 Knapsack / MILP** | Bütçe kısıtı altında NPV maksimizasyonu (kesin çözüm) | Kellerer, Pferschy & Pisinger (2004), *Knapsack Problems* |
| **Azalan verim (çarpımsal tasarruf)** | Aynı prosesteki önlemlerin toplanamaması; `1 − ∏(1−rᵢ)` | Endüstriyel su verimliliği mühendislik pratiği (SYGM NACE rehberleri, IFC 2017) |

**Sunumda kullanılacak tek cümle:** *"Buharlaşmayı FAO-56 ile, kuraklığı SPEI ile, iklim modeli düzeltmesini QDM + XGBoost ile, belirsizliği CMIP6 topluluğunun P10–P90 dağılımıyla hesaplıyoruz; yatırım kararını da kesin çözümlü bütçe kısıtlı optimizasyonla veriyoruz. Hiçbir adım kara kutu değil."*
