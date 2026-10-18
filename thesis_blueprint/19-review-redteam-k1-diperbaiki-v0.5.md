# Thesis Blueprint — Part 19: Tinjauan *red team* atas "K1 diperbaiki" v0.5

> Ditulis 2026-10-19. Objek: [19-k1-diperbaiki-v0.md](19-k1-diperbaiki-v0.md) (isi v0.5, 2026-10-19), dinilai sebagai
> **desain eksperimen** untuk skripsi S1. Ini tinjauan awal atas draf yang belum dibekukan, **bukan** gerbang 6 protokol.
> Brief: [tools/redteam-k1-diperbaiki/brief.md](../tools/redteam-k1-diperbaiki/brief.md). Tidak ada perintah *cloud*
> yang dijalankan; analisis lokal memakai data repo (skrip di *scratchpad* sesi, bukan di repo; ringkasan hasil di
> Lampiran A). Anggaran, biaya, dan jadwal tidak dipakai sebagai faktor skor.
>
> **Label bukti.** **[F]** fakta dari berkas repo (`path:baris`), data, atau dokumentasi/kode resmi (URL). **[H]**
> hitungan yang langkahnya ditunjukkan. **[P]** pendapat (tidak ikut menentukan skor). **[BD]** belum dapat diverifikasi.
> "belum dapat dinilai" = bergantung pada hasil yang belum ada; tidak masuk skor.
>
> **Dua fase.** Fase 1 (bagian 1–6 dan Lampiran A) ditulis **sebelum** membuka tinjauan *red team* terdahulu. Fase 2
> (bagian 7) mencatat temuan tambahan dari tinjauan itu dan perubahan skor.

## 1. Ringkasan

**Skor akhir fase 1: 6 / 10** (patokan brief: 5–6 = perlu perbaikan berarti sebelum pilot).

| Dimensi | Skor | Alasan singkat |
|---|---|---|
| 1. Validitas konstruk | 6 | Rantai kontras satu-perubahan-per-langkah, uji naik *limit* dengan kontrol negatif, dan aturan D1 adalah desain yang baik. Dikurangi: kesetaraan pemicu hanya diperiksa pada 1 *pod* (K-1); H2 → H2p bukan satu variabel (M-2); "dibatasi slot" direkayasa dan sumber praktiknya masih [BD] (M-1). |
| 2. Validitas internal | 6 | Blok kecil per layanan × pola, urutan acak, *Deployment* baru, *pool* `sut`/`load`/`infra` ber-*taint*, *digest*. Dikurangi: kepadatan *pod* di satu *node* dan perangkat keras Dasv5 yang heterogen belum ditangani (K-1, M-9); `infra` dipakai bersama (M-10); aturan eksklusi yang salah baca (M-5). |
| 3. Validitas kesimpulan statistik | 5 | Satu keluaran primer, *intersection-union*, *signed-rank* eksak, δ_min dari mekanisme. Dikurangi: b, SENS-f, dan aturan cadangan P22 digerakkan oleh SD dari n = 2 per sel (K-2); aturan keputusan Hipotesis 2 tidak operasional (M-4); validasi model D1-b tidak diskriminatif (M-3). |
| 4. Dasar parameter | 6 | Hampir semua nilai punya dasar, alternatif, sensitivitas, dan jawaban "dari mana". Dikurangi: nilai warisan K1 berlabel B-konv "kontinuitas" padahal dasar aslinya *ad hoc*, termasuk yang menentukan efek (*request*/*limit* 250m/500m); label B/B-rumus yang terlalu kuat (tabel 3). |
| 5. Pengukuran dan keterulangan | 6 | Keluaran dari data mentah per permintaan, versi dikunci, *watcher*, ekspor. Dikurangi: aturan mutu data, pengulangan, dan penghentian tidak ada di Part 19 (M-6); riwayat OOM *adapter* untuk H2p (M-2); model CPU *node* tidak dicatat (M-9). |
| 6. Pelajaran K1 | 6 | Sebagian besar kesalahan K1 ditutup eksplisit (tabel 4). Terulang dalam bentuk baru: pemicu tidak setara pada N > 1, nilai warisan berlabel kontinuitas, gerbang tanpa aturan, SD pilot tipis. |

**Alasan skor akhir (bukan rata-rata mekanis).** Desainnya sudah jauh lebih matang daripada K1: banyak keputusan
tercatat dengan dasar, ada jalan mundur yang sah (D1 gagal → jalur *shipping* K1), dan klaim sengaja dibuat bersyarat.
Tidak ada cacat yang membuat desain tak dapat diperbaiki; dua cacat Kritis dan empat belas Mayor (dua belas dari fase 1,
N-1 dan N-2 dari fase 2) semuanya dapat diperbaiki
sebelum pilot dengan cek tambahan atau penulisan aturan. Skor 6, bukan 7–8, karena dua hal yang menyentuh inti: (i)
semua kontras CPU → laju diputuskan pada N ≥ 2 *pod*, tetapi kesetaraan pemicu dan kurva CPU hanya diukur pada N = 1
dan data K1 sendiri menunjukkan CPU/kapasitas per *pod* berubah dengan N; (ii) kumpulan uji konfirmatori yang tersisa
ditentukan oleh SD dengan 1 derajat kebebasan.

**Setelah fase 2 (bagian 7):** skor akhir **tetap 6**; validitas internal turun 6 → 5 karena bukti baru (fase HPA terkunci, N-1);
dua temuan tambahan (N-1 fase terkunci, N-2 uji arah tanpa efek minimum) dan satu minor (N-3 disk OS efemeral pada Dasv5). Beberapa temuan
fase 1 (K-1, K-2, M-7) ternyata sudah pernah diperingatkan oleh tinjauan terdahulu dan belum diserap Part 19.

**Tiga temuan terpenting.**

1. **K-1 — Kesetaraan pemicu dan kurva CPU(laju) hanya diperiksa pada 1 *pod*.** Pada r × C_SLO dengan f = 0,8,
   keputusan jatuh pada ≥ 2–3 *pod*. Data K1: CPU *shipping* per *pod* pada laju per *pod* yang sama 12–27% lebih tinggi
   pada 5 *pod* daripada 1 *pod*; p95 *auth* pada 8 req/s per *pod*: 1.225 ms (1 *pod*) vs 1.765 ms (5 *pod*).
   Akibatnya "pemicu setara" bisa terulang sebagai ketidaksetaraan pada langkah ke-2 dan seterusnya.
2. **K-2 — b, SENS-f, dan P22 bersandar pada SD dari n = 2 per sel (maksimum atas 8 sel).** [H] Peluang SD dari dua
   pengamatan berada dalam faktor 0,5–2 dari nilai sebenarnya hanya 57%; maksimum atas 8 sel menggelembungkan σ rata-rata
   ×1,7 (b ×3). Aturan P22 lalu memangkas komponen non-inferioritas *auth* secara asimetris, jadi separuh Hipotesis 1
   ("CPU tetap kompetitif") kemungkinan besar tidak pernah diuji.
3. **M-1/M-2 — Konstruk inti masih bersyarat pada dua hal yang sudah dapat dijawab sekarang.** (a) "Dibatasi slot"
   adalah sifat yang direkayasa agar target 80% tidak memicu (Part 17 §17.3 butir 4), berlabel B/B-konv sementara
   sumber praktiknya [BD] (19.6); (b) H2 → H2p disebut hanya jalur ukur, padahal kode `replica_calculator.go`
   memperlakukan metrik kustom tipe *Pods* berbeda dari *Resource* CPU untuk *pod* baru: [BD] di 19.3.5 (g) sudah
   terjawab dari kode.

**Gerbang yang terblokir oleh temuan di bawah:** gerbang 1 (lembar konstruk: K-1, M-1, M-2), gerbang 2 (register
parameter: tabel 3, M-6, M-7), gerbang 4 (pilot: K-2, M-3), gerbang 5 (pembekuan: M-4, M-6). Tidak ada temuan yang menyentuh
gerbang 7 selain M-9, M-10.

## 2. Temuan

Urutan di dalam kelompok: paling berat dulu. "Gerbang" = gerbang protokol yang terblokir. Lokasi Part 19 ditulis
`19-k1-diperbaiki-v0.md:baris`.

### 2.1 Kritis

#### K-1 — Kesetaraan pemicu, kurva CPU, dan kapasitas hanya diukur pada 1 *pod*, padahal kontras diputuskan pada N ≥ 2

- **Lokasi.** `:116-117` (pemeriksaan pemicu "dengan satu *pod*"); `:108-111` (u\* dari CPU(L\*) yang diinterpolasi dari
  kurva *ladder*); `:333-335` dan `:382` (D1-a: CPU pada C_SLO dari *ladder* satu *pod*); `:209` (C_SLO "pada satu *pod*");
  `:875` (PM4); `:93` (B2 diukur langsung hanya pada puncak). Part 17 memuat *ladder* 1–4 *pod* di gerbang 4
  (`17-kampanye-2-ringan-v0.md:78`); Part 19 tidak membawanya.
- **Masalah.** Dengan f = 0,8 dan r ≥ 1,7, jumlah *pod* yang diminta ⌈r / f⌉ ≥ 3 (`:170-171`; r = 1,6 digeser turun oleh
  aturan ±5% di `:213-215`). Keputusan konfigurasi CPU
  (H1, H2, H2p) dan laju (H3, K1) jatuh pada N ≥ 2. Pemicu disamakan hanya pada N = 1 (`:116`); kurva CPU(laju)
  untuk u\* diukur pada N = 1; premis H1 (CPU(C) < 200m) diuji pada N = 1. Bila CPU per *pod* pada laju per *pod* yang
  sama naik dengan N, target CPU yang dikalibrasi pada N = 1 memicu pada laju per *pod* yang lebih rendah daripada L\*
  sejak langkah ke-2, sedangkan ambang laju tidak bergeser. Itu adalah kesalahan K1 "pemicu tidak setara" (variabel P)
  dalam bentuk baru, dan bersifat berkorelasi dengan perlakuan karena tiap konfigurasi mencapai N berbeda pada waktu
  berbeda.
- **Bukti.**
  - [F/H] K1, CPU rata-rata per *pod* *shipping* pada laju per *pod* yang sama (`analysis/ladder.json`; Lampiran A.3):
    10 req/s: 58,5m (median `base_cpu_m_per_pod`, 1 *pod*, `analysis/part12/runs.csv`); 40 req/s: 266m (1 *pod*) vs 337m
    (rata-rata 5 *pod*: 318, 372, 336, 351, 308); interpolasi 1-*pod* pada 24 dan 32 req/s: 155m dan 211m vs 177m dan 236m
    (5 *pod*). Selisih +14%, +12%, +27%. Dua *ladder* 1-*pod* pada 50 req/s sendiri berbeda 7% (377m vs 405m), jadi
    derau ≈ ±7%; selisih +27% berada di atasnya. Penyebabnya tidak diketahui (penempatan *node*, k6, *carrier*) [BD].
  - [H] Kurva CPU(laju) *shipping* cembung (N = 5: 7,4 m per req/s antara 24 dan 32; 12,6 antara 32 dan 40), jadi interpolasi
    lurus 10 → 40 req/s untuk 1 *pod* menaksir terlalu tinggi CPU 1-*pod* di tengah; selisih sebenarnya bukan lebih kecil.
  - [F] K1, kapasitas per *pod* *auth*: 8 req/s per *pod* → p95 1.225 ms pada 1 *pod* vs 1.765 ms pada 5 *pod*; 6 req/s per
    *pod* → 653 vs 787 ms (`ladder.json`; Part 17 `:263`: "tidak linear").
  - [H] Part 19 memusatkan 7 *pod*-sebagian di satu *node* 16 vCPU (`:180-190`) dan menyatakan persaingan antar-*pod* "sama
    untuk semua konfigurasi pada jumlah replika yang sama" (`:186-187`). Jumlah replika justru berbeda antar-konfigurasi
    pada saat yang sama (itulah keluarannya), jadi persaingan itu berkorelasi dengan perlakuan.
  - [F] Dokumentasi Dasv5 mencantumkan **dua** generasi prosesor untuk seri yang sama (EPYC 7763v Milan dan EPYC 9004 Genoa;
    https://learn.microsoft.com/en-us/azure/virtual-machines/sizes/general-purpose/dasv5-series, dicek 2026-10-19). Apakah
    vCPU berupa *thread* SMT tidak dinyatakan di halaman itu [BD]; bila ya, kepadatan *pod* menurunkan kecepatan per vCPU.
- **Perbaikan.**
  1. Tambahkan ke *ladder* baru langkah pada N = 2, 3, 4 (dan N pada puncak) di *pool* `sut` dengan laju per *pod* tetap:
     0,8 × C_SLO, 1,3 × L\*, dan C_SLO. Catat CPU per *pod* dan p95.
  2. Tulis aturan penerimaan: rasio metrik/target tiap konfigurasi dalam 1,0 ± 0,1 (toleransi HPA) di N = 1 sampai N
     puncak; bila gagal, u\* dihitung dari kurva pada N yang relevan atau klaim ditulis bersyarat dan efek paketnya
     dilaporkan.
  3. D1-a diuji pada N = 1 **dan** N = 2–3.
  4. Catat `lscpu` (model, *thread* per inti) tiap *node* `sut` per sesi.
- **Gerbang.** 1 (lembar konstruk), 2, 4.

#### K-2 — Jumlah blok, SENS-f, dan aturan cadangan P22 bersandar pada SD dari n = 2 per sel, diambil maksimumnya

- **Lokasi.** `:441-443` (pilot: 4 strata × 2 blok × 7 = 56 *run*); `:154-158` (b_SENS = ⌈2 × (1,96 × σ_pilot / δ_min)²⌉,
  σ_pilot = SD tak berpasangan terbesar di antara kedua layanan dan konfigurasi); `:468-476` (P22: σ pilot "per sel",
  ρ = 0, daya < 0,8 → estimasi); `:460-466` (b ditetapkan dari sebaran pilot).
- **Masalah.** Satu sel (layanan × pola × konfigurasi) di pilot hanya punya 2 pengamatan, jadi SD punya 1 derajat
  kebebasan. Tiga keputusan desain bergantung pada SD itu: b, apakah SENS-f dijalankan, dan komponen mana yang tetap
  konfirmatori. Karena aturannya memakai maksimum atas banyak sel, ia menggelembung secara sistematis.
- **Bukti.**
  - [H] Simulasi (Lampiran A.4): untuk n = 2, P(s/σ < 0,5) = 0,38, P(s/σ > 2) = 0,046, P(0,5 ≤ s/σ ≤ 2) = 0,57. Maksimum
    atas 8 sel (2 layanan × 4 konfigurasi autoscaler): median 1,73 σ, rentang 90% 1,03–2,74 σ. Karena b ∝ σ², b_SENS
    median ×3 terlalu besar bila semua sel punya σ sama.
  - [F/H] K1 heteroskedastik: SD fraksi buruk *gradual* (SLO 1.000 ms, n = 5; Lampiran A.1) berkisar 0,0023 (B2 *auth*)
    sampai 0,0378 (B1 *auth*), dan di antara autoscaler 0,0012 (K1 *shipping*) sampai 0,0279 (H1 *shipping*): faktor
    ≥ 10 (tertinggi/terendah: 16 pada B1/B2 *auth*, 23 antar-autoscaler *shipping*). "Terbesar di antara semua" ditentukan satu sel (H1), bukan sebaran kontras yang diuji.
  - [H] Dengan SD K1 itu (bukan tebakan), b_SENS = ⌈2 × (1,96 × 0,0279 / δ)²⌉ = 31 untuk δ = 0,014 dan 9 untuk δ = 0,0268
    (rentang δ_min `:481-482`). SENS-f hampir pasti jatuh ke "dicatat sebagai batasan" untuk δ_min *gradual* kecil,
    jadi sensitivitas terhadap f (parameter berdampak tinggi) tidak pernah diuji secara empiris.
  - [F] `:474-476` memberi daya non-inferioritas *auth* 0,78/0,28/0,14 pada σ 0,01/0,02/0,03 (margin 0,014). SD K1 H1
    *auth* *gradual* 0,0151 (Lampiran A.1) berada di antara 0,01 dan 0,02, jadi komponen ini kemungkinan besar daya < 0,8
    dan menjadi estimasi.
  - Aturan P22 menjatuhkan komponen berdaya rendah dan memutuskan hipotesis dari "komponen sisanya"
    (`:471-472`). Komponen superioritas *shipping* adalah yang paling mudah lolos karena sebagian ditentukan rancangan
    D1; komponen non-inferioritas *auth* adalah satu-satunya yang bisa menyangkal klaim "CPU tetap kompetitif". Jadi
    P22 secara sistematis mempertahankan bagian yang hampir pasti benar dan membuang bagian yang bisa salah, lalu
    memberi label "diuji sebagian".
- **Perbaikan.**
  1. Pilot memakai SD **terpool** per layanan × pola dengan model yang disebut (mis. galat dalam-blok dari ANOVA blok ×
     konfigurasi), dilaporkan dengan batas atas kepercayaan (χ²), bukan SD per sel; atau jumlah blok pilot dinaikkan
     sampai derajat kebebasan ≥ 10 per kontras.
  2. Tulis di muka bahwa σ yang masuk aturan b adalah batas atas 80% atau 90% dari σ terpool, bukan maksimum atas sel.
  3. P22 diperluas: setiap komponen yang jatuh ke estimasi harus disebut dalam klaim, dan putusan "didukung" tidak boleh
     dipakai untuk hipotesis yang komponen non-inferioritasnya jatuh. Pilihan netral: tetapkan sekarang bahwa
     non-inferioritas *auth* adalah estimasi (bukan uji) dan tulis klaim "CPU tetap kompetitif" sebagai estimasi dengan
     interval.
  4. Sebutkan dasar "b ≤ 10" di D1-b (`:402`: "keputusan jadwal pemilik"): aturan ini membatasi desain tanpa dasar
     statistik; dasarnya harus daya, bukan jadwal.
- **Gerbang.** 2, 4, 5.

### 2.2 Mayor

#### M-1 — Konstruk "dibatasi slot": direkayasa, sumber praktik [BD], dan operasionalisasi H1 yang ikut dipilih untuk mempertahankan prediksi

- **Lokasi.** `:94` (baris 19.2: "pola *bulkhead*, konvensi bernama"); `:862-864` (sumber praktik [BD]); `:679-683` (P13);
  `:416-418` ("sengaja berpihak melawan efek H1"); Part 17 `:128-129`.
- **Masalah.**
  - Part 17 §17.3 butir 4 sendiri menulis bahwa untuk *shipping* yang didesain ulang "target 80% **tidak pernah**
    memicu" [F]; D1-a menjamin CPU(C) < 200m sebelum kampanye. Bagian *shipping* Hipotesis 1 dan hipotesis kalibrasi
    karena itu sebagian besar adalah konsekuensi rumus HPA yang dipasang oleh rancangan (pertanyaan AK-2, Part 17
    `:970-971`, belum terjawab di Part 19).
  - Baris 19.2 melabel dasar "dibatasi slot" sebagai konvensi bernama, sementara `:862-864` mengakui bahwa sumber bahwa
    layanan seperti itu ada di praktik masih [BD]. Label dan kenyataan tidak cocok: ini BB sampai sumbernya dibaca.
  - P13 (`:679-683`) mengganti operasionalisasi "CPU" dari "(H1 dan H2)" di teks asli menjadi H1 saja, dengan alasan
    "bila keduanya ikut dihitung, keunggulan laju atas CPU hilang oleh rancangan pada pola *gradual*". Alasan itu
    bergantung pada hasil yang diprediksi. Keputusan dibuat sesudah data K1 terlihat. Disklosur ada di BAB 3 (bagus),
    tetapi konstruk Hipotesis 1 sekarang adalah "HPA CPU yang tidak dikalibrasi", bukan "HPA berbasis CPU".
- **Bukti.** [F] sumber-sumber di atas; [H] `:333-335` + rumus HPA (CPU > 1,1 × 0,8 × 250m = 220m untuk bertindak).
- **Perbaikan.** (1) Turunkan label "dibatasi slot" menjadi BB di register sampai ada sumber yang dibaca; (2) tulis di
  lembar konstruk bahwa hasil *shipping* diprediksi dari rumus dan dilaporkan sebagai pengujian prediksi terhitung (bukan
  bukti tentang layanan nyata) dengan klaim eksternal "pada layanan dengan CPU(C) < target × *request*"; (3) klaim
  Hipotesis 1 ditulis "HPA CPU dengan target bawaan 80%" dan hasil H2/H2p selalu dilaporkan berdampingan di kalimat yang
  sama (jangan memisahkannya ke subbab lain); (4) pembimbing memutuskan P13 sebelum pembekuan.
- **Gerbang.** 1, 5.

#### M-2 — H2 → H2p bukan satu variabel; [BD] 19.3.5 (g) sudah terjawab dari kode; adapter H2p punya riwayat OOM

- **Lokasi.** `:55`, `:372-376`, `:760-776`; Part 17 / `infrastructure/kubernetes/monitoring/prometheus-adapter-values.yaml:77-80`.
- **Masalah.** (a) Part 19 menandai perlakuan HPA atas *pod* baru untuk metrik kustom tipe *Pods* sebagai [BD]. Kode
  menjawabnya: logika "belum siap / periode inisialisasi CPU" hanya dijalankan bila `resource == v1.ResourceCPU`
  (`groupPods`); `GetMetricReplicas` meneruskan nama sumber daya kosong, sehingga untuk metrik kustom *pod* yang
  *Running* tetapi belum *Ready* tetap dihitung dengan CPU saat *startup*-nya; hanya fase *Pending* yang dianggap belum
  siap [F]. Jadi H2 (Resource) dan H2p (Pods) berbeda di variabel K (perlakuan *pod* baru), bukan hanya A (jalur ukur).
  (b) K1 mencatat bahwa memasukkan seri `container_*` ke *adapter* membuat satu-satunya *pod adapter* di-OOMKill berulang
  di AKS dan memutus H3 di tengah *run*. H2p memerlukan persis seri `container_cpu_usage_seconds_total`.
- **Bukti.**
  - [F] https://raw.githubusercontent.com/kubernetes/kubernetes/master/pkg/controller/podautoscaler/replica_calculator.go
    (dicek 2026-10-19; pembacaan lewat alat pengambil, **cabang master**, bukan tag 1.35; periksa ulang pada tag yang dipakai):
    kutipan `if resource == v1.ResourceCPU {` di `groupPods`; `c.calcPlainMetricReplicas(..., "")` di `GetMetricReplicas`.
  - [F] `prometheus-adapter-values.yaml:77-80`: "...(container_* plus many namespace-scoped series), which has caused the
    single adapter pod to OOMKill repeatedly on AKS and break H3 mid-run".
  - [F] Part 19 `:372-376` sudah mengakui [BD]; `:769` mencantumkan baris "perlakuan HPA atas pod yang baru mulai".
- **Perbaikan.** (1) Tutup [BD] dengan kutipan kode pada **tag** versi Kubernetes klaster dan tulis kontras H2 → H2p sebagai
  "jalur ukur + perlakuan *pod* baru" (paket A + K), bukan menunggu kind; (2) uji adapter H2p di ukuran klaster
  sebenarnya, bukan hanya kind: `seriesQuery` dibatasi label (`namespace="ecommerce",container="…"`), batas memori diuji,
  restart *adapter* jadi pemeriksaan mutu data per *run* (DQ8 sudah menyebut "tidak restart"); (3) pertimbangkan
  *recording rule* Prometheus untuk CPU per *pod* agar *adapter* hanya melayani deret kecil.
- **Gerbang.** 1, 3.

#### M-3 — Validasi model D1-b lemah dan modelnya mengandaikan kurva "keras" yang bertentangan dengan data *auth*

- **Lokasi.** `:387-405` (isi, *back-test*, daya); `:477-483` (δ_min *gradual* dari model D1-b); `:383` (D1-b).
- **Masalah.** (a) Kriteria penerimaan *back-test* ("tanda cocok" dan besar "di dalam interval kepercayaan 95% data K1")
  tidak dapat menolak model yang salah pada resolusi yang dibutuhkan: lebar interval K1 pada kontras H1 − H3 dan H2 − H3 adalah
  0,038–0,086, yaitu ≈ 1,4–6 × δ_min (0,014–0,027). (b) Data K1
  tidak memuat rezim *shipping* dibatasi slot, jadi *back-test* tidak menyentuh kuantitas yang memutuskan D1-b
  (H1 − H3 *gradual* pada layanan dengan CPU(C) < 200m). (c) Model memakai fraksi buruk = (λ − N × C_SLO)₊ / λ,
  yaitu nol di bawah kapasitas; kurva terukur *auth* mulus.
- **Bukti.**
  - [H] Lampiran A.2: interval Hodges–Lehmann 95% (n = 5 vs 5, urutan ke-3 dan ke-23 dari 25 selisih) untuk kontras K1
    pada SLO 1.000 ms: lebar 0,038 (H1 − H3 *auth gradual*), 0,086 (H1 − H3 *auth spike*), 0,063 (H1 − H3 *shipping
    gradual*), 0,059 (H1 − H3 *shipping spike*), 0,011 (H2 − H3 *shipping gradual*), 0,033 (H2 − H3 *auth gradual*).
    δ_min = 0,014–0,027 (`:481-482`). Tanda H2 − H3 *shipping gradual*: +0,0002 dengan interval [−0,0036, +0,0074], jadi
    syarat "tanda cocok" di sana tidak membatasi apa pun.
  - [H] Lampiran A.6: fraksi buruk pada SLO 1.000 ms di *ladder* K1 1-*pod* *auth* naik mulus: 3,3% (6 req/s), 6,4% (8),
    15,7% (10), 18,9% (12). Pada C_SLO sendiri sudah 3,3%, bukan nol; model D1-b (dan δ_min *gradual* untuk *auth*,
    `:482`) mengabaikan itu. *Shipping* K1 tajam (0% pada 50, 67–85% pada 60), jadi model lebih cocok di sana.
  - [F] D1-b hanya memakai pola *gradual* (`:432-433`); K1 *gradual* adalah pola dengan efek lantai (`:160-161`).
- **Perbaikan.** (1) Ganti kriteria *back-test* dengan kriteria yang menyebutkan toleransi absolut ≤ ½ δ_min atau
  eksplisit mengakui bahwa K1 tidak cukup untuk memvalidasi dan model hanya dipakai sebagai syarat perlu; (2) kurva
  fraksi buruk(laju per *pod*) dimasukkan sebagai fungsi terukur dari *ladder* baru (bukan fungsi tangga di C_SLO); (3)
  tulis bahwa D1-b adalah prediksi eksploratori, bukan bukti, dan putusan D1 tidak boleh bergantung padanya semata:
  tambahkan syarat langsung (CPU(C) + 2σ < 200m pada N = 1 dan 2) yang tidak memerlukan model (D1-a sudah ada).
- **Gerbang.** 2, 4.

#### M-4 — Aturan keputusan Hipotesis 2 tidak operasional

- **Lokasi.** `:710-714`.
- **Masalah.** Syarat kedua ("estimasi efek mesin lebih kecil daripada estimasi efek jenis sinyal pada kedua layanan,
  dibaca dari estimasi dan interval, bukan uji kesetaraan") tidak punya kriteria: perbandingan titik atau interval?
  nilai mutlak? selisih harus berbeda dari nol? Ini dua besaran dengan sebaran berbeda pada pola *spike* yang sama.
  Menurut protokol gerbang 5 aturan keputusan harus beku sebelum data; aturan ini akan ditulis setelah data (kesalahan K1).
- **Bukti.** [F] `:710-714`; protokol (gerbang 5: "Hypotheses with decision rules; ... equivalence margins for any 'no
  difference' ... claim"). "Efek mesin ≈ kecil" di sini adalah klaim "tidak ada perbedaan" tanpa margin.
- **Perbaikan.** Definisikan kontras tunggal: D = |HL(efek sinyal)| − |HL(efek mesin)| dengan interval bootstrap-blok,
  atau uji perbedaan selisih (selisih-dari-selisih di dalam blok, uji *signed-rank* pada d_blok = (H3 − H2p) − (K1 − H3)),
  atau margin non-inferioritas bernama untuk efek mesin (δ_min). Tulis arah, level, dan hasil "tak dapat diputuskan".
- **Gerbang.** 5.

#### M-5 — Pemeriksaan per *run* `ScalingLimited` salah baca dan dapat mengeksklusi *run* secara berkorelasi dengan perlakuan

- **Lokasi.** `:193-195`; `:665-667` (DQ per *run*); `:874-878` (PM7).
- **Masalah.** Part 19 menulis bahwa kondisi `ScalingLimited` "seharusnya tidak pernah muncul" dan menandai *run* sebagai
  masalah mutu data bila muncul. Kondisi itu juga menyala dengan alasan `ScaleUpLimit` ketika jumlah replika yang
  diminta melebihi batas laju *scale-up* bawaan, bukan hanya `TooManyReplicas` (batas M).
- **Bukti.** [F] https://raw.githubusercontent.com/kubernetes/kubernetes/master/pkg/controller/podautoscaler/horizontal.go
  (dicek 2026-10-19; cabang master): bila objek HPA tanpa blok `behavior` (maksud Part 19: "300 s (bawaan)", `:31`, `:90`;
  Part 17 R41 `:513` "tanpa blok `behavior`; KEDA tanpa `advanced`") dipakai `normalizeDesiredReplicas`;
  `calculateScaleUpLimit` = max(2 × replika sekarang, 4); bila yang diminta lebih besar, kondisi `ScalingLimited=True`
  dengan alasan `ScaleUpLimit`. Dengan blok `behavior`, batasnya dari kebijakan, dengan alasan yang sama. [H] Dari 1 *pod*
  batasnya 4; konfigurasi laju dengan penghitung kedatangan meminta ⌈r / f⌉ (`:170-171`): r > 3,2 → ≥ 5 → `ScaleUpLimit`.
  Konfigurasi CPU dibatasi rasio *limit*/target, tetapi dari N ≥ 2 juga dapat melewati batas 4. Frekuensi kemunculannya
  berbeda antar-konfigurasi, jadi eksklusi atas dasar kondisi ini tidak netral terhadap perlakuan.
- **Perbaikan.** Periksa hanya `reason == TooManyReplicas` atau bandingkan `desiredReplicas` dengan M; catat
  `ScaleUpLimit` sebagai keluaran mekanisme. Tulis di muka bahwa *run* tidak dikeluarkan karena alasan yang berkorelasi
  dengan perlakuan.
- **Gerbang.** 5, 7.

#### M-6 — Aturan mutu data, pengulangan, penghentian, dan pergeseran kapasitas B2 tidak ada di Part 19

- **Lokasi.** `:186`, `:194-195`, `:635`, `:666`, `:542-543` ("aturan berhenti kampanye tertulis"); `:455` ("B2 ... memeriksa pergeseran kapasitas").
- **Masalah.** Part 19 merujuk "aturan mutu data (pra-registrasi)" berkali-kali tetapi tidak memuatnya. Rujukan terdekat
  adalah Part 17 §17.11 (DQ1–DQ8) yang ambangnya masih BB (x, y, z; `17-kampanye-2-ringan-v0.md:426-441`) dan tidak memuat
  pemeriksaan sebaran beban per *pod* (G5 K1). "B2 sekaligus memeriksa pergeseran kapasitas" tidak punya kriteria atau
  tindakan. Ini adalah bentuk baru kesalahan K1 (gerbang G6 yang tidak punya aturan lalu dilonggarkan setelah data;
  `11-provenance-and-validity.md:131-132`).
- **Bukti.** [F] di atas; [F] pencarian teks pada Part 19 tidak menemukan G5, dan DQ hanya disebut sebagai DQ4 (`:663`) dan
  DQ8 (`:900`, "tidak berlaku"); [F] Part 17 `:437-441`.
- **Perbaikan.** Tambahkan ke Part 19 satu tabel pendek: aturan, ambang berangka dengan dasar, tindakan (ulang/eksklusi),
  batas pengulangan, dan kriteria berhenti. Sebutkan aturan pergeseran kapasitas (mis. C_SLO B2 vs *ladder* dalam ±x%,
  dengan x dari derau *ladder* ulang) dan apa yang terjadi bila dilanggar. Bawa kembali pemeriksaan sebaran beban per *pod*.
- **Gerbang.** 2, 5.

#### M-7 — Nilai warisan K1 berlabel kontinuitas yang menentukan efek (*request*/*limit* 250m/500m)

- **Lokasi.** `:506-507` (catatan sensitivitas wajib, bukan desain); Part 17 R16 (`:478`, B-konv); `:333-335` (premis H1
  = 80% × 250m); `:382` (D1-a < 200m).
- **Masalah.** *Request* 250m ditetapkan 13 April 2026 agar target 70% H1 tidak memicu pada 70m di *auth*, lalu disalin ke
  *shipping* (Part 17 §17.23.2 `:909-910`; Part 11 §11.2 C). Ia menentukan titik pemicu H1 (200m), ambang D1-a, dan CPU(C)/
  *request* (premis Hipotesis 1). Part 19 sendiri menilai sensitivitasnya tinggi (`:506-507`), tetapi labelnya B-konv
  (kontinuitas) dan tidak ada faktor atau cek sensitivitas di desain. Alasan "kontinuitas" tidak berlaku untuk nilai
  yang oleh analisis akar K1 sendiri dinilai sebagai "jejak riwayat, bukan desain" (Part 17 `:924-925`).
- **Bukti.** [F] baris-baris di atas; [H] H1 memicu pada CPU > 1,1 × 0,8 × *request*; ubah *request* 250m → 500m dan
  ambang H1 menjadi 440m.
- **Perbaikan.** Pilih satu: (a) nilai diturunkan dari aturan (mis. *request* = CPU terukur pada beban yang dipilih,
  dengan basis), (b) dijadikan faktor sensitivitas di blok pilot/model D1-b (dua level), atau (c) klaim Hipotesis 1 ditulis
  bersyarat pada *request* = 250m dan nilai itu dilabel DEC (bukan B-konv) dengan alasan "tidak ada".
- **Gerbang.** 2.

#### M-8 — Cek pra-pembekuan yang mengukur kontras tesis

- **Lokasi.** `:362-365` (uji langkah HPA-*adapter* vs KEDA, ≥ 8–10 ulangan per jalur; "dilaporkan sebagai estimasi HL
  dengan interval"); `:289-292` (urutan: *ladder* singkat "datanya bukan data tesis"); `:705-706` dan `:713` (efek mesin
  diestimasi lagi di kampanye).
- **Masalah.** Protokol mengizinkan cek *cloud* pendek sebelum gerbang lain **hanya** untuk memverifikasi konstruk atau
  parameter gerbang 1–2; outputnya "bukti untuk register, bukan data tesis". Uji langkah (e) mengukur selisih waktu
  kenaikan replika H3 vs K1 (efek mesin) secara langsung dan dilaporkan sebagai estimasi; kampanye lalu mengulang efek
  yang sama sebagai bagian Hipotesis 2. Dua keadaan: bila dilaporkan, itu data tesis tanpa pra-registrasi; bila
  tidak, `:362` salah.
- **Bukti.** [F] baris-baris di atas; protokol (bagian "Enforcement", paragraf cek pendek).
- **Perbaikan.** Tulis status uji (e): "eksploratori, bertanggal, tidak masuk analisis konfirmatori; hasilnya tidak
  mengubah desain kecuali menutup [BD] konstruk". Atau ubah tujuan uji (e) menjadi cek konstruk saja (apakah jalur beda
  secara mekanis) tanpa estimasi besaran.
- **Gerbang.** 1, 5.

#### M-9 — Heterogenitas perangkat keras antar-sesi dan penggunaan *ladder* satu sesi untuk sesi lain

- **Lokasi.** `:180-190`; `:455` (blok diacak antar-sesi); `:277-295` (*ladder* sebagai sumber angka).
- **Masalah.** Seri Dasv5 memuat dua generasi CPU [F]. `sut` adalah satu VM; tiap sesi (AKS dihentikan/dijalankan)
  menghasilkan VM baru, mungkin generasi lain. Angka C_SLO, r, W, L\*, dan N diukur pada satu sesi *ladder* dan dipakai di
  semua sesi blok. Blok yang utuh dalam satu sesi memang meniadakan efek sesi pada kontras berpasangan, tetapi tidak pada
  **kebenaran angka desain** di sesi lain: di K1 lutut kapasitas *auth* bergeser 10 → 8 req/s antar-kalibrasi
  (`:218-219`) dan konfigurasi *autoscaled* cenderung lebih buruk di sesi 1 (uji tanda p = 0,064 dan 0,053;
  `13-bab4-bab5-brief.md:428-429`), dengan penyebab yang tidak diuji (`13-bab4-bab5-brief.md:472-476`).
- **Bukti.** [F] di atas; Dasv5 https://learn.microsoft.com/en-us/azure/virtual-machines/sizes/general-purpose/dasv5-series
  (dicek 2026-10-19).
- **Perbaikan.** Tambahkan ke daftar versi per *run* model CPU dan jumlah *thread* per inti (`/proc/cpuinfo`) per *node*;
  hentikan sesi/ulangi *ladder* ringkas (C_SLO satu langkah) bila model CPU berbeda dari sesi *ladder*; tetapkan aturan
  pergeseran kapasitas B2 (M-6) berdasarkan itu.
- **Gerbang.** 2, 7.

#### M-10 — `infra` dipakai bersama oleh jalur permintaan layanan uji dan monitoring

- **Lokasi.** `:512-525`.
- **Masalah.** Argumen untuk `load` terpisah (`:523-525`: "isolasi oleh desain lebih kuat daripada 'diukur dan kecil'")
  tidak diterapkan ke `auth-db` dan `carrier-mock`, yang oleh dokumen sendiri adalah "SUT dalam arti fungsi" (`:521-522`),
  tetapi berbagi `infra` dengan Prometheus (ekspor `query_range` per *run*, `:646`), Grafana, *adapter*, KEDA, dan
  *metrics-server*. Penempatan hanya dicatat, tidak dipaku (`:510`). Sebagian beban di `infra` (ekspor, *adapter*) berubah
  menurut konfigurasi (H2p/H3 memakai *adapter*, H1/H2 tidak).
- **Bukti.** [F] di atas; Microsoft Learn *Use system node pools* menyarankan *pool* sistem khusus ber-*taint*
  `CriticalAddonsOnly=true:NoSchedule` agar *pod* aplikasi tidak dijadwalkan di sana (dicek 2026-10-19). Rancangan Part 19
  sengaja menaruh `auth-db` dan `carrier-mock` di *pool* sistem karena minimum 2 *node* D4as_v5 sudah ada; itu sah, tetapi
  bukan isolasi.
- **Perbaikan.** Pisahkan `auth-db` dan `carrier-mock` ke *pool* terpisah (mis. `deps`, ber-*taint*), atau paku penempatan
  dan catat CPU/*throttling* mereka per *run* sebagai kovariat dengan batas (DQ).
- **Gerbang.** 2, 7.

#### M-11 — Kontradiksi aturan K antara Part 19 dan Part 17; spesifikasi *bulkhead* hanya di Part 17

- **Lokasi.** `:275` ("Batas *in-flight* K: aturan K1, C × p99(C)") vs Part 17 R25 (`:487`: K = W + C_SLO × (SLO − T_svc)); `:406-429` (W, C); `:855-856` (Part 17 §17.12 "dipakai ulang").
- **Masalah.** Part 19 tidak mengulang bahwa *bulkhead* adalah semafor yang membuat permintaan menunggu di dalam *pod*
  sampai K (Part 17 `:270-272`), dan bahwa K ≥ W. Untuk *shipping* baru, K = C × p99(C) dan K = W + C_SLO × (SLO −
  T_svc) memberikan angka berbeda, dan dua-duanya bergantung pada p99 yang dipengaruhi antrean semafor. Ini mengubah c_tolak,
  C_SLO, dan jumlah permintaan yang ditolak (keluaran primer).
- **Bukti.** [F] di atas; [F] kode `admission_control.py`: batas *in-flight* adalah penolakan 503 seketika
  (`backend/services/shipping-rate-service/internal/middleware/admission_control.py:68-71`), bukan antrean; semafor yang
  menunggu (Part 17) harus ditambahkan sebagai mekanisme baru di samping batas ini.
- **Perbaikan.** Satu aturan K, ditulis di Part 19 bersama semantik *bulkhead* (menunggu vs menolak, posisi di *middleware*,
  apakah penolakan dihitung di `http_requests_shed_total`). Posisi menentukan c_tolak (K1: penolakan di lapisan dalam
  menghabiskan seluruh *limit* CPU pada ±80 req/s; di lapisan terluar ±2–3 ms, Part 17 `:116-119`).
- **Gerbang.** 1, 3.

#### M-12 — δ_min berlabel B-rumus padahal 15 s adalah pilihan; margin non-inferioritas bergantung padanya

- **Lokasi.** `:477-483`, `:691`.
- **Masalah.** Turunan matematis (1 − 1/r) × 15 / 420 benar [H], tetapi angka 15 s (satu periode *sync* HPA) adalah
  pilihan tentang apa yang dianggap perbedaan bermakna, bukan hasil pengukuran. Alternatif "angka tetap atau relatif"
  ditolak karena "tanpa dasar", tetapi 15 s juga tanpa dasar selain granularitas *controller*. Label cocok: B-konv/DEC dengan
  sensitivitas (7,5 s, 30 s).
- **Perbaikan.** Ubah label, sebutkan alternatif, dan sertakan dalam laporan b dan P22 daya pada ½ × dan 2 × δ_min.
- **Gerbang.** 2, 5.

### 2.3 Minor

- **m-1.** Aturan `CARRIER_DELAY_SCALE` (`:410-412`) menyamakan p95 bawaan *shipping* dengan p95 bawaan *auth* **pada λ0**,
  tetapi ilustrasinya (653 / 917 → ±0,7) memakai p95 *auth* pada 6 req/s, bukan di λ0. [F] p95 *auth* pada 2 req/s
  (jendela pemanasan K1, n = 10.000): 514 ms; *shipping* pada 10 req/s: 916 ms (Lampiran A.7). Skala menurut aturan
  ≈ 514 / 916 = 0,56, bukan 0,7, sehingga W lebih kecil (mis. C = 23, T̄ ≈ 0,4 s → W ≈ 9). Dasar menyamakan sela
  tersisa B-konv; p95 *auth* sebagian besar adalah ekor *login bcrypt* (p50 6 ms), jadi menyamakan dengan ekor itu
  tidak punya alasan mekanisme.
- **m-2.** Urutan ketergantungan melingkar: W = bulat(C_target × T̄_svc) memakai T̄_svc "pada λ0" (`:415`), λ0 = 0,2 × C_SLO
  (`:232`), C_SLO diukur dengan W final (`:425-427`). Pengaruh numerik kecil (T_svc tidak bergantung beban), tetapi aturan
  harus menyebut iterasi atau memakai T̄_svc pada laju tetap.
- **m-3.** SD yang masuk c_D1 (`:382`) tidak didefinisikan populasinya: SD bacaan CPU 60 s dalam satu langkah *ladder*
  (berautokorelasi) atau antar-ulangan *ladder*? Yang relevan bagi HPA adalah sebaran bacaan pada saat acak antar-*run*.
- **m-4.** Biaya menolak c_tolak (`:337-339`) diperkirakan dari CPU yang sudah di *limit* (rasio *throttling* ≈ 1,0);
  CPU yang tersaturasi memberi batas atas, bukan estimasi. Tulis sebagai batas dan ukur pada langkah di bawah *limit*.
- **m-5.** Replika-detik dan CPU-detik hanya dihitung di jendela beban dengan ekor 180 s < 300 s (`:604-606`); RQ3 (biaya
  vs mutu) dan klaim "penghematan terhadap B2" harus ditulis "selama jendela beban" dan tidak mencakup kelebihan
  replika setelah beban (konfigurasi laju dengan penghitung kedatangan mungkin menyalakan lebih banyak *pod*).
- **m-6.** Dua uji superioritas *shipping* (H3 > H1, K1 > H1) berkorelasi tinggi (H3 ≈ K1 sengaja); daya gabungan
  *intersection-union* ≈ daya uji yang lebih lemah, bukan hasil kali (`:473` mengatakan hasil kali). Jangan dipakai
  sebagai alasan P22.
- **m-7.** DaemonSet `sut` (kube-proxy, *cloud-node-manager*, *node-exporter*) disebut; pasang juga promtail/Loki dari
  `infrastructure/kubernetes/monitoring/` (promtail.yaml, loki.yaml) bila dipasang: catat atau larang di `sut` (DQ4).
- **m-8.** Tidak ada pemeriksaan sisa antar-*run* yang berurutan (urutan diacak, jadi tidak bias sistematis; tetapi
  tidak ada kovariat "konfigurasi sebelumnya" atau uji kehadiran efek berurutan). Tambahkan sebagai pemeriksaan
  eksploratori di analisis.
- **m-9.** Perkiraan waktu blok ±2,9 jam *(est.)* (`:47`, `:454`) tidak cocok dengan 7 × 17,5–18,5 menit = 2,0–2,2 jam
  (`:590`). Bukan faktor skor; perbaiki agar konsisten karena dipakai untuk argumen jarak antar-*run* berpasangan.
- **m-10.** Kutipan ICH E9 untuk α/2 diakui dari sumber sekunder (`:809-810`); verifikasi atau ganti dengan Hollander &
  Wolfe/Lakens untuk NI.

## 3. Tabel nilai/aturan BB atau berbasis lemah

| # | Butir | Lokasi | Label sekarang | Kenapa kurang | Cara memperoleh dasar |
|---|---|---|---|---|---|
| 1 | *Request*/*limit* CPU 250m/500m | `:506-507`, Part 17 R16 | B-konv (kontinuitas) | Dasar K1 *ad hoc* (13 Apr, untuk *auth*; disalin ke *shipping*; Part 17 `:909-910`), menentukan titik pemicu H1 dan premis Hipotesis 1 | Faktor sensitivitas dua level, atau aturan penurunan, atau DEC dengan klaim bersyarat (M-7) |
| 2 | "Shipping dibatasi slot" sebagai konstruk | `:94`, `:862-864` | B / B-konv | Sumber praktik [BD]; rancangan memastikan CPU(C) < target | BB sampai sumber dibaca; klaim eksternal bersyarat (M-1) |
| 3 | H2 → H2p sebagai "jalur ukur" saja | `:55`, `:96` | B (alasan) | Perlakuan *pod* baru berbeda antara Resource dan Pods (kode `replica_calculator.go`) | Kutip kode pada tag K8s yang dipakai; tulis paket A + K (M-2) |
| 4 | δ_min = 15 s | `:477-483` | B-rumus | 15 s adalah pilihan SESOI, bukan pengukuran | B-konv/DEC + sensitivitas ½× dan 2× (M-12) |
| 5 | Cadangan 20% pada r = 0,8 × λ_runtuh | `:217-219` | B-rumus | Satu kejadian (lutut *auth* K1 10 → 8) | B-konv; uji pergeseran antar-sesi di pilot (M-9) |
| 6 | λ0 = 0,2 × C_SLO | `:232-251` | B-konv | Rasio K1 diakui *ad hoc* (`:236-239`) | Syarat keras sudah B-rumus; sebutkan bahwa nilai 0,2 hanya batas atas yang cukup, dan ukur derau CPU di *ladder* |
| 7 | b ≤ 10 di D1-b | `:402` | "keputusan jadwal pemilik" | Bukan dasar statistik | Tetapkan dari daya (K-2) |
| 8 | Jumlah blok pilot = 2 per strata | `:441` | tanpa dasar | Menentukan derajat kebebasan σ (K-2) | Turunkan dari kebutuhan σ terpool (K-2) |
| 9 | Ambang rasio 1,5 uji naik *limit* | `:344-349` | B-konv | "Titik tengah" 1,0–2,0; belum diperiksa terhadap batas K = 22 *in-flight* dan satu proses uvicorn | Tambahkan: uji pada K tetap dan laporkan rasio plato tanpa *shedding* |
| 10 | c_D1 = rata-rata + 2 SD | `:382` | B-konv | Populasi SD tak terdefinisi (m-3) | Definisikan; gunakan interval prediksi |
| 11 | Skala `CARRIER_DELAY_SCALE` | `:410-412` | B-konv | Titik ukur tidak cocok dengan ilustrasi (m-1) | Ukur di λ0; atau jangkar lain (mis. p95 pada 0,5 × SLO) |
| 12 | K untuk *shipping* baru | `:275` vs Part 17 R25 | B-rumus | Dua aturan berbeda (M-11) | Satu aturan dan satu semantik *bulkhead* |
| 13 | Aturan mutu data/pengulangan/berhenti | `:186`, `:635` | "pra-registrasi" tanpa isi | Ambang BB di Part 17 (x, y, z) | Tabel aturan dengan ambang berdasar (M-6) |
| 14 | Pergeseran kapasitas B2 | `:455` | tanpa kriteria | Tidak ada tindakan | Kriteria berangka dari derau *ladder* ulang (M-6, M-9) |
| 15 | Aturan keputusan Hipotesis 2 (syarat 2) | `:710-714` | "usulan" | Tidak operasional (M-4) | Kontras tunggal dan interval |
| 16 | Aturan adapter CPU untuk H2p | `:372-376` | BB (jujur) | OOM pada AKS (M-2) | Uji di klaster sebenarnya dengan *seriesQuery* terbatas |
| 17 | Level f untuk sensitivitas | `:151-161` | B-konv, SENS-f bersyarat | Aturan b_SENS gagal secara struktural pada SD K1 (K-2) | Pooled σ atau tetapkan SENS-f sebagai prediksi model saja |

Butir yang labelnya **sudah jujur** dan tidak perlu diubah: f = 0,8 (B-konv, `:147-150`), SLO 1.000 ms (B-konv, `:253-257`),
M = 100 (B-konv, `:173-177`), P8/P16 (B-konv), dan tanda BB/[BD] pada 19.3.5 (g), 19.3.9 (EKS/GKE).

## 4. Kesalahan K1 yang berpotensi terulang

| # | Kesalahan K1 (sumber) | Tempat di Part 19 | Bukti | Perbaikan |
|---|---|---|---|---|
| 1 | Pemicu tidak setara (H2 50% ≈ 0,34 C vs ambang 30–62,5% C; Part 17 `:897`) | 19.3.1 menyamakan di L\* untuk N = 1 | K-1: CPU/kapasitas per *pod* berubah dengan N | Cek pemicu pada N = 1…N puncak (K-1) |
| 2 | Parameter dari kalibrasi lokal dibawa lintas rezim ("jejak riwayat"; Part 17 `:916-925`) | λ0 (0,2), *request*/*limit*, RESET/STABILIZE, 720 s, *watcher* 5 s berlabel B-konv kontinuitas | `:236-239`, `:626-636`, `:506-507` | Tabel 3 (#1, #6); tandai yang menentukan efek sebagai DEC atau faktor |
| 3 | Aturan/keluarga uji dipilih setelah data (Part 11 §11.6; 13 `:411-420`) | P8/P16 dibekukan sebelum data ✔; tetapi aturan Hipotesis 2 syarat 2, mutu data, dan P22 tidak lengkap | M-4, M-6, K-2 | Lengkapi sebelum gerbang 5 |
| 4 | Gerbang tanpa jalan mundur yang kredibel, lalu dilonggarkan (G6 v1 → v2, `11` `:131-132`; Part 17 `:937-939`) | D1 punya jalur mundur ✔; mutu data/B2 shift tanpa kriteria | M-6 | Tabel aturan mutu data dengan ambang |
| 5 | Sinyal laju buta saat *pod* runtuh; penghitung di proses yang sama (K1 pilot v1) | λp ≤ 0,8 × λ_runtuh ✔; penghitung tetap di proses yang sama | `:318-320`; *adapter* H2p memakai seri baru | Uji *adapter* di klaster sebenarnya (M-2) |
| 6 | Replika baru menumpuk di *node* k6; tanpa *taint* (`:510-511`; 13 `:472-474`) | *pool* `sut`/`load`/`infra` ✔ | `analysis/part12/runs.csv`: 268 dari 268 (sesi 1), 288 dari 396 (sesi 2) ✔ (dihitung ulang) | Tambah: kepadatan `sut` (K-1), `infra` bersama (M-10) |
| 7 | `:latest` + `Always`; versi tak tercatat (`:539-540`; `13` `:699`) | *digest* + `IfNotPresent` + *pre-pull* ✔ | `infrastructure/kubernetes/shipping/deployment.yaml:` *imagePullPolicy: Always* | Verifikasi *manifest* baru; catat model CPU (M-9) |
| 8 | Pilot hanya *spike*, 2 repetisi, tanpa H1 (Part 17 `:885`) | Pilot 56 *run* penuh ✔ | `:441-443` | n = 2 per sel menentukan σ (K-2) |
| 9 | O1 *bin* bug; O3 = O2; keluaran redundan | Fraksi buruk kontinu ✔, catatan redundansi ✔ | `:487-500` | Model D1-b memakai kurva keras (M-3) |
| 10 | SLO diputuskan setelah data (Part 20 T9) | SLO 1.000 ms dibekukan sebelum *ladder* ✔ | `:252-275` | — |
| 11 | maxReplicas 5 mengikat | M = 100 ✔ | `:173-196` | Cek `ScalingLimited` salah (M-5) |
| 12 | "Mesin" (H3 → K1): hasil nyaris pasti dari dokumentasi | Diturunkan menjadi verifikasi ✔ | `:705-706` | Uji (e) tidak boleh jadi data tesis (M-8) |
| 13 | Premis jenis layanan runtuh (*shipping* CPU-bound) | D1 + uji naik *limit* + kontrol negatif ✔ | `:333-357` | AK-2 terbuka; sumber BD (M-1) |
| 14 | Efek sesi pada konfigurasi *autoscaled* (p = 0,053–0,064) | Blok utuh per sesi ✔ | `13-bab4-bab5-brief.md:428-429` | Heterogenitas CPU Dasv5 (M-9) |
| 15 | Asumsi platform tak diverifikasi (*metrics-server* "15 s") | 19.3.9 memeriksa dokumentasi ✔ | FAQ 60 s [F] | Tutup [BD] *Pods* dengan kode (M-2) |
| 16 | Ekor/*scale-down* tidak diamati | Diputuskan tidak dibandingkan, dicek di pilot ✔ | `:596-610` | RQ3 ditulis "selama jendela beban" (m-5) |

## 5. Hal yang sudah benar (jangan diubah tanpa alasan)

Semua angka K1 di bawah ini saya hitung ulang dari data repo dan cocok dengan yang tertulis di Part 19.

- Rantai kontras satu perubahan per langkah (19.0), dan penamaan "jalur ukur" / "jenis sinyal" yang tidak mengklaim "murni".
- Urutan aturan: SLO dibekukan lebih dulu (`:203-206`); ketergantungan C_SLO pada SLO dicatat dengan data (`ladder.json`: *auth*
  6 req/s p95 653 ms; 8 req/s p95 1.225 ms; 10 req/s *error* 3,9% ✔).
- Lantai B2 *auth*: 3,0% (*gradual*) dan 4,1% (*spike*) pada 1.000 ms ✔ (Lampiran A.1: rata-rata 0,0297 dan 0,0410).
- Penumpukan replika di *node* k6: 268/268 (sesi 1), 288/396 (sesi 2) ✔; durasi *run* median 1.206,5 s (1.166–1.299) ✔; waktu
  kenaikan pertama *shipping spike*: H3 19,7 s vs K1 35,0 s ✔ (Lampiran A.5).
- Angka daya di 19.3.7 mereproduksi dalam simulasi saya: *signed-rank* / Mann–Whitney pada efek 0,03, σ 0,03, ρ = 0,11:
  0,39 / 0,45 (b = 8), 0,53 / 0,51 (b = 10); ρ = 0,51: 0,61 / 0,42 (b = 8), 0,79 / 0,53 (b = 10) (dokumen: 0,37/0,44,
  0,52/0,51, 0,60/0,43, 0,78/0,51) ✔.
- Turunan δ_min *spike* = (1 − 1/r) × 15 / 420 benar secara aritmetika ✔.
- Dokumentasi: KEDA 2.17 `maxReplicaCount` bawaan 100, `useCachedMetrics` bawaan `false`, `pollingInterval`/`cooldownPeriod`
  tidak berlaku untuk 1 → N (https://keda.sh/docs/2.17/reference/scaledobject-spec/) ✔; FAQ *metrics-server* "Default 60
  seconds ... not recommending setting values below 15s" ✔; AKS *pool* sistem ≥ 2 *node* dan VM ≥ 4 vCPU/4 GB, B-series tidak
  didukung ✔ (Microsoft Learn *Use system node pools*).
- D1 sebagai aturan bersyarat dengan jalan mundur; uji naik *limit* dengan kontrol negatif; pemisahan *pool* `load`.
- Fraksi permintaan buruk sebagai satu keluaran primer, dengan catatan redundansi, komposisi, dan lantai.
- Hasil negatif diterima: "r tidak dinaikkan demi efek" (`:229-231`), dan klaim lintas layanan ditulis per layanan (19.4.5).
- Label jujur untuk f, SLO, M, dan banyak [BD]; penolakan terbuka atas alternatif beserta alasan.

## 6. Pertanyaan yang kemungkinan diajukan penguji

1. "Mengapa *request* 250m? Kalau 500m, apakah Hipotesis 1 masih berlaku?" (M-7)
2. "Apakah layanan yang dibatasi slot itu ada di dunia nyata, atau Anda membuatnya supaya HPA CPU kalah?" (M-1)
3. "Mengapa 'berbasis CPU' diwakili H1 saja? Bukankah H2 yang dikalibrasi lebih adil untuk CPU?" (M-1, P13)
4. "Bagaimana Anda tahu pemicu H2 dan H3 setara ketika *pod* sudah dua atau tiga?" (K-1)
5. "Berapa SD yang Anda pakai untuk jumlah blok, dan dari berapa pengamatan?" (K-2)
6. "Jika non-inferioritas *auth* jatuh menjadi estimasi, apa tersisa dari 'CPU tetap kompetitif'?" (K-2)
7. "Mengapa pola utama Hipotesis 1 *gradual* tetapi Hipotesis 2 *spike*? Apakah itu dipilih karena di situ efeknya besar?" (19.4.1, 19.4.2; dibela dengan mekanisme, bukan data K1)
8. "Dari mana 15 detik dalam δ_min?" (M-12)
9. "Mengapa satu *node* 16 vCPU? Apakah *pod* saling mengganggu ketika jumlahnya bertambah?" (K-1)
10. "Apa yang terjadi bila CPU Dasv5 di sesi 3 berbeda dari sesi *ladder*?" (M-9)
11. "Aturan apa yang menyatakan sebuah *run* dibuang atau diulang?" (M-6)
12. "Kalau uji langkah KEDA vs *adapter* Anda jalankan sebelum pembekuan, bukankah itu data hipotesis?" (M-8)

## 7. Fase 2 — cek silang dengan tinjauan terdahulu

Dibuka setelah bagian 1–6 dan Lampiran A.1–A.7 (dan A.9 dokumentasi) tertulis; A.8 ditambahkan di fase 2: `17-review-redteam-ringan-v0.md` (Part 17, 2026-10-18),
`17-review-redteam-varian-seimbang.md` (2026-10-15), `14-review-redteam-v0.md` (Part 14, 2026-10-11),
`15-review-redteam-perbaikan-tanpa-kampanye.md` (2026-10-15), serta judul-judul `13-review-redteam-thesis-1.7.md` dan
`15-review-redteam-thesis-2.2.md` (keduanya meninjau naskah, bukan desain Part 19; tidak ada butir desain baru di sana
selain yang sudah ada di tabel 4). Teks fase 1 di atas tidak diubah kecuali dua koreksi ketelitian yang tercatat di 7.5.

### 7.1 Pemetaan temuan fase 1 terhadap tinjauan terdahulu

| Temuan fase 1 | Sudah ada sebelumnya? | Yang baru dari fase 1 / catatan |
|---|---|---|
| K-1 (pemicu dan kurva CPU hanya 1 *pod*; kepadatan di satu *node*) | **Sebagian.** Part 14 F2 (kapasitas N·C tidak linear; usulan *ladder* N = 1…4); varian seimbang Q5 dan S7 (kepadatan *pod* di `sut` D8 tunggal "bisa memperburuk ketidaklinearan", *ladder* N *pod* harus di tata letak akhir); Part 17 gerbang 4 (*ladder* 1–4 *pod*) | Part 19 **tidak membawa** *ladder* N-*pod* itu. Baru: kurva CPU(laju) *shipping* tidak sama pada N = 1 dan N = 5 (+12–27%), dan akibatnya pada kesetaraan pemicu (bukan hanya pada C_SLO) |
| K-2 (σ pilot dari n = 2) | **Ya.** Part 14 F11.1 ("dua sesi K1 = 1 df dan dua blok pilot = 1 df; tidak ada dasar estimasi varians antar-blok yang andal"); varian seimbang Q (tuas 6) dan S5 ("2 blok pilot = 1 derajat bebas, jadi bukan untuk estimasi varians, sumbernya data K1") | Part 19 melakukan kebalikan dari saran itu (b dan P22 dari σ pilot). Baru: aturan maksimum atas sel (×1,7), SD K1 yang heteroskedastik, dan asimetri P22 |
| M-1 (slot direkayasa, P13) | **Ya.** Part 14 F6; Part 17 M-3 dan §8.3(4) ("peragaan rumus"); AK-2 | Baru: label B/B-konv vs sumber [BD] di Part 19 sendiri; P13 beralasan hasil |
| M-2 (H2 → H2p, *adapter*) | **Sebagian.** Part 17 M-4 butir (3) dan §8.2 O2 syarat (3); `15-review-…-tanpa-kampanye` jebakan (3) ("tidak otomatis di jalur *adapter* [F]") | Part 19 masih menulis [BD]. Baru: dokumentasi HPA ("When scaling on CPU, if any pod has yet to become ready...") dan kode menutupnya; riwayat OOM *adapter* pada seri `container_*`. **Tidak sepakat** dengan §8.2 O2 syarat (3) ("aturan *pod*-belum-siap kemungkinan berlaku" untuk metrik kustom): kode dan dokumentasi menunjukkan sebaliknya |
| M-3 (validasi D1-b) | **Sebagian.** Part 17 Lampiran A.5 menyebut modelnya "model fluida kasar (urutan besaran, bukan prediksi)" yang mengabaikan lutut latensi, beban tak rata, dan *warm-up* CPU *pod* baru | Part 19 `:387-405` menaikkan model yang sama menjadi alat putusan D1-b. Baru: lebar interval K1 vs δ_min; kurva *auth* mulus |
| M-4 (aturan Hipotesis 2) | **Sebagian.** Part 17 M-6 (IUT dan keluarga) | Baru: syarat kedua tidak operasional |
| M-5 (`ScalingLimited`) | Tidak | Baru |
| M-6 (aturan mutu data) | **Sebagian.** Part 14 F8 (DQ5 bergantung perlakuan); Part 11 §11.6 #4 (G6) | Baru: Part 19 tidak memuat aturannya sama sekali |
| M-7 (*request*/*limit* 250m/500m) | **Ya.** Part 17 M-9 ("R16 ... hanya kontinuitas, padahal menentukan CPU(C)/*request* ... perlakukan sebagai BB bersensitivitas atau syarat klaim") | Belum ditindaklanjuti di Part 19 (masih B-konv) |
| M-8 (uji (e) sebagai data) | **Sebagian.** Part 14 F7 (cek *cloud* pra-gerbang; pembaruan protokol dikonfirmasi penulis) | Baru: uji (e) spesifik mengukur kontras tesis |
| M-9 (Dasv5 heterogen) | **Sebagian.** Part 14 M4 ("pin platform CPU atau catat `lscpu` per *node*") dan M14 ("VM baru vs VM persisten per blok: tetapkan kebijakan") | Baru: dokumentasi Dasv5 yang menyebut dua generasi; efek sesi K1 |
| M-10 (`infra` bersama) | Tidak persis. Varian seimbang W1 meninjau ukuran `infra` | Baru: argumen isolasi tidak diterapkan ke `auth-db`/`carrier-mock` |
| M-11 (aturan K) | **Ya.** Part 14 F5 (K menggerakkan sinyal CPU; Little hanya memberi L = λW; label B salah) dan F2.4 (rantai sirkular) | Part 19 `:787-789` menolak SENS-K tanpa menjawab bahwa K ikut menentukan CPU pod kewalahan dan c_tolak |
| M-12 (δ_min = 15 s) | **Ya, sebagai usulan.** Part 17 §8.3(6) sendiri mengusulkan periode *sync* 15 s sebagai dasar margin | Saya menurunkan bobot: label B-konv/DEC, bukan B-rumus; arah usulan tinjauan itu diikuti dengan benar |

Tinjauan terdahulu yang **dipenuhi** Part 19 (tidak perlu dibuka lagi): c_tolak dan MC3(b) → aturan D1 (Part 17 K-1); kesetaraan
TOST dilepas (K-2); satu keluaran primer (Part 14 F9, Part 17 M-5 sebagian); *intersection-union* dan keluarga per hipotesis
(M-6); sebaran tak berpasangan untuk daya (M-7); *oscillating* dikeluarkan dengan pembanding (M-8); penghitung kedatangan
dan aturan pelaporan kegagalan *scrape* (m-7); `useCachedMetrics: false` (m-2); versi AKS ≥ 1.35 (m-1); DQ5 sebagai keluaran
(Part 14 F8).

### 7.2 Temuan tambahan dari fase 2 (terlewat di fase 1)

#### N-1 (Mayor) — Fase *tick* HPA terkunci terhadap onset beban; model D1-b memakai fase acak

- **Lokasi.** `:387-393` (model D1-b: CPU di-*refresh* tiap 60 s "dengan fase acak", *scrape* "berfase acak", 150–200 undian
  fase); `:477-483` (δ_min = satu periode *sync*, 15 s); `:362-365` (uji langkah (e)); tidak ada langkah di 19.3.10 yang
  mengacak fase relatif terhadap onset.
- **Masalah.** `15-review-redteam-perbaikan-tanpa-kampanye.md` §3 menulis: "88% pemicu pertama jatuh pada fase 3–6,5 s modulo 15 s;
  O4 terkuantisasi 15 s; lima repetisi bukan sampel fase yang independen; fase bisa bergeser di sesi baru." Prosedur *run* Part 19
  mempertahankan urutan K1 (objek HPA dibuat, tunggu tetap, Job k6, onset pada t = 120 s), jadi fase itu akan tetap terkunci.
  Akibatnya: (i) variasi antar-*run* pada skala 15 s adalah kuantisasi (waktu pemicu melompat antara dua *tick* yang
  berdekatan), bukan derau independen; (ii) δ_min = 15 s berada tepat pada skala kuantum itu, sehingga selisih sebesar δ_min
  tidak dapat dibedakan dari selisih fase konfigurasi yang objeknya dibuat pada saat yang sedikit berbeda (mis. HPA buatan KEDA
  muncul setelah *reconcile* KEDA; ini dugaan penyebab [P], belum diuji); (iii) model D1-b dan simulasi dayanya mengandaikan fase acak, jadi sebarannya tidak mewakili
  eksperimen.
- **Bukti.** [H] data K1 (Lampiran A.8): waktu kenaikan replika pertama dalam 80 sel-*run* (H1–K1, *spike* dan *gradual*, kedua
  layanan) mod 15 s mempunyai panjang resultan melingkar 0,886 dan 91% berada dalam pita 3,5 s; pada *shipping* *spike* nilainya
  19,4–19,9 s pada empat dari lima *run* H3 dan 34,8–36,5 s pada empat dari lima *run* K1: dua konfigurasi hanya berbeda pada
  peluang mendarat di *tick* pertama vs kedua. Itu persis selisih "tak terjelaskan" 19,7 vs 35,0 s yang disebut di `:362-365`
  (Tabel 4.11).
- **Perbaikan.** Acak penundaan onset per *run* dengan U(0, 15) s (dicatat; k6 `startTime` atau tunda Job) sehingga fase
  *tick* HPA dan *scrape* relatif terhadap onset menjadi acak; laporkan fase sebagai kovariat; model D1-b memakai fase yang diacak
  yang sama; uji (e) mengulang dengan fase acak. Alternatif: kunci fase dan hitung selisih konfigurasi terhadap fase tersebut
  (tidak dianjurkan, fase bergeser antar-sesi).
- **Gerbang.** 1 (konstruk "mesin"), 3 (*runner*), 4.

#### N-2 (Mayor) — Uji arah tidak mensyaratkan efek minimum, padahal δ_min didefinisikan untuk itu

- **Lokasi.** `:689-695` (Hipotesis 1 "didukung" bila kedua uji arah lolos pada α); `:710-711`; `:798` dan `:795-799`; δ_min di `:477-483`.
- **Masalah.** Hipotesis arah (H3 > H1, K1 > H1, H2 > H1, efek sinyal) dinyatakan didukung bila uji lolos pada level α, tanpa syarat
  |HL| ≥ δ_min. δ_min dipakai hanya untuk non-inferioritas *auth* dan untuk keputusan D1-b. Efek yang signifikan tetapi lebih kecil
  daripada satu periode *sync* akan disebut "mengungguli", sedangkan pada non-inferioritas margin yang sama menentukan "kompetitif".
  Part 14 F1.5 sudah menyebutnya ("efek yang signifikan tetapi lebih kecil dari δ akan dinyatakan 'didukung' di H1a dan 'setara' di
  H1b"); Part 17 menjaga syarat |HL| > 0,02 di simulasi dayanya (`17-review…:506`). Part 19 menghapus syarat itu tanpa menyebut alasannya.
- **Bukti.** [F] baris-baris di atas; [F] Part 14 review F1.5, Part 17 review A.4.
- **Perbaikan.** Tulis keputusan dua tingkat dan bekukan: (a) "ada efek" bila batas bawah interval HL 95% > 0; (b) "efek bermakna" bila
  HL ≥ δ_min dan (a); daya dihitung untuk (b) bila (b) yang menjadi klaim ("mengungguli").
- **Gerbang.** 5.

#### N-3 (Minor) — `--node-osdisk-type Ephemeral` pada seri Dasv5

- **Lokasi.** `05-architecture-and-tooling.md:194` (perintah pembuatan *node pool* K1); `:512-520` (tata letak *pool* baru, ukuran Dasv5).
- **Masalah.** Dokumentasi Dasv5 menyatakan "Ephemeral OS Disk: Not Supported" [F] (https://learn.microsoft.com/en-us/azure/virtual-machines/sizes/general-purpose/dasv5-series,
  dicek 2026-10-19; temuan sama di varian seimbang Q5). Bila perintah Part 05 dipakai untuk `sut`, `load`, `infra`, pembuatan gagal atau *flag* harus diubah, dan itu
  mengubah disk OS (kinerja I/O *node*) dibandingkan K1.
- **Perbaikan.** Cek perintah pembuatan *pool* di gerbang 7 dan catat jenis disk OS sebagai versi/konfigurasi per *run*.
- **Gerbang.** 7.

### 7.3 Pembaruan atas temuan fase 1

- **M-2.** Bukti tambahan dari dokumentasi resmi (bukan hanya kode): halaman HPA menulis bahwa pod yang belum siap dikesampingkan
  "**when scaling on CPU**" (https://kubernetes.io/docs/concepts/workloads/autoscaling/horizontal-pod-autoscale/, bagian *Pod readiness and
  autoscaling metrics*, dicek 2026-10-19), dan menyebut perlakuan terpisah untuk metrik eksternal/objek ("replica count is based on the number of Running
  and Ready Pods"); metrik kustom tipe *Pods* tidak dinyatakan. Jadi: perlakuan *pod* baru H2 vs H2p berbeda **menurut dokumentasi** untuk CPU,
  dan kode (`groupPods`) tidak menerapkannya pada *Pods*. Ini cukup untuk menutup [BD] pada tingkat "berbeda"; besarnya tetap diukur di kind.
- **M-11.** Ditambah dari Part 14 F5: K menggerakkan CPU *pod* kewalahan; Part 19 `:787-789` menolak SENS-K dengan alasan K "diturunkan dari aturan".
  Alasan itu tidak menjawab bahwa nilai K, bukan hanya turunannya, menentukan c_tolak dan CPU dalam keadaan kewalahan, yaitu penggerak
  utama Hipotesis 1. Minimal: laporkan c_tolak dan CPU pada dua nilai K di *ladder* langkah kelebihan beban (tanpa menambah *run* kampanye).
- **K-2.** Diperkuat: dua tinjauan terdahulu sudah menolak σ pilot dan mengusulkan σ dari data K1; Part 19 membalik arah itu. Perbaikan 1 pada K-2
  menjadi: gunakan SD K1 per sel sebagai prior (diperlakukan sebagai masukan konservatif untuk b) dan pilot hanya untuk gladi analisis dan
  pengecekan asumsi, atau naikkan jumlah blok pilot bila σ pilot memang ingin dipakai.
- **M-12.** Bobot diturunkan (lihat tabel 7.1): usulan 15 s berasal dari tinjauan terdahulu; yang tetap perlu adalah label dan sensitivitas.

### 7.4 Pertanyaan penguji tambahan

13. "Mengapa waktu mulai beban tidak diacak terhadap siklus 15 detik HPA? Apakah selisih 15 detik antara H3 dan KEDA hanya artefak fase?" (N-1)
14. "Apa arti 'mengungguli' bila efeknya lebih kecil daripada satu siklus HPA?" (N-2)
15. "Model fluida yang menentukan D1 adalah model kasar yang ditulis peninjau; seberapa jauh ia sudah divalidasi pada rezim *shipping* baru?" (M-3)

### 7.5 Perubahan skor dan koreksi ketelitian

| Dimensi | Fase 1 | Setelah fase 2 | Alasan |
|---|---|---|---|
| 1. Konstruk | 6 | 6 | M-2 diperkuat tetapi sudah di skor |
| 2. Validitas internal | 6 | **5** | Bukti baru: fase HPA terkunci (N-1; data K1 saya hitung ulang, 91% dalam pita 3,5 s) berarti variasi antar-*run* pada skala δ_min bukan derau acak dan tidak diacak oleh desain; bersama K-1 (kepadatan), M-9, M-10, dan M-5 lima butir internal terbuka |
| 3. Kesimpulan statistik | 5 | 5 | N-2 menambah celah aturan keputusan; tidak menurunkan karena dapat ditutup dengan aturan tertulis |
| 4. Dasar parameter | 6 | 6 | M-7 sudah dicatat sebelumnya oleh tinjauan Part 17 tetapi belum ditindaklanjuti; tidak mengubah skor |
| 5. Pengukuran | 6 | 6 | N-3 adalah butir gerbang 7 |
| 6. Pelajaran K1 | 6 | 6 | Beberapa butir (K-1, K-2, M-7) adalah peringatan terdahulu yang belum diserap Part 19; ditegaskan, bukan diturunkan |
| **Akhir** | **6** | **6** | Tidak berubah: semua kelemahan dapat ditutup sebelum pilot, dan struktur desain (rantai kontras, D1 bersyarat, blok kecil, isolasi, SLO dibekukan lebih dulu) lebih kuat daripada versi sebelumnya yang ditinjau (Part 17 v0: 4/10) |

Koreksi ketelitian atas teks fase 1 (satu-satunya perubahan pada bagian 1–6): tidak ada perubahan isi; seluruh angka dan bukti fase 1 dipertahankan. Dua klaim
yang saya periksa ulang dan tidak saya ubah: (a) angka K1 di Part 19 (C_SLO, lantai B2, penumpukan replika, durasi, waktu kenaikan) cocok dengan
data; (b) klaim dokumentasi Part 19 yang saya cek (KEDA, *metrics-server*, AKS) cocok.

**Hal yang sudah dikerjakan Part 19 dan tidak perlu dikerjakan ulang** (tambahan dari fase 2): prosedur *Deployment* baru + UID *pod* (Part 14 M13 sebagian), `useCachedMetrics: false`,
DQ5 sebagai keluaran (Part 14 F8), SLO dibekukan sebelum *ladder* (Part 14 F2.5), satu keluaran primer (Part 14 F9), dan *intersection-union* (Part 17 M-6).

**Belum dapat dinilai** (bukti yang dibutuhkan): (i) efek terkecil yang terbaca untuk Hipotesis 2 pada *shipping* — σ per sel dari pilot yang diperbaiki (K-2); (ii) apakah r akhir
cukup besar agar *autoscaler* melewati ≥ 3 *pod* — *ladder* kelebihan beban kedua layanan; (iii) besarnya c_tolak pada implementasi *bulkhead* final — kind dan *ladder*; (iv) apakah
`ScaleUpLimit` benar-benar muncul pada r terpilih — watcher di pilot; (v) apakah vCPU Dasv5 adalah *thread* SMT — `lscpu` di *node* `sut`.

## Lampiran A. Hitungan dan sumber (fase 1)

Skrip lokal (di *scratchpad* sesi, dijalankan dengan `uv run --quiet --with numpy --with scipy python -I`): `ladder_sum.py`,
`k1_badfrac.py`, `k1_ci.py`, `runs_chk.py`, `ladder_bad.py`, `power_chk.py`, `warm_p95.py`. Semua membaca `experiment-results-openloop/`
(`analysis/cache/*.npz`, `analysis/ladder.json`, `analysis/part12/runs.csv`, `*/*/*/rep*/k6-output.log`); jendela [120, 540) s
dari awal skenario k6, permintaan dihitung dari waktu mulai (seperti `scripts/pilot_openloop.py:336-339`); buruk = gagal
atau lebih lambat dari SLO.

**A.1 Fraksi permintaan buruk K1 (SLO 1.000 ms, jendela [120, 540) s), median [SD] dari 5 repetisi.**

| Layanan | Pola | B1 | B2 | H1 | H2 | H3 | K1 |
|---|---|---|---|---|---|---|---|
| *auth* | *gradual* | 0,674 [0,038] | 0,029 [0,002] | 0,068 [0,015] | 0,051 [0,013] | 0,046 [0,005] | 0,042 [0,004] |
| *auth* | *spike* | 0,840 [0,054] | 0,039 [0,004] | 0,257 [0,028] | 0,210 [0,028] | 0,143 [0,021] | 0,165 [0,024] |
| *shipping* | *gradual* | 0,706 [0,004] | 0,000 [0,001] | 0,057 [0,028] | 0,0003 [0,004] | 0,000 [0,002] | 0,0001 [0,001] |
| *shipping* | *spike* | 0,874 [0,035] | 0,000 [0,002] | 0,189 [0,021] | 0,160 [0,028] | 0,093 [0,014] | 0,115 [0,013] |

**A.2 Interval Hodges–Lehmann 95% (n = 5 vs 5; urutan ke-3 dan ke-23 dari 25 selisih) pada data A.1.**

| Layanan / pola | Kontras | HL | Interval | Lebar |
|---|---|---|---|---|
| *auth gradual* | H1 − H3 | +0,0255 | [+0,0133, +0,0513] | 0,038 |
| *auth gradual* | H2 − H3 | +0,0050 | [−0,0081, +0,0252] | 0,033 |
| *auth gradual* | K1 − H3 | −0,0042 | [−0,0117, +0,0037] | 0,015 |
| *auth spike* | H1 − H3 | +0,1018 | [+0,0562, +0,1421] | 0,086 |
| *auth spike* | H2 − H3 | +0,0585 | [+0,0123, +0,0875] | 0,075 |
| *auth spike* | K1 − H3 | +0,0143 | [−0,0278, +0,0429] | 0,071 |
| *shipping gradual* | H1 − H3 | +0,0570 | [+0,0108, +0,0741] | 0,063 |
| *shipping gradual* | H2 − H3 | +0,0002 | [−0,0036, +0,0074] | 0,011 |
| *shipping gradual* | K1 − H3 | 0,0000 | [−0,0038, +0,0026] | 0,006 |
| *shipping spike* | H1 − H3 | +0,0883 | [+0,0607, +0,1199] | 0,059 |
| *shipping spike* | H2 − H3 | +0,0590 | [+0,0311, +0,1050] | 0,074 |
| *shipping spike* | K1 − H3 | +0,0164 | [−0,0060, +0,0362] | 0,042 |

Catatan: pada data ini H1 − H3 *shipping gradual* = +0,057 muncul walaupun pada K1 ambang H3 (30% C) jauh lebih awal daripada H1,
yaitu ketidaksetaraan pemicu K1, bukan jenis sinyal.

**A.3 CPU per *pod* *shipping* pada laju per *pod* sama (K1, `ladder.json`).**

| Laju per *pod* | 1 *pod* | 5 *pod* (rata-rata; per *pod*) | Selisih |
|---|---|---|---|
| 10 req/s | 58,5m (median `base_cpu_m_per_pod`) | — | — |
| 24 | ≈155m (interpolasi 10 → 40) | 177m (180, 171, 169, 185, 178) | +14% |
| 32 | ≈211m (interpolasi) | 236m (236, 239, 239, 255, 211) | +12% |
| 40 | 266m | 337m (318, 372, 336, 351, 308) | +27% |
| 50 | 377m / 405m (dua *ladder*) | (jenuh) | derau 1-*pod* ±7% |

*Auth* (CPU per *pod*, rata-rata): 6 req/s: 257m vs 236m; 8 req/s: 314m vs 317m; 10 req/s: 411m vs 399m. Tidak ada efek jelas pada CPU;
efek ada pada p95 (653 vs 787 ms pada 6 req/s; 1.225 vs 1.765 ms pada 8 req/s).

**A.4 SD dari n = 2 (simulasi normal, 200.000 undian).** s/σ untuk n = 2 mengikuti √χ²₁: P(s/σ < 0,5) = 0,383; P(s/σ > 2) = 0,046;
P(0,5 ≤ s/σ ≤ 2) = 0,570. Maksimum atas 8 sel independen (σ sama): median 1,73σ; persentil 5–95%: 1,03–2,74σ. b ∝ σ², jadi
median b terlalu besar ×3,0. Dengan SD K1 terbesar *gradual* (0,0279, H1 *shipping*) dan rumus `:155`: b_SENS = 31 (δ = 0,014), 9 (δ = 0,0268).

**A.5 Pemeriksaan klaim K1 lain.** Durasi 180 *run*: min 1.166, median 1.206,5, maks 1.299 s. Waktu median kenaikan pertama
(`O4_first_up_s`, *spike*): *auth* H1 65,1, H2 65,0, H3 35,2, K1 35,5; *shipping* H1 65,1, H2 64,8, H3 19,7, K1 35,0; *pod* baru siap
17–18 s setelahnya. `base_cpu_m_per_pod` K1: *auth* 11–115m (median 71m) pada 2 req/s; *shipping* 14–88m (median 59m) pada 10 req/s.

**A.6 Fraksi buruk vs laju pada *ladder* 1-*pod* (SLO 1.000 ms, 90 s stabil per langkah).** *Auth*: 6 req/s 0,033; 8: 0,064; 10: 0,157; 12:
0,189; 16: 0,498; 30: 0,930. *Shipping* (dua *ladder*): 40–50 req/s: 0,000; 50 (ke-2): 0,049; 60: 0,854/0,667; 80: 0,953/0,828; 105:
1,000/0,913.

**A.7 p95 pada beban dasar (jendela t 20–120 s, hanya permintaan sukses, semua B2/H1/H2/H3/K1 *gradual* dan *spike*).**
*auth* 2 req/s: p50 6 ms, p95 514 ms, p99 530 ms (n = 10.000); *shipping* 10 req/s: p50 711 ms, p95 916 ms, p99 933 ms (n = 50.000).

**A.8 (ditambahkan di fase 2) Fase HPA terkunci ( `runs.csv`, kolom `O4_first_up_s`).** Waktu kenaikan replika pertama (detik) per sel, 5 repetisi:
*auth spike* H1 65,1/80,2/48,0/64,1/95,1; H2 65,2/65,0/64,2/79,4/49,9; H3 34,4/35,2/34,6/35,7/35,4; K1 35,5/36,8/35,5/27,9/35,6.
*shipping spike* H1 64,6/79,4/78,9/65,1/64,5; H2 79,5/48,8/64,8/64,9/49,0; H3 34,8/19,9/19,6/19,7/19,4; K1 35,0/36,0/34,8/19,5/36,5.
Nilai-nilai mengumpul pada kelipatan ±15 s. Mod 15 s atas 80 nilai (H1–K1, *spike* dan *gradual*, kedua layanan): panjang resultan
melingkar 0,886 (1,0 = terkunci penuh, 0 = seragam); 91% jatuh dalam satu pita lebar 3,5 s. Cocok dengan temuan 88% dalam pita 3–6,5 s di
`15-review-redteam-perbaikan-tanpa-kampanye.md` §3.

**A.9 Dokumentasi/kode yang diperiksa (2026-10-19).** Kubernetes `horizontal.go` dan `replica_calculator.go` (cabang master, via
alat pengambil; periksa ulang pada tag 1.35+); KEDA 2.17 *ScaledObject specification*; kubernetes-sigs/metrics-server `FAQ.md`; Microsoft
Learn *Use system node pools in AKS* dan *Dasv5 size series*.
