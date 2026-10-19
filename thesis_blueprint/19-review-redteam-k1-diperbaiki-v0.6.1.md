# Tinjauan red team independen: desain eksperimen "K1 diperbaiki" (Part 19 v0.6.1)

> Ditulis 2026-10-19 oleh sesi peninjau independen, satu fase (tanpa cek silang), atas brief `tools/redteam-k1-v061/brief.md`.
> Objek: `tools/redteam-k1-v061/bahan/19-k1-diperbaiki-v0.6.1-salinan.md` (rujukan baris ditulis `salinan:baris`).
> Ini bukan gerbang 6 protokol. Tidak ada berkas blueprint yang diubah, tidak ada perintah *cloud*, tidak ada *commit*.
>
> **Label bukti.** [F] fakta dari berkas repo, data, kode atau dokumentasi resmi (sumber disebut). [H] hitungan atau
> simulasi yang langkahnya ditunjukkan (Lampiran). [P] pendapat (tidak menentukan skor). [BD] belum dapat diverifikasi.
> Kekhawatiran yang bergantung pada hasil yang belum ada ditulis "belum dapat dinilai; bukti yang dibutuhkan: …" dan
> tidak dimasukkan ke skor.

---

## 1. Ringkasan

**Skor akhir: 6 / 10** ("perlu perbaikan berarti sebelum pilot"; tidak ada cacat mendasar yang membuat desain tak
dapat diselamatkan).

| Dimensi | Skor | Alasan singkat |
|---|---|---|
| 1. Validitas konstruk | 6 | Rantai kontras dan H2p adalah kemajuan nyata atas K1. Tetapi: kontras "mesin" (H3 → K1) memakai fungsi HPA yang berbeda (kode resmi), bentuk deret H2p vs H3 belum disamakan, ambang kesetaraan pemicu sama besar dengan cadangan yang disebut sensitif, penghitung laju memuat permintaan non-beban, dan tidak ada batas bawah r agar kontras sinyal bisa berbeda (M-1 … M-3). |
| 2. Validitas internal | 7 | Blok per layanan × pola, urutan acak, penundaan acak (bukti K1: 91%), isolasi *pool*, DQ biner, laporan *run* ulang: baik. Sisa: semua replika berbagi satu *node* (jumlah replika berbeda antar-konfigurasi), DQ *steal* dari Part 17 hilang, kebergantungan *kube-state-metrics* tidak tercatat (m-3, M-2). |
| 3. Validitas kesimpulan statistik | 5 | Struktur *intersection-union* dan dekomposisi S > \|E\| benar secara logika. Tetapi uji D2 tidak sah seperti ditulis (ukuran uji nyata 0,033–0,042 vs nominal 0,025 pada keluaran miring [H]); dasar b tertulis tidak berlaku; daya komponen non-inferioritas 0,15–0,29 pada σ ≥ 0,02; margin gradual bergantung pada model yang belum ada (C-1, C-2, M-5). |
| 4. Dasar parameter | 5 | Banyak nilai diberi dasar nyata dan ditulis jujur, tetapi sejumlah label B-konv atau B-rumus lebih kuat daripada dasarnya (kontinuitas K1 sebagai dasar, "separuh SLO", faktor 0,8 pada r dari satu pengamatan yang terkonfound, toleransi HPA sebagai toleransi kesetaraan, batas "≈ 0"/"jelas" tanpa angka). Lihat §3. |
| 5. Pengukuran dan keterulangan | 7 | Data mentah k6 per permintaan, *digest*, `lscpu` per *run*, versi otomatis, DQ yang jelas. Semua angka K1 yang saya hitung ulang cocok dengan desain (Lampiran A). Sisa: definisi penghitung laju, inventaris komponen, ambang vague. |
| 6. Pelajaran K1 | 6 | Pemicu setara, laju-dilayani, SLO pasca-data, uji pasca-data, fase HPA deterministik, isolasi: tertutup atau jauh membaik. Terulang dalam bentuk baru: faktor yang masih berupa paket (mesin), nilai yang diwariskan (bentuk *run*), kesetaraan pemicu yang longgar, statistik yang diputuskan tanpa daya pada ukuran efek yang dituju, dan klaim yang bersandar pada "tinjauan terdahulu" (§4). |

**Alasan skor akhir (bukan rata-rata).** Rata-rata mekanis 6,0, dan saya mempertahankan 6 karena dua alasan yang
berlawanan arah. (a) Naik dari 5: tidak ada temuan yang membatalkan desain; semua temuan Kritis dan Mayor dapat
diperbaiki di tingkat aturan sebelum pembekuan, dan lebih dari tiga puluh angka K1 yang saya hitung ulang dari data
mentah semuanya cocok (Lampiran A), sehingga fondasi empirisnya bersih. (b) Turun dari 7: dua cacat berada pada
inferensi inti, bukan pada detail: uji D2 yang menentukan putusan Hipotesis 2, dan b = 10 yang dasarnya tidak
sesuai protokol dan yang, menurut hitungan desain sendiri, membuat komponen *auth* Hipotesis 1 hampir tak mungkin
disimpulkan.

### Tiga temuan terpenting

1. **C-1.** Uji Wilcoxon *signed-rank* pada D2 = H2p + K1 − 2·H3 tidak sah sebagaimana ditulis. Klaim "sah sebagai uji
   randomisasi" (salinan:975) berlaku untuk selisih dua konfigurasi (D1), bukan untuk kombinasi berbobot tiga
   konfigurasi. Simulasi: ukuran uji satu sisi 0,025 menjadi 0,033 / 0,037 / 0,042 pada tiga bentuk sebaran miring,
   dan putusan Hipotesis 2 mensyaratkan D2 lolos.
2. **C-2.** b = 10 ditetapkan sebelum pilot dengan dasar "keterbatasan sumber daya" (salinan:529), sedangkan premis
   desain menyatakan sumber daya bukan batasan (salinan:7); protokol gerbang 4 meminta b dipilih lewat simulasi daya
   dengan varians pilot. Akibatnya: daya non-inferioritas *auth* (margin δ_min) hanya 0,15–0,29 pada σ 0,02–0,03,
   efek sebesar δ_min tidak terdeteksi oleh b ≤ 20 (desain sendiri, salinan:552), dan D2 butuh S + E ≥ 0,054–0,077.
3. **M-1.** "Pemicu setara" (pelajaran K1 yang utama) ditutup dengan pita rasio metrik/target 1,0 ± 0,1
   (salinan:122-124). Untuk metrik yang proporsional dengan beban, pita itu setara dengan titik pemicu antara 0,80 C
   dan 0,98 C [H], padahal cadangan 12% vs 23% disebut berpengaruh tinggi (salinan:155-158). Ditambah: penghitung laju
   K1 memuat `/metrics` dan *probe* (≈ 0,13 req/s per *pod auth* [F]), dan CPU berbasis offset *idle* menggeser titik
   pemicu CPU searah lebih lambat.

---

## 2. Temuan

Definisi tingkat: **Kritis** = bila tidak diperbaiki sebelum pembekuan, satu klaim konfirmatori inti tidak sah atau
tidak dapat disimpulkan oleh desain sendiri. **Mayor** = merusak satu kontras atau satu parameter inti, atau membuat
aturan tak dapat dijalankan. **Minor** = kontradiksi, ambang tak berangka, atau label.

### Kritis

#### C-1. Uji D2 (Hipotesis 2) tidak sah; keabsahan randomisasi hanya berlaku untuk D1

- **Lokasi.** salinan:862-872 (aturan keputusan: D1 = H2p − K1, D2 = H2p + K1 − 2 × H3, masing-masing signed-rank satu
  sisi 0,025), salinan:973-982 (uji P8, "Sah sebagai uji randomisasi karena urutan *run* diacak di dalam blok"),
  salinan:546-550 (daya D1/D2), salinan:842 (non-inferioritas *auth*).
- **Masalah.**
  1. Acak urutan *run* di dalam blok adalah permutasi 7 konfigurasi ke 7 posisi. Di bawah hipotesis nol tajam "H2p ≡ K1",
     pertukaran peran dua konfigurasi memberi pembalikan tanda D1 yang simetris, jadi sign-flip sah untuk D1.
     D2 melibatkan tiga konfigurasi berbobot (1, 1, −2); pertukaran peran tidak membalik tanda D2, dan D2 tidak simetris
     bila sebaran keluaran per konfigurasi miring: kumulan ke-3 D2 = (1 + 1 − 8) κ₃ = −6 κ₃ ≠ 0 [H]. *Signed-rank*
     eksak mensyaratkan simetri sekitar nol.
  2. Desain sendiri mengakui keluaran punya pencilan/keruntuhan metastabil (salinan:981-982), jadi kemiringan bukan
     skenario khayalan. Simulasi (Lampiran C; b = 10, 20.000 ulangan, semua tiga konfigurasi berdistribusi sama):
     ukuran uji sisi-atas nominal 0,025 → D1 0,024 pada semua bentuk, **D2 0,024 (normal), 0,033 (gamma, kemiringan 1,0),
     0,037 (lognormal, 1,73), 0,042 (campuran 10% pencilan, 2,04)**; pada batas komposit S = −E (D2 = 0 rata-rata, D1 > 0):
     0,025 / 0,031 / 0,042 / 0,043 [H]. Bentuk sebaran desain baru belum diketahui [BD]; yang terbukti adalah
     bahwa jaminan ukuran uji tidak ada tanpa asumsi simetri.
  3. Non-inferioritas *auth* (salinan:842) menguji d − δ_min dengan *signed-rank* dan interval Hodges–Lehmann eksak:
     H0 tidak tajam, jadi argumen randomisasi tidak berlaku sama sekali dan keabsahan bersandar pada simetri d = H1 − H3.
     Di K1, sebaran H1 dan H3 sangat berbeda (SD fraksi buruk *auth gradual*: H1 0,0151 vs H3 0,0046; *shipping gradual*:
     0,0279 vs 0,0017 [H, dihitung dari `analysis/cache`]), sehingga selisihnya tak simetris.
- **Perbaikan (pilih satu dan bekukan).** (a) Untuk D2: uji permutasi dengan permutasi peran tiga konfigurasi di dalam
  blok (valid terhadap H0 tajam S = E = 0, bukan terhadap seluruh H0 komposit S ≤ |E|, jadi ukuran uji di batas komposit
  tetap diperiksa lewat simulasi) atau *bootstrap* blok studentized, dengan bentuk residu pilot; (b) atau ganti syarat
  S > |E| menjadi dua selisih berpasangan (S − E dan S + E) yang diuji dengan prosedur yang tidak mensyaratkan simetri;
  (c) dalam semua kasus, wajibkan dry run gerbang 4 melaporkan ukuran uji simulasi pada bentuk sebaran pilot dan
  tetapkan kriteria terima (mis. ukuran ≤ 0,03). Hapus kalimat "Sah sebagai uji randomisasi" atau batasi pada D1.
- **Gerbang terblokir.** 5 (hipotesis dengan aturan keputusan dan uji); 4 (dry run analisis).

#### C-2. b = 10 tidak punya dasar yang sesuai protokol; daya komponen konfirmatori kunci tidak memadai menurut hitungan desain sendiri

- **Lokasi.** salinan:7 (anggaran bukan batasan), salinan:495-506 (pilot 2 blok per strata; "b = 10 … ditetapkan sebelum
  pilot"), salinan:500-505 (pilot tidak dipakai menetapkan b), salinan:528-553 (b dan tabel daya), salinan:554-560 (daya
  non-inferioritas), salinan:842 (komponen *auth*), salinan:1028 (pilot "tanpa mengubah b"); protokol gerbang 4.
- **Masalah.**
  1. *Dasar tertulis tidak berlaku.* b dibenarkan dengan "pembenaran sumber daya" (Lakens, 2022: keterbatasan sumber daya
     sebagai pembenaran sah, salinan:529-531). Premis salinan:7 menyatakan sumber daya bukan batasan desain. Ini
     temuan konsistensi dasar, bukan komentar tentang biaya: label dasar b tidak sejalan dengan premis, jadi b secara
     protokol berstatus **BELUM BERBASIS**.
  2. *Protokol gerbang 4* meminta jumlah repetisi dipilih lewat simulasi daya atau ukuran sampel dengan varians yang
     diestimasi dari pilot. Desain menetapkan b sebelum pilot dan melarang pilot mengubahnya (salinan:506, 1028). Alasan
     "1 derajat bebas per sel" (salinan:502-503) adalah akibat pilihan pilot 2 blok per strata (salinan:495-497),
     bukan keharusan.
  3. *Daya.* Saya mereproduksi tabel desain: efek terkecil terdeteksi b = 10 (signed-rank dua sisi 0,05, ρ = 0)
     0,014 / 0,029 / 0,043 untuk σ 0,01 / 0,02 / 0,03 (desain: 0,014 / 0,029 / 0,044) dan MDE D1/D2 0,032 / 0,036 / 0,043
     dan 0,054 / 0,062 / 0,077 untuk σ 0,022 / 0,025 / 0,030 (desain: 0,031–0,043 dan 0,054–0,074) [H, Lampiran C].
     Daya non-inferioritas (selisih sebenarnya 0, satu sisi 0,025, b = 10): margin 0,014 → **0,78 / 0,29 / 0,15**;
     margin 0,027 → 1,00 / 0,75 / 0,43 (σ 0,01 / 0,02 / 0,03). Jadi komponen *auth* Hipotesis 1, yang mensyaratkan lolos
     agar "didukung" (salinan:845), hampir pasti "tidak dapat disimpulkan" pada σ ≥ 0,02 *bahkan bila CPU memang kompetitif*.
     Desain mengakui bahwa tidak ada b ≤ 20 yang mendeteksi efek sebesar δ_min pada σ 0,03 (salinan:552), yaitu efek
     terkecil yang dianggap penting tidak dapat dibedakan dari nol.
  4. *Ekuivalen waktu* (aritmetika dari rumus desain sendiri, salinan:564-566, bukan prediksi efek): efek = Δt ×
     (1 − 1/r) / 420. MDE b = 10 setara pergeseran waktu Δt (detik) pada r = 1,5 / 1,65 / 3 / 4,5: untuk MDE 0,032:
     40 / 34 / 20 / 17; 0,044: 55 / 47 / 28 / 24; D2 0,054: 68 / 58 / 34 / 29; D2 0,077: 97 / 82 / 48 / 42 [H]. Pada r ≈ 1,5–1,65
     (hasil aturan P5 bila *shipping* K1 tetap, salinan:236-238) hanya pergeseran ≥ 34–97 detik yang terdeteksi.
     Besar efek H2p vs H3 sebenarnya: belum dapat dinilai; bukti yang dibutuhkan: model fluida tervalidasi atau pilot
     dengan σ terestimasi.
  5. σ yang dipakai (0,031 K1 *shipping spike*, salinan:451-453) berasal dari r 2,1–3,75, sedangkan desain baru memakai r
     yang mungkin ≈ 1,5; σ tidak otomatis berlaku pada skala fraksi buruk yang berbeda (σ lantai dan σ proporsional
     (1 − 1/r) bercampur). [BD]
  6. Peta putusan: salinan:845-846 memetakan hasil lain ke "tidak terbukti", sedangkan salinan:842-843 menyatakan
     non-inferioritas yang gagal harus "tidak dapat disimpulkan" (bukan "tidak kompetitif"). Dua kategori ini perlu
     dipisah di putusan Hipotesis 1, supaya daya rendah tidak terbaca sebagai bukti negatif.
- **Perbaikan.** (a) Pilih b lewat simulasi daya pada ukuran efek yang dituju (SESOI dengan argumen kepentingan praktis,
  bukan hanya satu siklus HPA) dengan σ berbatas atas dari pilot yang diperbesar sampai derajat bebas memadai (mis. ≥ 5
  per kontras; protokol gerbang 4); atau (b) tetapkan margin non-inferioritas pada nilai yang b-nya dapat dicapai dan
  beri dasar bagi margin itu (bukan δ_min otomatis); atau (c) turunkan komponen *auth* menjadi estimasi pra-terdaftar
  non-konfirmatori. Pisahkan "tidak terbukti" dari "tidak dapat disimpulkan" di peta putusan.
- **Gerbang terblokir.** 2 (b, δ_min, margin masih BB), 4, 5.

### Mayor

#### M-1. "Pemicu setara" belum benar-benar setara: pita 1,0 ± 0,1 sama besar dengan cadangan, penghitung laju memuat permintaan non-beban, dan offset CPU searah

- **Lokasi.** salinan:116-129 (pemeriksaan kesetaraan pada N pod), salinan:140-147 dan 155-158 (cadangan, sensitivitas),
  salinan:331-357 (penghitung laju), salinan:1045-1046 (PM3/PM4).
- **Masalah.**
  1. *Pita terlalu lebar.* Aturan terima: rasio metrik/target pada L\* ∈ [0,9; 1,1] "pita = toleransi HPA 10%"
     (salinan:122-124). Untuk metrik proporsional dengan beban, HPA bertindak saat rasio > 1,1, jadi titik pemicu =
     1,1 L\*/ρ = 0,88 C/ρ. ρ = 0,90 → 0,98 C (cadangan 2%); ρ = 0,95 → 0,93 C (7%); ρ = 1,00 → 0,88 C (12%);
     ρ = 1,05 → 0,84 C (16%); ρ = 1,10 → 0,80 C (20%) [H, Lampiran B1]. Desain menyatakan cadangan 12% vs 23% (f 0,8 vs 0,7)
     "tinggi" sensitivitasnya (salinan:155-158) dan seluruh logika *gradual* bertumpu pada cadangan 12%
     (salinan:140-147). Pita yang diterima mencakup rentang 2%–20%. Toleransi HPA adalah kriteria untuk HPA tidak
     bereaksi terhadap derau, bukan kriteria kesetaraan titik pemicu; label B-rumus-nya tidak menurunkan angka ini dari
     sensitivitas hasil.
  2. *Penghitung laju memuat permintaan non-beban.* Penghitung K1 `http_requests_total` tidak menyaring *handler*
     (`prometheus-adapter-values.yaml:58-68`; kueri KEDA `infrastructure/kubernetes/experiments/shipping-rate-service/k1-keda.yaml`). Data K1: pada fase dasar *auth* B1 *gradual*
     rep1 laju per *pod* 2,12 req/s untuk beban 2,00 req/s; dua deret non-beban masing-masing 0,067 req/s
     (`prom_http_requests_rate.json`; `/metrics` terhitung) → ≈ 0,13 req/s per *pod* = 2,8% dari L\* *auth* 4,8
     req/s dan ≈ 11% dari λ0 = 1,2 req/s [F/H]; *shipping* ≈ 0,16 req/s (0,018 + 0,067 + 0,071). Desain mengusulkan kedatangan = dilayani +
     ditolak (salinan:339-357) tanpa menyatakan penyaringan *handler*. Offset konstan per *pod* ini tidak ada pada
     sinyal CPU kecuali lewat CPU dasar, dan pita ± 0,1 menyembunyikannya.
  3. *Offset CPU searah.* Bila CPU(λ) = b + cλ dengan b > 0, target u\* = CPU(L\*) membuat pemicu CPU pada
     L_t = 1,1 L\* + 0,1 b/c > 1,1 L\* (lebih lambat daripada pemicu laju). Arah pasti (b > 0); besarnya diukur di
     *ladder*; di K1, CPU dasar 52–64 m pada beban dasar [F, `runs.csv`, `base_cpu_m_per_pod`].
  4. Kalibrasi pada 1 pod, N pod hanya dicek lewat pita yang sama (salinan:116-129), dengan data K1 yang menunjukkan
     CPU per pod meningkat 27% pada beban per pod sama (266 m pada 1 pod vs 337 m rata-rata 5 pod, 40 req/s per pod,
     *ladder* *shipping*) [F, `ladder.json`].
- **Perbaikan.** Definisikan kesetaraan pada **beban pemicu terukur** (laju per pod saat HPA pertama menaikkan replika,
  dari langkah beban kecil berulang pada N pod) bukan pada rasio dengan toleransi HPA, dan turunkan batas selisih
  dari sensitivitas hasil terhadap cadangan (model yang tervalidasi, lihat M-5). Saring penghitung laju ke *handler*
  beban (mis. `handler!~"/metrics|/health|/ready"`) dan laporkan penghitung per *pod* pada fase dasar. Atur ulang
  target CPU secara iteratif sampai selisih beban pemicu ≤ satu langkah *ladder*.
- **Gerbang terblokir.** 1 (lembar konstruk), 2 (aturan terima), 3 (kind: kueri gabungan).

#### M-2. Dua kontras lain belum "satu variabel": H3 → K1 (fungsi HPA berbeda) dan H2/H2p/H3 (bentuk deret, *kube-state-metrics*, toleransi tak bermakna)

- **Lokasi.** salinan:49 (rantai), salinan:96-114 (H2p), salinan:398-407 (cek (e)), salinan:414-421 (cek (g)),
  salinan:606 dan 784 (inventaris `infra`, DQ5), salinan:920-936 (tabel 19.4.6).
- **Masalah.**
  1. *H3 → K1 bukan hanya jalur API.* Tabel salinan:49 menyatakan yang berbeda hanya "jalur API"; "Yang sama … controller
     HPA". Kode resmi HPA memakai fungsi berbeda: Pods → `GetMetricReplicas` → `calcPlainMetricReplicas` (pod hilang/belum
     siap diisi nol saat *scale-up*, target saat *scale-down*, lalu rasio, toleransi, dan arah dievaluasi ulang);
     External AverageValue →
     `GetExternalPerPodMetricReplicas` (`replicaCount = ceil(usage / targetPerPod)` dengan `usageRatio = usage /
     (target × statusReplicas)`, tanpa perlakuan per pod) [F, kode `replica_calculator.go`, dicek 2026-10-19].
     Kesetaraan "ceil(N × avg/T) = ceil(total/T)" yang diklaim komentar `prometheus-adapter-values.yaml:45-57` berlaku
     hanya pada keadaan tunak tanpa pod hilang/belum siap/terminating dan di luar toleransi. Cek (e) hanya mengukur
     jeda nilai pada **satu pod** (salinan:399-401), jadi dinamika *pod* baru belum siap (justru situasi *spike*)
     tidak diperiksa, padahal untuk H2 vs H2p desain melakukan uji *scale-up* nyata (cek (g), salinan:419-421).
     Akibatnya "efek mesin" E dalam D1/D2 adalah paket (jalur + fungsi + perlakuan pod baru + bentuk kueri KEDA).
     Besarnya: belum dapat dinilai; bukti yang dibutuhkan: uji kind *scale-up* nyata yang membandingkan replika
     yang diminta H3 vs K1 per ronde.
  2. *Bentuk deret belum disamakan.* H2p dibuat dengan *recording rule* (salinan:112-114); `evaluation_interval` Prometheus
     K1 15 s (`infrastructure/kubernetes/monitoring/prometheus.yaml:48`) → 0–15 s usia tambahan. Desain tidak
     menyatakan apakah H3 (adapter) dan K1 (KEDA) memakai *recording rule* yang sama atau kueri langsung
     (salinan:343-345 hanya "mengubah kueri adapter dan KEDA atau menambah *recording rule*"). Bila berbeda, usia
     bacaan (variabel A) berbeda pada kontras yang diklaim hanya berubah di S dan O.
  3. *Filter Ready H2p bergantung pada komponen yang tak tercatat.* `kube_pod_status_ready` berasal dari
     *kube-state-metrics* (job `kube-state-metrics` di `prometheus.yaml:71-73`; K1 mengekspornya,
     `scripts/run-pilot-openloop.sh:520`). *KSM* tidak ada di daftar `infra` (salinan:606), DQ5 (salinan:784), maupun
     isi klaster (salinan:634-639). Selain itu filter `min_over_time(…[1m]) == 1` dihitung dari *scrape* 15 s dan
     *recording rule* 15 s, sedangkan HPA untuk CPU memakai `LastTransitionTime + metric.Window` dari cap waktu
     *metrics-server* (kode `groupPods`). Kedua waktu masuk adalah fungsi yang berbeda (kadensi *metrics-server* ±60 s dengan fase acak vs
     *scrape* 15 s + evaluasi aturan 15 s + 60 s sampel Ready), jadi tidak ada jaminan sama; besar selisihnya: belum dapat
     dinilai; bukti yang dibutuhkan: pengukuran di kind pada cek (g).
  4. *Kriteria terima cek (g) tanpa makna.* "Replika yang diminta H2 dan H2p … harus sama (toleransi satu replika)"
     (salinan:420-421), padahal replika maksimum yang diminta N = ⌈r/f⌉ = 2–3 (M-3). Toleransi 1 dari 2–3 adalah
     33–50% dari kuantitas yang diukur. Tanpa label dasar.
- **Perbaikan.** Tambahkan cek (e′) analog (g): *scale-up* nyata di kind, bandingkan replika diminta per ronde H3 vs
  K1; nyatakan bentuk deret yang sama untuk H2p, H3, K1 (semua *recording rule* dengan interval yang sama, atau semua
  kueri langsung) dan catat versi/interval; masukkan *KSM* ke inventaris dan DQ5; kriteria cek (g) = identik per ronde
  (toleransi 0) atau selisih waktu masuk yang diukur dan dilaporkan sebagai bagian "paket". Tulis di tabel 19.4.6 baris
  "fungsi HPA (Pods vs External)" untuk H3 → K1.
- **Gerbang terblokir.** 1 (lembar konstruk), 3.

#### M-3. Tidak ada batas bawah informativitas untuk r; pada r ≈ 1,5–1,6 kontras sinyal (H2p → H3) secara struktural tidak membedakan keputusan HPA

- **Lokasi.** salinan:221-244 (aturan r), salinan:117 ("⌈r/f⌉ ≥ 3"), salinan:236-238 ("r ≈ 1,6–1,7 untuk kedua layanan"),
  salinan:341-347 dan 353-357 (alasan kedatangan), salinan:924-932 (tabel batas jenuh).
- **Masalah.** Alasan memilih penghitung kedatangan adalah bahwa rasio CPU per ronde dibatasi ≈ 1/f = 1,25 sedangkan
  rasio laju tak terbatas (λ/L\*). Pada ronde pertama dari 1 pod: replika diminta CPU = ⌈1,25⌉ = 2 (atau 3 hanya bila rasio
  > 2); replika diminta laju = ⌈r/f⌉. Bila ⌈r/f⌉ = 2, kedua jenis sinyal meminta replika yang sama pada keputusan pertama
  dan pada keputusan berikutnya beban per pod 0,75 C masih di dalam toleransi: perbedaan "batas jenuh" dan "informasi
  kedatangan" (salinan:931-932) tidak dapat memengaruhi hasil, dan H2p → H3 hanya mengukur selisih usia bacaan
  [H, rumus HPA]. Menurut aturan P5 dengan angka K1 *shipping*: r maks = 0,8 × 105 / 50 = 1,68 → 1,6 → (r/f = 2,0 dalam ±5% bilangan
  bulat) → 1,5, ⌈1,5/0,8⌉ = 2. ⌈r/f⌉ ≥ 3 menuntut r > 1,6; di r = 1,6–1,7, r bergeser dari 2 ke 3 replika dalam rentang
  yang lebih sempit daripada resolusi C_SLO (langkah ≤ 10%, salinan:322); selain itu kedua *ladder* K1 tidak sepakat pada
  105 req/s (salinan:311-312), sehingga λ_runtuh *shipping* sendiri tidak pasti. Aturan "geser 0,1" (salinan:226-228) hanya
  menjaga bilangan bulat tepat, bukan sensitivitas ini. Pada r kecil, juga: fraksi buruk maksimum (B1) = (r − 1)/r ≈ 0,33–0,39 [H],
  sehingga rentang dinamis keluaran menyempit sementara MDE (C-2) tetap.
  Salinan:224 menetapkan r sebagai minimum lintas dua layanan: satu layanan rentan menentukan intensitas layanan lain
  (konsisten dengan tujuan "r sama", tetapi mengurangi informasi layanan kuat). Bukti: kode HPA di atas; ladder K1.
- **Perbaikan.** Tambahkan syarat informativitas pra-registrasi di aturan r (turunan HPA, bukan efek): mis. "H2p → H3
  hanya dilaporkan sebagai kontras sinyal bila ⌈r/f⌉ ≥ ⌈1/f⌉ + 1; bila tidak, dilaporkan sebagai perbandingan waktu usia
  bacaan", dan margin ±5% ditambah pita sensitivitas terhadap resolusi C_SLO (r ± satu langkah). Bila syarat tidak
  terpenuhi di ladder, putuskan sebelum pembekuan (naikkan batas aman dengan cara yang ada dasarnya, mis. memperbaiki
  K sehingga λ_runtuh naik, atau tulis klaim terbatas), bukan sesudah pilot.
- **Gerbang terblokir.** 2 (aturan r), 1 (konstruk sinyal).

#### M-4. Aturan D1 tidak dapat dijalankan sebagaimana ditulis: definisi C ambigu, ketergantungan melingkar r ↔ s ↔ W, dan seleksi pada derau

- **Lokasi.** salinan:427-431 (tabel D1), salinan:457-483 (rancangan *shipping* baru, urutan), salinan:224-238 (r).
- **Masalah.**
  1. *Ketergantungan melingkar.* D1-b′: Δt = (λ_H1 − 0,88 C) / s dengan s kemiringan *ramp*; s = (r − 0,2) C / 300
     (salinan:259-260) bergantung pada r; r bergantung pada λ_runtuh *shipping baru* (salinan:224-238, "bila D1 lolos, r
     ditentukan yang lebih rendah antara batas *auth* dan batas *shipping* baru"); λ_runtuh *shipping baru* baru diukur di
     langkah (4) sesudah W dipilih (salinan:477-481). Pemilihan C_target (langkah 3) membutuhkan s; s membutuhkan hasil
     langkah 4. Aturan konvergensi (salinan:317-321) hanya mencakup K ↔ C, tidak mencakup r ↔ s.
  2. *"C" dipakai untuk tiga besaran.* C_target (kapasitas slot, W/T̄), C_SLO (p95 ≤ SLO, error ≤ 1%), dan plato *goodput*
     berbeda. D1-b′ menulis "CPU(C) + c_tolak × (λ − C)" (salinan:428), yang benar bila C = plato *goodput* (laju yang
     dilayani saat penolakan dimulai); D1-a mengevaluasi "pada C_SLO" (salinan:427), sementara pemilihan W memakai
     C_target (salinan:469). Di antara C_SLO dan plato, CPU naik per layanan yang dilayani (c_layani ≈ 6–7 ms, K1), bukan
     c_tolak (≈ 2,4–3,3 ms, batas atas); memakai C_SLO sebagai C meremehkan CPU(λ) dan melebihkan λ_H1 sehingga Δt melebih-lebihkan
     (D1-b′ lolos secara keliru). Arah kesalahan: [H], besar: ukur di *ladder*.
  3. *Seleksi pada derau.* C_target = C terbesar pada grid 2 req/s yang lolos "rata-rata + 2 SD < 200 m"
     (salinan:469, 427). Langkah grid 2 req/s × ≈ 6,5 ms ≈ 13 m sebanding dengan 2 SD (≈ 20 m pada SD 10 m). Memilih
     titik batas terbesar yang lolos berarti memilih kandidat yang derau pengukurannya condong menguntungkan; pada kampanye
     rata-rata sebenarnya cenderung lebih tinggi (regresi ke rata-rata). Desain melaporkan rasio CPU(C)/*request*
     sebagai moderator (salinan:830-831) tetapi tidak menyatakan bahwa D1-a dievaluasi ulang pada *ladder* konfirmasi
     dengan W final (langkah 4, salinan:480).
  4. *SD ilustrasi tidak berbasis.* Ilustrasi memakai "SD ±10 m" (salinan:472); K1 tidak menyimpan SD per langkah
     (salinan:427), dan SD antar-*run* CPU dasar K1 = 17,6 m (*shipping*, rata-rata 51,8 m) dan 25,5 m (*auth*, 64,2 m)
     [F/H, `runs.csv`, n = 90 per layanan] — bukan SD yang sama (konteks beban berbeda), tetapi menunjukkan
     bahwa 10 m bukan angka konservatif untuk dipakai sebagai ilustrasi aturan 2σ.
- **Perbaikan.** Tulis algoritma D1 sebagai iterasi dengan satu daftar variabel (C_target, C_SLO, C_plato, λ_runtuh, r, s, K,
  W) dan urutan eksplisit; jadikan r ↔ s bagian konvergensi atau pakai batas r konservatif (r_maks aman) saat memilih C;
  definisikan C di D1-b′ sebagai plato *goodput*; wajibkan D1-a dan D1-b′ dievaluasi ulang pada *ladder* konfirmasi
  dengan W final dan hasilnya (bukan hanya pilihan awal) menentukan status D1; ganti 2σ dengan interval yang memakai
  derajat bebas ulangan (≥ 2–3 ulangan memberi SD yang sangat tidak pasti).
- **Gerbang terblokir.** 2, 1.

#### M-5. Margin non-inferioritas dan δ_min *gradual* bergantung pada model fluida yang belum ada dan yang validasinya (menurut desain sendiri) tidak dapat memvalidasi besaran

- **Lokasi.** salinan:432-456 (model, *back-test*), salinan:561-570 (δ_min), salinan:842 (margin NI *auth*), salinan:983-989
  (tingkat putusan "bermakna").
- **Masalah.** Uji konfirmatori utama komponen *auth* Hipotesis 1 dilakukan pada *gradual* (salinan:835-838, 842), dan
  margin-nya = δ_min *gradual* "dihitung dengan model fluida (19.3.5)" (salinan:566). Model "ditulis ulang … sebelum cek
  dijalankan" (salinan:438-439), belum ada, dan kriteria terimanya cukup tanda selisih dan besaran "di dalam interval
  kepercayaan 95% data K1" dengan lebar K1 0,011–0,086 yang desain sendiri akui tidak cukup untuk memvalidasi besaran
  pada resolusi δ_min (salinan:436-438). Jadi angka margin tidak akan punya bukti validasi pada saat dibekukan. Selain
  itu δ_min diberi label B-konv ("15 s adalah pilihan efek terkecil yang dianggap penting", salinan:568-569): yang
  bernama bukan konvensi eksternal, melainkan pilihan sendiri; kaitan 15 s dengan kepentingan praktis bagi
  pengguna tidak diargumentasikan, dan 0,014 setara 28% dari seluruh anggaran galat SLO p95 (5%) [H]. Perubahan
  pada rumus δ_min *spike* (1 − 1/r) × 15/420 benar secara aritmetika (saya periksa ulang) tetapi mengandaikan
  fraksi buruk = kekurangan kapasitas (salinan:443-444) yang di K1 tidak berlaku mulus: fraksi buruk *auth* sudah
  3,3% pada C_SLO (salinan:436-437).
- **Perbaikan.** Bekukan margin sebagai angka dengan dasar yang dapat diperiksa (mis. turunan analitik *spike* sebagai
  batas atas untuk *gradual* dengan argumen, atau SESOI dari argumen kepentingan praktis), bukan "keluaran model";
  bila model dipertahankan, tulis kriteria validasi yang dapat gagal (mis. kesalahan absolut model pada data pilot
  *gradual* ≤ δ_min/2) dan jalankan sebelum pembekuan; ubah label δ_min menjadi DEC dengan sensitivitas ½× dan 2×
  (yang sudah ada) sebagai bagian dari putusan, bukan eksploratori.
- **Gerbang terblokir.** 2, 5.

#### M-6. Aturan K = C_SLO × SLO: klaim lebih kuat daripada Hukum Little, dan syarat penerimaan K1 ("tidak ada *shedding* pada ≤ C") dihilangkan

- **Lokasi.** salinan:288-295, salinan:296-300.
- **Masalah.** Desain menyatakan "pod hanya menerima pekerjaan yang masih bisa selesai dalam SLO … permintaan yang pasti melewati
  SLO ditolak lebih awal". Hukum Little memberi **rata-rata**: K/λ = SLO adalah waktu tinggal *rata-rata* pada
  antrean penuh; sekitar separuh permintaan yang diterima pada antrean penuh akan melewati SLO (varians waktu layanan
  tambahan). Pada *shipping* baru: T̄ ≈ 0,4–0,5 s, W = C × T̄; K − W = C × (SLO − T̄) ≈ 0,5–0,6 s × C antrean tunggu sehingga waktu
  tinggal rata-rata di antrean penuh = SLO. Di K1, aturan K (`ceil(C × p99 at C)`) disertai syarat verifikasi "tidak ada
  *shedding* pada ≤ C, *goodput* bertahan di atas C" (`experiment-results-openloop/pilot-config.env`, komentar di
  atas `MAX_INFLIGHT_*`; Part 08 §8.11). Aturan baru hanya "fraksi tolak pada C_SLO dilaporkan" (salinan:319-321) dan
  K menentukan c_tolak dan CPU saat kewalahan (salinan:293-295), dua besaran yang menggerakkan premis H1 dan D1-b′.
  Untuk *auth*: K = 6 × 1,0 = 6 vs K1 22 (salinan:305-306). Data K1 menunjukkan *inflight_max* 3 pada 6 req/s dan 7 pada 8 req/s
  [F, `ladder.json`; sumber nilai ini kemungkinan deret `http_requests_inflight` ber-*scrape* 15 s, jadi mungkin batas bawah — BD],
  sehingga K = 6 sudah mengikat sedikit di atas C_SLO (1,33 × C_SLO) dan jaraknya ke kondisi pada C_SLO hanya sekitar 2×.
- **Perbaikan.** Tulis kriteria terima K: fraksi tolak pada L\* dan C_SLO = 0 (atau ≤ ambang berangka berdasar) pada
  *ladder* konfirmasi; ganti klaim "pasti melewati SLO" dengan "waktu tinggal rata-rata pada antrean penuh = SLO"; atau
  K dengan faktor yang diturunkan dari p99 (aturan K1) bila alasan penggantian (p99 > SLO pada *auth*) diselesaikan dengan
  cara lain.
- **Gerbang terblokir.** 2.

#### M-7. Fraksi pemicu f = 0,8 dan r bertumpu pada satu titik; cadangan 12% lebih kecil daripada ketidakpastian kapasitas yang tercatat

- **Lokasi.** salinan:131-171 (f), salinan:221-244 (r), salinan:230-232 ("cadangan 20% = pergeseran lutut … 10 → 8").
- **Masalah.**
  1. *Basis faktor 0,8 pada r* adalah satu perbandingan 10 → 8 req/s antara dua *ladder* K1 yang konfigurasinya berbeda
     (v1 tanpa *shedding*, v2 K = 22) [F, Part 08 §8.11 baris 353]. Part 08 sendiri mencatat (parafrase): B2 pada 40 req/s sehat
     di v1 (p95 1.156 ms), tidak lagi di v2 (1.765 ms, +53%), dengan CPU per pod hampir sama (302 vs 317 m). Itu bukan
     pengukuran keterulangan (pergeseran 10 → 8 terkonfound oleh perubahan konfigurasi), jadi label B-rumus dan
     "cadangan 20% = …" lebih kuat dari dasarnya; yang terbukti hanyalah bahwa p95/kapasitas *auth* dapat bergeser besar
     antar-sesi pada CPU yang hampir sama.
  2. *Cadangan 12%* (salinan:140-147) lebih kecil daripada pergeseran lutut 20% dan perubahan p95 +53% yang sudah terekam. C_SLO *auth*
     sudah diakui "peka derau" (salinan:283). Konsekuensi untuk klaim "pada titik pemicu 0,8 × C_SLO": 0,8 × C_SLO yang diukur
     pada satu ladder tidak sama dengan 0,8 × kapasitas sebenarnya pada saat *run*. Pemantauan B2 3σ (salinan:799-804)
     mendeteksi hanya pergeseran besar.
  3. *Sensitivitas f hanya prediksi model* (P19, salinan:163-171) yang divalidasi hanya arah (M-5). Protokol meminta
     sensitivitas terhadap nilai yang berbasis konvensi; di sini sensitivitasnya tidak ada bukti empiris.
- **Perbaikan.** Ukur keterulangan C_SLO (ulangan *ladder* pada beberapa hari/sesi) sebelum membekukan faktor cadangan; ubah label
  0,8 pada r menjadi DEC sampai ada pengukuran keterulangan; tetapkan sensitivitas f dengan model tervalidasi (M-5) atau jadikan f = 0,7 dan 0,8
  level pilot yang dideskripsikan (bukan faktor kampanye) agar sedikitnya mekanisme cadangan teramati.
- **Gerbang terblokir.** 2.

#### M-8. Bentuk *run* diwarisi dari K1; prediksi hasil ditulis sebagai fakta

- **Lokasi.** salinan:671-696 (bentuk), salinan:143-147 ("tidak terjadi pada f = 0,8"), salinan:835-838 (pola utama *gradual*).
- **Masalah.** Bentuk 720 s (pemanasan 120, naik 10 s + tahan 410 / *ramp* 300 + tahan 120, ekor 180) berlabel DEC
  pemilik dan kontinuitas K1 (salinan:685). Pelajaran K1 butir 2 adalah nilai yang diwariskan melintasi perubahan
  rezim (Part 17 §17.23.3). Konsekuensi yang desain akui sendiri: pada f = 0,8 pertumbuhan beban selama waktu reaksi
  melebihi cadangan pada langkah pertama untuk semua konfigurasi terkalibrasi (salinan:143-147). Kalimat
  "Efek lantai *gradual* K1 … tidak terjadi pada f = 0,8" (salinan:145-147) adalah prediksi hasil yang ditulis sebagai fakta.
  Belum dapat dinilai; bukti yang dibutuhkan: pilot dan model tervalidasi. Pola utama Hipotesis 1 adalah *gradual*
  (salinan:835-838), yaitu pola yang menurut desain sendiri "tidak bebas kewalahan"; uji Hipotesis 1 dan non-inferioritas
  *auth* pada pola ini menjadi pertanyaan waktu reaksi satu keputusan (M-3).
- **Perbaikan.** Ubah kalimat prediksi menjadi hipotesis mekanisme terdaftar; sertakan di register alasan numerik T_ramp (bukan hanya
  "tidak lebih panjang dari *spike*") dan hasilnya sebagai konsekuensi yang diuji pilot (bukan di-"nyatakan").
- **Gerbang terblokir.** 2.

### Minor

- **m-1. Kontradiksi internal.** (a) D1-b′ diputuskan 2026-10-19 menggantikan D1-b (salinan:428) tetapi P12 menyebut D1-b′
  diputuskan 2026-10-18 (salinan:1006). (b) r "dibulatkan ke bawah ke 0,1" (salinan:226) tetapi δ_min dihitung pada
  r = 1,65 (salinan:565). (c) "N ≥ 2 pod (⌈r/f⌉ ≥ 3)" (salinan:117) menyiratkan ⌈r/f⌉ ≥ 3, yang tidak dijamin aturan r: pada r ≈ 1,5 ⌈r/f⌉ = 2 (M-3).
  (d) salinan:153-154 menyebut f = 0,7 "level sensitivitas bersyarat", sedangkan salinan:163-171 menyatakan tanpa *run*. (e)
  salinan:51-53 menyatakan rantai "mengikuti aturan satu variabel", sedangkan salinan:934 menyatakan kontras tidak "murni";
  kalimat 19.0 sebaiknya mengikuti 19.4.6.
- **m-2. Ambang tanpa angka.** "jelas di bawah" (salinan:148-149, 261), "≈ 0" untuk *throttling* k6 (salinan:619-620; K1
  menunjukkan maksimum rasio *throttling* k6 0,153 pada CPU k6 maksimum 0,135 core [F/H, Lampiran A9]), "jelas di
  bawah 1.000 ms" (salinan:284), "≥ 2–3 ulangan" (salinan:322). Register (gerbang 2) memerlukan angka.
- **m-3. DQ *steal* dari Part 17 hilang.** Part 17 §17.11 DQ3 (*CPU steal* ≤ y% per node) dan "cek kesehatan node dan CPU steal"
  per blok (kutipan 17:56, 82) tidak muncul di DQ Part 19 (salinan:778-787); kovariat (salinan:805-806) tidak
  memuat *steal*. `node-exporter` dipasang (salinan:617-618) tetapi tidak dipakai di aturan.
- **m-4. Posisi *run* ulang.** *Run* yang gagal DQ diulang "di akhir blok yang sama" (salinan:789-790): posisi tidak
  teracak, dan jarak waktunya ke pasangan di blok bertambah. Sensitivitas "percobaan pertama" (salinan:794-796) sudah ada;
  tambahkan posisi dan jarak waktu sebagai kovariat.
- **m-5. Klaim yang bersandar pada "tinjauan terdahulu" atau "model terdahulu".** Yang dapat saya periksa dan cocok:
  salinan:465-466 (p95 *auth* 514 ms / *shipping* 916 ms; saya hitung 502 ms / 915 ms pada fase pemanasan, Lampiran A8),
  salinan:615 (CPU k6 maksimum 0,135 core; saya hitung 0,1347, Lampiran A9), salinan:168 (aturan b_SENS "31 pada δ = 0,014";
  2 × (1,96 × 0,028/0,014)² ≈ 30,7 bila σ = 0,028, yaitu SD H1 *shipping gradual*; aturan itu sudah dibuang). Yang tidak
  dapat saya periksa dan karena itu diperlakukan belum terbukti (tidak dipakai di skor): salinan:521-523 (model kasar:
  ±0,05 / ±0,02, daya ±0,15 pada b = 8), salinan:701-702 ("model terdahulu menaruh 80–84% pod-detik berlebih di ekor"),
  salinan:875-876 (H2p memulihkan separuh selisih), salinan:430 ("jalur tinjauan terdahulu"). Dua di antaranya
  (salinan:521-523 untuk "b kemungkinan ≥ 10"; salinan:701-702 untuk "ekor tidak dibandingkan") dipakai sebagai alasan keputusan.
- **m-6. Toleransi HPA sekarang dapat dikonfigurasi per HPA.** Dokumentasi Kubernetes menyebut bidang `tolerance` per HPA
  (`HPAConfigurableTolerance`, tersedia sejak v1.33, stabil sejak v1.37) dan kode `horizontal.go` membacanya dari
  `spec.behavior` [F]. Desain mengunci "toleransi 10%" sebagai konstanta; di klaster ≥ 1.35 cek bahwa semua HPA (termasuk
  yang dibuat KEDA) tidak memiliki `behavior.*.tolerance` dan catat bawaan *controller*; bila diset, hanya bila sama
  untuk semua. Perilaku bawaan KEDA saat `behavior` tidak diisi tidak dinyatakan dokumentasi KEDA 2.17 [BD]: baca HPA yang dihasilkan
  KEDA di gerbang 1.
- **m-7. Versi *add-on* terkelola.** KEDA dan *metrics-server* adalah *add-on* AKS terkelola; versinya tidak dapat dikunci
  oleh desain (salinan:640-641 menjanjikan penguncian *chart*/*digest* dan pencatatan otomatis). Pencatatan per run
  memadai untuk mendeteksi, tidak untuk mencegah perubahan di tengah kampanye [BD: apakah AKS memperbarui *add-on* tanpa
  *upgrade* klaster].
- **m-8. Klaim *shipping* berlaku "menurut rumus HPA".** Hipotesis 1 untuk *shipping* adalah uji mekanisme yang
  diprediksi rumus (salinan:827-831) pada layanan yang dirancang sehingga kapasitas habis sebelum CPU mencapai target
  (C dipilih sebagai yang terbesar yang masih memenuhi D1; salinan:469-471). Ini diungkapkan jujur di desain; sebagai [P]
  saya mencatat bahwa vonis atas "wait-dominant" tetap tak punya wakil di dunia nyata di luar contoh pola *bulkhead* di
  dokumentasi Resilience4j/HikariCP (nilai bawaan konkurensi saja, bukan bukti layanan nyata dibatasi slot; tugas pendamping
  salinan:1032-1035 masih terbuka).
- **m-9. Operasionalisasi Hipotesis 2.** Putusan memakai S (H2p → H3) saja, sehingga komponen jalur ukur (H2 → H2p) keluar dari
  hipotesis (salinan:851-861, 864-872). Itu konsisten dengan P18 (menunggu pembimbing), tetapi hasil "H2 didukung"
  tidak berlaku bagi praktisi yang memilih antara CPU lewat *metrics-server* dan laju lewat *adapter* (efek total). [P]
- **m-10. Multiplisitas lintas hipotesis tidak dikoreksi** (salinan:961-966); alasan menolak Holm ("terlalu ketat untuk
  tiga pertanyaan berbeda") adalah argumen daya, bukan argumen tipe-I. Dengan 10 uji konfirmatori (3 + 4 + 2 + 1)
  peluang setidaknya satu klaim "didukung" palsu tidak nol; pernyataan di naskah sudah dijanjikan (salinan:965-966).
- **m-11. "Bukan HARKing".** Kalimat salinan:816-818 terlalu kuat: rumusan Hipotesis 1 tidak berubah, tetapi sistem yang diuji
  (layanan *shipping*) dan operasionalisasi (H1 saja) diubah setelah K1 menunjukkan hipotesis tidak dapat diuji. Itu sah bila
  diungkapkan (sudah), tetapi bukan "bukan HARKing".
- **m-12. Lingkup "ladder singkat".** Ladder baru memuat: dua–tiga putaran K ↔ C, langkah kelebihan beban, langkah N pod,
  grid kandidat C/W, ulangan ≥ 2–3 pada langkah rapat, kedua varian *shipping* (salinan:313-327, 477-481), tetapi disebut
  "singkat" dan dijalankan sebelum gerbang 3 selesai (salinan:361-363, 1023-1027). Protokol memperbolehkan cek *cloud* pendek
  untuk gerbang 1–2 sebelum gerbang lain lolos; apakah cakupan ini masih "pendek" adalah tafsir protokol yang sebaiknya
  dicatat sebagai keputusan bertanggal dengan persetujuan pemilik, bukan diasumsikan. [P]
- **m-13. Cabang "terima dan ungkap".** Beberapa kegagalan gerbang berakhir sebagai deviasi bertanggal, bukan berhenti:
  konvergensi K gagal (salinan:319-321), cek (g) gagal → judul "paket" (salinan:421), pita kesetaraan gagal → klaim
  ditulis ulang (salinan:124-129). Semuanya pra-terdaftar, sehingga bukan penawaran pasca-data; tetapi pola "gagal →
  lanjut dengan klaim lebih lemah" adalah bentuk jinak dari konsekuensi gerbang yang tidak kredibel (Part 17 §17.23.4).
  Pastikan klaim yang lebih lemah itu juga memengaruhi hipotesis mana yang tetap konfirmatori. [P]

---

## 3. Nilai atau aturan yang belum berbasis atau berlabel lebih kuat daripada dasarnya

| # | Butir | Lokasi | Label sekarang | Kenapa kurang | Cara memperoleh dasar |
|---|---|---|---|---|---|
| 1 | b = 10 | salinan:506, 528-553 | DEC + "pembenaran sumber daya" | Dasar tertulis bertentangan dengan salinan:7; protokol gerbang 4 meminta simulasi daya dengan varians pilot; daya NI 0,15–0,29 pada σ ≥ 0,02 (C-2) | Simulasi daya pada SESOI beralasan dengan σ berbatas atas dari pilot yang diperbesar; atau margin yang dapat dicapai |
| 2 | δ_min = 15 s → (1 − 1/r) × 15/420 | salinan:561-570 | B-konv (turunan B-rumus) | Tidak ada konvensi yang dinamai; pilihan sendiri; kepentingan praktis tidak diargumentasikan; MDE melebihi δ_min 2–3× (C-2, M-5) | Tandai DEC dengan argumen kepentingan (mis. porsi anggaran galat SLO), atau SESOI dari pemangku kepentingan |
| 3 | Margin NI = δ_min *gradual* dari model fluida | salinan:432-456, 566, 842 | B-rumus | Model belum ada; validasi hanya arah, lebar CI K1 tidak memvalidasi besaran (salinan:436-438) | Turunan analitik atau kriteria validasi yang bisa gagal (M-5) |
| 4 | f = 0,8 | salinan:131-171 | B-konv | Angka 80% adalah utilisasi terhadap *request*, dipakai terhadap C_SLO (desain mengakui, salinan:159-162); sensitivitas "tinggi" dengan satu level dan sensitivitas hanya model | Ukur sensitivitas empiris (≥ 2 level di pilot) atau ubah menjadi klaim bersyarat eksplisit pada f |
| 5 | Faktor 0,8 pada r (cadangan 20%) | salinan:221-232 | B-rumus | Dasar = satu perbandingan 10 → 8 terkonfound (Part 08 §8.11) | Ukur keterulangan C_SLO dan λ_runtuh; ubah label |
| 6 | Pita kesetaraan pemicu 1,0 ± 0,1 | salinan:122-124 | B-rumus ("toleransi HPA") | Toleransi HPA bukan toleransi kesetaraan; 0,10 = rentang cadangan 2–20% (M-1) | Turunkan dari sensitivitas cadangan; definisikan pada beban pemicu terukur |
| 7 | "Toleransi satu replika" (cek g) | salinan:420-421 | tanpa label | N maks = 2–3 → 33–50% | Toleransi 0 per ronde atau selisih waktu terukur |
| 8 | K = C_SLO × SLO | salinan:288-295 | B-rumus | Little memberi rata-rata, bukan batas; syarat penerimaan K1 hilang (M-6) | Kriteria terima berangka di *ladder* konfirmasi |
| 9 | T_svc: p95 bawaan = 0,5 × SLO | salinan:461-467 | B-konv | "Separuh SLO sebagai sela" bukan konvensi yang dinamai; menentukan W, C_target, D1, klaim | Tandai DEC + sensitivitas (0,4 / 0,6) pada D1 |
| 10 | D1-a: rata-rata + 2 SD < 200 m | salinan:427 | B / B-rumus / B-konv | SD dari ≥ 2–3 ulangan (derajat bebas rendah); ilustrasi SD 10 m vs SD antar-run CPU dasar K1 17,6–25,5 m; seleksi pada derau (M-4) | Interval prediksi; evaluasi ulang pada *ladder* konfirmasi |
| 11 | D1-b′: Δt ≥ 15 s | salinan:428 | B-rumus | Ambang 15 s adalah pilihan; variabel C dan s ambigu/melingkar (M-4) | Definisikan variabel; ambang diturunkan dari sensitivitas atau DEC |
| 12 | Konvergensi ≤ 10% C, ≤ 3 putaran | salinan:317-321 | B-rumus | 10% = resolusi langkah *ladder*, bukan toleransi statistik; 3 putaran tanpa dasar | Hitung ketidakpastian C_SLO dari ulangan; tetapkan stop bila tak konvergen |
| 13 | Bentuk *run* (pemanasan 120, naik 10, tahan 410 / *ramp* 300 + tahan 120, ekor 180) | salinan:671-696 | DEC + B-konv kontinuitas | Kontinuitas dengan K1 adalah pelajaran K1 butir 2; konsekuensi cadangan diakui desain | Turunkan T_ramp dan tahan dari tujuan klaim, atau jadikan salah satu faktor sensitivitas di pilot |
| 14 | *Request/limit* 250m/500m | salinan:831-834, 593 | DEC | Menentukan premis H1 (CPU(C)/*request*) dan kapasitas; sensitivitas hanya model | Simpan sebagai moderator terukur (sudah) + sensitivitas kind |
| 15 | `sut` ≥ 2 × replika tertinggi pilot | salinan:197-199 | B-konv | Faktor 2 tanpa dasar | DQ7 menjaga; pertahankan dengan label DEC |
| 16 | `RESET_WAIT` 120 s, `STABILIZE_WAIT` 90 s | salinan:715-738 | B-konv (kontinuitas) | Teks sendiri menyebut "tanpa dasar tercatat" lalu menurunkan batas bawah; label seharusnya B-rumus (batas bawah turunan), bukan kontinuitas | Ubah label menjadi B-rumus + alasan |
| 17 | Pergeseran B2 3σ (σ_B2 = max(K1, pilot)) | salinan:799-804 | B-konv | σ dari 5 *run* K1 (B2 5 pod) dan 2 *run* pilot; desain mengakui batas bawah | Perbarui dengan σ pilot yang diperbesar |
| 18 | Jendela *rate* 1 menit untuk H2p dan H3 | salinan:98, 595 | B-konv (disamakan) | Sensitivitas hanya "catatan wajib" | Uji 30 s vs 60 s di pilot sebagai sensitivitas deskriptif |
| 19 | Syarat Ready sepanjang 60 s untuk H2p | salinan:103-111 | B (kode HPA) | Dasar kode benar [F]; implementasi bergantung KSM dan *recording rule* yang tidak diinventaris (M-2) | Inventaris, interval sama, cek (g) tanpa toleransi |
| 20 | Kriteria validasi model "dalam CI 95% K1" | salinan:447-450 | B-konv | CI K1 terlalu lebar untuk menolak model (desain sendiri) | Kriteria yang dapat gagal pada data pilot |
| 21 | σ = 0,031 (K1 *shipping spike*) untuk daya | salinan:451-453, 542-544 | B (data K1) | Berasal dari r 2,1–3,75; desain baru r mungkin ≈ 1,5; skala fraksi buruk berbeda | σ pilot berbatas atas |
| 22 | Keluarga uji lintas hipotesis tanpa koreksi | salinan:961-966 | B-konv | Alasan "terlalu ketat" adalah argumen daya | Nyatakan tingkat galat keluarga gabungan; atau Holm sebagai sensitivitas |
| 23 | Ambang tak berangka ("jelas", "≈ 0", "kecil") | salinan:148-149, 261, 284, 619-620 | tanpa label | Register menuntut angka | Beri angka berdasar atau hapus dari DQ |
| 24 | Pola utama per hipotesis (P14), operasionalisasi H1/H2 (P13/P18) | salinan:835-838, 859-861, 1007-1012 | usulan pemilik | Menunggu konfirmasi pembimbing; pola utama menentukan uji konfirmatori | Konfirmasi tercatat sebelum gerbang 5 |

---

## 4. Kesalahan K1 yang berpotensi terulang tanpa disadari

Sumber kesalahan K1: Part 17 §17.23 (kutipan), Part 13 §13.6–13.8 dan §13.15 (salinan), Part 08 dan 11, kode dan data.

| # | Kesalahan K1 (sumber) | Tempat di desain baru | Bukti | Status | Perbaikan |
|---|---|---|---|---|---|
| 1 | Faktor adalah label yang menggeser paket variabel (17.23.2, 17.23.5) | H3 → K1 disebut "hanya jalur API" (salinan:49); H2 → H2p dan H2p → H3 bundel | Kode `replica_calculator.go` (Pods vs External) [F]; bentuk deret H2p vs H3 tak sama (M-2) | **Sebagian terulang**: H2p memperbaiki besar; "mesin" tetap paket | M-2 |
| 2 | Nilai diwariskan melintasi perubahan rezim (17.23.3) | Bentuk *run*, `RESET`/`STABILIZE`, 250m/500m, VU, `noConnectionReuse` (salinan:671-738, 593) | Label B-konv/DEC "kontinuitas" | **Sebagian terulang** (diakui sebagian) | M-8, §3 baris 13-16 |
| 3 | Pemicu tidak setara (PM4; Part 13 §13.8) | Pita 1,0 ± 0,1 (salinan:122-124); penghitung laju memuat non-beban; offset CPU | M-1; data K1 `prom_http_requests_rate.json` [F] | **Sebagian terulang** (dari 20–30 poin selisih ke ≤ 10% yang tidak diturunkan dari sensitivitas) | M-1 |
| 4 | Laju = dilayani, rasio per ronde dibatasi (17.23.2 "kopling kedua") | Usulan (b) kedatangan (salinan:339-357) | Kode `admission_control.py:11-19`; adapter `prometheus-adapter-values.yaml:58-68` [F] | **Tertutup** konstruk; sisa: penyaringan *handler* dan bentuk deret (M-1, M-2); informativitas bergantung r (M-3) | M-1 – M-3 |
| 5 | Gerbang memeriksa instrumen, bukan konstruk, dan konsekuensinya tidak kredibel (17.23.4) | Gerbang 1–7 + cek (c)(d)(e)(g) + D1 | Cek konstruk ada; beberapa gagal → "terima dan ungkap" (m-13) | **Sebagian tertutup** | Tegaskan klaim mana yang gugur pada tiap kegagalan |
| 6 | Aturan dibuat setelah data (SLO "Opsi 2", keluarga Holm, uji; Part 13 §13.15) | SLO, λ0, r, f, K, uji, keluarga ditetapkan di muka (salinan:265-295, 951-989) | Bagian besar pra-terdaftar [F] | **Tertutup**; sisa: margin NI dari model yang belum ada (M-5), aturan "perbaiki dan ulangi pilot" (salinan:507) tanpa daftar perbaikan yang diizinkan | M-5; tulis daftar izin |
| 7 | Statistik sebagai pelaporan, bukan masukan desain (17.23.4) | b dan margin | C-2: b tanpa daya pada SESOI; daya NI 0,15–0,29 [H] | **Terulang dalam bentuk baru** (daya dihitung dan diterima, bukan dipakai memilih b) | C-2 |
| 8 | Fase siklus HPA deterministik terhadap *onset* | Penundaan acak U(0, 15) s (salinan:722) | 109 dari 120 (90,8%) kenaikan pertama jatuh dalam pita 3,5 s modulo 15; H1/H2/H3 30/30, K1 23/30 [H, `runs.csv`, Lampiran A2] | **Tertutup**; siklus 60 s *metrics-server* tidak diacak dan tidak dicatat (hanya fase 15 s) | Catat cap waktu bacaan terakhir *metrics-server* sebelum *onset* sebagai kovariat |
| 9 | Fakta platform dipahami setelah data (resolusi 60 s, delegasi KEDA 1→N) | 19.3.9, cek (f)(e) | Resolusi 60 s [F, FAQ *metrics-server*]; `cooldownPeriod` hanya 0↔1 [F, KEDA 2.17] | **Sebagian tertutup**; sisa [BD]: bawaan `behavior` KEDA, argumen *metrics-server* di AKS ≥ 1.35, versi *add-on* terkelola (m-6, m-7) | Baca HPA/Deployment aktual di gerbang 1 |
| 10 | Isolasi: replika baru menumpuk di *node* k6 (X4) | Pool `sut`/`load`/`deps`/`infra` (salinan:599-607) | Desain; tidak dapat diuji sampai klaster ada | **Tertutup**; sisa: semua replika berbagi satu *node* 16 vCPU (SMT, cache) sehingga jumlah replika yang berbeda antar-konfigurasi memengaruhi kapasitas per pod (bukti K1: p95 *auth* 8 req/s per pod: 1.225 ms pada 1 pod vs 1.765 ms pada 5 pod [F, `ladder.json`]) | Langkah N pod di tata letak final sudah ada (salinan:324-325); jadikan hasilnya masukan C_SLO per N |
| 11 | Pilot terbatas (hanya *spike*, 2 repetisi, tanpa H1/*gradual*) (17.23.1) | Pilot penuh 56 *run* (salinan:490-507) | Desain | **Tertutup**; tetapi pilot dilarang menentukan b (C-2) | C-2 |
| 12 | Premis jenis layanan tidak diukur (17.23.2) | Cek (c) uji naik *limit*, kontrol negatif *shipping*, D1 | Desain; data K1 menolak kriteria CPU ≥ 0,8 × *limit* dan rasio *throttling* [F, `ladder.json`] | **Tertutup** konstruk; hasil menentukan cabang | — |
| 13 | Klaim bersandar pada ringkasan tinjauan/model, bukan data (butir proses) | Beberapa angka "tinjauan terdahulu" (m-5) | Tujuh butir; empat tak dapat diperiksa, dua di antaranya (b ≥ 10; ekor) dipakai sebagai alasan keputusan | **Terulang** (jenis sumber yang sama) | Ganti dengan hitungan di repositori atau hapus |
| 14 | Pilot → kampanye tanpa menurunkan ulang nilai | Aturan diturunkan; angka dari *ladder* baru | — | **Tertutup** | — |

---

## 5. Hal yang sudah benar (jangan diubah tanpa alasan)

1. **Urutan aturan** SLO → C_SLO → L\*, u\*, λp, λ0 → N, K, M, dengan SLO dibekukan lebih dulu (salinan:216-219). Ini menutup kesalahan SLO pasca-data K1.
2. **Penghitung kedatangan** (dilayani + ditolak) dan alasannya (salinan:339-357): arah benar dan terverifikasi lewat kode `admission_control.py`
   (penolakan di lapisan terluar tidak dihitung di `http_requests_total`).
3. **Dekomposisi S > |E| menjadi D1 dan D2** (salinan:862-868): S − E > 0 dan S + E > 0 setara S > |E|; logika *intersection-union* benar. (Masalahnya ada pada uji D2, bukan pada dekomposisi.)
4. **Penundaan acak U(0, 15) s** (salinan:722): bukti K1 saya konfirmasi (Lampiran A2).
5. **Jendela *scale-down* 300 s untuk semua**, tanpa blok `behavior`; kode `horizontal.go` memastikan batas *scale-up* bawaan
   `max(2 × replika, 4)` dan alasan `ScalingLimited` (salinan:203-208) [F].
6. **Isolasi *pool*, *digest*, *pre-pull*, `lscpu` per *run*, klaster tidak dihentikan, DQ biner dan prinsip "tidak ada eksklusi
   yang berkorelasi dengan perlakuan"** (salinan:775-811).
7. **Pelaporan jujur daya** (salinan:534-553, 558-560): semua angka daya yang saya reproduksi cocok (Lampiran C); P22 (aturan cadangan berbasis daya) dibuang dengan alasan yang benar.
8. **Pemisahan tingkat putusan "bermakna" vs "kecil"** dengan δ_min (salinan:983-989) dan kata "mengungguli" hanya untuk "bermakna".
9. **Pemeriksaan kesetaraan pemicu pada N pod** (salinan:116-129) sebagai gagasan; yang perlu diperbaiki hanya ambangnya (M-1).
10. **Pembagian pola utama menurut mekanisme** (P14) dan label usulan yang menunggu pembimbing; pelabelan BB/DEC yang terbuka di §19.5.
11. **Verifikasi klaim platform yang saya periksa**: KEDA `maxReplicaCount` bawaan 100, `useCachedMetrics` bawaan `false`, `cooldownPeriod` hanya 0↔1;
    *metrics-server* bawaan 60 s; Dasv5 tanpa *Ephemeral OS Disk* dan mendukung *live migration* serta dua generasi CPU;
    *pool* sistem AKS ≥ 2 *node*; kalender AKS (1.33 berakhir Jul 2026; 1.34 Nov 2026; 1.35 Mar 2027) (Lampiran D).
12. **Angka K1 yang dikutip**: seluruhnya cocok dengan data mentah saat saya hitung ulang (Lampiran A).

---

## 6. Pertanyaan yang kemungkinan diajukan penguji

1. "Anda menyatakan Hipotesis 2 didukung bila D2 lolos. Mengapa *signed-rank* sah untuk kombinasi berbobot tiga konfigurasi, dan berapa ukuran uji sebenarnya pada sebaran miring?" (C-1)
2. "Dari mana b = 10? Jika sumber daya bukan batasan, mengapa tidak dipilih agar efek terkecil yang Anda anggap penting terdeteksi?" (C-2)
3. "Mengapa SESOI Anda satu siklus *sync* HPA? Apa artinya 0,014 bagi pengguna, dan mengapa percobaan tidak mampu mendeteksinya?" (C-2, M-5)
4. "Bagaimana Anda tahu titik pemicu keempat konfigurasi setara? Pita ± 10% itu sama dengan cadangan yang Anda sebut berpengaruh." (M-1)
5. "Apakah 'mesin' KEDA vs HPA hanya jalur API? Fungsi penghitung replika Pods dan External berbeda di kode." (M-2)
6. "Bagaimana kontras sinyal bermakna bila kedua sinyal meminta jumlah replika yang sama pada keputusan pertama?" (M-3)
7. "Layanan *shipping* Anda dirancang agar CPU kalah. Apa isi ilmiah hasilnya selain mengonfirmasi rumus HPA?" (m-8, salinan:827-831)
8. "Mengapa C dipilih terbesar yang lolos D1, dan bagaimana Anda tahu D1 tidak lolos hanya karena derau?" (M-4)
9. "Mengapa bentuk *run* sama dengan K1 padahal parameter lain berubah, dan apakah *gradual* sungguh *gradual* bila semua konfigurasi kewalahan pada langkah pertama?" (M-8)
10. "Apa yang membedakan 'tidak terbukti' dari 'tidak dapat disimpulkan' dalam putusan Hipotesis 1 bila dayanya 0,15?" (C-2)
11. "Penghitung laju Anda memuat permintaan `/metrics` dan *probe*? Apa efeknya pada titik pemicu?" (M-1)
12. "Siapa yang menjamin versi *add-on* AKS (KEDA, *metrics-server*) tidak berubah selama kampanye?" (m-7)
13. "Mengapa 0,8 × λ_runtuh? Dasar 20% itu hasil perubahan konfigurasi, bukan keterulangan." (M-7)

---

## 7. Lampiran: hitungan dan sumber yang saya periksa

Skrip ada di *scratchpad* sesi (bukan di repositori); perintah: `uv run --quiet --with numpy --with scipy python -I skrip.py`.
Data: `experiment-results-openloop/` (`analysis/ladder.json`, `analysis/cache/*.npz`, `analysis/part12/runs.csv`,
`*/*/*/rep*/metadata.json`, `prom_*.json`), kode `scripts/pilot_openloop.py`, `scripts/run-pilot-openloop.sh`,
`backend/services/*/internal/middleware/admission_control.py`, `infrastructure/kubernetes/monitoring/`,
`infrastructure/kubernetes/experiments/`.

### A. Angka K1 yang saya hitung ulang (semuanya cocok dengan desain)

| # | Klaim desain | Hasil saya | Sumber |
|---|---|---|---|
| A1 | *Auth* 6 req/s p95 653 ms; 8 req/s 1.225 ms; 10 req/s *error* 3,9% (salinan:218-219) | 653,5 / 1.225,4 / 3,889%; CPU 257 / 314 m, rasio *throttling* 0,445 / 0,619 pada 6 / 8 req/s | `ladder.json` |
| A1b | *Shipping* CPU 266 m (40 req/s) dan 377 m (50 req/s); *shipping* 5 pod 40 req/s per pod rata-rata 337 m (salinan:119-121) | 266 / 377 m (1 pod); 5 pod pada 200 req/s: 318, 372, 336, 351, 308 m → rata-rata 337 m. *Auth* 5 pod, 40 req/s: p95 1.765 ms, CPU 261–377 m, rata-rata 317 m vs 314 m (1 pod pada 8 req/s) | `ladder.json` |
| A2 | 91% kenaikan pertama dalam pita 3,5 s modulo 15 (salinan:722) | 109/120 = 90,8% (pita mulai 3,6 s); H1, H2, H3: 30/30; K1: 23/30 | `runs.csv` `O4_first_up_s` |
| A3 | Fraksi buruk B2 pada 1.000 ms: *auth gradual* 3,0%, *spike* 4,1%; *shipping* ≈ 0 (salinan:280-283) | 2,98% / 4,10%; *shipping* 0,03% / 0,11% | `cache` jendela [120, 540) menurut waktu mulai |
| A4 | SD tak berpasangan H2 − H3 *spike*: 0,035 (*auth*), 0,031 (*shipping*); berpasangan 0,033 / 0,024; korelasi residu 0,11 / 0,51 (salinan:516-519) | 0,0353 / 0,0312; 0,0333 / 0,0238; 0,11 / 0,51 | `cache` |
| A5 | σ per konfigurasi *spike* ≈ 0,022–0,025; H1 *shipping gradual* ±0,028 (salinan:538, 542) | SD per konfigurasi *spike*: *auth* H1 0,028, H2 0,028, H3 0,021, K1 0,024; *shipping* H1 0,021, H2 0,028, H3 0,014, K1 0,013; H1 *shipping gradual* 0,0279. SD berbeda antar-konfigurasi (CPU ≈ 2 × laju) | `cache` |
| A6 | δ_min = (1 − 1/r) × 15/420: 0,014 (r = 1,65), 0,027 (r = 4) | 0,01407 / 0,02679 | aritmetika |
| A7 | Batas atas r *shipping* K1: 0,8 × 105/50 = 1,68 (salinan:236-238) | 1,68; setelah dibulatkan 0,1 → 1,6; r/f = 2,0 → geser → 1,5 | aritmetika |
| A8 | p95 pemanasan *auth* 2 req/s 514 ms; *shipping* 10 req/s 916 ms (salinan:465-466, "tinjauan terdahulu") | *auth* median 502 ms (473–526); *shipping* 915 ms (910–921), p50 708 ms | `cache` t ∈ [10, 120) s |
| A9 | CPU k6 maksimum 0,135 core (salinan:615) | 0,1347 core (*shipping* h3 gradual rep2); memori maks 0,51 GiB; rasio *throttling* k6 maks 0,153 (m-2) | `prom_k6_*.json` |
| A10 | Laju per pod fase dasar | *auth* B1 *gradual* rep1: 2,12 req/s untuk beban 2,00 (deret non-beban 0,067 + 0,067); *shipping*: 9,90 total, non-beban 0,156 | `prom_http_requests_rate.json`, `prom_pod_request_rate.json` |
| A11 | CPU dasar per pod fase dasar | *auth* rata-rata 64,2 m, SD 25,5 m (n = 90); *shipping* 51,8 m, SD 17,6 m (n = 90) | `runs.csv` `base_cpu_m_per_pod` |
| A12 | Pergeseran lutut *auth* 10 → 8 (salinan:231) | Part 08 §8.11 baris 353: "knee is noisy … B2 at 40 healthy in v1 (1156 ms) but not now (1765 ms) with almost the same CPU per pod (302 vs 317 m)"; konfigurasi *ladder* berbeda (v1 tanpa K, v2 K = 22) | `thesis_blueprint/08-open-loop-study.md` |

### B. Perhitungan

**B1. Cadangan vs rasio metrik/target pada L\*.** Untuk metrik ∝ beban: HPA bertindak saat rasio > 1,1; pada beban L rasio
= ρ × L/L\* (ρ = rasio di L\*). Titik pemicu L_t = 1,1 L\*/ρ = 0,88 C/ρ (L\* = 0,8 C).

| ρ | L_t / C | cadangan |
|---|---|---|
| 0,90 | 0,978 | 2,2% |
| 0,95 | 0,926 | 7,4% |
| 1,00 | 0,880 | 12,0% |
| 1,05 | 0,838 | 16,2% |
| 1,10 | 0,800 | 20,0% |

Untuk f = 0,7 (cadangan 23%, salinan:156): 1,1 × 0,7 = 0,77.

**B2. Replika diminta pada keputusan pertama.** Laju: ⌈r/f⌉ (f = 0,8). CPU: ⌈ρ_CPU⌉ dengan ρ_CPU ≤ ≈ 1/f = 1,25 (CPU
saturasi; dengan CPU dasar b > 0, (b + cC)/(b + c·fC) < 1/f). Tabel:

| r | r/f | ⌈r/f⌉ laju | ⌈ρ_CPU⌉ ≤ ⌈1,25⌉ | sama? |
|---|---|---|---|---|
| 1,5 | 1,875 | 2 | 2 | ya |
| 1,6 | 2,000 (geser → 1,5) | 2 | 2 | ya |
| 1,7 | 2,125 | 3 | 2 | tidak |
| 2,4 | 3,000 (geser) | 3 | 2 | tidak |
| 3,0 | 3,75 | 4 | 2 | tidak |

**B3. Ekuivalen waktu MDE.** efek = Δt × (1 − 1/r)/420 → Δt = efek × 420 / (1 − 1/r).

| r | (1 − 1/r) | MDE 0,032 | MDE 0,044 | D2 0,054 | D2 0,077 |
|---|---|---|---|---|---|
| 1,5 | 0,333 | 40 s | 55 s | 68 s | 97 s |
| 1,65 | 0,394 | 34 s | 47 s | 58 s | 82 s |
| 3 | 0,667 | 20 s | 28 s | 34 s | 48 s |
| 4,5 | 0,778 | 17 s | 24 s | 29 s | 42 s |

(Perhitungan memakai rumus desain sendiri, salinan:564-566; bukan prediksi besar efek.)

**B4. Offset CPU.** CPU(λ) = b + cλ, u\* = CPU(L\*)/*request*; HPA bertindak pada 1,1 u\* *request* = 1,1 b + 1,1 c L\* = b + c L_t →
L_t = 1,1 L\* + 0,1 b/c.

**B5. Fraksi buruk maksimum B1.** (r − 1)/r: r = 1,5 → 0,333; r = 1,65 → 0,394.

### C. Simulasi (uji *signed-rank* eksak; b = 10; enumerasi penuh 2¹⁰ tanda pada *midrank*)

Setelan: seed tetap, ρ = 0, α satu sisi 0,025. Skrip: `sim_sr.py`, `sim_ni.py`, `sim_d2.py` (scratchpad).

**C1. Reproduksi tabel desain (efek terkecil terdeteksi, daya 0,8, dua sisi 0,05).** b = 10: 0,0141 / 0,0289 / 0,0428
(σ 0,01 / 0,02 / 0,03); b = 8: 0,018 / 0,0354 / 0,0534. Desain: 0,014 / 0,029 / 0,044 dan 0,018 / 0,035 / 0,053. Cocok.

**C2. Daya non-inferioritas** (selisih sebenarnya 0; uji pada d − margin, sisi bawah 0,025; 4.000 ulangan): margin 0,014 → 0,78 / 0,29 / 0,15
untuk σ 0,01 / 0,02 / 0,03; margin 0,027 → 1,00 / 0,75 / 0,43. Desain (salinan:559-560): 0,78 / 0,28 / 0,14 dan
1,00 / 0,74 / 0,42. Cocok.

**C3. MDE D1/D2** (satu sisi 0,025, b = 10): σ 0,022 / 0,025 / 0,030 → D1 0,032 / 0,036 / 0,043; D2 0,054 / 0,062 / 0,077.
Desain: D1 0,031 / 0,036 / 0,043, D2 0,054 / 0,063 / 0,074. Cocok.

**C4. Ukuran uji D1 dan D2 saat ketiga konfigurasi berdistribusi sama** (20.000 ulangan, kolom: ukuran sisi-atas D1 / D2):

| Bentuk X per konfigurasi | kemiringan X | D1 | D2 | D2 sisi-bawah |
|---|---|---|---|---|
| Normal(0,10; 0,03) | 0,00 | 0,0237 | 0,0242 | 0,0256 |
| Gamma(k = 4; skala 0,025) | 1,00 | 0,0241 | 0,0330 | 0,0170 |
| Lognormal(σ = 0,5), rata-rata 0,10 | 1,73 | 0,0241 | 0,0372 | 0,0157 |
| N(0,10; 0,02) + 10% pencilan +0,15 | 2,04 | 0,0249 | 0,0418 | 0,0135 |

Pada batas komposit S = −E (a = 0,03, 10.000 ulangan): ukuran D2 = 0,0253 (normal), 0,0312, 0,0417, 0,0427.

Kode inti (potongan):

```python
SIGNS = {n: np.array(list(itertools.product([1,-1], repeat=n)), dtype=np.int8) for n in range(1, 11)}
def sr(d):                       # p sisi-atas dan sisi-bawah, signed-rank eksak, selisih nol dibuang
    d = d[d != 0]; n = len(d)
    r = rankdata(np.abs(d)); obs = r[d > 0].sum()
    stat = ((SIGNS[n] == 1) * r).sum(axis=1)
    return (stat >= obs - 1e-9).mean(), (stat <= obs + 1e-9).mean()
# X: bentuk (3, b) = H2p, K1, H3 per blok; D1 = X[0]-X[1]; D2 = X[0]+X[1]-2*X[2]
```

Catatan: bentuk sebaran di desain baru [BD]; simulasi hanya menunjukkan bahwa ukuran uji D2 bergantung pada simetri.

### D. Dokumentasi dan kode resmi yang saya periksa

| Klaim desain | Hasil | URL |
|---|---|---|
| Fungsi HPA Pods vs External berbeda; Pods mengisi nol untuk pod hilang/belum siap saat *scale-up*; `groupPods` logika CPU dan *initialization period*; External: `ceil(usage/targetPerPod)` | Terkonfirmasi (kutipan pendek dari kode) | https://raw.githubusercontent.com/kubernetes/kubernetes/master/pkg/controller/podautoscaler/replica_calculator.go |
| Batas *scale-up* `max(2 × replika, 4)` tanpa `behavior`; `behavior == nil` → jalur *legacy*; alasan `ScalingLimited`; toleransi per-HPA dibaca dari `spec.behavior` | Terkonfirmasi | https://raw.githubusercontent.com/kubernetes/kubernetes/master/pkg/controller/podautoscaler/horizontal.go |
| Bawaan HPA: *scale-down* 300 s; *scale-up* 4 pod atau 100% per 15 s; toleransi 10%; pod hilang/belum siap dianggap 100% (turun) atau 0% (naik); *CPU initialization period* 5 menit; *initial readiness delay* 30 s; `tolerance` per HPA | Terkonfirmasi | https://kubernetes.io/docs/tasks/run-application/horizontal-pod-autoscale/ |
| KEDA 2.17: `maxReplicaCount` 100, `useCachedMetrics` `false`, `cooldownPeriod` hanya skala ke 0; perilaku `behavior` yang tidak diisi: tidak dinyatakan | Terkonfirmasi/[BD] | https://keda.sh/docs/2.17/reference/scaledobject-spec/ |
| *metrics-server*: resolusi bawaan 60 s; di bawah 15 s tidak dianjurkan; `window` pada Metrics API | Terkonfirmasi | https://github.com/kubernetes-sigs/metrics-server/blob/master/FAQ.md |
| *Pool* sistem AKS ≥ 2 *node*, VM ≥ 4 vCPU/4 GB, B-series tak didukung; *pool user* boleh 1 *node* | Terkonfirmasi | https://learn.microsoft.com/en-us/azure/aks/use-system-pools |
| Dasv5: EPYC 7763v dan 9004; tanpa penyimpanan lokal; *Ephemeral OS Disk* tidak didukung; *Live Migration* didukung | Terkonfirmasi | https://learn.microsoft.com/en-us/azure/virtual-machines/sizes/general-purpose/dasv5-series |
| Kalender AKS: 1.33 berakhir Jul 2026; 1.34 Nov 2026; 1.35 Mar 2027; 1.36 Jun 2027 | Terkonfirmasi | https://learn.microsoft.com/en-us/azure/aks/supported-kubernetes-versions |

**Tidak saya periksa ulang (bukan inti temuan):** Resilience4j `maxConcurrentCalls` 25 dan HikariCP `maximumPoolSize` 10, Nielsen 1993,
Lakens 2022, Berger 1982, ICH E9, harga Azure, perilaku *metrics-server* pada GKE/EKS (ditandai [BD] di desain).

### E. Daftar berkas yang saya baca atau buka (independensi)

Dibaca: `tools/redteam-k1-v061/brief.md`; ketiga berkas di `tools/redteam-k1-v061/bahan/`; `thesis_blueprint/08-open-loop-study.md` (hanya
§8.11 dan pencarian `knee`); `thesis_blueprint/11-provenance-and-validity.md` (hanya §11.6 dan daftar judul); data dan kode K1 yang
disebut di brief; `infrastructure/kubernetes/monitoring/prometheus-adapter-values.yaml`, `prometheus.yaml`, manifes `experiments/`;
`scripts/pilot_openloop.py`, `scripts/run-pilot-openloop.sh`; `admission_control.py`, `app/main.py` dan `carrier_service.py`.

Tidak dibuka, tidak dicari isinya, tidak dijalankan: berkas `review`/`review-redteam` di `thesis_blueprint/`; berkas asli Part 13, 14, 15, 16, 17,
18, 19, 20 di `thesis_blueprint/` (salinan dipakai); folder `tools/redteam-*` selain `redteam-k1-v061`; transkrip sesi lain; riwayat git
`thesis_blueprint/`. Indeks memori proyek dimuat otomatis ke konteks sesi oleh sistem; saya tidak membuka berkas memori dan tidak
memakainya sebagai bukti.

*Akhir tinjauan.*
