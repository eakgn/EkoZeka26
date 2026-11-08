# Konuşmacı Notları — Herhangi Bir Proje · 5:00

> PDF: `Herhangi-Bir-Proje-Sunum.pdf` (9 sayfa) · Kaynak: `docs/sunum/sunum.html`
> Yedek sunum: HTML'i tarayıcıda aç, `←` / `→` ile slayt geç. `#3` gibi hash tek slayt açar.

---

## 1. Zaman çizelgesi (sert limit 5:00)

| Saat | Ne | Slayt |
|---|---|---|
| 0:00–0:30 | Kriz | 2 |
| 0:30–0:52 | Kullanıcı + kim öder | 3 |
| 0:52–1:37 | Model + 4 AI rolü + mayın 1 | 4 |
| 1:37–2:10 | Kanıt tablosu | 5 |
| 2:10–2:28 | Etki + sınırlar + etik | 6 |
| 2:28–4:42 | Canlı demo (13 adım) | uygulama |
| 4:42–5:00 | Kapanış | 7 |

> 4:42'de bitmezsen **etik sütununu atla**, doğrudan kapanışa geç. Kapanış asla kesilmesin.

---

## 2. Slayt metinleri (birebir okunacak)

### Slayt 2 — Kriz (30 sn)
> "Haberlerde İzmir barajları %44 dolu deniyor; bu beş barajın basit ortalaması. Kapasitenin %58'ini tutan Gördes %28'de olduğu için gerçek ağırlıklı doluluk **%34**. Bu krizin hacim faturası tarımda, ama **m³ başına en pahalı sanayide**: Gediz'de sanayi suyunun tamamı kuyudan geliyor, kurak yılda tahsis %37'ye düşüyor — **%63 kesinti**. Suyun metre küpü 404 lira ve 27 Aralık 2029'a kadar belge almak zorunlu."

### Slayt 3 — Kullanıcı (22 sn)
> "İki kullanıcı, iki soru. Yeni yatırımcı 'nereye' diye soruyor; mevcut tesis 'ne yapayım, kaça mal olur, belgeyi alır mıyım' diye soruyor. Ödeyen taraf net: OSB yönetimi, tesisin kendisi veya yeşil kredi veren banka. Türkiye'de 416 OSB ve 68 bin fabrika var; Yeşil OSB sayısı 27. Pazarın %93'ü henüz dönüşmedi."

### Slayt 4 — Model (30 sn + 15 sn mayın)
> "Mimari tek cümle: iklimi fizikle kuruyoruz, ML'i yalnızca etiketin gerçekten olduğu yere koyuyoruz. Yedi CMIP6 modelini ayrı ayrı QDM ile ERA5'e kalibre ediyoruz; ET₀'yü FAO-56 ile hesaplıyoruz. Risk skoru beş bileşenin şeffaf toplamı — kara kutu değil. XGBoost'a gelince: ona '2050'yi tahmin et' demedik."

**Mayın 1 — kendin sor:**
> "Şimdi haklı olarak şunu soracaksınız: madem Aqueduct 2050'yi zaten veriyor, neden XGBoost'la 2050 tahmin etmediniz? Çünkü o **döngüsel hedef** olurdu: modele Aqueduct'in sayısını tahmin ettirmek yeni bilgi üretmez. Üstelik elimizde 639 satır var. XGBoost'u gerçekten etiketli olan işe koyduk: kaba **yıllık** projeksiyonu **yaz pik aylarına** indirmek. Çünkü fabrikanın suyu temmuzda kesilir, ocakta değil."

### Slayt 5 — Kanıt (33 sn)
> "Doğrulama iddiası şu: aynı havza hem eğitimde hem testte yok — `GroupKFold`, grup `pfaf_id`. Kaba yıllık baseline hatası 0,479; doğrusal model 0,294; XGBoost **0,153**, R² **0,796** — hatada %68 düşüş. En kötü fold R² 0,593, en iyi 0,919; bunu da söylüyorum çünkü ortalamayı saklamak istemiyorum. Ayrıca 1984–2025 Gediz debi backtest'i R² 0,673. Repoda 23 test var, hepsi geçiyor. Etiketler yerinde ölçüm değil, Aqueduct'in yayımlanmış aylık model çıktısı — bunu da açıkça yazıyoruz."

### Slayt 6 — Etki / Sınır / Etik (18 sn)
> "Etki: üç tesiste yılda 7,35 milyon metreküp su, bunun 258 bini akifer. 193,8 milyon lira yatırımla 242,9 milyon lira net NPV. Sınırlarım üç tane ve saklamıyorum: tek iklim noktası, 639 poligon 116 havza, kesinti günü sezgisel. Etik taraf: kişisel veri işlemiyoruz, her sayının güven seviyesi ekranda, ve yanlış alarmın bedeli gereksiz yatırım olduğu için tek sayı değil bant veriyoruz."

### Slayt 7 — Kapanış (18 sn)
> "Su krizini durdurmanın en hızlı yolu, su tasarrufunu fabrika için en kârlı yatırım haline getirmek. Biz bunu üç gerçek tesiste sayıyla gösterdik: yılda 7,35 milyon metreküp su, 242,9 milyon lira net NPV ve 2029 belgesi. **Hangi sayıyı isterseniz açayım** — model metrikleri, tarife duyarlılığı veya veri soyu; hepsi ekranda."

---

## 3. Canlı demo — 13 adım (toplam ~2:27)

Rehber sağ üstte. Sunumdan önce aç, **1. adımda beklet**. Adım 10'da otomatik 2. sekmeye geçer ve Tofaş yüklenir.

| # | Adım | Sn | Söylenecek cümle |
|---|---|---:|---|
| 3 | Canlı veri şeridi | 10 | "Resmî İZSU: ağırlıklı doluluk %34; kil metin modelin yakaladığı Kasım 2025 Tahtalı çöküşü — aylık üretim %76,5 düştü." |
| 4 | Senaryo | 8 | "2050, normal, tekstil; iyimser/olası/kötümser SSP1-2.6 / SSP2-4.5 / SSP3-7.0 eşlemesi." |
| 5 | Risk skoru | 12 | "Kemalpaşa 82,8 — kritik. Kesinti günü iyi yıl 17,4, beklenen 33,5, kurak yıl 60,7: tek sayı değil bant." |
| 6 | Harita | 10 | "639 poligon, 116 tekil havza; renk çekilen su bölü yenilenebilir su. Bu ulusal katman ön tarama." |
| 7 | Bileşenler | 15 | "82,8'in kırılımı ekranda: yaz pik stresi +25,0, yeraltı +22,4, SPEI-12 +18,0, sektörel tahsis +13,4. Kara kutu yok." |
| 8 | SHAP + iklim | 18 | "Solda SHAP: en güçlü sürücü yaz pik çarpı yıllık stres; ortada yedi CMIP6 modelinin P10–P90 su dengesi; sağda barajlar." |
| 9 | 7 OSB karşılaştırma | 10 | "Bursa 57,8, Gebze 55,0. Kemalpaşa ile Manisa aynı Aqueduct alt-havzasında olduğu için eşit — çözünürlük sınırı, hata değil." |
| 10 | Gerçek fabrikalar | 10 | "Tofaş: 2024 raporundan 430.782 m³, tamamı yeraltı kuyusu, 4.409 çalışan. Kurgu senaryo değil." |
| 12 | Dört KPI | 14 | "Yılda 31,1 milyon lira beklenen duruş riski, 154 bin m³ tasarruf, 5 yıllık finansal NPV +6,64 milyon, 2029 Yeşil." |
| 13 | Önlem portföyü | 14 | "6 milyon bütçeyle Knapsack dört önlem seçti — nozullar, kaskad durulama, buhar kondensi, RO konsantresi; CAPEX 5,71 milyon, bütçenin %95'i." |
| 14 | Nakit akışı | 12 | "Yeşil finansal birikim, kil duruş riski — ayrı eksende. Risk NPV'ye dahil değil çünkü tarihsel kesinti verisi yok; katınca geri ödeme 2–8 aya düşüyor ve EPA/PNNL benchmark'ıyla çelişiyor. Finansal geri dönüş 17,3 ay." |
| 15 | 2029 belgesi | 8 | "Kriterler tek tek: hangisi sağlandı, hangisi eksik. Bu bir ön değerlendirme, resmî denetim değil." |
| 16 | Yönetici özeti | 6 | "Ve tüm bunlar yönetim kuruluna gidecek metne dönüşüyor — yalnızca doğrulanmış sayılardan." |

**Atlanan adımlar:** 1 (Giriş), 2 (Gezinme), 11 (Form). Jüri isterse adım 11'e tek tuşla dönülür.

---

## 4. Mayın temizleme — sunum içinde cevaplanan 2 soru

1. **"Neden XGBoost ile 2050 tahmin etmediniz?"** → Slayt 4 sonunda (yukarıda).
2. **"Duruş zararını neden NPV'ye katmıyorsunuz?"** → Demo adım 14'te: tarihsel veri yok + 2–8 aya düşüyor + EPA ~5 yıl / PNNL ~6 yıl benchmark çelişkisi.

Bunlar en yüksek olasılıklı iki itiraz. Sunum içinde cevaplanınca Q&A'de tekrar gelme olasılığı düşer.

---

## 5. Söylenmemesi gerekenler

| Yanlış | Doğru |
|---|---|
| "639 bağımsız havza" | "639 poligon / 116 tekil havza; ulusal ön tarama" |
| "Kesin geri ödeme 17,3 ay" | "Finansal headline 17,3 ay; tarife ±%40 → 12,4–28,9 ay bandı" |
| "Duruş zararı garanti" | "Beklenen risk; tarihsel kesinti verisi yok, garanti değil" |
| "Tahtalı %76,5 düştü" | "Tahtalı **aylık üretimi** %76,5 düştü; baraj doluluğu değil" |
| "Petkim Turkuaz" | "Petkim Yeşil; Turkuaz gönüllü üst kademe" |
| "ISO 14046 / resmî belge denetimi yapıyoruz" | "Ön değerlendirme; denetim ürünü değil" |

---

## 6. Sunum öncesi 60 saniyelik kontrol

- [ ] `bash scripts/run.sh` → `127.0.0.1:8000`
- [ ] `curl -s http://127.0.0.1:8000/api/izsu-live` → `live_cache` veya `verified_snapshot`
- [ ] Sekme 1: Kemalpaşa 2050 BAU tekstil → **82,8**; **17,4 / 33,5 / 60,7**
- [ ] Sekme 2: Tofaş → **31,1M TL**, **+6,64M TL**, **17,3 ay**, **Yeşil**
- [ ] Rehber açık, 1. adımda; tarayıcı zoom %100
- [ ] PDF açık, 2. sayfada bekliyor (demo dönüşü için)
- [ ] Yedek: `docs/demo/tab1_location_risk.png` + `tab2_roi_simulator.png`

---

## 7. Yedek plan

| Sorun | Yapılacak |
|---|---|
| İnternet yok | Aynı demo `verified_snapshot` ile çalışır; **söyle, özür dileme**. |
| Rehber overlay'i bozuldu | `Esc`, elle tıkla; 3 saniyeden fazla uğraşma. |
| Uygulama çöktü | PDF slayt 8'deki üç vaka tablosunu göster, anlatmaya devam et. |
| Süre 4:42'yi geçti | Slayt 6'nın etik sütununu atla, kapanışa geç. |
