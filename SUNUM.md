# SUNUM — EkoZeka26: AquaSanayi AI Sunum ve Savunma Rehberi

> **Durum (sunum sürümü, 8 Kasım 2026):** `uv run pytest -q` → **23 passed**. Canlı demo `127.0.0.1:8000` üzerinde çalışır. İZSU zinciri: taze canlı önbellek (6 saat TTL) → doğrulanmış snapshot → fallback. Üç gerçek fabrika vakası **finansal headline** ile günceldir: Tofaş `%35,8` / **17,3 ay**; Vestel `%24,0` / **3,9 ay**; Petkim `%48,0` / **20,8 ay**. Önlenen duruş riski ayrı gösterilir ve finansal NPV'ye dahil edilmez.
> **Süre:** 4–5 dakika (soru-cevap dahil) · **Format:** Canlı sunum + canlı demo · **Rehber:** Sağ üstteki **Rehber** düğmesi (16 adım; `←` / `→` / `Esc`).

---

## 0. Sunumun 5 Vurgusu (Ezberlenecek Cümleler)

1. **Kriz gerçek ve güncel.** İzmir barajları kapasite-ağırlıklı **%34,0** dolu; kapasitenin **%58'ini** tutan Gördes **%28,0**. Tahtalı geçen yıl aynı gün **≈%1,5** iken bugün **%41,4**. 2025, Türkiye'nin **1964'ten beri en kurak yılı** (yağış normalin **%27,6** altında).
2. **Doğru problem.** Türkiye'de suyun **%79'u tarımda**; ama sanayi, tatlı su şebekesinin **~%15'ini** çeker. Gediz'de sanayi suyunun **%100'ü yeraltı kuyularından** gelir; kuraklıkta tahsis **%37,1'e** düşer — yani **%62,9 kesinti**. Üstüne **27.12.2029 Yeşil Su Verimliliği Belgesi** zorunluluğu var.
3. **İki soru, iki sekme.** “Fabrikamı nereye kurmalıyım?” → şeffaf risk + P10–P90 kesinti aralığı. “Mevcut fabrikamda ne yapmalıyım?” → bütçe kısıtlı **finansal NPV** + 2029 belgesi.
4. **Şeffaf yapay zekâ.** 5 bileşenli risk indeksi (kara kutu değil), 7 gerçek CMIP6 modeli + ayrı QDM, XGBoost ölçek indirme (`R² = 0,7958`, `MAE = 0,1534`), SHAP, KMeans arketipleri ve İZSU Isolation Forest anomalisi.
5. **Finansal dürüstlük.** Headline yalnızca **su faturası + OPEX − CAPEX**. Duruş riski ayrı ve “beklenen, garanti değil”. Tofaş **17,3 ay / +6,64M TL**, Vestel **3,9 ay / +93,27M TL**, Petkim **20,8 ay / +142,97M TL**; üçü de **2029 Yeşil** hedefini karşılar.

---

## 0.1 Rehber Turu ve 60 Saniyelik Demo Rotası

- **Rehber nerede?** Sağ üstte, “Rehber” düğmesi. Açınca 16 adımlı spot ışıklı tur başlar; `←` / `→` ile gezinilir, `Esc` veya **Kapat** ile çıkılır. Adım 10'da otomatik olarak **2. sekme** açılır ve Tofaş örneği hesaplanır.
- **4 dakikalık kısa rota (önerilen):** Adım **1 → 3 → 5 → 6 → 8 → 10 → 12 → 14 → 15 → 16**. Diğer adımları atlayın.
- **2 dakikalık çok kısa rota:** Adım **1 → 3 → 5 → 6 → 10 → 12 → 14 → 16**.
- **Sunum öncesi:** Rehberi bir kez açıp 1. adımda bekletin; demo sırasında hazır açılmış olsun. Tarayıcı zoom'u **%100** olsun.

---

## 1. Altın Sayılar Tablosu (Slaytlarda ve Konuşmada Kullanılacak Doğrulanmış Veriler)

### A) İklim ve İzmir/Ege Su Krizi Verileri

| Gösterge | Sayısal Değer | Kaynak | Sunumda Nasıl Kullanılır? |
|---|---|---|---|
| Küresel ısınma | **2015–2025** kayıtlı en sıcak 11 yıl; 2025 **+1,43°C** | WMO (Mart 2026) | “İklim krizi gelecek tahmini değil, içinde bulunduğumuz gerçek.” |
| Türkiye kuraklık rekoru | 2025: **1964'ten beri (61 yılın) en kurak yılı**, yağış normalin **%27,6 altında** | MGM | “Türkiye son 60 yılın en sert kuraklık rejimine girdi.” |
| İzmir barajları gerçek doluluk (6 Kas 2026) | Kapasite-ağırlıklı **%34,01** (`257,17 / 756,19 Mm³`); basit ortalama **%44,24** | İZSU Canlı Veri | **Veri okuryazarlığı kancası:** “Medyada %44 deniyor çünkü 5 barajın basit ortalamasını alıyorlar. Oysa kapasitenin **%57,9'unu** tutan Gördes Barajı sadece **%27,96** dolu!” |
| Yıllar arası aşırı oynaklık | Tahtalı Barajı: Geçen yıl (6 Kas 2025) **≈%1,5** → Bu yıl **%41,39** | İZSU Canlı Veri | “Tek yıllık ortalamayla plan yapılamaz; olasılıksal (P10–P90) yapay zekâ şart.” |
| İzmir yeraltı suyu baskısı | **~1.600 kuyu**, 2025'te **110 yeni kuyu**, **318 kıyı kuyusu** tuzlanma riskinde | İZSU | “Yüzey suyu yetmeyince yeraltına yükleniyoruz, kuyular tuzlanıyor.” |
| Gediz Havzası su stresi projeksiyonu | Baseline: **0,99** (Aşırı Yüksek) → 2030: **1,06** → 2050: **1,72** → 2080: **2,53** (Kötümser: **3,16**) | WRI Aqueduct 4.0 (`pfaf_id=211055`) | “1,0'ın üzeri demek, havzadaki su talebinin doğanın yenileyebildiği suyu aşması demek.” |

### B) Neden Sanayi? (Sektörel Gerçekler ve Tuzaktan Kaçınma)

| Gösterge | Sayısal Değer | Kaynak | Sunumda Nasıl Kullanılır? |
|---|---|---|---|
| Türkiye toplam su kullanımı (DSİ) | Toplam **61,7 milyar m³**: Tarım **%79** (`48,7 Mr m³`), İçme+Sanayi **%21** (`13,0 Mr m³`) | DSİ / ÇŞB (2024) | **Asla “en çok suyu sanayi harcıyor” deme!** “Hacim olarak suyun %79'unu tarım harcar; ama 2,2 milyon çiftçiye B2B karar yazılımı satamazsınız.” |
| Şebeke/Temin tatlı su çekimi (TÜİK) | Toplam çekim **20,3 Mr m³** (Tatlı su **9,2 Mr m³**): Belediyeler **%81**, Sanayi toplamı **~%14,7** (İmalat %7,3 + Maden/OSB %5,8 + Termik %1,6) | TÜİK (Aralık 2025) | **Veri bilimi jürisine dipnot:** “DSİ barajdan sulamaya verilen suyu, TÜİK temin ağlarını ölçer; aradaki fark kapsam farkıdır.” |
| **Gediz Havzası sanayi bağımlılığı (KRİTİK!)** | Sanayi su talebi (**72,2 hm³/yıl → 162,4 hm³/yıl**): **%100'ü yeraltı suyundan** karşılanıyor | Tarım ve Orman Bakanlığı (SYGM) Gediz Tahsis Planı | “İzmir-Manisa sanayisi tamamen yeraltı kuyularına bağımlı.” |
| **Kuraklıkta sanayi kesintisi (KRİTİK!)** | Tahsis karşılama: Normalde **%85,9** → Kuraklık senaryosunda **%37,1** (**%62,9 kesinti!**) | SYGM Gediz Sektörel Su Tahsis Planı | **“Kurak bir yılda fabrikanın suyunun üçte ikisi kesiliyor; bu doğrudan üretimin durması demek!”** |
| İzmir sanayi su fiyatı (Haziran 2026) | Sanayi (1c) 21 m³/ay üstü: **403,79 TL/m³** (KDV hariç). Geri kazanılmış su: **11,95 TL/m³** | İZSU Resmi Tarife (01.06.2026) | “Şebeke suyu 404 TL iken geri kazanım 12 TL; su verimliliği artık çevre hayırseverliği değil, doğrudan finansal kârlılık.” |
| **Yasal Zorunluluk (Deadline)** | **27 Aralık 2029**: OSB'ler ve Ek-2 NACE listesindeki 50+ çalışanlı fabrikalar **Yeşil Su Verimliliği Belgesi** almak zorunda | Su Verimliliği Yönetmeliği (RG 27.12.2024, No. 32765) | “Şirketlerin önünde 2029'a kadar yasal bir saatli bomba var.” |
| Pazar büyüklüğü (Türkiye) | **416 OSB**, **68.000+ fabrika**; sadece **27 Yeşil OSB** ve **3 ISO 46001** belgeli OSB var | OSBÜK / TSE | “Pazarın %93'ü henüz dönüşmedi; hedef kitlemiz net ve ödeme gücüne sahip.” |

### C) Önlem ve Yatırım Geri Dönüşü (ROI) Katsayıları

| Önlem / Kategori | Tasarruf Oranı | Tipik Geri Ödeme (Payback) | Kaynak |
|---|---|---|---|
| Tüm sektörel MET'ler (potansiyel tavan) | **%17 – %78** | 1 – 5 yıl | SYGM NACE Rehberleri |
| Kapalı devre soğutma kulesi dönüşümü | Soğutmada **>%95** geri kazanım | **< 2 – 4 yıl** | SYGM / IFC (2017) |
| Basınçlı/otomatik nozullar & sensör kontrolü | Proseste **%20 – %30** (toplamda %4–10) | **< 60 gün – 1 yıl** | SYGM / IFC |
| Durulama / proses suyu kaskad geri kazanımı | **%15 – %35** | **1 – 2,5 yıl** | SYGM NACE Rehberleri |
| Yağmur suyu hasadı + gri su | Toplamda **%5 – %10** | **3 – 3,5 yıl** | IFC (2017) |
| ISO 46001 dijital su izleme & kaçak kontrolü | Toplamda **%3 – %6** | **6 – 12 ay** | SYGM |

> **Dış benchmark:** US EPA soğutma kulesi ~**5 yıl**, PNNL soğutma suyu geri kullanımı ~**6 yıl**, yerinde su geri kazanımı **3–7 yıl**, MWRA ticari verimlilik ~**1,4 yıl**. Bizim finansal headline'ımız (3,9–20,8 ay) bu aralığın altında ama artık aynı mertebede; katalog tipik süreleri (3,5–24 ay) ile birlikte okunmalıdır.

### D) Kendi Modelimizin Çıktı Metrikleri

- **Kapsanan Türkiye Poligonu / Havza:** `639` poligon (WRI Aqueduct 4.0 GDB) = `116` tekil `pfaf_id` hidrolojik havza; **“639 bağımsız havza” değildir**, ulusal katman ön taramadır.
- **İklim Modeli Topluluğu:** **7 gerçek CMIP6 HighResMIP modeli** (2020–2050, Open-Meteo) + ERA5 (1940–2025), `3` senaryo (OPT/BAU/PES). Her model ayrı QDM ile kalibre edilir; P10–P90 bandı gerçek model yayılımıdır.
- **Kuraklık İndeksleri:** `SPI-3`, `SPI-12`, `SPEI-3`, `SPEI-12` (log-logistic); kuraklık sınıfları ve trend eğimi (tek referans noktası: İzmir/Gediz).
- **Bölgesel iklim referansı (sınırlama):** ERA5/CMIP6 şu an tek noktadan (İzmir) alınır; Bursa/Kocaeli/Konya farkı Aqueduct + enlem offseti ile üretilir. **Bursa/Konya P−ET₀ eğrisi ikincil güvenilirliktedir**; risk sıralaması büyük ölçüde Aqueduct ağırlıklı olduğu için tamamen bozulmuş değildir. Bölgesel iklim çapaları sonraki sürümde eklenecek.
- **İZSU canlı/offline:** Demo önce **6 saatlik taze canlı önbelleği** kullanır; yoksa 6 Kasım 2026 doğrulanmış snapshot'ına, o da yoksa `data/fallback/` snapshot'ına düşer. `uv run python -m ekozeka26.izsu_source --refresh` ile canlı baraj sayfası çekilir; başarısız olursa API çökmez ve `fallback_reason` döner.
- **XGBoost Mevsimsel/Mekânsal Ölçek İndirme (5-katlı GroupKFold, 1.392 Aqueduct havza-ay model çıktısı):** Naive (Kaba Yıllık) `MAE = 0,4789, RMSE = 0,9598, R² = -0,0044` → Doğrusal Regresyon (Ridge) `MAE = 0,2940, RMSE = 0,5827, R² = 0,6297` → **XGBoost Downscaler (`max_depth=4`) `MAE = 0,1534, RMSE = 0,4328, R² = 0,7958` (Naive modele göre hatada %68,0 düşüş; SHAP çıkarımı tipik 2–15 ms, soğuk çalıştırmada <50 ms)**. Not: Etiketler yerinde ölçüm değil, WRI Aqueduct aylık model çıktısıdır.
- **Backtest (1984–2025 ERA5 + GloFAS Gediz Debi & 2021/2024/2025 Kurak Yıllar):** `2015–2025` (132 ay) dış-örneklem test dönemi **XGBoost `R² = 0,6732` (`MAE = 0,0269 m³/s`, `RMSE = 0,0545 m³/s`)**; 2024 ve 2025 yaz aylarında gözlenen minimum debi `0,00 m³/s` kuraklık çöküşü doğrulandı.
- **İZSU Gerçek Anomali Bulguları (`izsu_aylik.html` 137 ham satır → 126 tekil tesis-ay + 23 günlük baraj kesiti):** Kasım 2025 kuraklığında Tahtalı **aylık üretimi** **6,91 Mm³ → 1,62 Mm³ (-%76,5)** çökerken yeraltı kuyuları (Göksu + Halkapınar + Sarıkız + Menemen) arzın **%69,33'ünü** üstlendi (**Isolation Forest Anomali Skoru: `0,5932`, `ANOMALİ = TRUE`**); son 23 günde (14 Ekim → 6 Kasım 2026) Balçova Barajı **-%7,43 puan** (`%44,77 → %37,34`) düştü ve Gördes/Balçova günlük üretimi `0 m³/gün` oldu. **Güncel günlük kuyu payı %81,1'dir; %69,3 Kasım 2025 aylık üretim payıdır.**
- **3 Gerçek Fabrika Vakası ve ROI Çıktıları (2024 kamuya açık rapor verileri):**
  1. **Tofaş — Bursa Tesisi (`430.782 m³/yıl`, %100 yeraltı kuyusu `24,80 TL/m³`, `4.409` çalışan, `6,0M TL` bütçe, 2030 BAU):** Risk skoru **53,7/100**; “hiçbir şey yapılmazsa” beklenen duruş riski **31,05M TL/yıl** (P10–P90: 16,2–55,1M TL; **20,7 gün**). Seçilen portföy: `M01, M03, M04, M10` → **`%35,8` tasarruf (`154.091 m³/yıl`)**, **CAPEX 5,71M TL (bütçenin %95'i)**, **finansal NPV = +6,64M TL**, **finansal geri ödeme 17,3 ay**, **Yeşil Su Verimliliği Belgesi (Tam Uyum)**. Ayrıca **12,77M TL/yıl** beklenen duruş riski azaltımı (finansal NPV'ye dahil değil).
  2. **Vestel — Manisa Kampüsü (`1.510.208 m³/yıl`, %71,4 şebeke + %28,6 kuyu, `29.000` çalışan, `12,0M TL` bütçe, 2030 BAU):** Risk skoru **80,2/100**; beklenen duruş riski **82,5M TL/yıl** (**33,0 gün**). Seçilen portföy: `M01, M02, M10` → **`%24,0` tasarruf (`362.450 m³/yıl`)**, **CAPEX 10,67M TL**, **finansal NPV = +93,27M TL**, **finansal geri ödeme 3,9 ay**, **Yeşil Belge**. Ayrıca **22,77M TL/yıl** beklenen duruş riski azaltımı.
  3. **Petkim — Aliağa Kompleksi (`14.230.105 m³/yıl`, %62 soğutma, yüzey suyu `15,00 TL/m³`, `2.433` çalışan, `250M TL` bütçe, 2050 BAU):** Risk skoru **68,2/100**; beklenen duruş riski **420,0M TL/yıl** (**28,0 gün**). Finansal optimizasyonun seçtiği portföy: `M01, M05, M10` (`M05` Kapalı Devre Soğutma) → **`%48,0` tasarruf (`6.831.873 m³/yıl`)**, **CAPEX 177,41M TL**, **finansal NPV = +142,97M TL**, **finansal geri ödeme 20,8 ay**, **Yeşil Su Verimliliği Belgesi**. Ayrıca **231,89M TL/yıl** beklenen duruş riski azaltımı. *Not: Risk-dahil eski portföy `M01, M04, M05, M10` ile Turkuaz'a ulaşıyordu; finansal optimizasyon M04'ü seçmediği için kademe Yeşil'e indi. Turkuaz gönüllü üst kademedir; 2029 zorunlu Yeşil hedefi karşılanıyor.*

### E) Doğrulama Durumu (Jüriye Şeffaf Cevap)

| Veri | Durum | Sunumda Söylenecek |
|---|---|---|
| Tofaş 430.782 m³; Vestel 1.510.208 m³; Petkim 14.230.105 m³ | **Doğrulandı** (2024/2025 kamuya açık rapor snippet'leri) | “Su hacimleri şirketlerin kendi raporlarından.” |
| İZSU sanayi 403,79 TL/m³; geri kazanım 11,95 TL/m³ | **Doğrulandı** (resmî İZSU tarifesi) | “İZSU resmî tarifesi.” |
| Konya KOSKİ 98,39 TL/m³ | **Doğrulandı** (2026 tarife haberi) | “KOSKİ resmî tarifesi.” |
| 416 OSB / 68.000+ fabrika / 27 Yeşil OSB / 3 ISO 46001 | **Doğrulandı** (OSBÜK / TSE) | “Pazarın %93'ü dönüşmedi.” |
| Manisa/Kemalpaşa/Aliağa 118,50 TL/m³ | **Kalibre varsayım** (BOSB referanslı; iç tarifeler kamuya kapalı) | “OSB iç tarifesi kamuya açık değil; BOSB referansıyla kalibre ettik.” |
| Tofaş kuyu 24,80 TL/m³ | **Kalibre varsayım** (pompaj + bakım + YAS) | “Kuyu maliyeti kalibre; resmî tarife değil.” |
| Petkim yüzey suyu 15,00 TL/m³ | **Kalibre varsayım** (DSİ ham su + arıtma) | “Yüzey suyu maliyeti kalibre.” |
| Bursa BOSB 122,00 TL/m³ | **Resmî tarife notu** (BOSB 2026; bağımsız kamu snippet'i yok) | “BOSB'nin kendi resmî tarife notu.” |
| Kocaeli 80,33 TL/m³ | **Kurum tarifesi** (İSU 73,33 + GOSB 7,00; bağımsız snippet yok) | “İSU + GOSB altyapı bedeli.” |
| Kesinti günleri (P10–P90) | **Sezgisel risk-süre indeksi** (tarihsel fabrika kesinti verisi yok) | “Gösterge niteliğinde; garanti değil.” |
| CAPEX ölçeklemesi | **Doğrusal** (150.000 m³/yıl referans; 0,5–100×) | “Mühendislik yaklaşımı; önlem tipine göre üs sonraki sürümde.” |

### F) Tarife Duyarlılığı (Finansal Headline)

| Tesis | 0,6× tarife | Baz | 1,4× tarife |
|---|---:|---:|---:|
| Tofaş | 28,9 ay | **17,3 ay** | 12,4 ay |
| Vestel | 6,4 ay | **3,9 ay** | 2,8 ay |
| Petkim | 39,9 ay (NPV −13,8M TL) | **20,8 ay** | 17,1 ay |

> **Cümle:** “Tek bir kesin geri ödeme söylemiyoruz; tarife ±%40 oynadığında bant veriyoruz. Petkim'de %40 düşük tarifede NPV negatife döner; bu yüzden karar bandı önemli.”

### G) Tofaş Önlem Bazlı Geri Ödeme (Model vs Katalog)

| Önlem | Model (finansal) | Katalog tipik | Farkın nedeni |
|---|---:|---:|---|
| M01 — Basınçlı nozullar | 7,6 ay | 3,5 ay | Tofaş kuyu suyu 24,80 TL/m³; katalog daha yüksek tarife varsayar |
| M03 — Kaskad durulama | 16,6 ay | 11,0 ay | CAPEX kapasiteye göre 2,87× ölçeklendi |
| M04 — Buhar kondensi | 25,2 ay | 9,0 ay | Kazan hattı CAPEX'i yüksek; su tasarrufu tek başına sınırlı |
| M10 — RO konsantre geri kazanımı | 18,6 ay | 10,5 ay | Membran/hat CAPEX'i ölçekle öne çıkıyor |

> **Cümle:** “Katalog ‘tipik’tir; model tesisin gerçek tarifesi, proses payı ve CAPEX ölçeğiyle hesaplar. İkisini yan yana gösteriyoruz; farkı saklamıyoruz.”

---

## 2. Dakika Dakika Sunum ve Canlı Demo Senaryosu (Toplam: 4 Dakika)

### 0:00 – 0:45 | 1. Perde: Kanca ve Doğru Problem Çerçevesi

- **Açılış cümlesi:** *“Bugün İzmir'de haberleri açarsanız barajlarımız %44 dolu diyorlar. Ama bu 5 barajın basit ortalaması. İzmir'in su kapasitesinin %58'ini tek başına tutan Gördes Barajı bugün %28 dolu; yani gerçek ağırlıklı doluluğumuz sadece **%34**.”*
- **Pivot (Neden Sanayi?):** *“Peki su kıtlığını nasıl çözeriz? Türkiye'de suyun %79'unu tarım harcar ama 2 milyon çiftçiye kurumsal karar yazılımı satamazsınız. Sanayi ise tatlı su şebekesinin ~%15'ini çeker ama Gediz Havzası'nda sanayi suyunun **%100'ü yeraltı kuyularından** gelir ve Bakanlığın tahsis planına göre kurak bir yılda sanayiye verilen su **%37'ye düşer — yani %63 kesinti ve üretimin durması!** Üstelik İZSU sanayi su fiyatı **404 TL/m³** oldu ve 2024 sonunda çıkan yönetmelikle fabrikalar **27 Aralık 2029'a kadar Yeşil Su Verimliliği Belgesi** almak zorunda. Biz su kıtlığını, bu krizden milyonlarca lira zarar edecek olan fabrikaya, kendi kârıyla çözdürüyoruz.”*

### 0:45 – 1:50 | 2. Perde: Canlı Demo — Sekme 1 (Yer Seçimi, Şeffaf Risk & SHAP)

- Ekranda **AquaSanayi AI — Sekme 1 (Yatırım & Yer Seçimi)** açıktır.
- **Göster:** Türkiye'nin **639 poligonunu (116 tekil hidrolojik havza)** içeren haritada 2050 Kötümser/Normal su stresi katmanı. Sağ üstte İZSU canlı baraj kartları.
- **Aksiyon:** *“Diyelim ki otomotiv, elektronik veya petrokimya sektöründe yeni bir fabrika kuracağız veya bir banka olarak kredi vereceğiz. Bursa, Manisa ve Aliağa OSB'lerini karşılaştırıyoruz.”*
- **Yapay Zeka Vurgusu:**
  1. **Şeffaf Bileşik Risk İndeksi:** Tek bir kara kutu sayısı değil; skorun **her bileşeni ve ağırlığı** ekranda. *“Kemalpaşa OSB'de 2050 (BAU, tekstil) risk skoru **82,8 / 100** çıktı çünkü gelecek/yaz pik su stresi +25,0, yeraltı suyu düşüşü ve kuyu bağımlılığı +22,4, SPEI-12 kuraklık trendi +18,0 ve sektörel tahsis baskısı +13,4 puan ekledi (Bursa OSB 57,8, Gebze OSB 55,0).”* **Not:** Manisa OSB de aynı Aqueduct alt-havza değerlerini (`pfaf_id=211056`) paylaştığı için 82,8 çıkar; bu bir hata değil, Aqueduct çözünürlük sınırıdır.
  2. **Belirsizlik (P10–P90):** **7 gerçek CMIP6 modelinin** dağılımından **P10 (İyimser: 17,4 gün) / P50 (Beklenen: 33,5 gün) / P90 (Kötümser: 60,7 gün)** yıllık kesinti günü aralığı + “Kemalpaşa'da 6/7 model (%85,7) kuraklaşma yönünde” mutabakat oranı. *(Kesinti günü aralığı risk indeksinden türetilen sezgisel göstergedir; tarihsel kesinti etiketi değildir.)*
  3. **XGBoost + SHAP (dürüst rolü):** *“XGBoost'u iklimi taklit etsin diye değil, kaba yıllık projeksiyonları **yaz pik su stresine ölçek indirsin (downscaling)** diye kullandık; 7 CMIP6 modelini ise ayrı ayrı ERA5'e **QDM** ile kalibre ettik. SHAP grafiği (tipik 2–15 ms) bu havzada yaz pik stresini en çok hangi fiziksel sürücülerin (`summer_x_bws`, `month`, `bws_raw`, `sev_raw`) artırdığını gösteriyor.”*

### 1:50 – 3:10 | 3. Perde: Canlı Demo — Sekme 2 (Mevcut Fabrika ROI Optimizasyonu & 2029 Belgesi)

- **Aksiyon:** *“Peki fabrikamız zaten buradaysa? İkinci sekmeye geçiyoruz.”*
- **“Gerçek Fabrika Vakası”** butonlarından **Tofaş — Bursa**'ya tıkla: *“Kendi açık şemamıza uyan, kamuya açık 2024 entegre raporundan doğrulanmış bir tesisi tek tıkla yüklüyoruz: Tofaş Bursa, yılda 430.782 m³ suyun tamamını yeraltı kuyularından çekiyor. Bu şema herhangi bir ayak izi platformunun dışa aktarımıyla eşlenebilir; ama biz hiçbir ticari platforma bağımlı değiliz.”*
- **Kritik Mühendislik Detayı:** Su kaynağını **“Kendi Kuyusu (24,80 TL/m³)”**, **“OSB Şebekesi (118,50 TL/m³)”** ve **“Yüzey Suyu (15,00 TL/m³)”** arasında değiştirerek göster: *“Fabrika ‘benim kendi kuyum var, şebekeye para ödemiyorum’ diyebilir. Ama kuyu seçtiğinizde motorumuz havza tahsis kesintisi ve akifer riski yüzünden fabrikanın kaç gün duracağını ve **günlük üretim kaybı zararını** ayrı bir **risk kartında** hesaplıyor; bunu finansal NPV'ye katmıyor. Petkim gibi yüzey suyu kullanan dev tesislerde ise asıl risk soğutma kulesi buharlaşması.”*
- **Optimizasyon Çıktısı:** Tofaş için bütçeyi `6.000.000 TL` olarak gir → **0-1 Knapsack / MILP Optimizasyon Motoru** Bakanlığın NACE rehberindeki 12 önlem arasından bütçeye sığan **finansal olarak en kârlı** kombinasyonu seçer (proses bazında azalan verim kuralıyla, asla %100 üstü hatalı toplama yapmadan; CAPEX tesis kapasitesine göre ölçeklenir).
- Ekranda **Finansal Geri Ödeme Süresi**, **5 Yıllık Finansal NPV**, ayrı **risk azaltımı (beklenen)**, **2029 Yeşil Su Verimliliği Belgesi kademesi**, **JSON/CSV indir** ve **Gemini AI Yönetim Kurulu Özeti** görünür.
- **Tofaş'ta söylenecek üç sayı:** *“Hiçbir şey yapılmazsa yılda **31,1M TL** beklenen duruş riski; yatırım **5,71M TL**; beş yıllık **finansal NPV +6,64M TL** ve **17,3 ayda** finansal geri dönüş. Ayrıca yılda **12,8M TL** beklenen duruş riski azaltımı ve **Yeşil Belge**.”*

### 3:10 – 4:00 | 4. Perde: İş Modeli, Ölçeklenebilirlik ve Kapanış

- **Kim öder?** Türkiye'deki **416 OSB ve 68.000 fabrika**, Yeşil OSB olmak isteyen yönetimler ve yeşil kredi/leasing veren bankalar.
- **Gelir modeli:** Tesis başı yıllık SaaS aboneliği + yatırım bankaları/leasing için portföy risk analizi lisansı. Veri dışa aktarımı açık şema (JSON/CSV) ile yapılır; ticari platforma bağımlılık yoktur.
- **Kapanış:** *“Su krizini durdurmanın en hızlı yolu, su tasarrufunu fabrikalar için en kârlı yatırım haline getirmektir. Teşekkür ederim.”*

---

## 3. Jüri Soru-Cevap (Q&A) Cephaneliği

1. **[Musa Can Minaz — CarbonEmit] “Biz zaten ISO 14046 su ayak izi raporu veriyoruz, müşterimiz neden sizi de alsın?”**
   - **Cevap:** *“ISO 14046 geçmiş yılın doğrulanmış muhasebesidir ve denetim/raporlama bütçesinden çıkar. Biz doğrulanmış ayak izi raporu üretmiyoruz ve sizin verinize/API'nize de ihtiyaç duymuyoruz. Bizim sorumuz şu: ‘Önümüzdeki 10–25 yılda bu tesisin suyu kesilir mi, bu kesinti kaç TL üretim kaybı demek, ve 27 Aralık 2029 Yeşil Su Verimliliği Belgesi'ni en düşük CAPEX ile almak için hangi önlemleri seçmeliyim?’ Yani sizin raporunuz geçmişi belgeler; bizim platformumuz o belgenin üzerine ileriye dönük yatırım kararı koyar. Birbirini tamamlayan iki katmanız — ve tesis verisini kendi açık şemamızla JSON/CSV alıp verebildiğimiz için entegrasyon iddiamız yok, bağımlılığımız da yok.”*

2. **[Veri Topluluğu Jürisi] “Aqueduct ve CMIP6 zaten açık veri. Sizin XGBoost modeliniz tam olarak neyi öğreniyor ve aşırı öğrenmeyi (overfitting) nasıl engellediniz?”**
   - **Cevap:** *“İki kritik boşluğu dolduruyoruz: Birincisi, CMIP6 serbest-koşulu bir iklim simülasyonu olduğu için ERA5 ile takvim günü bazında eşleştirilemez; bu yüzden her CMIP6 modelinin olasılık dağılımını ayrı ayrı ERA5'e **Quantile Delta Mapping (QDM)** ile kalibre ediyoruz ve eksik olan `ET₀` buharlaşmasını FAO-56/Hargreaves ile hesaplıyoruz. İkincisi, gelecek projeksiyonları yalnızca **kaba yıllık ortalama** su stresini verir; oysa fabrikaların suyu **Temmuz–Ekim yaz pikinde** kesilir. **XGBoost modelimiz**, Türkiye'nin 116 havzasındaki 1.392 Aqueduct havza-ay model çıktısı üzerinde kaba yıllık hidrolojik göstergelerden (`bws`, `gtd`, `sev`, `iav`, `drr`) **aylık/yaz pik su stresine ölçek indirmeyi (downscaling)** öğreniyor. Overfitting'i **5-katlı `GroupKFold` (havza bazlı)** çapraz doğrulamayla engelledik: hiçbir havza aynı anda hem eğitim hem test setine girmedi. Sonuçta kaba yıllık baseline `MAE = 0,4789`, doğrusal regresyon `MAE = 0,2940 (R² = 0,63)` verirken, XGBoost hatayı **%68 düşürerek `MAE = 0,1534` ve `R² = 0,7958`** başarı sağladı. Etiketler yerinde ölçüm değil, WRI Aqueduct'in yayımlanmış aylık model çıktısıdır; bunu da açıkça belirtiyoruz.”*

3. **[Veri Bilimi Jürisi] “Neden doğrudan XGBoost ile 2050 riskini tahmin etmediniz?”**
   - **Cevap:** *“Çünkü o kurgu **döngüsel** olurdu: Aqueduct zaten 2050 su stresini veriyor; biz XGBoost'a ‘Aqueduct'in verdiği sayıyı tahmin et’ dersek model yeni bilgi üretmez, sadece onu taklit eder. Üstelik Türkiye için elimizde 639 satır var — bu, denetimli öğrenme için çok az. Bu yüzden mimariyi **fizik-öncelikli** kurduk: su dengesi (`P − ET₀`), SPEI/SPI, Aqueduct göstergeleri ve yeraltı bağımlılığı şeffaf bir indekste birleşiyor. XGBoost'u ise gerçekten etiketli olan yere koyduk: iklim modeli yanlılık düzeltmesi. Ayrıca KMeans ile havza arketipleri, Isolation Forest ile İZSU canlı veri anomalileri üretiyoruz. Yani ‘yapay zeka süs değil’ diyorsak, onu doğru işe koyduk.”*

4. **[DEÜ Bilgisayar Bilimleri Jürisi] “LLM (Gemini) burada sayı uydurursa (halüsinasyon) fabrika yanlış yatırım yapmaz mı?”**
   - **Cevap:** *“Kesinlikle haklısınız, bu yüzden mimarimizde **LLM hiçbir matematiksel işlem yapmaz.** Tüm risk skorları şeffaf indeksten, tüm TL ve m³ hesapları ise deterministik Knapsack optimizasyon motorumuzdan kesin JSON şemasıyla çıkar. Gemini yalnızca bu doğrulanmış JSON tablosunu yönetim kurulu diline tercüme eder; API kesilirse veya saparsa deterministik şablon motorumuz (offline fallback) devreye girer.”*

5. **[Genel Jüri] “Fabrika iki önlem aldığında ikisi de %50 tasarruf sağlıyorsa %100 mü tasarruf ediyor?”**
   - **Cevap:** *“Hayır, bu en sık yapılan mühendislik hatasıdır. Motorumuzda fabrikayı 4 alt prosese (soğutma, yıkama/proses, kazan, evsel) ayırdık. Aynı prosese uygulanan önlemler çarpımsal azalan verim formülüyle ($1 - (1-r_1)(1-r_2)$) hesaplanır ve Bakanlığın NACE rehberindeki teknik üst sınırla (%78) sınırlandırılır.”*

6. **[Genel Jüri] “Bu sistemi tek başına 22 saatte nasıl yaptın, sürdürülebilir mi?”**
   - **Cevap:** *“Mimariyi baştan modüler ayırdım: veri hattı, iklim motoru, kuraklık indeksi, risk indeksi, ML, ROI optimizasyonu, API ve arayüz birbirinden bağımsız test edilebilir. Her modülün otomatik testi var; biri çökerse diğeri çalışmaya devam ediyor. Veri katmanı tamamen önbellekli, internet giderse çevrimdışı rozetle aynı demo çalışıyor. Yani bu bir ‘demo hack’i değil, ürünün ilk sürümü.”*

7. **[Finans Jürisi] “Neden duruş zararını NPV'ye katmıyorsunuz? Fabrika için asıl risk o değil mi?”**
   - **Cevap:** *“Tam da bu yüzden ayrı gösteriyoruz. Tarihsel fabrika kesinti günü verisi kamuya açık değil; kesinti günü risk indeksinden türetilen sezgisel bir göstergedir. Bu kalemi NPV'ye katarsak geri ödeme 2–8 aya düşüyor ve dış benchmark'larla (EPA ~5 yıl, PNNL ~6 yıl) çelişiyor. O yüzden headline'ı yalnızca **su faturası + OPEX − CAPEX** yaptık; duruş riskini **ayrı, ‘beklenen, garanti değil’** etiketiyle gösteriyoruz. Yatırım kararı için iki sayıyı da görüyoruz: finansal geri dönüş ve risk azaltımı.”*

8. **[Finans Jürisi] “Tofaş 17,3 ay diyorsunuz ama katalog 3,5–11 ay diyor. Hangisi doğru?”**
   - **Cevap:** *“Katalog ‘tipik’tir; model tesisin gerçek tarifesi, proses payı ve CAPEX ölçeğiyle hesaplar. Tofaş %100 kuyu suyu kullanıyor ve kuyu maliyeti 24,80 TL/m³; katalogdaki tipik süreler daha yüksek şebeke tarifesi varsayar. Ayrıca CAPEX'i 150.000 m³/yıl referansa göre 2,87× ölçekliyoruz. Bu yüzden tabloda **model** ve **katalog** sütunlarını yan yana gösteriyoruz; farkı saklamıyoruz.”*

9. **[Genel Jüri] “Petkim neden Turkuaz değil?”**
   - **Cevap:** *“Petkim'de finansal optimizasyon `M01, M05, M10` seçti; bu **%48,0** tasarruf ve **Yeşil** belge demek. Turkuaz gönüllü üst kademe; risk-dahil eski portföy `M01, M04, M05, M10` ile Turkuaz'a ulaşıyordu ama finansal NPV'si daha düşüktü. 2029'da zorunlu olan Yeşil hedefini rahatça karşılıyoruz; Turkuaz'ı isterseniz sertifika kısıtı ekleyip ~10M TL NPV'den feragat edebiliriz.”*

10. **[Genel Jüri] “Vestel 3,9 ay çok iyi değil mi? Bu kadar hızlı geri döner mi?”**
    - **Cevap:** *“Vestel'de tarife 91,70 TL/m³ ve su hacmi 1,51 milyon m³; bu, tasarrufun TL değerini yükseltiyor. Yine de tek sayıya güvenmeyin: tarife ±%40 oynarsa 2,8–6,4 ay bandına kayıyor. CAPEX ölçeklemesi doğrusal; izleme/kaçak önlemleri için iyimser olabilir. Bu yüzden headline'ı bantla okuyoruz.”*

11. **[Veri Jürisi] “Manisa ve Kemalpaşa neden aynı 82,8 skoru veriyor? Kopyala-yapıştır mı?”**
    - **Cevap:** *“Hayır; iki OSB de aynı Aqueduct alt-havza değerlerini (`pfaf_id=211056`) paylaşıyor. Aqueduct'in bu poligonunda `bws`, `gtd`, `drr`, `sev`, `iav` değerleri aynı; bu yüzden skorlar eşit. Bu bir hata değil, **Aqueduct çözünürlük sınırı**. Yerel OSB/kuyu verisi geldiğinde ayrışacak; nitekim Tab 2'de tesisin %100 kuyu bağımlılığı ve 1,38× kırılganlık çarpanı devreye giriyor.”*

12. **[Genel Jüri] “Grafikte 5 yıllık çizgi neden düz görünüyor?”**
    - **Cevap:** *“Artık grafik çift eksenli: yeşil finansal çizgi sol eksende, kil duruş riski sağ eksende. Böylece risk çizgisi finansal çizgiyi ezmiyor; tooltip'te her yılın TL değeri var. Bu bir hesap hatası değil, iki farklı büyüklüğün ayrı eksenlerde gösterimidir.”*

---

## 4. Sunum Öncesi 60 Saniyelik Kontrol Listesi

- [ ] `uv run pytest -q` → **23 passed**.
- [ ] `bash scripts/run.sh` veya `uv run uvicorn ekozeka26.app:app --host 127.0.0.1 --port 8000`.
- [ ] `curl -s http://127.0.0.1:8000/api/izsu-live` → `source_mode` = `live_cache` veya `verified_snapshot`; `snapshot_date` = `2026-11-06`.
- [ ] Sekme 1 varsayılan: **Kemalpaşa 2050 BAU tekstil** → **82,8**; P10/P50/P90 = **17,4 / 33,5 / 60,7**.
- [ ] Sekme 2 varsayılan: **Tofaş 2030 BAU** → risk **31,1M TL/yıl**, NPV **+6,6M TL**, geri ödeme **17,3 ay**, **Yeşil**.
- [ ] Sağ üst **Rehber** açılıyor; 16 adım; `←`/`→`/`Esc`; adım 10'da Tab 2'ye geçiyor ve Tofaş yükleniyor.
- [ ] Tarayıcı zoom **%100**; 1366×768 ve 1920×1080'de yatay taşma yok; konsol hatası yok.
- [ ] Yedek: internet yoksa `verified_snapshot` ile aynı demo; `--refresh` başarısız olsa bile API çökmez.

---

## 5. Söylenmemesi Gerekenler (Jüri Tuzağı)

| Yanlış cümle | Doğru cümle |
|---|---|
| “639 bağımsız havza” | “639 poligon / 116 tekil hidrolojik havza; ulusal ön tarama” |
| “Tüm Türkiye'de canlı veri var” | “İzmir/Gediz canlı İZSU; diğer iller Aqueduct tarama katmanı” |
| “Kesin geri ödeme 17,3 ay” | “Finansal headline 17,3 ay; tarife ±%40 → 12,4–28,9 ay bandı” |
| “Petkim Turkuaz” | “Petkim Yeşil; Turkuaz gönüllü üst kademe” |
| “Duruş zararı garanti” | “Beklenen risk; tarihsel kesinti verisi yok, garanti değil” |
| “Tahtalı %76,5 düştü” | “Tahtalı **aylık üretimi** %76,5 düştü; baraj doluluğu değil” |
| “Katalog 3,5 ay diyor, siz 17,3 ay” | “Katalog tipik; model tesisin tarifesi/CAPEX ölçeğiyle hesaplıyor; ikisini yan yana gösteriyoruz” |
| “Manisa ve Kemalpaşa aynı; kopya” | “Aynı Aqueduct alt-havza değerleri (`pfaf_id=211056`); Aqueduct çözünürlük sınırı” |

---

## 6. Üç Cümlelik Kapanış (Ezber)

1. *“Su krizi gelecek tahmini değil; İzmir'de bugün barajlar ağırlıklı %34 dolu.”*
2. *“Biz fabrikaya ‘su kesilir mi, kaç TL kaybedersin, 2029 belgesini en düşük CAPEX ile nasıl alırsın?’ sorusunu tek ekranda yanıtlıyoruz.”*
3. *“Ve bunu yaparken finansal getiriyi riskten ayırıyor, hangi sayının doğrulanmış hangisinin kalibre olduğunu açıkça söylüyoruz.”*
