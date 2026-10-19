# Thesis Blueprint — Part 19: Eksperimen 2 "K1 diperbaiki" — Usulan v0.6.1

> Ditulis 2026-10-18 atas usulan pemilik: mengulang Kampanye 1 (K1) dengan perubahan sesedikit mungkin, sebagai
> alternatif yang lebih ringan dari Kampanye 2-ringan (Part 17). **v0.1** menerapkan temuan tinjauan *red team* atas Part 17
> yang juga berlaku di sini (pemetaan di 19.8). **v0.2** menambahkan konfigurasi H2p (CPU lewat Prometheus) sehingga
> efek CPU → laju terurai menjadi efek jalur ukur dan efek jenis sinyal. **v0.3** mencatat resolusi *metrics-server* per
> platform dan akibatnya bagi arti H2 (19.3.9). **v0.4** mencatat keputusan pemilik soal bentuk dan durasi *run*
> (*gradual* dan *spike* sama panjang seperti K1, ekor 180 s, replika-detik hanya di jendela beban; 19.3.10) dan aturan
> f = 0,8 (diputuskan pemilik, B-konv; 19.3.1), serta aturan SLO 1.000 ms, beban dasar λ0 = 0,2 × C_SLO, dan puncak r
> untuk kedua layanan (diputuskan pemilik; 19.3.3), dengan angka dari *ladder* baru, serta parameter aturan D1 (c_D1,
> model D1-b, ambang *auth*; 19.3.5). **v0.5** (2026-10-19) mencatat maxReplicas M = 100, tata letak *pool* (`sut`, `load`, `infra`), dan isi
> klaster (hanya layanan uji dan dependensinya; 19.3.2, 19.3.8), langkah per *run* (19.3.10), serta aturan rancangan *shipping* baru (T_svc, C, W;
> 19.3.5). **v0.6** (2026-10-19) menindaklanjuti semua temuan (Kritis, Mayor, dan Minor) tinjauan *red team*
> atas v0.5 (status di 19.11; aturan mutu data baru di 19.3.11); catatan
> perubahan di 19.10; **v0.6.1** (2026-10-19) memuat hasil pemeriksaan ulang menyeluruh. **Status: usulan v0.6.1 —
> belum dibekukan, belum ada *run*, belum ada biaya.** Protokol eksperimen (`~/.claude/CLAUDE.md`) berlaku penuh;
> catatan gerbang di 19.1. Varian mana yang dipakai (Part 17 atau bagian ini) adalah keputusan pembimbing dan pemilik.
> Anggaran bukan batasan desain (pemilik, 2026-10-18; Part 17 §17.16).
>
> **Label.** **B** = berbasis (sumber disebut); **B-konv** = konvensi bernama; **B-rumus** = aturan berbasis, angkanya
> dari pengukuran; **BB** = belum berbasis (cara memperolehnya ditulis); **DEC** = keputusan pemilik/pembimbing. **[F]**
> fakta dari berkas/data/dokumentasi; **[H]** hitungan; **[P]** pendapat; **[BD]** belum diverifikasi. "H1, H2, H2p, H3,
> K1" = **konfigurasi** (H2 dan H2p di sini berbeda isi dari H2 di K1); "Hipotesis 1–3" = hipotesis proposal; "hipotesis
> kalibrasi" = hipotesis tambahan (19.4.4).

## 19.0 Ringkasan

| Butir | K1 (6–9 Okt 2026) | Usulan v0.4 |
|---|---|---|
| Pola beban | *gradual*, *spike*, *oscillating* | *spike*, *gradual*; pola utama dipilih per hipotesis (19.4) |
| Bentuk dan durasi *run* | 720 s: pemanasan 120 s, beban 420 s, turun 180 s; *gradual* = *ramp* 300 s + tahan 120 s | sama dengan K1 untuk kedua pola (keputusan pemilik 2026-10-18; 19.3.10) |
| Jendela *scale-down* | 300 s (H1); 30 s (H2, H3, K1) | 300 s (bawaan) untuk semua; replika-detik hanya di jendela beban |
| Fraksi pemicu f | — (ambang dan target tidak dari satu titik) | 0,8 (diputuskan pemilik 2026-10-18, B-konv; 19.3.1) |
| Puncak λp | *auth* 30 req/s (3–3,75 × C), *shipping* 105 req/s (2,1 × C) | r × C_SLO, r = min(0,8 × λ_runtuh / C_SLO) antar-layanan dari *ladder* baru (B-rumus; 19.3.3) |
| Beban dasar λ0 | *auth* 2 req/s, *shipping* 10 req/s (dipilih *ad hoc*, ±0,2 × kapasitas sehat) | 0,2 × C_SLO untuk kedua layanan (B-konv; 19.3.3) |
| SLO | *auth* 1.500 ms, *shipping* 1.200 → 1.000 ms (aturan p95 B2 *closed-loop*, diputuskan setelah data) | 1.000 ms untuk kedua layanan, ditetapkan sebelum pengukuran (Nielsen 1993, B-konv; 19.3.3) |
| B1 | 1 *pod* | 1 *pod* |
| B2 | 5 *pod* | N terukur |
| maxReplicas M | 5 (mengikat untuk H3 dan K1) | 100 untuk semua konfigurasi (bawaan KEDA, B-konv); `sut` 1 × D16as_v5 ≥ 2 × replika tertinggi pilot (19.3.2) |
| Langkah per *run* | `RESET_WAIT` 120 s, `STABILIZE_WAIT` 90 s, `EXPORT_WAIT` 180 s, `:latest` + `Always`, *onset* pada jarak tetap dari pembuatan HPA | sama, kecuali `EXPORT_WAIT` 30 s, *pre-pull* dengan *digest* + `IfNotPresent`, dan penundaan acak U(0, 15) s sebelum Job k6 (19.3.10) |
| Isi klaster | seluruh aplikasi e-commerce, 1 replika per layanan | layanan uji + *auth-db* + *carrier-mock* saja (19.3.8) |
| *Pool node* | satu *pool* 3 × D4as_v5, tanpa *taint* | `sut` (*taint*, 1 × D16as_v5), `load` (*taint*, 1 × D2as_v5, k6), `deps` (*taint*, 1 × D4as_v5, *auth-db* + *carrier-mock*), `infra` (*pool* sistem, 2 × D4as_v5) (19.3.8) |
| *shipping-rate-service* | asinkron tanpa batas konkurensi; ternyata dibatasi CPU | dibatasi slot menunggu (*bulkhead* W slot, C terbesar yang lolos D1-a dan D1-b′, jeda *carrier* disetarakan dengan *auth*), **bersyarat** (aturan D1, 19.3.5) |
| Konfigurasi H1 | CPU 80% (bawaan) | tetap; mewakili "CPU sebagaimana lazim" untuk Hipotesis 1 |
| Konfigurasi H2 | CPU 50% | CPU lewat *metrics-server* dengan target dari titik pemicu yang sama dengan H3/K1 |
| Konfigurasi H2p | — | **baru:** CPU per *pod* lewat Prometheus dan *prometheus-adapter* (jalur yang sama dengan H3), titik pemicu sama |
| Konfigurasi H3, K1 | laju yang dilayani; ambang 5 / 15 (April) | laju kedatangan (dilayani + ditolak; diputuskan pemilik 2026-10-19, P3); ambang dari aturan yang sama |
| Keluaran primer | O1 (detik di atas SLO, *bin* 10 s) | fraksi permintaan buruk (diputuskan pemilik 2026-10-19, P7); O1 sekunder |
| Blok | satu repetisi = 36 *run* | satu layanan × satu pola × tujuh konfigurasi (±2,1 jam *(est.)*: 7 × ±18 menit, ditambah *run* ulang) |
| Hipotesis | 1–3 proposal; aturan keputusan ditulis setelah data | 1–2 proposal dengan operasionalisasi dan aturan keputusan sebelum data; Hipotesis 2 dengan dekomposisi jalur + sinyal; Hipotesis 3 DEC (usul: dilepas); hipotesis kalibrasi |

**Rantai kontras (satu perubahan per langkah).**

| Langkah | Yang berubah | Yang sama | Mengukur |
|---|---|---|---|
| H1 → H2 | target CPU (80% → terkalibrasi) | sinyal CPU, jalur *metrics-server* | efek kalibrasi (hipotesis kalibrasi) |
| H2 → H2p | jalur ukur CPU: *metrics-server* (±60 s, berundak) → Prometheus dan *adapter* (*scrape* 15 s, jendela `rate` 1 menit) | sinyal CPU, titik pemicu L\* | efek jalur ukur (komponen Hipotesis 2) |
| H2p → H3 | jenis sinyal: CPU → laju permintaan | jalur *adapter*, *scrape* 15 s, jendela 1 menit, tipe metrik Pods, titik pemicu L\* | efek jenis sinyal ("jenis metrik" pada Hipotesis 2) |
| H3 → K1 | jalur API: *adapter* (Custom Metrics API) → KEDA (External Metrics API) | sinyal laju, ambang, *controller* HPA | efek "mesin" = efek jalur metrik (verifikasi, Hipotesis 2) |

Rantai ini mengikuti aturan "setiap kontras inti hanya berbeda pada satu variabel penyebab" (Part 17 §17.23.5). Langkah
H2p → H3 menjawab pertanyaan perencanaan AK-1 (Part 17 §17.23.7): apakah makna sinyal masih berpengaruh setelah titik
pemicu dan umur bacaan disamakan.

**Hubungan dengan Part 17 dan tinjauan *red team*.** Kondisi eksperimen ini hampir sama dengan Kampanye 2-ringan v0,
tanpa lapisan tambahannya (set hipotesis baru, TOST sebagai hipotesis, SENS-f, keluaran primer baru), ditambah H2p yang
di Part 17 hanya modul opsional. Tinjauan *red team* (2026-10-18, [17-review-redteam-ringan-v0.md](17-review-redteam-ringan-v0.md))
menyarankan jalur yang lebih sempit: *shipping* K1 tidak diubah dan Hipotesis 1 hanya dilaporkan sebagai prediksi
terhitung. Bagian ini tetap mendesain ulang *shipping*, tetapi bersyarat (D1); bila syaratnya gagal, rancangannya jatuh ke
jalur *red team* itu.

## 19.1 Catatan gerbang

| Gerbang | Status |
|---|---|
| 1 Lembar konstruk | TERBUKA |
| 2 Register parameter | TERBUKA |
| 3 Pengembangan lokal (kind) | TERBUKA |
| 4 Pilot *cloud* + uji coba analisis | TERBUKA |
| 5 Pembekuan pra-registrasi | TERBUKA |
| 6 Tinjauan *red team* | TERBUKA |
| 7 Daftar periksa peluncuran | TERBUKA |

Tinjauan *red team* awal atas Part 17 (2026-10-18) dipetakan ke 19.8; itu bukan gerbang 6. Tinjauan *red team* awal atas
Part 19 v0.5 (2026-10-19, skor 6/10; [19-review-redteam-k1-diperbaiki-v0.5.md](19-review-redteam-k1-diperbaiki-v0.5.md))
dipetakan ke 19.11; itu juga bukan gerbang 6. Deviasi dari protokol: belum ada.

## 19.2 Perubahan dari K1

| Perubahan | Masalah K1 yang ditutup | Dasar ("dari mana") | Status |
|---|---|---|---|
| *Oscillating* dihapus | hasil *oscillating* K1 ditentukan jendela 30 s yang tidak berdasar (23 *scale-down* berlawanan fase, semuanya H2) | dengan jendela 300 s semua konfigurasi menahan *pod* melewati lembah 80 s; kontrafaktual Part 15 (berbasis model, eksploratori) memperkirakan selisih antar-konfigurasi mengecil | B (alasan). Klaim bersyarat pada *spike* dan *gradual*; arah K1 yang berbalik pada *oscillating* disebut sebagai pembanding di batasan |
| Jendela *scale-down* 300 s untuk semua | 30 s tanpa dasar; H1 vs H2 tercampur target dan jendela | nilai bawaan Kubernetes (dokumentasi HPA) | B-konv. H1 vs H2 tinggal beda target. Replika-detik dan CPU-detik dibandingkan hanya di jendela beban; ekor tetap 180 s seperti K1 dan *scale-down* dicek di pilot (19.3.10) |
| *Spike* dan *gradual* tetap | — | kontinuitas K1 | bentuk dan durasi K1 (19.3.10); aturan besaran beban diputuskan (SLO, λ0, r; 19.3.3), angkanya dari *ladder* baru |
| B1 = 1 *pod* | — | templat Binus "sistem yang berjalan"; kontinuitas | B |
| B2 = N terukur | B2 5 *pod* melebihi kebutuhan; penghematan dihitung terhadap *over-provisioning* | *ladder*: N terkecil yang memenuhi SLO pada puncak, diukur langsung (kapasitas tidak linear: B2 *auth* K1 sudah melewati SLO pada 40 req/s di *ladder* 2) | B-rumus |
| *Shipping* dibatasi slot | premis jenis layanan gagal (kedua layanan dibatasi CPU) | yang membuat HPA CPU terlambat adalah CPU rendah saat kapasitas penuh, bukan latensi yang didominasi waktu tunggu; *bulkhead* (W slot) membatasi kapasitas C ≈ W / T_svc tanpa menaikkan CPU (pola *bulkhead*; dasar praktik B-konv sejak 2026-10-19: batas konkurensi bawaan di pustaka umum, Resilience4j *Bulkhead* `maxConcurrentCalls` 25 dan HikariCP `maximumPoolSize` 10 [F, dokumentasi]; klaim bersyarat rasio CPU(C)/*request*, 19.4.1) | T_svc, C, dan W dari aturan yang diputuskan pemilik 2026-10-19 (B-konv dan B-rumus, 19.3.5); **bersyarat D1** |
| Konfigurasi H2 diganti | efek metrik tercampur titik pemicu | target CPU dari titik pemicu yang sama dengan ambang laju (19.3.1); tanpa kode baru | f = 0,8, diputuskan pemilik (B-konv, 19.3.1). Alternatif: CPU 50% seperti K1 |
| Konfigurasi H2p ditambahkan (pemilik, 2026-10-18) | efek metrik K1 adalah paket sinyal + jalur ukur (tinjauan K1 M-2) | memisahkan jalur ukur dari jenis sinyal; tinjauan *red team* O2 (setuju masuk inti); aturan satu variabel per kontras (Part 17 §17.23.5) | B (alasan); aturan *adapter* CPU **BB** sampai diuji di kind (19.3.5 g) |

## 19.3 Yang tetap harus ikut berubah walau "minimal"

### 19.3.1 Ambang laju dan target CPU dari satu aturan

- **Masalah di K1 [F].** Ambang laju 5 dan 15 req/s per *pod* berasal dari kalibrasi *closed-loop* April 2026, sedangkan
  target CPU 80% (bawaan) dan 50% (komentar *manifest* 6 April) tidak diturunkan dari titik yang sama. Terhadap kapasitas
  sehat satu *pod* (*auth* 8–10, *shipping* 50 req/s), ambang laju setara 50–62,5% dan 30% kapasitas; target CPU 50%
  tercapai pada 3,3 dan 17,9 req/s per *pod* (X5, Tabel H.3). CPU memicu lebih awal di *auth*, laju lebih awal di
  *shipping*, jadi "efek metrik" tercampur dengan kepekaan pemicu.
- **Aturan [B-rumus].** Satu fraksi pemicu f terhadap kapasitas sehat satu *pod* pada SLO (C_SLO, dari *ladder*):
  L\* = f × C_SLO.
  - H3 dan K1: ambang (`averageValue`) = L\* req/s per *pod*.
  - H2: target CPU u\* = CPU(L\*) / *request*, dengan CPU(L\*) diinterpolasi dari kurva CPU per *pod* terhadap laju di
    *ladder*.
  - H2p: metrik tipe Pods dari `rate(container_cpu_usage_seconds_total[1m])` per *pod* (kontainer layanan saja, tanpa
    kontainer *pause*), target `averageValue` = CPU(L\*) dalam *millicore*. Setara dengan u\* pada H2, tanpa target
    Utilization di atas 100%. Jendela 1 menit sengaja sama dengan jendela laju H3 [B-konv, disamakan]. **Hanya *pod* yang
    Ready** yang dimuat dalam deret H2p (digabung dengan `kube_pod_status_ready`; diputuskan pemilik 2026-10-19, tinjauan
    *red team* v0.5 M-2): *pod* yang belum siap menjadi "tanpa metrik", dan HPA menghitung *pod* tanpa metrik sebagai 0%
    saat *scale-up* ("on a scale-up, treat missing pods as using 0% of the resource request", `calcPlainMetricReplicas`),
    sama dengan aturan *pod* belum siap untuk CPU Resource di H2 [F, kode `replica_calculator.go`, dicek 2026-10-19].
    **Syarat Ready sepanjang satu jendela (diputuskan pemilik 2026-10-19 setelah pemeriksaan ulang):** untuk CPU Resource,
    di dalam *CPU initialization period* (bawaan 5 menit) HPA juga menganggap *pod* belum siap selama jendela metriknya
    masih mencakup waktu sebelum Ready (`unready = condition.Status == False || metric.Timestamp.Before(
    condition.LastTransitionTime + metric.Window)`, `groupPods`) [F]. Agar setara, deret H2p hanya memuat *pod* yang sudah
    Ready sepanjang satu jendela `rate` penuh (60 s): `min_over_time(kube_pod_status_ready{condition="true"}[1m]) == 1`
    sebagai penyaring. **Asimetri yang tersisa (dicatat, bukan disamakan):** saat *scale-down*, *pod* tanpa metrik pada
    metrik Pods dihitung memakai tepat nilai target ("on a scale-down, treat missing pods as using exactly the target
    amount"), sedangkan pada CPU Resource *pod* belum siap dikeluarkan dari perhitungan [F]. *Scale-down* di jendela beban
    jarang terjadi (stabilisasi 300 s), jadi dampaknya kecil; kejadiannya dicatat dari *watcher*.
    Deretnya dibuat dengan *recording rule* Prometheus yang dibatasi *namespace* dan *container*, sehingga *adapter* hanya
    melayani deret kecil (K1: memasukkan deret `container_*` membuat satu-satunya *pod adapter* OOM berulang dan memutus H3,
    `prometheus-adapter-values.yaml:77-80`); batas memori *adapter* diuji di klaster sebenarnya, dan *restart* = DQ5.
  - H1: tetap 80% (bawaan), sengaja tidak dikalibrasi, sebagai "praktik umum".
- **Pemeriksaan kesetaraan pemicu pada N *pod* (diputuskan pemilik 2026-10-19; tinjauan *red team* v0.5 K-1) [B-rumus].**
  Keputusan konfigurasi jatuh pada N ≥ 2 *pod* (⌈r / f⌉ ≥ 3), sedangkan kurva CPU(laju) untuk u\* diukur pada 1 *pod*. Data
  K1 menunjukkan CPU per *pod shipping* pada laju per *pod* yang sama 266m (1 *pod*) vs rata-rata 337m (5 *pod*) pada 40
  req/s per *pod*, dan p95 *auth* pada 8 req/s per *pod* 1.225 ms (1 *pod*) vs 1.765 ms (5 *pod*) [F, `ladder.json`]. Karena
  itu *ladder* baru memuat langkah N *pod* di tata letak final (`sut` 1 × D16as_v5): N = 1, 2, 3, …, ⌈r / f⌉, pada laju per
  *pod* L\* dan C_SLO; dicatat CPU per *pod*, p95, dan rasio metrik/target. **Aturan terima:** untuk H2, H2p, H3, dan K1,
  rasio metrik/target pada laju per *pod* L\* berada di 1,0 ± 0,1 untuk semua N tersebut (pita = toleransi HPA 10%,
  dokumentasi), dan pada 1,3 × L\* keempatnya menskalakan. **Bila gagal:** kalibrasi tetap pada N = 1 (titik pemicu
  didefinisikan pada pemicu pertama; target HPA hanya satu angka, jadi tidak dapat dibuat bergantung N), g(N) = CPU per
  *pod*(N) / CPU per *pod*(1) pada L\* dilaporkan dan dimasukkan ke model fluida, dan klaim ditulis "pemicu setara pada
  langkah pertama; pada langkah berikutnya CPU memicu g(N) × lebih awal". Ini sifat sinyal CPU ketika *pod* berbagi *node*,
  jadi dilaporkan sebagai bagian paket "jenis sinyal" (19.4.6). Alternatif yang ditolak: kalibrasi pada N puncak
  (ketidaksetaraan pindah ke langkah pertama, yang paling menentukan hasil *spike*); dibiarkan sebagai batasan (mengulang
  kesalahan K1 "pemicu tidak setara").
- **Yang tidak ikut disamakan:** lihat 19.4.6 (yang diubah setiap langkah rantai).
- **Nilai: f = 0,8 (diputuskan pemilik, 2026-10-18) [B-konv].**
  - **Dari mana:** 80% adalah target bawaan HPA bila metrik tidak diisi (referensi API HPA v2, dicek 2026-10-18) dan
    salah satu contoh target di panduan *cost optimization* GKE ("70% or 80%"). Angka yang sama dipakai terhadap kapasitas
    SLO, bukan terhadap *request* CPU, sehingga H1 → H2 hanya berbeda acuan (*request* vs C_SLO). Pemindahan angka ke
    besaran lain itu adalah konvensi yang dinyatakan, bukan nilai bawaan f.
  - **Akibat per layanan [H, angka K1]** — akibat, bukan alasan memilih f (pemilik mengusulkan 0,8 dari nilai bawaan HPA
    sebelum angka ini dihitung). *Auth*: H1 terpicu di ±5,1 req/s per *pod* ≈ 0,73–0,85 × C_SLO (6–7 req/s pada
    SLO 1.000 ms), karena CPU *auth* pada C_SLO ≈ *request* (257–314m pada 6–8 req/s, *request* 250m), jadi H1 ≈ H2 di *auth* (kontrol: selisih kalibrasi diprediksi kecil, 19.4.4). *Shipping*: H1 baru
    terpicu di atas C (CPU(C) < 200m bila D1 lolos), jadi H1 ≠ H2 (uji).
  - **Cadangan saat pemicu:** toleransi 10% membuat HPA bertindak di 1,1 × 0,8 = 0,88 × C, sehingga cadangan satu *pod*
    0,12 × C. Dengan *ramp gradual* 300 s (19.3.10), pertumbuhan beban selama waktu reaksi melebihi cadangan itu pada
    langkah pertama untuk semua konfigurasi terkalibrasi. Jadi *gradual* berarti "lebih lambat dari *spike*, tidak bebas
    kewalahan" (Part 17 D-R9(b)). Ini disengaja: panduan Google Cloud memasangkan target 70/80% dengan cadangan yang cukup
    selama replika baru menyala; di sini yang diukur adalah seberapa jauh tiap jalur tertinggal saat pertumbuhan melebihi
    cadangan. Efek lantai *gradual* K1 (fraksi buruk H3/K1 0,0003–0,03) berasal dari pemicu rendah (ambang laju 30–62,5%
    C) dan tidak terjadi pada f = 0,8. CPU yang mentok di *limit* sementara laju kedatangan terus naik adalah konstruk jenis
    sinyal itu sendiri (Part 17 §17.18 butir 10), bukan perancu.
  - **Syarat batas bawah** otomatis terpenuhi, tetapi dicek di *ladder*: f > 1,1 × λ0 / C (tidak menskalakan saat
    pemanasan); ⌈r / f⌉ ≤ M (19.3.2); CPU(0,8 × C) jelas di atas CPU diam plus derau.
  - **Alternatif yang dipertimbangkan:** (a) rentang turunan [f_bawah, f_atas] dengan f_atas = (1 − s × T_reaksi / C) /
    1,1 dan sensitivitas di kedua ujung — ditolak: pada *ramp* 300 s rentangnya sempit atau kosong, dan konstanta derau,
    margin, serta jeda jalur laju masih BB; (b) f = 0,8 dengan *ramp* yang diperpanjang sampai jalur tercepat masih
    mengejar (T_ramp ≥ (r − λ0/C) × T_reaksi / 0,12, ±23–36 menit) — ditolak pemilik (19.3.10); (c) f = 0,7 (contoh GKE
    yang lain) — bukan nilai utama; dipakai sebagai level sensitivitas bersyarat (P19, di bawah).
  - **Sensitivitas:** tinggi untuk besar efek jalur ukur dan waktu reaksi semua konfigurasi terkalibrasi (cadangan 12%
    pada 0,8 vs 23% pada 0,7); sedang untuk selisih CPU vs laju, karena lompatan CPU per ronde dibatasi ±1/f (Part 17
    E-f). Rumus f_atas tetap dipakai, tetapi hanya untuk memprediksi kapan tiap jalur mulai kewalahan (mekanisme), bukan
    untuk memilih f.
  - **Status:** diputuskan pemilik 2026-10-18 (P4). Label B-konv, bukan B: dokumentasi HPA mendefinisikan 80% terhadap
    *request* CPU, bukan terhadap kapasitas SLO, jadi yang terdokumentasi adalah angkanya, sedangkan pemakaiannya pada C_SLO
    adalah konvensi yang dinyatakan. Keduanya berbasis menurut protokol ("an explicitly named convention"); f tidak lagi
    BELUM BERBASIS.
  - **Sensitivitas f (diputuskan pemilik 2026-10-19, P19):** klaim ditulis bersyarat "pada titik pemicu 0,8 × C_SLO".
    Prediksi untuk f = 0,7 dihitung dengan model fluida (19.3.5) sebagai prediksi model eksploratori, **tanpa *run***
    (diperbarui pemilik 2026-10-19 setelah tinjauan *red team* v0.5 K-2). Prediksinya: selisih H1 − H3 dan H1 − H2
    membesar, selisih jalur H2 − H2p mengecil (cadangan 23% vs 12%). Aturan presisi sebelumnya (b_SENS = ⌈2 × (1,96 ×
    σ_pilot / δ_min)²⌉, dijalankan bila ≤ 10) dibuang: σ_pilot berasal dari 2 *run* per sel (1 derajat bebas), dan dengan SD
    K1 aturan itu hampir pasti menghasilkan b > 10 (*red team*: 31 pada δ = 0,014), jadi praktis sama dengan prediksi
    model saja. Alternatif yang ditolak: 40 *run* dengan b = 5 tetap (b hanya kontinuitas repetisi K1; interval selisih
    ±1,96 × σ × √(2/b) ≈ ±0,037 pada σ 0,03, lebih lebar dari δ_min), uji penuh b = 10 sebagai keluarga tersendiri, dan
    aturan presisi berbasis σ pilot.

### 19.3.2 maxReplicas cukup untuk konfigurasi dengan pemicu terendah

- **Masalah di K1 [F].** maxReplicas 5 untuk semua. Pada puncak, ambang laju meminta 30/5 = 6 *pod* (*auth*) dan
  105/15 = 7 *pod* (*shipping*), sehingga H3 dan K1 mentok di 5 selama puncak (BAB 4.6.1). Saat batas mengikat,
  konfigurasi bertemu di batas yang sama: yang terukur tinggal "seberapa cepat mencapai 5", dan replika-detik ikut
  terpotong.
- **Syarat:** M tidak boleh pernah mengikat, dan kapasitas *node* juga tidak (pod *Pending* adalah batas diam-diam).
  Kebutuhan: konfigurasi laju meminta ⌈λp / L\*⌉ = ⌈r / f⌉ (contoh dengan f = 0,8: r = 3 → 4; r = 4,5 → 6); konfigurasi
  CPU (H1, H2, H2p) bisa meminta lebih banyak karena bacaan tertunda atau CPU dari penolakan (Part 17 R43: CPU target
  lazim pada *auth* ±12–16 *pod*). Penskalaan berlebih itu perilaku yang diukur, bukan dipotong.
- **Keputusan (pemilik 2026-10-19): M = 100 untuk semua konfigurasi dan kedua layanan [B-konv].**
  - **Dari mana:** nilai bawaan `maxReplicaCount` KEDA (100; dokumentasi ScaledObject 2.17, "passed to the HPA
    definition that KEDA will create"). `maxReplicas` HPA wajib diisi dan tidak punya nilai bawaan, jadi untuk konfigurasi
    HPA angka ini konvensi yang disamakan. M tidak berbiaya: hanya batas di objek HPA, sedangkan jumlah *pod* yang menyala
    tetap sebanyak yang diminta.
  - **Alternatif yang ditolak:** 5 seperti K1 (terbukti mengikat); ⌈r / f⌉ + 1 (konfigurasi CPU bisa meminta lebih);
    2 × kebutuhan pilot (butuh pengukuran dan konvensi 2× untuk sebuah batas yang cukup dibuat tidak mengikat).
- **Kapasitas *node* (pemilik 2026-10-19) [B-rumus; cadangan B-konv]:** *pool* `sut` = **1 × Standard_D16as_v5** (16 vCPU,
  64 GiB; ±15,8 vCPU *allocatable*, ±60 *pod* 250m), keluarga Dasv5 yang sama dengan K1 (performa per vCPU sama).
  Harganya praktis sama dengan 4 × D4as_v5 (US$0,778 vs 0,776 per jam, Azure Retail Prices API, Indonesia Central, dicek
  2026-10-19), tetapi semua *pod* uji berada di satu *node*, jadi penempatan identik di setiap *run* dan perancu penempatan
  K1 (tinjauan *red team* M-8) hilang oleh desain; DaemonSet cukup satu set. Pool *user* boleh berisi satu *node* ("User
  node pools can contain zero or more nodes", Microsoft Learn *Use system node pools*). Risiko: *node* mati berarti *run*
  hilang dan diulang lewat aturan mutu data; persaingan antar-*pod* di dalam *node* (*memory bandwidth*, *cache*) sama untuk
  semua konfigurasi pada jumlah replika yang sama. Syarat: kapasitas `sut` ≥ 2 × replika tertinggi yang diminta
  konfigurasi mana pun di pilot; bila kurang, `sut` diganti Standard_D32as_v5 sebelum pembekuan (cadangan 100% karena
  ukuran *node* tidak boleh berubah selama kampanye). Tidak perlu muat 100 *pod*: kebutuhan nyata belasan sampai puluhan.
  Alternatif yang ditolak: 4 × D4as_v5 (harga sama, penempatan tersebar dan bisa berbeda antar-*run*). `--max-pods` disetel eksplisit saat membuat *node pool*, ≥ jumlah
  *pod* yang muat per *node* (nilai bawaan AKS bergantung CNI: Overlay 250, kubenet dan *pod subnet* 110, Azure CNI lama
  30; maksimum 250 [F, Microsoft Learn *IP address planning*, dicek 2026-10-19]); CNI klaster K1 tidak tercatat di repo.
- **Cek per *run* (diperbaiki 2026-10-19; tinjauan *red team* v0.5 M-5):** kondisi `ScalingLimited` menyala dengan beberapa
  alasan (`TooManyReplicas`, `TooFewReplicas`, `ScaleUpLimit`, `ScaleDownLimit`; batas *scale-up* bawaan tanpa blok
  `behavior` = max(2 × replika sekarang, 4)) [F, kode `horizontal.go`, dicek 2026-10-19]. Yang menjadi masalah mutu data
  hanya `reason = TooManyReplicas` (terbentur M) dan pod *Pending* (kapasitas *node*): keduanya DQ7 (19.3.11).
  `ScaleUpLimit` dicatat sebagai keluaran mekanisme, `TooFewReplicas` wajar pada beban rendah; keduanya bukan alasan
  eksklusi. Pilot mencatat replika tertinggi per konfigurasi (deskriptif, dan dasar ukuran `sut`).
- **Sensitivitas:** tidak ada selama tidak mengikat; itulah fungsi kedua cek di atas.

### 19.3.3 Kalibrasi ulang dan urutan aturan

- **Kenapa.** Layanan *shipping* berubah, jadi angka K1-nya tidak berlaku: kapasitas 50 req/s, puncak 105 req/s,
  SLO 1.000 ms, batas *shedding* 48, ambang 15. *Auth* tidak berubah, tetapi aturan yang sama tetap diterapkan, jadi
  angkanya ikut dihitung ulang.
- **Urutan aturan (tinjauan *red team* M-2).** Aturan SLO → C_SLO per layanan → L\*, u\*, λp, λ0 → N, K, M. C_SLO peka
  terhadap SLO: *auth* K1 ±6–7 req/s pada SLO 1.000 ms, tetapi 8–10 req/s pada 1.500 ms (`ladder.json`: 6 req/s p95
  653 ms, 8 req/s p95 1.225 ms, 10 req/s *error* 3,9%) [F]. Karena semua turunan ikut bergeser, aturan SLO dibekukan lebih
  dulu (diputuskan 2026-10-18: 1.000 ms, di bawah), dan C_SLO juga dilaporkan pada 1.500 ms (eksploratori).
- **Yang diukur ulang dan aturannya:**
  - **C_SLO:** laju tertinggi yang memenuhi SLO dengan *error* ≤ 1% pada satu *pod* (aturan *ladder* K1). B-rumus.
  - **Puncak λp = r × C_SLO, dengan r yang sama untuk kedua layanan.** Di K1, puncak *auth* 3–3,75 × C dan *shipping*
    2,1 × C, sehingga intensitas relatif beban berbeda antar-layanan: perancu tersembunyi bagi Hipotesis 1.
    - **Aturan (diputuskan pemilik 2026-10-18, P5) [B-rumus]:** r = min atas kedua layanan dari 0,8 × λ_runtuh / C_SLO,
      dibulatkan ke bawah ke 0,1; bila r / f berada dalam ±5% dari bilangan bulat, r digeser turun 0,1 sampai tidak lagi
      (agar ⌈r / f⌉ tidak duduk di batas pembulatan; tinjauan v0 F3). λ_runtuh = laju terendah pada satu *pod* yang membuat
      penghitung, *scrape*, atau *probe* buta (MC5, Part 17 R79). Dipilih hanya dari batas runtuh dan kapasitas, bukan dari
      efek yang tampak di pilot (M-8). N untuk B2 dan M harus muat di klaster (jumlah *node* menyesuaikan; anggaran bukan
      batasan).
    - **Dari mana:** batas aman terukur, yaitu 80% dari laju runtuh satu *pod* pada layanan yang paling rentan; cadangan
      20% = pergeseran lutut kapasitas *auth* antar-kalibrasi K1 (10 → 8 req/s, Part 08 §8.11). Alasan syaratnya: setiap
      *run* mulai dari satu *pod*, jadi menit pertama *spike* ditanggung satu *pod*; bila runtuh, metrik dan *probe* buta
      (pilot K1 v1).
    - **Ilustrasi dari *ladder* K1 (bukan angka final) [F]:** *auth* C_SLO 6 req/s, belum runtuh pada 30 req/s (±10 req/s
      dilayani, 60% ditolak), jadi r maks ≥ 4,0; *shipping* K1 C_SLO 50 req/s, runtuh di 105–140 req/s (*ladder* ke-1
      runtuh di 105, *ladder* ke-2 tidak), jadi r maks ≤ ±1,7. **r praktis ditentukan oleh D1:** bila *shipping* K1 tetap,
      r ≈ 1,6–1,7 untuk kedua layanan (puncak *auth* ±10 req/s); bila D1 lolos, r ditentukan yang lebih rendah antara batas
      *auth* dan batas *shipping* baru.
    - **Alternatif yang ditolak:** r tetap (4,5 di Part 17, atau ≥ 2,5 × C seperti K1) — angkanya tanpa dasar, dan dengan
      *shipping* K1 cek runtuh pasti gagal; r per layanan — intensitas relatif berbeda lagi; angka K1 (*auth* 30,
      *shipping* 105 req/s) — r 5 vs 2,1, dan 105 req/s sudah titik runtuh di *ladder* ke-1.
    - **Sensitivitas:** tinggi pada besar efek. δ_min *spike* ≈ (1 − 1/r) × 15 / 420: ±0,014 pada r = 1,6 vs 0,024 pada
      r = 3. Bila r kecil (D1 gagal), nilainya diterima dan efek yang lebih kecil ditulis; b ditentukan simulasi daya dari
      pilot. r tidak dinaikkan melewati batas aman demi efek.
  - **Beban dasar λ0 = 0,2 × C_SLO, sama untuk kedua layanan (diputuskan pemilik 2026-10-18) [B-konv].**
    - **Syarat keras [B-rumus]:** tidak ada penskalaan saat pemanasan. HPA bertindak di 1,1 × L\* = 0,88 × C_SLO (H1 *auth*
      sedikit di atasnya, ±5,1 × 1,1 req/s), jadi λ0 harus jelas di bawahnya dengan cadangan derau CPU; λ0 tidak nol
      (sistem hangat, semua jalur metrik sudah punya deret).
    - **Dari mana:** rasio beban dasar K1 terhadap kapasitas sehat satu *pod* (*auth* 2/10, *shipping* 10/50 = 0,2)
      [F, Part 08 §8.5]. Di K1 angka itu hasil pengukuran *ad hoc* agar H2 (CPU 50%) tidak menskalakan saat pemanasan,
      bukan prinsip; di sini rasionya dipertahankan sebagai konvensi kontinuitas dan diterapkan ke C_SLO. Rasio yang sama
      untuk kedua layanan menyamakan bentuk beban relatif (sejalan dengan r yang sama).
    - **Akibat (ilustrasi data K1):** *auth* 1,2 req/s (C_SLO 6; CPU ±50–60m, jauh di bawah 220m), *shipping* 10 req/s
      (C 50) atau ±4 req/s bila D1 lolos (C ≈ 20).
    - **Alternatif yang ditolak:** 0,6 × pemicu terendah ≈ 0,48 C (Part 17 R38; 0,6 tanpa dasar, lebih dekat ke pemicu);
      0,88 C − 3σ derau (butuh *ladder*, rasio berbeda per layanan); angka K1 tetap 2 dan 10 req/s (rasio berbeda
      antar-layanan, perancu yang sama dengan puncak K1).
    - **Sensitivitas:** rendah untuk *spike* (beban melompat ke r × C dalam 10 s); rendah–sedang untuk *gradual*: waktu dari
      awal *ramp* sampai HPA bertindak = (0,88 − 0,2) / (r − 0,2) × 300 s ≈ 73 s (r = 3) atau 47 s (r = 4,5), vs 48 s dan
      30 s pada 0,48 C; kemiringan *ramp* berubah ≤ ±10%.
    - **Cek pilot:** replika semua konfigurasi tetap 1 sampai t = 120 s; bila gagal, λ0 diturunkan sebelum pembekuan.
      Gangguan `setup()` *auth* K1 (120 *login bcrypt* dalam ±28 s sebelum pemanasan membuat H2 menskalakan sebelum *onset*;
      Part 08 temuan #3) dihindari: token disiapkan lebih dulu seperti di *ladder* K1, atau pemanasan baru dimulai setelah
      jeda ≥ umur bacaan CPU + jendela *rate*.
  - **SLO: 1.000 ms untuk kedua layanan (diputuskan pemilik 2026-10-18, P6) [B-konv].**
    - **Dari mana:** batas 1,0 detik Nielsen (1993, *Usability Engineering*; NN/g "Response Times: The 3 Important
      Limits"): batas agar alur pikir pengguna tetap tidak terputus. Sejalan dengan Google SRE Book bab 4 ("Start by
      thinking about … what your users care about"; "Don't pick a target based on current performance"). B-konv, bukan B:
      batas Nielsen berlaku untuk respons yang dilihat pengguna, sedangkan di sini dipakai sebagai p95 per *endpoint*
      (masing-masing satu aksi pengguna: login, cek ongkos kirim; *overhead* jaringan dan *gateway* tidak dihitung).
    - **Bentuk kriteria (tetap dari K1, R53):** satu langkah *ladder* memenuhi SLO bila p95 ≤ 1.000 ms dan *error* ≤ 1%;
      permintaan "buruk" = lebih lambat dari 1.000 ms atau gagal.
    - **Alternatif yang ditolak:** (b) aturan K1 "Opsi 2" diadaptasi (p95 B2 pada puncak, dibulatkan ke atas ke 100 ms):
      target dari performa saat ini, nilainya baru ada setelah *ladder* (tidak dapat dibekukan paling awal), sirkular
      dengan N untuk B2, dan versi K1-nya diputuskan setelah data (Part 20 T9); (c) m × p95 beban rendah: pengali m tanpa
      dasar (masalah yang sama dengan 1,3× di K1); (d) nilai K1 tetap (*auth* 1.500, *shipping* 1.000): mewarisi
      kelemahan (b), hanya berlaku bila *shipping* tidak didesain ulang, dan 1,5 detik tidak punya jangkar literatur.
    - **Akibat [F/H, data K1].** *Auth*: C_SLO turun dari ±8 ke ±6 req/s (*ladder*: 6 req/s p95 653 ms; 8 req/s p95
      1.225 ms), jadi beban mutlak *auth* ±25% lebih ringan dari K1 pada r yang sama; tekanan relatif tetap diatur lewat r.
      **Lantai *auth*:** fraksi buruk B2 di jendela beban 3,0% (*gradual*) dan 4,1% (*spike*) pada 1.000 ms, vs 1,3% dan
      1,8% pada 1.500 ms (ekor *login bcrypt*; dihitung 2026-10-18 dari `analysis/cache`, jendela [120, 540)). Lantai ini
      sama untuk semua konfigurasi dan ditulis terang; efek berada di atasnya (19.3.8). Sela di atas latensi bawaan *auth*
      ±350 ms, jadi C_SLO *auth* peka derau. *Shipping*: lantai B2 ±0%. Bila D1 lolos, T_svc *shipping* baru dipilih agar
      p95 bawaannya jelas di bawah 1.000 ms (masuk aturan W dan C target); bila D1 gagal, *shipping* K1 hanya punya sela
      ±80 ms di atas p95 bawaan ±917 ms (risiko: C_SLO peka derau).
    - **Sensitivitas:** tinggi (di K1, signifikansi efek kalibrasi berubah antar-nilai SLO; BAB 4.6.5). Keluaran dihitung
      ulang pada 1.500 ms dari data yang sama sebagai analisis eksploratori, tanpa *run* tambahan.
  - **Batas *in-flight* K = C_SLO × SLO, untuk kedua layanan (diputuskan pemilik 2026-10-19; tinjauan *red team* v0.5
    M-11) [B-rumus].** Hukum Little (L = λW) dengan λ = C_SLO dan waktu tinggal maksimum W = SLO: *pod* hanya menerima
    pekerjaan yang masih bisa selesai dalam SLO pada kapasitasnya, dan permintaan yang pasti melewati SLO ditolak lebih
    awal. Untuk *shipping* baru, rumus Part 17 R25 K = W + C_SLO × (SLO − T_svc) sama persis dengan ini karena W = C_SLO ×
    T̄_svc (19.3.5), jadi kontradiksi Part 17/Part 19 hilang. Tidak memerlukan angka p99. Alternatif yang ditolak: aturan K1
    K = C × p99(C) (pada *auth* p99 pada C_SLO 1.816 ms > SLO, jadi permintaan yang diterima bisa menunggu melewati SLO;
    `ladder.json`) — posisi pemilik sebelumnya (2026-10-18), diganti. Sensitivitas: K menentukan CPU *pod* saat kewalahan
    dan c_tolak (tinjauan *red team* Part 14 F5), jadi c_tolak dan CPU diukur pada K dan 1,5 × K di langkah kelebihan beban
    *ladder* (deskriptif, tanpa *run* kampanye).
  - **Semantik *bulkhead* dan K (*shipping* baru):** *bulkhead* = semafor W slot di dalam *handler*; permintaan yang belum
    mendapat slot menunggu di dalam *pod*. K = batas total permintaan di dalam *pod* (diproses + menunggu), ditegakkan oleh
    *middleware admission control* terluar yang menolak seketika dengan 503 dan menaikkan `http_requests_shed_total`
    (`admission_control.py`). K ≥ W otomatis karena SLO ≥ T_svc. Semafor menunggu ini mekanisme baru di samping batas K yang
    sudah ada (tinjauan *red team* v0.5 M-11), di belakang *flag* yang bawaannya mati.
  - **N untuk B2:** 19.2. **M:** 19.3.2. **Ambang dan target:** 19.3.1.
- ***Ladder* baru sebagai sumber angka (diputuskan pemilik 2026-10-18).** Aturan di atas dibekukan sekarang; angkanya diisi
  dari *ladder* baru di platform terpilih. *Ladder* K1 (6 Okt 2026) hanya bahan perencanaan (ukuran kasar, grid, bukti awal
  D1-a dan biaya menolak), bukan angka final, karena:
  - konfigurasi layanan berubah: K dihitung ulang dengan aturan K = C_SLO × SLO (ilustrasi *auth*: 6 req/s × 1,0 s = 6,
    vs 22 di K1), dan K mengatur *shedding*, jadi titik runtuh dan latensi ikut berubah; penghitung kedatangan baru;
  - *shipping* berubah bila D1 lolos, dan D1-a butuh CPU *shipping* baru pada C_SLO;
  - klaster dan versi berbeda: K1 di AKS 1.33.7 (dukungan berakhir), *image* `:latest` tanpa *digest*; P2 bisa berarti
    perangkat keras lain;
  - resolusi dan jangkauan kurang: langkah *auth* 6 → 8 req/s (±25%), C_SLO *shipping* pas di batas (p95 tepat 1.000 ms
    pada 50 req/s di *ladder* ke-2), runtuh *auth* tidak diuji di atas 30 req/s, runtuh *shipping* hanya terkurung
    105–140 req/s dan kedua *ladder* tidak sepakat di 105 req/s.
- **Syarat *ladder* baru:**
  - urutan: P2 diputuskan → cek di kind → *ladder* singkat (cek parameter gerbang 1–2, boleh sebelum gerbang lain lolos
    dengan persetujuan biaya; datanya bukan data tesis);
  - versi dan konfigurasi dikunci: *digest image*, K final, penghitung kedatangan; dua putaran karena K bergantung pada C
    (ukur C → tetapkan K → konfirmasi dengan K final). **Aturan konvergensi (diputuskan pemilik 2026-10-19 setelah pemeriksaan
    ulang) [B-rumus]:** putaran diulang sampai C_SLO berubah kurang dari satu langkah *ladder* (≤ 10% C) antara dua putaran
    berurutan, paling banyak 3 putaran; bila belum konvergen, K dari putaran terakhir dipakai dan dicatat sebagai deviasi
    bertanggal. Pada setiap putaran, fraksi tolak pada C_SLO dilaporkan, karena K = C_SLO × SLO dapat mengubah sebagian
    permintaan lambat menjadi penolakan;
  - langkah rapat di sekitar C_SLO (≤ 10% C) dengan ≥ 2–3 ulangan;
  - langkah kelebihan beban sampai runtuh untuk kedua layanan (19.3.5 d);
  - langkah N *pod* (N = 1, 2, 3, …, ⌈r / f⌉) pada laju per *pod* L\* dan C_SLO di tata letak final, untuk cek kesetaraan
    pemicu (19.3.1) dan C_SLO per *pod* pada N *pod* (kapasitas *auth* tidak linear);
  - model CPU dan jumlah *thread* per inti (`lscpu`) setiap *node* dicatat **per *run*** (tinjauan *red team* v0.5 K-1, M-9; per *run* sejak 2026-10-19 karena klaster tidak dihentikan dan Dasv5 mendukung *live migration*);
  - kedua varian *shipping* (baru dan K1) diukur selama D1 belum diputuskan.

### 19.3.4 Penghitung laju: dilayani atau kedatangan

- **Di K1 [F].** *Middleware load shedding* didaftarkan paling akhir sehingga menjadi lapisan terluar; permintaan yang
  ditolak tidak sampai ke instrumentasi, jadi `http_requests_total` hanya menghitung permintaan yang dilayani (BAB 4.2.2).
  Akibatnya:
  - laju per *pod* mentok di kapasitas *pod* (*ladder* K1: *shipping* 42–44 req/s pada 60–105 req/s yang ditawarkan);
  - rasio metrik/target per ronde HPA dibatasi C / ambang, sehingga ambang harus rendah agar sinyal berguna (Part 17
    §17.23.2);
  - tanpa *shedding*, *pod* runtuh, `/metrics` tidak menjawab, dan H3/K1 *shipping* tetap satu replika (pilot,
    Lampiran E).
- **Pilihan:**
  - **(a) Dilayani**, seperti K1: tanpa perubahan. Dengan ambang setara (L\* < C) sinyal tetap memicu, tetapi lompatan
    per ronde dibatasi ±1/f, sama seperti CPU, sehingga selisih H2p vs H3 menjadi kecil karena kedua sinyal jenuh.
  - **(b) Kedatangan = dilayani + ditolak.** Penolakan sudah dihitung per *pod* di `http_requests_shed_total` (kode
    *admission control* kedua layanan), jadi cukup mengubah kueri *adapter* dan KEDA atau menambah *recording rule*
    Prometheus; tidak perlu kode layanan baru. Rasio per ronde = λ / L\*, tidak terbatas.
- **Usulan: (b).** Sinyal laju seharusnya melihat beban yang datang, termasuk yang ditolak; (a) membuat sinyal laju jenuh
  tepat saat kelebihan beban. Klaimnya harus menyebut bahwa sinyal laju membawa informasi beban di atas kapasitas yang
  tidak dimiliki CPU.
- **Catatan.** `http_requests_total` naik saat respons selesai (tertinggal sebesar latensi, < 1 s), penolakan naik saat
  permintaan datang; dibanding jendela *rate* 1 menit selisihnya kecil [P]. Penghitung di proses yang sama tetap buta bila
  *pod* runtuh, jadi λp harus di bawah batas runtuh (19.3.3). Laju kedatangan menjadi titik tunggal bagi H3, K1,
  Hipotesis 1–2, dan hipotesis kalibrasi (PM3, 19.7), jadi kuerinya diuji di kind terhadap jadwal k6. Kegagalan *scrape*
  pada λp dicatat sebagai keluaran yang dilaporkan, bukan alasan membuang *run* (tinjauan *red team* m-7).
- **Status.** Diputuskan pemilik 2026-10-19 (P3): **(b) kedatangan** [B: alasan konstruk dan *ladder* K1]. Dengan f = 0,8,
  penghitung dilayani membatasi rasio metrik/target per ronde HPA pada 1/f = 1,25 (dari 1 *pod*: ⌈1,25⌉ → 2 → 3 → 4, satu
  *pod* per siklus), sehingga sinyal laju jenuh seperti CPU; dengan kedatangan rasionya λ / L* (pada 4 C satu *pod* langsung
  meminta 5 *pod*). Perubahan H3 dan K1 dari K1 (dilayani → kedatangan) dicatat di BAB 3. Sensitivitas: tinggi untuk efek
  jenis sinyal (H2p → H3) dan Hipotesis 1.

### 19.3.5 Cek murah sebelum membangun semuanya, dan aturan D1

Semua cek di bawah dijalankan sebelum sisa jalur dibangun: di kind (indikatif; CPU laptop atau VM berbeda), lalu
*ladder* singkat di platform terpilih (beberapa jam; cek konstruk gerbang 1–2, dengan persetujuan biaya). Angka untuk
keputusan berasal dari platform terpilih.

- **(a) CPU *shipping* baru saat kapasitas penuh.** Premis Hipotesis 1 menuntut CPU per *pod* pada C_SLO di bawah target
  H1 (80% × 250m = 200m), sehingga beban yang dilayani tidak pernah memicu H1. Di K1, *shipping* mencapai 377m pada
  50 req/s (151% *request*), jadi premisnya gagal.
- **(b) Biaya menolak.** Dengan *shedding* di dalam *pod*, setiap penolakan memakan CPU.
  - Dari *ladder* K1 (*shipping*, *shedding* terluar): pada 105 req/s, 42,4 req/s dilayani, 62,6 req/s ditolak, CPU
    mentok 500m (rasio *throttling* ≈ 1,0) → ±2,4–3,3 ms per penolakan [H; tinjauan *red team* K-1, angka *ladder* dicek
    ulang]. Karena CPU sudah mentok di *limit*, angka ini **batas atas**, bukan estimasi (tinjauan *red team* v0.5 m-4); biaya
    melayani juga bisa ikut naik saat *pod* kewalahan.
  - **Cara ukur di *ladder* baru (diputuskan pemilik 2026-10-19) [B-rumus]:** pada langkah di atas C yang CPU-nya masih di
    bawah *limit* (±1,2–1,5 × C dengan *shedding* aktif), c_tolak = (CPU − CPU(C)) / laju tolak; diukur pada K dan 1,5 × K
    (19.3.3). Nilai inilah yang dipakai D1-b′; angka K1 hanya pembanding.
  - Ilustrasi untuk *shipping* baru (C ≈ 20 req/s, ±7,5 ms per permintaan, CPU(C) ≈ 150m): pada *spike* 90 req/s,
    ±70 penolakan/s × ±3 ms ≈ 210m, total ±360m (144% *request*). H1 tetap terpicu, jadi beda yang diprediksi
    Hipotesis 1 mengecil pada *spike*. Pada *gradual*, penolakan baru muncul setelah beban melewati C, jadi premisnya
    lebih setia (dasar pola utama, 19.4.1).
- **(c) Konstruk *auth* "dibatasi CPU" (tinjauan *red team* M-1; ambang diputuskan pemilik 2026-10-18).**
  - **Uji naik *limit* [B-rumus; ambang B-konv]:** *goodput* plato satu *pod* (laju dilayani tertinggi yang bertahan pada
    langkah kelebihan beban) diukur pada *limit* CPU 1.000m dan 500m (*request* tetap 250m). *Auth* dianggap dibatasi CPU
    bila rasio plato 1.000m / 500m ≥ 1,5. **Dari mana:** sebuah sumber daya adalah hambatan bila menaikkannya menaikkan
    *throughput*; 1,5 adalah titik tengah antara tanpa kenaikan (1,0) dan kenaikan sebanding (2,0). Rasio C_SLO pada
    kedua *limit* ikut dilaporkan.
  - **Kontrol negatif:** uji yang sama pada *shipping* baru, diharapkan rasio ≈ 1,0 (< 1,5). Hasil kedua layanan masuk
    lembar konstruk (gerbang 1) sebagai bukti bahwa jenis hambatannya berbeda.
  - **Rasio *throttling* CFS hanya deskriptif:** data K1 menunjukkan rasio itu tidak membedakan jenis hambatan
    (*shipping* K1 juga ±1,0 saat jenuh; pada C_SLO dua *ladder shipping* memberi 0,036 dan 0,284; *auth* 0,445 pada
    C_SLO) [F, `ladder.json`]. CPU ≥ 0,8 × *limit* juga bukan kriteria: gagal pada data K1 (257–314m = 51–63% *limit*
    pada 6–8 req/s) [F].
  - **Biaya:** ±dua langkah *ladder* tambahan per layanan; indikatif di kind lebih dulu.
  - **Bila gagal:** Hipotesis 1 dan hipotesis kalibrasi tidak dapat diuji.
- **(d) Batas runtuh satu *pod* untuk kedua layanan (m-5, PM2).** Langkah kelebihan beban naik sampai *pod* runtuh: grid
  ×C_SLO 1,5; 2; 3; 4; 5; 6, lalu dipersempit di antara langkah terakhir yang selamat dan langkah pertama yang gagal
  (menggantikan "sampai 1,2 × λp", yang sirkular karena λp ditentukan dari r). Syarat λp ≤ 0,8 × laju runtuh menentukan r
  (19.3.3). *Ladder auth* K1 baru sampai 30 req/s pada satu *pod* [F].
- **(e) Cek konstruk jalur metrik *adapter* vs KEDA (tinjauan *red team* O1; diubah pemilik 2026-10-19 setelah tinjauan
  *red team* v0.5 M-8).** Hanya cek konstruk, bukan estimasi kontras tesis: langkah beban berulang pada satu *pod* (langkah
  ke 1,3–2 × L\*), dengan penundaan awal acak U(0, 15) s (N-1, 19.3.10); yang diukur adalah jeda dari langkah beban sampai
  nilai metrik berubah di objek HPA (`currentMetrics`) untuk Custom Metrics API (*adapter*) dan External Metrics API
  (KEDA), serta apakah HPA buatan KEDA menerima nilai pada setiap siklus. Selisih waktu kenaikan replika **tidak**
  diestimasi dan tidak dilaporkan sebagai hasil; efek mesin hanya diestimasi di kampanye (19.4.2). Hasil cek masuk lembar
  konstruk (gerbang 1), bertanggal, dan tidak mengubah desain kecuali menutup [BD] konstruk. Dasar: protokol (cek *cloud*
  pendek hanya untuk memverifikasi konstruk atau parameter; keluarannya bukti register, bukan data tesis). Latar K1:
  selisih yang belum terjelaskan pada *shipping spike* (kenaikan pertama 19,7 vs 35,0 s; *auth* 35,2 vs 35,5 s; Tabel
  4.11) [F], yang menurut tinjauan *red team* v0.5 N-1 kemungkinan artefak fase siklus HPA.
- **(f) Platform (gerbang 1; tinjauan *red team* m-1, m-2).** Klaster K1 memakai AKS 1.33.7, yang dukungannya berakhir
  Juli 2026; 1.34 berakhir November 2026, jadi klaster baru ≥ 1.35 [F, tabel versi AKS, dicek 2026-10-18]. Versi baru
  membawa *metrics-server* 0.8.x dan KEDA 2.17–2.20 [F, tabel komponen AKS], sehingga angka K1 tidak dapat dibandingkan
  langsung. Dicek ulang: resolusi bawaan *metrics-server*, delegasi KEDA 1→N ke HPA, dan `useCachedMetrics` (bawaan
  `false` [F, dokumentasi KEDA 2.17]; ditulis eksplisit di ScaledObject). Bila GKE dipilih (P2), cek setara untuk
  *metrics-server* dan pemasangan KEDA di GKE. Resolusi *metrics-server* per platform dan akibatnya bagi arti H2: 19.3.9.
- **(g) Aturan *adapter* CPU untuk H2p (baru di v0.2).** Di kind: nilai metrik kustom H2p cocok dengan CPU per *pod* dari
  Prometheus; rasio metrik/target ≈ 1 pada L\*. Perlakuan *pod* baru (diperbarui 2026-10-19; tinjauan *red team* v0.5 M-2):
  kode HPA menjalankan logika *pod* belum siap dan *CPU initialization period* hanya bila `resource == v1.ResourceCPU`
  (`groupPods`), sedangkan `GetMetricReplicas` untuk metrik Pods memberi nama sumber daya kosong [F, `replica_calculator.go`,
  cabang *master*; dicek ulang pada *tag* versi klaster di gerbang 1]. [BD] sebelumnya tertutup: perlakuannya berbeda bila
  deret H2p memuat *pod* yang belum siap. Penyamaan lewat deret "hanya *pod* yang Ready sepanjang 60 s" (19.3.1) diuji di kind dengan *scale-up*
  nyata: jumlah replika yang diminta H2 dan H2p pada langkah yang sama, dengan *pod* baru yang belum siap atau baru Ready (< 60 s), harus sama
  (toleransi satu replika). Bila tidak sama, kontras H2 → H2p ditulis "jalur ukur + perlakuan *pod* baru" (paket; 19.4.6).

**Aturan D1 — desain ulang *shipping* (bersyarat; ditulis 2026-10-18, sebelum cek dijalankan).**

| Butir | Isi | Status |
|---|---|---|
| D1-a konstruk | CPU per *pod shipping* baru pada C_SLO < 0,8 × *request* (200m), dengan cadangan c_D1: **lolos bila rata-rata + 2 SD bacaan CPU 60 detik per *pod* pada C_SLO < 200m pada N = 1 dan N = 2–3 *pod*** (tinjauan *red team* v0.5 K-1), dari ulangan *ladder* baru; SD = sebaran bacaan *metrics-server* 60 detik per *pod* (yang dilihat HPA) di bagian stabil langkah C_SLO, digabung dari semua ulangan *ladder* sehingga variasi antar-ulangan ikut masuk (tinjauan *red team* v0.5 m-3) | diputuskan pemilik 2026-10-18. Bacaan yang dipakai HPA (B), SD diukur (B-rumus), 2σ ≈ batas satu sisi 97,7% (B-konv). Toleransi 10% (HPA bertindak di 220m) tetap menjadi cadangan tambahan. *Ladder* K1 hanya mencatat rata-rata per langkah, jadi SD baru ada dari *ladder* baru |
| D1-b′ mekanisme (menggantikan D1-b, 2026-10-19) | jeda pemicu H1 di belakang konfigurasi laju pada ramp *gradual* *shipping*, dari angka terukur tanpa model: H1 terpicu bila CPU(C) + c_tolak × (λ − C) > 220m, jadi λ_H1 = C + (220m − CPU(C)) / c_tolak; laju terpicu di 0,88 × C; Δt = (λ_H1 − 0,88 × C) / s dengan s = kemiringan ramp; **lolos bila Δt ≥ 15 s** (satu siklus HPA, logika δ_min) pada N = 1 dan N = 2–3 | diputuskan pemilik 2026-10-19 (tinjauan *red team* v0.5 M-3) [B-rumus: rumus dan toleransi HPA, masukan *ladder*]. Pertanyaan daya ditangani b = 10 dan tabel efek terdeteksi (19.3.7, P23) |
| Lolos keduanya | *shipping* didesain ulang (*bulkhead*); Hipotesis 1 dan hipotesis kalibrasi diuji (19.4) | — |
| Gagal salah satu | *shipping* K1 apa adanya; Hipotesis 1 tetap "tidak dapat diuji" (vonis K1); fraksi pemicu dan prediksi model dilaporkan sebagai prediksi terhitung (jalur *red team*); hipotesis kalibrasi dilaporkan deskriptif per layanan | — |

- **Model fluida (dulu "model D1-b"; perannya diubah pemilik 2026-10-19, tinjauan *red team* v0.5 M-3).** Model tidak lagi
  memutuskan D1; D1 diputuskan oleh D1-a dan D1-b′ (tabel di atas), yang memakai angka terukur tanpa model. Model dipakai
  untuk: prediksi eksploratori (termasuk f = 0,7 dan *request* 500m / = CPU(C)), dan perhitungan δ_min *gradual* (19.3.7).
  Kurva fraksi buruk(laju per *pod*) diambil dari *ladder* baru sebagai fungsi terukur, bukan fungsi tangga di C_SLO
  (*auth* K1: fraksi buruk sudah 3,3% pada C_SLO dan naik mulus). *Back-test* K1 di bawah tetap dijalankan, tetapi hanya
  sebagai cek arah: lebar interval K1 (0,011–0,086) tidak cukup untuk memvalidasi besaran pada resolusi δ_min, dan K1 tidak
  memuat rezim *shipping* dibatasi slot. Model fluida tinjauan *red team* Part 17 (Lampiran A.5 dan B.1), ditulis ulang
  sebagai skrip repositori sebelum cek dijalankan.
  - **Isi:** langkah 1 s; *pod* siap 18 s (diganti angka terukur); *sync* HPA 15 s; toleransi 10%; batas *scale-up*
    max(100%, 4 *pod*) per 15 s; untuk Resource CPU, *pod* belum siap dihitung 0% saat *scale-up* dan HPA tidak
    menskalakan bila arah terbalik; CPU di-*refresh* tiap 60 s dengan fase acak, nilai = rata-rata 60 s terakhir; laju dari
    `rate` 60 s atas *scrape* 15 s berfase acak; fraksi buruk = (λ − N_siap × C_SLO)₊ / λ di jendela beban; 150–200 undian
    fase per sel.
  - **Masukan:** C_SLO, kurva CPU(laju), biaya menolak, dan waktu *pod* siap dari *ladder* baru; bentuk beban yang sudah
    diputuskan (*gradual* 300 s + tahan 120 s, λ0 = 0,2 × C_SLO, r dari P5, f = 0,8); M dari 19.3.2.
  - **Validasi lebih dulu (*back-test* K1) [B-konv: interval 95%]:** model dijalankan dengan setelan K1 (ambang, target,
    beban, kapasitas K1). Diterima bila tanda selisih H2 − H3 dan H1 − H3 pada *spike* dan *gradual* cocok dengan data K1
    dan besarnya berada di dalam interval kepercayaan 95% data K1. Bila tidak lolos, model diperbaiki sebelum dipakai;
    (Karena model tidak lagi memutuskan D1, *back-test* ini hanya cek arah; lihat paragraf pembuka.)
  - **Daya (tidak lagi bagian dari D1):** σ = SD tak berpasangan *shipping spike* K1 (0,031) sebagai nilai konservatif; SD *gradual* K1
    (0,002–0,008) tidak dipakai karena terkena efek lantai. Uji sesuai P8, dua sisi, α = 0,05 (keluarga *intersection-union*,
    19.4.8). b = 10 (P23, diputuskan pemilik 2026-10-19: pembenaran sumber daya + analisis sensitivitas daya, 19.3.7).
  - **Alternatif yang ditolak:** simulator HPA lengkap (terlalu mahal untuk sebuah cek); perkiraan kualitatif tanpa model
    (tidak dapat diputuskan).
  - Model yang sama dipakai untuk δ_min *gradual* dan margin non-inferioritas (19.3.7).
- **Rancangan *shipping* baru: T_svc, C, dan W (diputuskan pemilik 2026-10-19).** Kapasitas satu *pod* menurut hukum
  Little: C ≈ W / T̄_svc. T_svc hampir seluruhnya menunggu *carrier-mock*: tiga *carrier* dengan jeda dasar 220/360/520 ms
  ditambah tambahan per zona dan *jitter*, dikali `CARRIER_DELAY_SCALE` (`carrier_service.py`); pada *scale* 1,0 p95
  ±917 ms [F, *ladder* K1]. Batasan: SLO 1.000 ms (19.3.3), D1-a (CPU rata-rata + 2 SD pada C < 200m), W bilangan bulat.
  - **T_svc [B-konv] (jangkar diganti pemilik 2026-10-19; tinjauan *red team* v0.5 m-1):** `CARRIER_DELAY_SCALE` dipilih
    agar **p95 bawaan *shipping* pada laju rendah = 0,5 × SLO (500 ms)**: separuh SLO sebagai sela, tidak bergantung pada
    sifat *auth*. Jangkar sebelumnya (p95 *shipping* ≈ p95 *auth* pada λ0) ditolak karena p95 *auth* didominasi ekor *login
    bcrypt* (p50 6 ms), dan bila p95 *auth* di platform baru lebih tinggi, sela *shipping* ikut menyempit. Ilustrasi K1:
    p95 *auth* pada 2 req/s 514 ms dan p95 *shipping* pada 10 req/s 916 ms (*red team* v0.5 Lampiran A.7), jadi kedua
    jangkar memberi angka serupa: *scale* ≈ 500 / 916 ≈ 0,55. Alternatif yang ditolak: *scale* 1,0 seperti K1 (sela ±83 ms,
    C_SLO rapuh; *ladder* ke-2 p95 tepat 1.000 ms pada 50 req/s); jangkar ≈ *auth* (di atas).
  - **C dan W [B-rumus]:** C_target = C terbesar pada grid 2 req/s yang lolos D1-a (dari CPU diam, CPU per permintaan, dan
    SD terukur) dan D1-b′ (mekanisme Δt ≥ 15 s, tabel di atas); W = bulat(C_target × T̄_svc), dengan T̄_svc rata-rata waktu layanan pada **laju rendah tetap dengan rata-rata permintaan di dalam *pod* ≤ 1** (λ ≤ 1 / T̄_svc, ±2 req/s; di bawah titik jenuh waktu layanan tidak bergantung beban, hukum Little; tinjauan *red team* v0.5 m-2), bukan pada λ0, sehingga urutan C_SLO → λ0 tidak melingkar. Ini
    rancangan paling realistis (CPU paling dekat ke pemicu H1) yang masih membuat Hipotesis 1 dapat diuji, jadi sengaja
    berpihak melawan efek H1 dan menjawab kritik "dibatasi slot karena rancangan". Ilustrasi (CPU per permintaan K1 ±6–7
    ms: 266m pada 40 req/s, 377m pada 50 req/s; SD ±10m; *scale* ±0,55 → T̄_svc ±0,4 s): C ≲ 23 req/s, W ±9. Alternatif yang ditolak: W = 25,
    bawaan Resilience4j `maxConcurrentCalls` [F, dokumentasi Resilience4j *Bulkhead*, dicek 2026-10-19] — dengan
    T̄_svc ±0,5 s, C ≈ 50 dan CPU ≈ 330m sehingga D1-a gagal, dan agar lolos T_svc harus ≥ ±1,1 s (melewati SLO);
    CPU(C) ≤ 0,5 × *limit* = 250m (Part 17; tidak konsisten dengan D1-a); C kecil dengan celah CPU besar (memperkuat
    kritik "karena rancangan").
  - **Urutan (bagian *ladder* baru, sebelum D1 diputuskan):** (1) kind: *flag bulkhead*, CPU per permintaan dan CPU diam
    (indikatif); (2) *ladder* di platform: tetapkan *scale* agar p95 bawaan *shipping* pada laju rendah = 500 ms → ukur T̄_svc (laju rendah tetap), p95, CPU per
    permintaan, dan SD; (3) grid C: D1-a dan D1-b′ per kandidat, pilih C terbesar yang lolos, hitung W; (4) *ladder*
    konfirmasi *shipping* dengan W final: C_SLO, laju runtuh, K = C_SLO × SLO (19.3.3); λ0 = 0,2 × C_SLO dihitung sesudahnya; (5) bila tidak ada C yang lolos, D1 gagal
    dan *shipping* K1 dipakai.
  - **Sensitivitas:** tinggi untuk premis Hipotesis 1 (celah CPU(C) ke pemicu H1) dan untuk r (laju runtuh *shipping*
    baru); karena itu C diambil dari aturan, bukan dari efek yang tampak di pilot.
- D1 diputuskan sebelum gerbang 2 selesai, dicatat bertanggal, dan tidak dibuka lagi setelah pilot kecuali sebagai
  deviasi bertanggal.
- D1-b′ sengaja hanya memakai pola *gradual*: pada *spike* biaya menolak diperkirakan membuat CPU tetap bereaksi, dan itu
  sudah ditangani dengan memilih *gradual* sebagai pola utama (19.4.1), bukan alasan menolak desain ulang.
- D1 tidak bergantung pada H2p: Hipotesis 2 dan rantai H2 → H2p → H3 → K1 tetap diuji pada kedua cabang D1.

### 19.3.6 Pilot penuh

- **Masalah di K1 [F].** Pilot hanya *spike*, 2 repetisi, tanpa H1, *gradual*, dan *oscillating* (Part 17 §17.23.1);
  analisis lengkap baru dijalankan setelah 180 *run*. Isu seperti gerbang gagal, *bug bin* O1, O3 = O2, aturan SLO, dan
  target H1 70 → 80% ketahuan setelah data.
- **Aturan.** Setiap layanan × pola dengan ketujuh konfigurasi, 2 blok per strata (4 strata × 2 blok × 7 = 56 *run*,
  ±16,5–17,5 jam mesin *(est.; ±17,5–18,5 menit per run dengan langkah per run 19.3.10)*, ditambah *run* cek *scale-down*
  berekor panjang (19.3.10)), urutan acak. Skrip analisis lengkap
  dijalankan, draf tabel dan gambar BAB 4 dibuat dari data pilot, dan definisi setiap keluaran diperiksa (redundansi,
  satuan, apa yang sebenarnya diukur).
- **Fungsi pilot (diputuskan pemilik 2026-10-19; tinjauan *red team* v0.5 K-2):** gladi *pipeline* dan analisis ujung ke
  ujung, cek konstruk (termasuk kesetaraan pemicu pada N *pod*, 19.3.1), dan cek asumsi. Pilot **tidak** dipakai untuk
  menetapkan b, SENS-f, atau status komponen uji, karena 2 blok per strata hanya memberi 1 derajat bebas per sel. σ pilot
  hanya dipakai untuk memperbarui laporan efek terkecil yang terdeteksi (19.3.7): SD selisih di dalam blok, terpool per
  strata (layanan × pola) atas kontras yang diuji, dilaporkan dengan batas atas kepercayaan 80% (Browne, 1995, *Stat Med*
  14:1933–1940; faktor s × √(ν / χ²₀,₂;ν): 3,95 pada ν = 1, 1,73 pada ν = 3, 1,40 pada ν = 6).
- **Jumlah repetisi:** b = 10 blok per strata, ditetapkan sebelum pilot (19.3.7, P23).
- **Bila pilot memunculkan masalah:** perbaiki dan ulangi pilot. Data pilot tidak dipakai untuk menguji hipotesis.

### 19.3.7 Blok, daya, dan δ_min

- **Blok (tinjauan *red team* M-7).** Satu blok = satu layanan × satu pola × tujuh konfigurasi, dengan urutan acak di dalam
  blok; urutan blok diacak antar-sesi klaster dan sesinya dicatat. Semua kontras berada di dalam satu layanan dan pola,
  jadi blok tidak perlu memuat strata lain, dan *run* yang dipasangkan berjarak paling jauh ±2,1 jam *(est.; 7 × ±18 menit; tinjauan *red team* v0.5 m-9)*, bukan ±10–12 jam seperti
  blok berisi semua sel [P; rancangan blok acak lengkap: blok dibuat sehomogen mungkin]. B2 di setiap blok sekaligus
  memeriksa pergeseran kapasitas.
- **Daya.** Simulasi daya memakai sebaran **tak berpasangan**, karena di K1 pemblokan tidak terbukti mengurangi varians:
  untuk H2 − H3 pada *spike* (fraksi permintaan buruk, SLO 1.000 ms), SD selisih berpasangan 0,033 (*auth*) dan 0,024
  (*shipping*) vs tak berpasangan 0,035 dan 0,031, dengan korelasi residu +0,11 dan +0,51 [H, dihitung ulang 2026-10-18
  dari data mentah; cocok dengan tinjauan *red team* A.3]. Keuntungan pasangan adalah ketahanan terhadap efek sesi, bukan
  daya. b ditetapkan sebelum pilot (di bawah, P23); yang mengikat adalah uji utama dengan efek terkecil, kemungkinan efek jenis
  sinyal (H2p → H3): model kasar *red team* memperkirakan ±0,05 (*auth*) dan ±0,02 (*shipping*) fraksi permintaan buruk
  pada *spike* 4,5 × C [H, model, Lampiran B.1 tinjauan]; untuk efek ±0,02 dengan SD ±0,03, daya pada b = 8 hanya ±0,15
  (Lampiran A.4 tinjauan), jadi b kemungkinan ≥ 10 dan efek sinyal *shipping* mungkin hanya terbaca sebagai estimasi.
  Simulasi daya memakai uji yang diputuskan (P8: Wilcoxon *signed-rank* eksak pada selisih di dalam blok) dengan ρ = 0
  sebagai asumsi konservatif, dan ρ pilot dilaporkan. Cek 2026-10-19 [H, simulasi, efek 0,03, σ 0,03]: pada ρ = 0,11
  daya *signed-rank* 0,37 / 0,52 (b = 8 / 10) vs Mann–Whitney 0,44 / 0,51; pada ρ = 0,51 daya 0,60 / 0,78 vs 0,43 / 0,51;
  galat tipe I *signed-rank* pada b = 10, α 0,05: 0,044.
- **Jumlah blok b dan analisis sensitivitas daya (diputuskan pemilik 2026-10-19; tinjauan *red team* v0.5 K-2).** b
  ditetapkan **sebelum pilot** dengan pembenaran sumber daya disertai analisis sensitivitas daya (Lakens, 2022, "Sample
  Size Justification", *Collabra: Psychology* 8(1), doi 10.1525/collabra.33267: keterbatasan sumber daya adalah pembenaran
  yang sah bila disertai evaluasi daya untuk rentang efek). Efek terkecil yang terdeteksi (daya 0,8, *signed-rank* dua
  sisi 0,05, ρ = 0) dilaporkan di muka [H, simulasi 2026-10-19]:

| σ fraksi buruk | b = 8 | b = 10 | b = 15 | b = 20 |
|---|---|---|---|---|
| 0,01 | 0,018 | 0,014 | 0,011 | 0,010 |
| 0,02 | 0,035 | 0,029 | 0,022 | 0,019 |
| 0,03 (konservatif; K1 H1 *shipping gradual* ±0,028) | 0,053 | 0,044 | 0,034 | 0,029 |
| *Run* kampanye (28 × b) | 224 | 280 | 420 | 560 |

  σ di tabel adalah SD fraksi buruk **per konfigurasi** (simulasi memakai dua konfigurasi dengan σ yang sama, jadi SD
  selisih = σ√2). σ per konfigurasi K1 *spike* ≈ 0,022 (*shipping*) – 0,025 (*auth*), dari SD selisih tak berpasangan
  0,031–0,035 / √2 [H, data K1 di atas]; pada σ itu efek terkecil yang terdeteksi dengan b = 10 ≈ 0,032–0,037. Efek
  terkecil itu kira-kira sebanding lurus dengan σ (≈ 0,044 × σ / 0,03 pada b = 10).

  **Kontras Hipotesis 2 (dicek 2026-10-19) [H, simulasi, *signed-rank* satu sisi 0,025, b = 10, ρ = 0]:** D1 = H2p − K1
  (varians 2σ²) dan D2 = H2p + K1 − 2 × H3 (varians 6σ², SD √3 × lebih besar). Efek terkecil yang terdeteksi: D1 0,031 /
  0,036 / 0,043 dan **D2 0,054 / 0,063 / 0,074** pada σ 0,022 / 0,025 / 0,030. Jadi putusan S > |E| hanya dapat
  disimpulkan bila S + E kira-kira ≥ 0,05–0,07; ini ditulis di muka sebagai batas daya Hipotesis 2, bukan prediksi efek.
  Cek ulang tabel di atas dengan *seed* lain: 0,015 / 0,028 / 0,043 pada b = 10 (cocok dalam derau simulasi).

  Sebagai pembanding, δ_min 0,014–0,027: pada σ 0,03 tidak ada b ≤ 20 yang dapat mendeteksi efek sebesar δ_min, jadi efek
  di sekitar δ_min hanya terbaca sebagai estimasi, dan ini ditulis di muka. **b = 10** (diputuskan pemilik 2026-10-19, P23): 280 *run* kampanye (±84 jam mesin *(est.)*); efek terkecil yang terdeteksi ±0,032–0,037 pada σ K1 *spike*, 0,044 pada σ 0,03; dasar: pembenaran sumber daya + analisis sensitivitas daya (Lakens, 2022). Alternatif: b = 8 (sah, tetapi langkah Holm hanya tahan kehilangan satu pasangan), b = 15–20 (efek terkecil 0,029–0,034 pada σ 0,03).
- **Aturan cadangan berbasis daya (P22): dihapus 2026-10-19** (tinjauan *red team* v0.5 K-2). Alasannya: σ pilot dari n = 2
  per sel tidak andal, dan aturan itu secara sistematis menurunkan komponen non-inferioritas *auth*, satu-satunya
  komponen yang dapat membantah klaim "CPU tetap kompetitif". Semua komponen *intersection-union* yang dipra-registrasi
  tetap menjadi uji. Hasil yang tidak lolos karena daya rendah dilaporkan "tidak dapat disimpulkan" beserta daya dan
  efek terkecil yang terdeteksi, bukan sebagai bukti tidak adanya efek. Catatan daya non-inferioritas (cek 2026-10-19
  [H, simulasi, selisih sebenarnya 0, satu sisi 0,025]): margin 0,014 → daya 0,78 / 0,28 / 0,14 pada σ 0,01 / 0,02 /
  0,03 dan b = 10; margin 0,027 → 1,00 / 0,74 / 0,42.
- **δ_min [B-konv; turunannya B-rumus] (diputuskan pemilik 2026-10-19, P15; label diperbaiki setelah *red team* v0.5 M-12).** Perubahan keluaran primer akibat keterlambatan satu periode
  *sync* HPA (15 s, dokumentasi), dihitung per pola dari angka *ladder* sebelum pilot. Untuk *spike*: (1 − 1/r) × 15 / 420
  fraksi permintaan buruk. Turunan (dicek 2026-10-19): bila seluruh lintasan kapasitas bergeser 15 s dan naik dari C ke
  r × C di dalam jendela, kekurangan tambahan = 15 × (r − 1) × C; dibagi permintaan total r × C × 420 → (1 − 1/r) × 15 /
  420 (batas atas bila kapasitas tidak sampai r × C). Angka: ±0,014 pada r = 1,65 (bila *shipping* K1 tetap), ±0,027
  pada r = 4. Untuk *gradual* dihitung dengan model fluida (19.3.5). Margin non-inferioritas (19.4.1) memakai aturan yang sama.
  Alternatif yang ditolak: angka tetap (mis. 0,02) atau relatif terhadap H3 (bergantung lantai) — keduanya tanpa dasar.
  Label B-konv: 15 s adalah pilihan efek terkecil yang dianggap penting (satu siklus keputusan HPA, yaitu granularitas
  *controller*), bukan hasil ukur; aritmetika turunannya B-rumus. Sensitivitas: putusan non-inferioritas dan tingkat
  "bermakna" (19.4.8) dihitung ulang pada ½ × dan 2 × δ_min sebagai analisis eksploratori.

### 19.3.8 Sebelum kampanye

- **Keluaran primer (diputuskan pemilik 2026-10-19, P7): fraksi permintaan buruk** = (gagal + lebih lambat dari SLO) /
  terkirim, di jendela k6 t 120–540 s, dari data mentah k6 per permintaan [B-konv: SLI sebagai rasio kejadian baik
  terhadap kejadian valid, Beyer dkk. 2016, Google SRE]. Kontinu, tanpa *bin*; δ_min (19.3.7), model fluida, dan σ daya
  (0,031) sudah dihitung dalam satuan ini. Komponennya (fraksi gagal = ditolak + *error*; fraksi lambat) dilaporkan
  deskriptif. O1 K1 (detik di atas SLO, *bin* 10 s, dipecah gagal vs lambat) dihitung sebagai keluaran sekunder untuk
  perbandingan dengan K1. Alternatif yang ditolak sebagai primer: O1 dipecah (diskretisasi *bin*, riwayat *bug bin* O1
  di K1, tidak peka besar pelanggaran, dan semua hitungan daya dan δ_min harus dibuat ulang). Yang lain sekunder. Tiga
  catatan wajib (tinjauan *red team* M-5):
  - **redundan:** di K1, fraksi permintaan buruk berkorelasi 0,98–0,99 dengan *error rate* pada *spike*, dan O1–O2 0,96
    [H, dihitung ulang];
  - **komposisi:** B2 *auth* sudah ±4% "lambat" pada SLO 1.000 ms karena ekor *login bcrypt* (fraksi buruk B2 *auth spike*
    0,041 [H, dihitung ulang]);
  - **lantai:** semua *autoscaler* mulai dari satu *pod*, jadi efek apa pun berada di atas lantai itu. Waktu sampai
    kapasitas cukup diperlakukan sebagai variabel mekanisme, bukan keluaran yang berdiri sendiri.
- **Aturan keputusan, keluarga uji, dan arah uji:** 19.4. Di K1, kriteria ditulis 10–11 Oktober setelah data, dan
  keluarga Holm tiga uji dipilih setelah repetisi 2.
- **Aturan pemilihan parameter dibekukan di gerbang 2, angkanya diisi di gerbang 4 (tinjauan *red team* O4, M-9):** r,
  W, C target, K, M, δ_min, dan margin non-inferioritas (f, aturan SLO, λ0, dan aturan r sudah diputuskan: 19.3.1, 19.3.3;
  angka r tetap dari *ladder* baru). Angka diambil dari pengukuran, bukan dari efek yang
  tampak di pilot. Catatan sensitivitas wajib untuk *request/limit* CPU 250m/500m (DEC; menentukan CPU(C)/*request*, jadi premis
  Hipotesis 1; klaim lewat rasio, sensitivitas di model, 19.4.1), `noConnectionReuse` (menentukan biaya per koneksi, jadi biaya menolak), dan jendela `rate` 1 menit yang
  dipakai bersama H2p dan H3.
- **Isolasi:** *node pool* atau *taint* terpisah untuk k6 dan *monitoring* vs layanan uji; penempatan *pod* dicatat. Di
  K1 tidak ada *taint* (3 × D4as_v5 dalam satu *pool*), dan pada sesi 1 seluruh 268 replika baru menumpuk di *node* k6
  (sesi 2: 288 dari 396).
- **Tata letak *pool* (pemilik 2026-10-19, P21) [B: protokol gerbang 7; tinjauan *red team* M-8 "tidak ada isolasi
  generator beban/SUT/monitoring"]:**

| *Pool* | Isi | Ukuran |
|---|---|---|
| `sut` (*taint*) | layanan uji, termasuk B2 | 1 × Standard_D16as_v5; ≥ 2 × replika tertinggi pilot, bila kurang D32as_v5 (19.3.2) |
| `load` (*taint*) | k6 saja (*request* 1.000m / 1 GiB, *limit* 2.000m / 4 GiB) | 1 × Standard_D2as_v5 (2 vCPU, 8 GiB; ±1.900m *allocatable*, Part 05) |
| `infra` (*pool* sistem) | kube-system (termasuk *metrics-server*), Prometheus, Grafana, KEDA, *prometheus-adapter* | 2 × Standard_D4as_v5 (±7.700m *allocatable*; *request* ±1.500m setelah dependensi dipindah). Dasar [B]: *pool* sistem AKS wajib ≥ 2 *node* dengan VM ≥ 4 vCPU dan 4 GB, tanpa seri B ("System pools must contain at least two nodes but the recommendation is three nodes", Microsoft Learn *Use system node pools*, dicek 2026-10-19); bebannya sendiri muat di satu *node* |
| `deps` (*taint*; diputuskan pemilik 2026-10-19, tinjauan *red team* v0.5 M-10) | *auth-db*, *carrier-mock* (5 replika) | 1 × Standard_D4as_v5 (*request* ±1.500m). Dasar [B]: keduanya berada di jalur permintaan layanan uji (SUT dalam arti fungsi), jadi diisolasi oleh desain dari *monitoring*, KEDA, dan *adapter*, alasan yang sama dengan `load` (P21); *pool user* boleh 1 *node* |

  - **Kenapa k6 terpisah dari `infra` dan `deps`:** jalur metrik Prometheus, *adapter*, dan KEDA (di `infra`) adalah bagian
    dari perlakuan H2p, H3, dan K1 tetapi tidak H1 dan H2 (*metrics-server*), sehingga gangguan k6 di sana bisa membiaskan
    kontras H2 → H2p secara sistematis; *auth-db* dan *carrier-mock* (di `deps` sejak v0.6, M-10) berada di jalur permintaan
    layanan uji, jadi latensinya bagian dari yang diukur (SUT dalam arti fungsi). Isolasi oleh desain lebih kuat daripada
    "diukur dan kecil". Alternatif (berbagi `infra`, Part 17 R10) dapat dibela dengan CPU k6 K1 yang kecil, tetapi
    bergantung pada pengukuran ulang.
  - **Kenapa D2as_v5 cukup untuk `load` [B, ukur K1]:** CPU k6 maksimum 0,135 core (*limit* 2) di 180 *run* (*red team*
    M-8); memori ±0,6 GiB untuk ±1.050 VU, sedangkan VU terbanyak K1 788 (Part 08). Keluarga Dasv5 sama (*non-burstable*);
    seri B (*burstable*) tidak dipakai karena kredit CPU membuat kecepatan generator tidak konstan (Part 04). *Allocatable*
    memori dicek setelah *node* dibuat. DaemonSet di `load`: kube-proxy, cloud-node-manager, dan *node-exporter* (metrik
    level *node*, gerbang 7).
  - **Cek pilot untuk `load`:** `dropped_iterations` k6 = 0 di setiap *run* dan rasio *throttling* k6 ≈ 0, CPU *node*
    `load` jelas di bawah kapasitas; bila gagal, `load` diganti D4as_v5 sebelum pembekuan.
  - **Disk OS (diputuskan pemilik 2026-10-19; tinjauan *red team* v0.5 N-3) [B]:** `--node-osdisk-type Managed` eksplisit
    untuk ketiga *pool*, karena seri Dasv5 tidak mendukung *Ephemeral OS Disk* dan tidak punya penyimpanan lokal
    (Microsoft Learn *Dasv5 size series*, dicek 2026-10-19). Jenis disk OS dicatat per *run* bersama versi. Perintah K1 di
    Part 05 menulis `Ephemeral`, tetapi label *node* yang terekam di ekspor K1 menunjukkan disk OS K1 sebenarnya *Managed*
    Premium SSD (`kubernetes_azure_com_storageprofile="managed"`, `storagetier="Premium_LRS"`, mis.
    `experiment-results-openloop/auth-service/b1/gradual/rep1/prom_cpu_usage.json`) [F, dicek 2026-10-19]. Jadi `Managed`
    sama dengan K1; naskah Thesis-2.3 yang menyebut *Ephemeral OS disk* perlu dikoreksi (Part 20).
- **Perangkat keras antar-sesi (diputuskan pemilik 2026-10-19; tinjauan *red team* v0.5 M-9) [B].** Seri Dasv5 memakai dua
  generasi CPU (EPYC 7763v dan EPYC 9004; Microsoft Learn *Dasv5 size series*, dicek 2026-10-19), dan setiap kali AKS
  dihentikan lalu dijalankan, VM baru bisa jatuh di generasi lain. Karena itu klaster **tidak dihentikan** sejak *ladder*
  baru sampai kampanye selesai, sehingga VM `sut` tetap sama; jam *idle* bukan batasan (anggaran bukan batasan desain).
  `lscpu` (model CPU, *thread* per inti) dicatat setiap *node* **per *run*** (bukan per sesi; Dasv5 mendukung *live migration*, Microsoft Learn *Dasv5 size series*); bila berbeda dari *run ladder* (mis. setelah
  *live migration* atau pemeliharaan), berlaku aturan henti sesi di 19.3.11.
- **Isi klaster (pemilik 2026-10-19):** hanya layanan uji dan dependensinya, sesuai *manifest*: *auth-service* →
  *auth-db* (PostgreSQL, `DATABASE_URL`); *shipping-rate-service* → *carrier-mock* (`CARRIER_SERVICE_URL`; tetap 5 replika
  250m/500m seperti K1 dan dicek tidak menjadi hambatan, Part 17 R22/CS-R11). k6 menembak layanan langsung lewat alamat
  dalam klaster, tanpa *api-gateway* (`target_url` di metadata K1), jadi *product*, *cart*, *order*, *payment*, *frontend*,
  *api-gateway*, *product-db*, *order-db*, dan *redis* tidak dipasang (di K1 masing-masing 1 replika tanpa beban; sejalan
  dengan Part 17 D-R16). Arsitektur aplikasi lengkap tetap dijelaskan di BAB 3 sebagai konteks sistem.
- **Versi:** *digest image* dan versi *chart* dikunci; versi Kubernetes dan *add-on* dicatat otomatis per *run*. Di K1
  *image* `:latest`, versi *prometheus-adapter* tidak tercatat, versi KEDA hanya dari tabel AKS.
- ***Pod* baru setiap *run*.**
- **Pembekuan:** di-*commit* dan di-*tag* (gerbang 5); perubahan setelahnya dicatat sebagai deviasi bertanggal; aturan
  berhenti kampanye tertulis.

### 19.3.9 Resolusi *metrics-server* per platform dan arti H2 (dicek 2026-10-18)

- **Upstream [F].** FAQ *metrics-server*: "Default 60 seconds, can be changed using `metric-resolution` flag"; nilai di
  bawah 15 s tidak disarankan karena kubelet sendiri menghitung metrik tiap 15 s. Manifest resmi
  (`manifests/base/deployment.yaml`, sumber `components.yaml`) dan `defaultArgs` *Helm chart* resmi menyetel
  `--metric-resolution=15s`. Jadi 60 s adalah bawaan program bila dijalankan tanpa *flag*; pemasangan standar memakai 15 s.

| Platform | Resolusi bisa diubah? | Rincian | Arti H2 bila platform ini dipakai |
|---|---|---|---|
| **AKS** | **Tidak didukung** | *Add-on* terkelola. Satu-satunya kustomisasi terdokumentasi: ConfigMap `metrics-server-config` dengan `NannyConfiguration` (ukuran CPU/memori *pod metrics-server*), bukan *flag* [F, dokumentasi AKS]. Moderator Microsoft (Q&A, 2021): *add-on* berlabel Reconcile dikembalikan oleh *addon-manager*, pengguna AKS tidak dapat mengakses `$ADDON_PATH`, dan Microsoft "strongly recommend against forcing changes to kube-system" [F]. Tidak ada cara terdokumentasi untuk mematikan *metrics-server* bawaan. K1: bacaan CPU HPA berganti tiap ±61 s, jadi AKS memakai bawaan 60 s [F, data K1] | jalur lambat 60 s; H2 → H2p paling informatif; H2p satu-satunya jalan ke CPU yang lebih segar |
| **EKS** | **Ya**, bila dipasang sendiri | *metrics-server* tidak terpasang secara bawaan. Lewat manifest atau Helm: 15 s, *flag* bebas diubah. Lewat EKS *community add-on*: EKS mengelola sebagian *field* dengan *server-side apply*, dan mengubah *field* yang dikelola EKS bisa tertimpa saat pembaruan [F, dokumentasi EKS]; apakah skema konfigurasinya membuka *flag* resolusi belum dicek (`aws eks describe-addon-configuration --addon-name metrics-server`) [BD] | ±15 s, jadi H2 ≈ H2p kecuali resolusi sengaja diubah; bukan pilihan P2, dicatat untuk generalisasi |
| **GKE** | **Angkanya tidak dapat diatur**; ada sakelar jalur cepat | `metrics.k8s.io` dilayani `kube-system/metrics-server`; resolusinya tidak didokumentasikan [BD]. **Performance HPA profile**: "enables faster autoscaling on CPU and Memory metrics … by routing autoscaling metrics through the gke-metrics-agent DaemonSet" (release note 2025-03-21); referensi API: "faster metrics collection"; aktif secara bawaan di Autopilot ≥ 1.32.1-gke.1729000 dan Standard ≥ 1.33.2-gke.4605000 (sejak 2025-08-01) bila syaratnya terpenuhi; diatur dengan `gcloud container clusters update … --hpa-profile=performance\|none`. Tidak ada angka kesegaran resmi; dokumentasi *troubleshooting* menyebut jeda 15–30 s dari metrik melewati ambang sampai penskalaan sebagai normal [F] | jalur cepat profil dengan kesegaran yang belum diketahui (harus diukur di pilot); profil berlaku untuk seluruh klaster, jadi tidak dapat divariasikan di dalam blok; H2 → H2p kemungkinan lebih kecil daripada di AKS |

- **Akibat untuk desain.**
  1. Di AKS, H2 → H2p mengukur "*metrics-server* terkelola AKS (60 s) vs CPU lewat Prometheus (15 s)"; klaimnya ditulis
     bersyarat pada platform.
  2. Bila GKE dipilih, selang pembaruan bacaan CPU HPA diukur di pilot (seperti median 61,2 s di K1), dan status
     Performance HPA profile dicatat per *run*.
  3. Batas generalisasi: keunggulan laju yang berasal dari jalur ukur bergantung pada kesegaran CPU di platform. Di
     platform dengan CPU lebih segar (EKS dengan pemasangan standar, GKE dengan profil Performance), bagian itu diperkirakan
     mengecil, sedangkan efek jenis sinyal (H2p → H3) tetap bermakna lintas platform.
- **Untuk naskah K1:** kalimat "*metrics-server* secara bawaan 60 detik" perlu dipersempit menjadi sifat *metrics-server*
  terkelola AKS; dicatat di [20-perbaikan-naskah-thesis-2.4.md](20-perbaikan-naskah-thesis-2.4.md).
- **Status:** B (dokumentasi resmi dan data K1), kecuali butir bertanda [BD].

### 19.3.10 Bentuk dan durasi *run* (keputusan pemilik, 2026-10-18)

- **Keputusan [DEC, pemilik].** *Run gradual* tidak boleh lebih panjang dari *run spike*; keduanya memakai bentuk dan
  durasi K1. Ekor tetap 180 s seperti K1; replika-detik dan CPU-detik dibandingkan hanya di jendela beban; *scale-down*
  cukup dicek di pilot.
- **Bentuk [F, `k6-openloop-pilot.yaml`, `rateStages`]:**

| Fase | *Spike* | *Gradual* |
|---|---|---|
| Pemanasan | 120 s pada λ0 | 120 s pada λ0 |
| Beban | naik ke λp dalam 10 s, tahan 410 s | *ramp* linear λ0 → λp selama 300 s, tahan 120 s |
| Turun (ekor) | 180 s linear ke 0 | 180 s linear ke 0 |
| Total skenario | 720 s | 720 s |

- **Dasar:** kontinuitas K1 [B-konv] dan keputusan pemilik. Jendela analisis primer [120 s, 540 s) sama untuk kedua pola,
  sehingga δ_min (19.3.7) dan semua keluaran dihitung pada jendela yang sama. Di K1 waktu per *run* median 1.206 s
  (±20 menit; 1.166–1.299 s, `metadata.json` 180 *run*), termasuk *overhead* ±486 s [F]; rincian langkah dari `pilot.log` K1
  (median *auth* / *shipping*): *cleanup* + *pre-auth* 50 / 9 s, `RESET_WAIT` 122 s, pasang konfigurasi 5 / 4 s, `STABILIZE_WAIT`
  92 s, Job k6 735 / 745 s, `EXPORT_WAIT` 181 s, ekspor 13 s, metadata ±10 s [F]. Dengan langkah per *run* di bawah dan
  *Deployment* baru setiap *run* (+±15–45 s untuk hapus *pod* lama dan *pod* baru siap),
  ±1.050–1.110 s (±17,5–18,5 menit) *(est.)*, ditambah rata-rata 7,5 s penundaan acak (N-1).
- **Alternatif yang ditolak:** (a) aturan *ramp* aman Part 17 D-R9(a), T_ramp 300–1.100 s (contoh kasar *auth* ±1.300 s),
  25–38,5 menit per *run*: terlalu lama dan tidak sama dengan *spike* (pemilik); tinjauan *red team* Part 17 juga menilai
  *ramp* aman menghasilkan efek lantai (K-2) dan T_ramp sebagai penggerak biaya terbesar. (b) Ekor ≥ 450 s (Part 17 R37,
  dari tinjauan Part 14 F4) untuk mengamati *scale-down* penuh: +±4,5 menit per *run* untuk keluaran yang hampir
  ditentukan rancangan (di bawah).
- **Kenapa *scale-down* tidak dibandingkan:**
  - tidak ada hipotesis yang menyangkut *scale-down*; Hipotesis 1, 2, dan kalibrasi diukur di jendela beban;
  - *spike* dan *gradual* berpuncak tunggal, jadi kecepatan *scale-down* tidak memengaruhi mutu beban berikutnya, hanya
    biaya (pola yang mengujinya, *oscillating*, sudah dihapus);
  - jendela stabilisasi 300 s sama untuk semua konfigurasi: model tinjauan Part 14 (F4) menaruh 80–84% pod-detik
    berlebih di ekor akibat jendela yang identik itu, jadi ekor terutama mengukur nilai bawaan, bukan jalur atau sinyal;
  - "penghematan" terhadap B2 (N *pod* tetap) membesar seiring panjang ekor yang diamati, jadi angkanya ditentukan pilihan
    pengamat.
  Karena ekor 180 s < 300 s, *scale-down* akibat beban turun tidak sempat terjadi di dalam *run*; perbandingan di jendela
  beban tidak bergantung pada ekor. Kalimat untuk naskah: biaya setelah beban turun ditentukan jendela stabilisasi 300 s yang sama untuk semua
  konfigurasi (dokumentasi HPA), sehingga tidak dibandingkan.
- **Cek *scale-down* di pilot (cek konstruk, bukan data tesis):** satu sampai dua *run* per konfigurasi dengan ekor ≥ 450 s
  pada λ0 (turunan Part 17 R37: jendela 300 s + jendela *rate* 60 s + umur bacaan ±60 s + *sync* 15 s + cadangan). Lolos
  bila setiap konfigurasi turun skala setelah ±300 s tanpa *flapping* (tidak ada *scale-up* ulang pada λ0); *scale-down*
  selama tahan, bila ada, dicatat sebagai temuan. Hasilnya masuk lembar konstruk (gerbang 1).
- **Sensitivitas:** tidak ada pada keluaran primer (jendela beban tidak berubah); keluaran efisiensi menjadi "selama
  beban", bukan total biaya *run*.

**Langkah per *run* dan waktu tunggunya (diputuskan pemilik 2026-10-19; paket minimal).** Urutan dan waktu tunggu K1
(`run-pilot-openloop.sh`) dipertahankan, kecuali tunggu ekspor dan *pre-pull image*.

| Langkah | Nilai | Dasar |
|---|---|---|
| *Reset*: hapus *autoscaler* (`kubectl wait --for=delete`, *timeout* 60 s) dan *Deployment* lama, *pre-auth* login *auth* | `RESET_WAIT` **120 s** (tetap seperti K1) | Kontinuitas K1 [B-konv]. Menjamin ≥ 120 s antara lonjakan bcrypt *pre-auth* (±28 s, Part 08) dan pemasangan H1/H2, apa pun urutan *pre-auth* terhadap *Deployment* baru |
| Pasang konfigurasi: *Deployment* baru (UID *pod* dicatat), `rollout status` (*timeout* 180 s), lalu *autoscaler* | `STABILIZE_WAIT` **90 s** (tetap seperti K1) | Kontinuitas K1 [B-konv]; ≥ bacaan *metrics-server* AKS ±61 s + 1 *scrape*; sama untuk semua konfigurasi, jadi umur *pod* saat beban mulai seragam |
| Penundaan acak sebelum Job k6 (diputuskan pemilik 2026-10-19; tinjauan *red team* v0.5 N-1) | **U(0, 15) s per *run***, dengan *seed* tercatat; fase relatif terhadap siklus HPA dicatat sebagai kovariat | randomisasi memutus penyelarasan deterministik fase siklus HPA 15 s terhadap *onset* (objek HPA dibuat pada jarak tetap sebelum *onset*). Bukti K1: 91% kenaikan replika pertama jatuh dalam pita 3,5 s modulo 15 s (tinjauan *red team* v0.5 Lampiran A.8). Siklus 60 s *metrics-server* tidak terikat pada saat objek HPA dibuat, jadi tidak perlu diacak. Rata-rata +7,5 s per *run* |
| Job k6: pemanasan 120 s di dalam skenario 720 s | tetap | P20, Part 17 R33 |
| Ambil dan verifikasi data mentah (md5, `gzip -t`) | tetap | integritas data K1 |
| Tunggu sebelum ekspor | **`EXPORT_WAIT` 180 → 30 s** | 2 × *scrape* 15 s [B-rumus]. Fungsi lamanya ("*cooldown capture*", merekam *scale-down*) gugur sejak P20; jendela beban berakhir di 540 s dan skenario di 720 s |
| *Image* | ***pre-pull*** ke *node*, `imagePullPolicy: IfNotPresent` dengan *digest* dikunci | waktu mulai *pod* konsisten dan tanpa ketergantungan *registry* (Part 17 §17.12 tabel lingkungan; tinjauan *red team* K1 m-2) |

- **Label komponen lain (dicek 2026-10-19):** `RESET_WAIT` 120 s dan `STABILIZE_WAIT` 90 s berasal dari *runner closed-loop*
  tanpa dasar tercatat; labelnya B-konv (kontinuitas) dan keduanya dicek lebih panjang daripada kebutuhan turunan
  (120 s ≥ bacaan CPU ±61 s + 1 *scrape* untuk lonjakan bcrypt, dan ≥ *conntrack* TIME_WAIT 120 s; 90 s ≥ ±61 s + 15 s).
  *Pre-auth* (120 token, sebelum *autoscaler* ada): B (temuan K1 #3; Part 17 R15). *Deployment* baru setiap *run*: B
  (protokol gerbang 7). Parameter di dalam Job k6 sudah di register Part 17: VU ⌈1,5 × laju × *timeout*⌉ dan *timeout* 5 s
  (R30, B), `noConnectionReuse` (R31, B), pemanasan 120 s (R33, B), *scrape* 15 s (R6, B), *payload shipping* (R23, B).
  *Watcher* 5 s: B-konv (kontinuitas); waktu kejadian diambil dari stempel waktu HPA dan *pod* (`lastScaleTime`,
  `lastTransitionTime`), jadi 5 s hanya batas resolusi cadangan dan sensitivitasnya rendah. *Timeout* operasional (60 s
  hapus *autoscaler*, 180 s *rollout* dan cek replika, 1.500 s Job k6) hanya batas pengaman: bila tercapai, *run* gagal
  dan diulang lewat aturan mutu data, tanpa memengaruhi data *run* yang lolos. Durasi langkah lain (*rollout*, ambil data,
  ekspor, metadata) diukur, bukan dipilih. Tidak ada komponen per *run* yang berstatus BB.
- **Penghematan:** ±150 s per *run* dari tunggu ekspor (±11,7 jam untuk 280 *run*; ±2,3 jam pilot); *pre-pull* 0–20 s.
- **Alternatif yang ditolak (2026-10-19):** *reset* berbasis kondisi (hemat 75–100 s, risiko sisa *run* sebelumnya);
  *stabilize* 75 s (hemat 15 s, umur *pod* tidak seragam); ekspor paralel dengan *reset* berikutnya (hemat 30–60 s, beban
  kueri ekspor bisa menunda *scrape* dan kueri *adapter*/KEDA, padahal jalur metrik bagian dari perlakuan).
- **Hasil pemeriksaan risiko (dicek 2026-10-19 di kode dan data K1) [F]:**
  - analisis memakai jendela KPI k6 t 120–540 s (`pilot_openloop.py` `LOAD_WINDOW`), CPU dengan geser setengah jendela
    *rate* (sampai 570 s), dan *timeline pod*/HPA hanya di dalam jendela itu (`analyze_openloop_campaign.py`); tidak ada
    keluaran yang memakai data setelah 720 s. `thesis_bab4_outputs.py` hanya membaca *spec* (`stabilizationWindowSeconds`,
    `cooldownPeriod`) dari `hpa-status.yaml`/`keda-status.yaml`, bukan statusnya;
  - ekspor Prometheus memakai `query_range` dari awal *run* sampai saat ekspor, jadi seluruh skenario tetap tercakup;
    *event* Kubernetes disaring dari awal *run* (TTL bawaan 1 jam);
  - *watcher* 5 s sudah mencatat kondisi HPA (`hpa-snapshot`: `conditions` type/status/reason), termasuk HPA buatan KEDA,
    jadi cek `ScalingLimited` dan `ScalingActive` per *run* bisa diambil dari `hpa-timeline.jsonl`;
  - jeda antara akhir skenario dan pemanasan berikutnya turun dari ±390 s ke ±240 s (ekor skenario sudah turun ke 0 selama
    180 s). Proses yang perlu mereda lebih pendek dari itu: TIME_WAIT TCP 60 s, *conntrack* TIME_WAIT 120 s, bacaan
    *metrics-server* ±60 s, penanda *stale* Prometheus pada *scrape* berikutnya. *Login* dan `/me` *auth* hanya membaca
    *auth-db* (`register` hanya bila *login* gagal), jadi tidak ada beban tulis atau *checkpoint* yang terbawa;
  - validator lama `validate-results.sh` (ambang *run* < 900 s = kritis) tidak dipakai *runner open-loop*, dan durasi
    baru ±1.050–1.110 s tetap di atasnya; konstanta perkiraan `PILOT_RUN_SECONDS_EST` (1.260) hanya untuk ETA dan diperbarui.
- **Yang wajib dikerjakan bersama paket ini:**
  - *pre-pull* hanya aman dengan *digest*: K1 memakai `:latest` dan `imagePullPolicy: Always` untuk *auth*, *shipping*,
    *carrier-mock*, dan B1 [F, *manifest*], jadi setiap *pod* baru (termasuk *pod scale-up*) menghubungi *registry*. Dengan
    *digest* + `IfNotPresent`, waktu *pod* siap kemungkinan sedikit lebih pendek dan lebih stabil daripada K1 (17–19 s);
    karena itu waktu *pod* siap diukur ulang di *ladder*/pilot (masukan D1-b′, model fluida, dan waktu reaksi) dan perbedaannya
    dari K1 ditulis di BAB 3;
  - mekanisme *pre-pull* (DaemonSet dengan *toleration*) dihapus sebelum *run* pertama setiap sesi, agar `sut` tetap
    hanya berisi layanan uji dan DaemonSet sistem (DQ4); *upgrade* otomatis *node* dimatikan agar *image* tidak hilang;
    *event* `Pulling` per *run* dicatat sebagai cek;
  - cek validasi (bukan tunggu tambahan, supaya waktu tetap seragam): kondisi HPA saat beban mulai dari *watcher*
    (`ScalingActive=False` = masalah mutu data, *run* diulang); CPU *auth-db* dan *carrier-mock* pada fase dasar dicatat
    deskriptif; CPU fase dasar layanan uji (`base_phase_cpu`) dibandingkan dengan K1;
  - run cek *scale-down* di pilot memakai skenario dengan ekor λ0 ≥ 450 s di dalam k6, sehingga *watcher* tetap merekam;
  - semua diuji ujung ke ujung di kind (gerbang 3) dan pilot; bila cek gagal, `EXPORT_WAIT` dikembalikan ke 180 s.

### 19.3.11 Aturan mutu data, pengulangan, dan penghentian (diputuskan pemilik 2026-10-19; tinjauan *red team* v0.5 M-6)

Prinsip: tidak ada *run* yang dikeluarkan karena alasan yang berkorelasi dengan perlakuan. Semua ambang di bawah biner dan
berdasar, kecuali pergeseran B2 (3σ, B-konv).

| DQ | Cek | Dasar | Tindakan bila gagal |
|---|---|---|---|
| DQ1 | Data mentah k6 terverifikasi (md5, `gzip -t`) dan k6 *exit* 0 | integritas data (*runner* K1) [B] | ulang *run* |
| DQ2 | `dropped_iterations` k6 = 0 | beban *open-loop* harus terkirim utuh (dokumentasi k6) [B] | ulang |
| DQ3 | Sebelum *onset* (t < 120 s): replika = 1, dan HPA `ScalingActive=True` (bukan B1/B2) | syarat λ0 (19.3.3); kondisi status HPA [B] | ulang |
| DQ4 | `sut` hanya berisi *pod* uji dan DaemonSet yang diizinkan (kube-proxy, cloud-node-manager, *CSI node driver*, *node-exporter*); *pod* uji hanya di `sut`. Loki dan promtail tidak dipasang di Kampanye 2 karena analisis tidak memakai log (tinjauan *red team* v0.5 m-7) | isolasi gerbang 7 [B] | ulang |
| DQ5 | Tidak ada *restart* Prometheus, *prometheus-adapter*, KEDA, *metrics-server*, *auth-db*, *carrier-mock* selama *run* | jalur metrik bagian perlakuan; *adapter* OOM di K1 [F] | ulang |
| DQ6 | Sebaran beban per *pod*: tidak ada *pod* Ready ≥ 60 s dengan porsi laju < 20% rata-rata *pod* lain (aturan G5 K1) | deteksi *connection pinning* K1 [B-konv, kontinuitas] | ulang sekali; berulang → hentikan sesi |
| DQ7 | `ScalingLimited` dengan `reason = TooManyReplicas`, atau *pod* *Pending* | M dan kapasitas *node* tidak boleh mengikat (19.3.2) [B] | **hentikan sesi**, perbaiki kapasitas, catat deviasi bertanggal |
| — | Gagal *scrape* atau `up` = 0 saat kelebihan beban, `ScaleUpLimit`, *shedding*, *timeout* permintaan | berkorelasi dengan perlakuan | **bukan eksklusi**: dilaporkan sebagai keluaran (tinjauan *red team* Part 17 m-7) |

- **Pengulangan:** *run* yang gagal DQ diulang sekali di akhir blok yang sama, dan posisinya dicatat. Bila gagal lagi,
  sel itu hilang dari blok dan kontras yang memakainya mengikuti aturan jumlah pasangan P8 (19.4.8).
- **Pelaporan pengulangan (diputuskan pemilik 2026-10-19 setelah pemeriksaan ulang):** beberapa DQ bisa berkorelasi
  dengan perlakuan, terutama DQ5 (*restart prometheus-adapter* hanya menyangkut H2p dan H3; *restart* KEDA hanya K1) dan
  DQ3 (penskalaan sebelum *onset* lebih mungkin pada konfigurasi CPU). Karena itu jumlah *run* ulang per konfigurasi, per
  strata, dan per DQ dilaporkan, dan analisis sensitivitas eksploratori mengulang uji utama dengan **percobaan pertama**
  setiap sel yang diulang (bila data mentahnya lengkap), di samping hasil konfirmatori dari percobaan ulang. Bila
  kesimpulan berbeda, keduanya dilaporkan.
- **Penghentian sesi:** (1) DQ yang sama gagal dua kali berturut-turut; (2) model CPU atau jumlah *thread* per inti
  (`lscpu`, dicatat per *run*) berbeda dari *run ladder* → sesi dihentikan sebelum blok berikutnya, lalu *ladder* ringkas
  (C_SLO satu langkah) diulang (tinjauan *red team* v0.5 M-9); (3) **pergeseran B2 (acuan diperbaiki 2026-10-19):** fraksi
  buruk B2 suatu blok berbeda dari **median B2 pilot untuk strata yang sama** lebih dari 3 × σ_B2, dengan σ_B2 =
  max(SD B2 K1, SD B2 pilot) untuk strata itu [B-konv 3σ; SD B2 K1 dari 5 *run* per strata, `analysis/cache`] → sesi
  ditandai, `lscpu` dicek, *ladder* ringkas diulang. Catatan: B2 K1 berisi 5 *pod*, sedangkan B2 di sini N *pod* terukur,
  jadi SD K1 hanya batas bawah sebaran; karena itu dipakai maksimum dengan SD pilot. Setiap penghentian dicatat sebagai
  deviasi bertanggal; desain tidak diubah selama kampanye kecuali pengulangan mutu data yang sudah dipra-registrasi.
- **Kovariat yang dicatat (bukan eksklusi):** CPU dan *throttling* *auth-db*, *carrier-mock*, dan k6 per *run*; umur *pod*
  saat *onset*; fase penundaan acak (19.3.10); urutan di dalam blok dan konfigurasi *run* sebelumnya.
- **Cek sisa antar-*run* (eksploratori; tinjauan *red team* v0.5 m-8):** korelasi residu *lag*-1 di dalam blok (residu =
  keluaran primer dikurangi rata-rata konfigurasi dan blok), dan model eksploratori dengan "konfigurasi *run* sebelumnya"
  sebagai kovariat. Urutan acak membuat sisa tidak bias secara sistematis; cek ini hanya melaporkan ada tidaknya efek
  berurutan, tidak mengubah analisis konfirmatori.

## 19.4 Hipotesis

### 19.4.1 Hipotesis 1 (proposal)

Rumusan tetap. Hipotesis ini dirumuskan Juni 2026, sebelum kedua eksperimen, jadi menguji ulangnya dengan konstruk yang
diperbaiki bukan HARKing, asal operasionalisasi dan aturan keputusannya ditetapkan sebelum data baru dan perbaikan
rancangannya diungkapkan (asalnya dari temuan K1). Vonis K1 tetap dilaporkan apa adanya.

- **Operasionalisasi (ditetapkan ulang sebelum data; DEC P13).**
  - "Penskalaan berbasis CPU" diwakili **H1** (target bawaan 80%). Teks asli menyebut "(H1 dan H2)" untuk konfigurasi K1,
    ketika H2 adalah CPU 50% sebagai setelan praktisi. **Alasan konstruk (diperbaiki 2026-10-19; tinjauan *red team* v0.5
    M-1):** di desain ini H2 dan H2p sengaja dikalibrasi ke titik pemicu laju, jadi keduanya konstruk penelitian, bukan
    "CPU sebagaimana lazim dipakai"; yang mewakili praktik adalah target bawaan. Hasil H2 dan H2p **selalu dilaporkan di
    tabel dan kalimat yang sama** dengan H1, dan klaim ditulis "HPA CPU dengan target bawaan 80%". Pembacaan ulang ini
    diungkapkan di BAB 3; pemutus akhir pembimbing (P13).
  - "Penskalaan berbasis laju permintaan" = H3 dan K1.
  - **Syarat klaim (diputuskan pemilik 2026-10-19; tinjauan *red team* v0.5 M-1, M-7) [B-rumus].** Menurut rumus HPA, H1
    terpicu sebelum kapasitas penuh hanya bila CPU(C) / *request* > 1,1 × 0,8 = 0,88. Jadi klaim *shipping* ditulis untuk
    "layanan dengan CPU(C) / *request* < 0,88, yaitu kapasitas habis sebelum CPU mencapai target", dan hasil *shipping*
    dilaporkan sebagai uji mekanisme yang diprediksi rumus HPA, bukan bukti tentang semua layanan nyata. Rasio CPU(C) /
    *request* terukur kedua layanan dilaporkan sebagai moderator. *Request* 250m adalah instance yang dipilih (DEC, bukan
    B-konv kontinuitas); sensitivitas terhadapnya dijalankan di model fluida (*request* 500m dan *request* = CPU(C)) sebagai
    analisis eksploratori. Catatan konseptual untuk batasan: bila *request* disetel sama dengan CPU pada kapasitas
    (*right-sizing* pada beban puncak), premis Hipotesis 1 hilang karena rasio = 1 > 0,88.
- **Pola utama: *gradual*; *spike* sekunder (DEC P14).** Alasannya dari mekanisme, sebelum data: pada *gradual*, H1 di
  *shipping* baru bereaksi setelah permintaan mulai ditolak (biaya menolak menaikkan CPU di atas 200m), sedangkan laju
  memicu di L\* sebelum jenuh; pada *spike*, biaya menolak membuat CPU tetap bereaksi di kedua layanan (19.3.5 b), sehingga
  perbedaan antar-layanan mengecil. *Spike* dilaporkan dengan aturan yang sama sebagai hasil sekunder.
- **Aturan keputusan (usulan; dibekukan di gerbang 2):**
  - **Bagian *shipping*** ("laju mengungguli CPU"): H3 lebih baik daripada H1 **dan** K1 lebih baik daripada H1
    (*intersection-union*: kedua uji arah lolos pada α).
  - **Bagian *auth*** ("CPU tetap kompetitif"): uji non-inferioritas H1 terhadap H3 dengan margin δ_min (19.3.7), satu sisi 0,025 (batas atas interval 95% < δ_min); tetap uji (P22 dihapus 2026-10-19); bila tidak lolos, hasilnya "tidak dapat disimpulkan" beserta dayanya, bukan "CPU tidak kompetitif". Pada
    *gradual* uji ini bisa lolos karena kedua konfigurasi tidak kewalahan; itu memang isi klaim "kompetitif", bukan bukti
    kesetaraan sinyal. Alternatif: dilaporkan deskriptif dengan interval.
  - **Didukung** bila kedua bagian lolos; **berlawanan** bila laju terbukti lebih buruk daripada H1 pada *shipping*;
    **tidak terbukti** untuk hasil lain; **tidak dapat diuji** bila D1 atau cek 19.3.5 (c) gagal. Tingkat putusan untuk
    komponen arah mengikuti 19.4.8 (bermakna / kecil).

### 19.4.2 Hipotesis 2 (proposal)

- **Operasionalisasi (v0.2).** "Jenis metrik" diukur sebagai **efek jenis sinyal H2p → H3**: CPU vs laju permintaan pada
  jalur, jendela, tipe metrik, dan titik pemicu yang sama. Efek total CPU → laju sebagaimana tersedia di klaster (H2 → H3)
  diuraikan menjadi:

  > efek total (H2 → H3) = efek jalur ukur (H2 → H2p) + efek jenis sinyal (H2p → H3)

  Efek "mesin" = H3 → K1 (jalur metrik); hasilnya dapat ditebak dari dokumentasi KEDA (1→N diputuskan *controller* HPA),
  jadi dilaporkan sebagai verifikasi, dengan estimasi dan uji langkah (19.3.5 e).
- **Pola utama: *spike*; *gradual* sekunder (DEC P14).** Setelah pemicu disamakan, sisa perbedaan (umur bacaan, batas
  jenuh, informasi kedatangan) paling terlihat saat beban melonjak; pada *gradual* konfigurasi terkalibrasi diperkirakan
  sama-sama dekat lantai.
- **Aturan keputusan (diputuskan pemilik 2026-10-19; tinjauan *red team* v0.5 M-4) [B-rumus; Berger 1982].** Rumusan
  proposal: "jenis metrik … memberikan kontribusi yang lebih besar … dibandingkan arsitektur mesin autoscaler" (Part 13),
  jadi syaratnya perbandingan dua efek. Dengan fraksi permintaan buruk (lebih kecil = lebih baik), efek sinyal
  S = H2p − H3 dan efek mesin E = K1 − H3. "S > |E|" setara dengan S − E > 0 **dan** S + E > 0, yang di dalam setiap blok
  menjadi dua kontras: **D1 = H2p − K1** dan **D2 = H2p + K1 − 2 × H3**. Masing-masing diuji Wilcoxon *signed-rank* satu
  sisi 0,025 (P8); Hipotesis 2 didukung bila D1 dan D2 lolos pada **kedua** layanan (*intersection-union*, empat uji).
  Karena S > |E| mengandung S > 0, uji arah efek sinyal tersendiri tidak diperlukan; S dan E tetap dilaporkan sebagai
  estimasi Hodges–Lehmann dengan interval. Varians D2 lebih besar (H3 berbobot 2), jadi efek terkecil yang terdeteksi
  untuk D2 dilaporkan tersendiri (19.3.7). Alternatif yang ditolak: membuang syarat perbandingan (mengubah hipotesis
  proposal); margin kesetaraan untuk efek mesin (tidak dapat diputuskan pada daya yang layak; tinjauan *red team* Part 17
  K-2). Efek jalur ukur diuji dalam keluarga dekomposisi (19.4.8) dan dilaporkan berdampingan dengan efek total. Cara K1,
  menghitung jumlah uji yang signifikan per faktor, tidak dipakai karena rapuh terhadap definisi keluarga.
- **Arti hasil.** Bila efek total besar tetapi efek jenis sinyal tidak terbukti, keunggulan laju di klaster ini terutama
  berasal dari jalur ukur CPU yang lambat, bukan dari jenis sinyalnya; itu temuan, bukan kegagalan rancangan. Model kasar
  *red team* memperkirakan H2p memulihkan kira-kira separuh selisih CPU → laju (*spike* 4,5 × C, fraksi permintaan buruk:
  *auth* ±0,20 → ±0,14 → ±0,10; *shipping* ±0,16 → ±0,11 → ±0,09) [H, model, bukan prediksi yang dibekukan].

### 19.4.3 Hipotesis 3 (proposal) — usulan: dilepas sebagai uji; RQ3 dijawab deskriptif

- **Alasan:** bagian keberadaan konfigurasi tak terdominasi selalu benar; tanda kurung "performa terbaik pada biaya
  terendah" bertentangan dengan arti Pareto-optimal (yang berarti *trade-off*); bagian "berbeda antar-layanan" hampir pasti
  terpenuhi bila dihitung dari median beberapa *run*.
- **Pengganti:** estimasi selisih setiap *autoscaler* terhadap B2 (N terukur) pada keluaran primer dan replika-detik,
  dengan interval, **di jendela beban saja** (ekor tidak dibandingkan, P20). Klaim efisiensi, RQ3, dan "penghematan
  terhadap B2" ditulis "selama jendela beban", dengan catatan bahwa replika yang masih menyala setelah beban turun tidak
  diukur (tinjauan *red team* v0.5 m-5). Pada *spike*, B2 punya N *pod* sejak awal, jadi selisih mutunya sebagian
  ditentukan rancangan; itu ditulis terang (tinjauan *red team* O3).
- **Alternatif:** dipertahankan dengan definisi operasional yang ditetapkan sebelum data (yang diuji = himpunan tak
  terdominasi berbeda antar-layanan secara stabil pada *resampling* blok; ambang stabilitas **BB**).
- **Pemutus:** pembimbing (P9), karena menyangkut isi proposal.

### 19.4.4 Hipotesis kalibrasi (tambahan)

- **Rumusan.** "Pada layanan yang dibatasi slot (*shipping*), HPA CPU dengan target bawaan 80% (H1) lebih buruk pada
  keluaran primer daripada HPA CPU dengan target yang dikalibrasi (H2); pada layanan yang dibatasi CPU (*auth*),
  selisihnya kecil."
- **Alasan:**
  - tanpa *run* tambahan: dengan jendela 300 s untuk semua, H1 vs H2 tinggal beda target;
  - menguji mekanisme di balik Hipotesis 1: CPU kalah karena target lazim tidak dikalibrasi terhadap CPU saat kapasitas
    penuh (fraksi pemicu ≈ u × *request* / CPU(C); Part 17 §17.3 butir 4, dari rumus HPA), bukan karena sinyalnya;
  - dapat gagal lewat biaya menolak;
  - menjawab kritik "CPU dirancang supaya kalah": bila H2 terkalibrasi menutup selisihnya, masalahnya ada pada target,
    bukan pada CPU;
  - memberi saran praktis yang jelas.
- **Pola utama: *gradual*; *spike* sekunder** (mekanisme sama dengan 19.4.1).
- **Aturan keputusan (usulan):** uji arah H2 lebih baik daripada H1 pada *shipping*; *auth* dilaporkan sebagai estimasi
  dengan interval. Prediksi *auth* bergantung pada f: selisihnya kecil bila L\* dekat titik pemicu 80% (±5,1 req/s per
  *pod* di K1; dengan f = 0,8 dan C_SLO 6–7 req/s, L\* ≈ 4,8–5,6 req/s, jadi dekat); prediksi kuantitatifnya dihitung dari *ladder* sebelum data. Prasyarat: D1 lolos; bila tidak, deskriptif
  per layanan.
- **Penomoran** di naskah (Hipotesis 3 atau 4) mengikuti keputusan P9. Pemutus: pembimbing (P10).

### 19.4.5 Klaim lintas layanan (tinjauan *red team* M-3)

Dua layanan = dua konstruk (n = 2) yang berbeda dalam banyak hal: kode dan CPU per permintaan, kapasitas, laju puncak
absolut, batas *shedding*, campuran permintaan (*auth*: 70% `/auth/me` yang cepat dan 30% *login bcrypt* yang menentukan
p95), lantai keluaran, jumlah *pod* keadaan-mantap, dan biaya menolak. Klaim lintas layanan karena itu ditulis sebagai
hasil per layanan berdampingan, bukan inferensi tentang "jenis layanan" secara umum. Uji inferensial utama ada di dalam
layanan. Kelipatan puncak r yang sama (19.3.3) menghapus satu perancu K1.

### 19.4.6 Yang diubah setiap langkah rantai CPU → laju (tinjauan *red team* M-4)

Pada K1 dan v0.1, H2 → H3 mengubah beberapa mekanisme sekaligus. Dengan H2p, mekanisme itu terbagi ke dua langkah:

| Mekanisme | H2 → H2p (jalur) | H2p → H3 (sinyal) |
|---|---|---|
| Pembaruan bacaan: *metrics-server* ±60 s berundak vs *scrape* 15 s | berubah | sama |
| Jendela: rata-rata CPU *metrics-server* vs `rate` 1 menit | berubah | sama |
| Jalur API: Resource (metrics.k8s.io) vs metrik kustom lewat *adapter* | berubah | sama |
| Perlakuan HPA atas *pod* yang baru mulai (khusus metrik Resource CPU) | kemungkinan berubah [BD, 19.3.5 g] | sama |
| Makna sinyal: CPU terpakai (termasuk biaya menolak, mentok di *limit*) vs laju permintaan | sama | berubah |
| Batas jenuh: rasio CPU per ronde ≤ *limit*/target vs laju kedatangan tidak terbatas | sama | berubah (bagian dari makna sinyal) |
| Informasi kedatangan sebelum *shedding* (bila P3 = kedatangan) | sama | berubah (bagian dari makna sinyal) |

Kontras ditulis "jalur ukur" dan "jenis sinyal", tidak "murni", sampai 19.3.5 (g) selesai. Arah keduanya dapat diduga dari
rumus HPA dan konstanta K1; yang diuji adalah besarnya, terutama besar efek jenis sinyal yang tidak dapat ditebak dari
dokumentasi.

### 19.4.7 Yang tidak ditambahkan

- Uji kesetaraan sebagai hipotesis (tidak dapat diputuskan pada margin wajar, tinjauan *red team* K-2); hipotesis tanpa
  *load shedding* (sudah dijawab pilot K1). Setiap hipotesis tambahan memperbesar keluarga uji dan kebutuhan repetisi.
  Sensitivitas f bukan hipotesis; f = 0,7 hanya prediksi model, tanpa *run* (P19, 19.3.1).
- Konfigurasi CPU 50% (target contoh di tutorial HPA resmi, `kubectl autoscale … --cpu=50%`, disajikan sebagai setelan
  tutorial, bukan rekomendasi [F, dicek 2026-10-18]) sebagai dosis ketiga di samping 80% dan terkalibrasi: tidak
  ditambahkan. Posisi pemilik (2026-10-18): H1 sudah mewakili nilai bawaan terdokumentasi (80%), jadi uji sensitivitas
  target CPU tidak menjawab pertanyaan penelitian; pembimbing masih dapat memintanya (P17).
- Uji sensitivitas K (Part 17 SENS-K) sebagai *run* kampanye: tidak ditambahkan. K diturunkan dari aturan K = C_SLO × SLO
  (Hukum Little; 19.3.3, diperbarui 2026-10-19). Sebagai gantinya, c_tolak dan CPU diukur pada K dan 1,5 × K di langkah
  kelebihan beban *ladder* (deskriptif), dan langkah itu juga mengukur batas runtuh (19.3.5 b, d).

### 19.4.8 Keluarga uji, arah uji, dan uji (diputuskan pemilik 2026-10-19, P8 dan P16; tinjauan *red team* M-6)

| Keluarga | Isi (pola utama) | Koreksi |
|---|---|---|
| Hipotesis 1 | dua uji arah *shipping* (H3 > H1, K1 > H1) + satu uji non-inferioritas *auth* (*gradual*) | *intersection-union*: setiap uji pada α, tanpa koreksi tambahan |
| Hipotesis 2 | S > |E| per layanan lewat dua kontras di dalam blok, D1 = H2p − K1 dan D2 = H2p + K1 − 2 × H3, satu sisi 0,025 (*auth*, *shipping*; empat uji) + estimasi S dan E (*spike*) | *intersection-union* |
| Dekomposisi (pendukung Hipotesis 2) | dua uji arah efek jalur ukur (H2 → H2p; *auth*, *shipping*) + estimasi efek total (*spike*) | Holm di dalam keluarga |
| Hipotesis kalibrasi | satu uji arah *shipping* (H2 > H1) (*gradual*) | — |
| Sekunder | uji yang sama pada pola sekunder | Holm di dalam keluarga sekunder |

- **Keluarga per hipotesis (P16)** [B-konv]: setiap hipotesis menjawab pertanyaan penelitian yang berbeda; koreksi
  multiplisitas diperlukan bila beberapa uji digabung menjadi satu kesimpulan (Bender & Lange, 2001, *J Clin Epidemiol*
  54:343–349), dan penggabungan di dalam satu hipotesis memakai *intersection-union*: setiap komponen pada level α,
  putusan = semua lolos, tetap ber-level α tanpa koreksi tambahan (Berger, 1982, *Technometrics* 24(4):295–300). Keluarga
  dekomposisi dan sekunder memakai Holm. Galat keluarga lintas hipotesis tidak dikoreksi dan dinyatakan di naskah.
  Alternatif yang ditolak: Holm atas semua putusan utama (terlalu ketat untuk tiga pertanyaan yang berbeda).
- **Arah (P16)** [B-konv]: dua sisi α = 0,05, dibaca per arah sebagai 0,025 (putusan "berlawanan" tetap ada; kontinuitas
  K1). Non-inferioritas *auth*: satu sisi 0,025, yaitu batas atas interval 95% < δ_min [F, ICH E9, teks asli EMA dicek
  2026-10-19; tinjauan *red team* v0.5 m-10]: "The approach of setting type I errors for one-sided tests at half the
  conventional type I error used in two-sided tests is preferable in regulatory settings" (§5.5) dan "For non-inferiority
  trials a one-sided interval should be used" (§3.3.2). Alternatif yang ditolak: satu sisi 0,05 (menghapus putusan
  "berlawanan").
- **Uji (P8)** [B-konv]: **Wilcoxon *signed-rank* eksak** pada b selisih di dalam blok, dengan estimasi **Hodges–Lehmann**
  (median rata-rata Walsh) dan interval eksak (Hollander & Wolfe, *Nonparametric Statistical Methods*); analisis mengikuti
  rancangan blok acak (Montgomery, *Design and Analysis of Experiments*). Sah sebagai uji randomisasi karena urutan *run*
  diacak di dalam blok. Distribusi eksak dihitung dengan enumerasi penuh 2ⁿ pembalikan tanda pada *midrank* (menangani
  ikatan). Selisih nol dibuang (cara Wilcoxon); hasil "tidak dapat diputuskan" bila p eksak terkecil yang mungkin untuk n
  pasangan tersisa (2/2ⁿ dua sisi, 1/2ⁿ satu sisi) lebih besar dari α uji itu: n ≥ 6 untuk dua sisi 0,05 dan
  non-inferioritas 0,025, n ≥ 7 untuk langkah pertama Holm (0,025). Mann–Whitney dan A12 tak berpasangan dihitung sebagai
  analisis sensitivitas (kontinuitas K1). Alternatif yang ditolak sebagai uji utama: Mann–Whitney (mengabaikan blok;
  lebih lemah bila korelasi di dalam blok tinggi, 19.3.7) dan permutasi *sign-flip* pada rata-rata (peka *run* pencilan,
  mis. keruntuhan metastabil K1). b ditetapkan sebelum pilot dengan analisis sensitivitas daya (19.3.7, P23).
- **Tingkat putusan komponen arah (diputuskan pemilik 2026-10-19; tinjauan *red team* v0.5 N-2) [B-konv].** Untuk setiap
  uji arah (H3 > H1, K1 > H1, H2 > H1, D1, D2, efek jalur): **didukung (bermakna)** bila uji lolos dan estimasi HL ≥ δ_min;
  **didukung (kecil)** bila uji lolos tetapi HL < δ_min; **tidak dapat disimpulkan** bila uji tidak lolos (efek terkecil
  yang terdeteksi dilaporkan, 19.3.7); **berlawanan** bila ekor sebaliknya lolos. Kata "mengungguli" hanya dipakai untuk
  tingkat "bermakna". Dasar: δ_min sebagai efek terkecil yang dianggap penting (Lakens, 2022), konsisten dengan margin
  non-inferioritas; daya untuk tingkat "lolos" tidak berkurang. Alternatif yang ditolak: mensyaratkan HL ≥ δ_min untuk
  "didukung" (menurunkan daya lagi), dan tanpa syarat efek (efek di bawah satu siklus HPA disebut "mengungguli").

## 19.5 Keputusan terbuka

| # | Keputusan | Pilihan | Usulan saat ini | Pemutus |
|---|---|---|---|---|
| P1 | Varian | Part 17 / Part 19 | **usulan pemilik 2026-10-19: Part 19** | pembimbing (konfirmasi) |
| P2 | Platform | AKS (kontinuitas alur; *metrics-server* 60 s tidak dapat diubah, jadi H2 → H2p paling informatif; klaster baru ≥ 1.35 tetap mengubah versi komponen) / GKE (pindah platform; Performance HPA profile mengubah jalur CPU H2 dan kesegarannya harus diukur) — 19.3.9 | menunggu pemilik (diputuskan paling akhir) | pemilik |
| P3 | Penghitung laju | dilayani / kedatangan | **diputuskan 2026-10-19 (pemilik): kedatangan** (19.3.4) | — |
| P4 | Fraksi pemicu f | 0,8 (angka bawaan HPA pada kapasitas SLO) / rentang turunan / lain | **diputuskan 2026-10-18 (pemilik): 0,8**, B-konv (19.3.1) | — |
| P5 | Puncak r | min(0,8 × λ_runtuh / C_SLO) antar-layanan / r tetap / r per layanan / angka K1 | **diputuskan 2026-10-18 (pemilik): aturan min(0,8 × λ_runtuh / C_SLO)**, B-rumus; angka dari *ladder* baru (19.3.3) | — |
| P6 | Aturan SLO | 1.000 ms untuk kedua layanan / p95 B2 seperti K1 / m × p95 beban rendah / nilai K1 tetap | **diputuskan 2026-10-18 (pemilik): 1.000 ms untuk kedua layanan**, B-konv (Nielsen 1993); lantai *auth* 3–4% ditulis; 1.500 ms eksploratori (19.3.3) | — |
| P7 | Keluaran primer | O1 dipecah / fraksi permintaan buruk | **diputuskan 2026-10-19 (pemilik): fraksi permintaan buruk**; komponen deskriptif, O1 sekunder (19.3.8) | — |
| P8 | Uji | berpasangan per blok kecil / Mann–Whitney | **diputuskan 2026-10-19 (pemilik): Wilcoxon *signed-rank* eksak di dalam blok + Hodges–Lehmann; Mann–Whitney/A12 sensitivitas** (19.4.8) | — |
| P9 | Hipotesis 3 | dilepas / definisi operasional | **usulan pemilik 2026-10-19: dilepas sebagai uji, RQ3 deskriptif** (19.4.3) | pembimbing (konfirmasi) |
| P10 | Hipotesis kalibrasi | tambah / tidak | **usulan pemilik 2026-10-19: tambah** (19.4.4) | pembimbing (konfirmasi) |
| P11 | CPU lewat Prometheus | — | **diputuskan 2026-10-18 (pemilik): masuk inti sebagai H2p** | — |
| P12 | Aturan D1 desain ulang *shipping* | seperti 19.3.5 / tanpa desain ulang / desain ulang tanpa syarat | seperti 19.3.5; **parameter c_D1, D1-b′ (mekanisme Δt ≥ 15 s, menggantikan model D1-b 2026-10-19), dan ambang *auth* (uji naik *limit*, rasio ≥ 1,5) diputuskan pemilik 2026-10-18; aturan D1 sendiri usulan pemilik 2026-10-19** | pembimbing (konfirmasi) |
| P13 | Operasionalisasi Hipotesis 1 | CPU = H1 saja / H1 dan H2 | **usulan pemilik 2026-10-19: H1 saja** (19.4.1) | pembimbing (konfirmasi) |
| P14 | Pola utama per hipotesis | *gradual* untuk Hipotesis 1 dan kalibrasi, *spike* untuk Hipotesis 2 / sama untuk semua | **usulan pemilik 2026-10-19: per hipotesis** (19.4) | pembimbing (konfirmasi) |
| P15 | δ_min dan margin non-inferioritas | aturan 15 s / lain | **diputuskan 2026-10-19 (pemilik): aturan 15 s** (19.3.7) | — |
| P16 | Keluarga dan arah uji | per hipotesis, dua sisi / Holm atas putusan utama / satu sisi | **diputuskan 2026-10-19 (pemilik): per hipotesis (*intersection-union*), Holm untuk dekomposisi dan sekunder, dua sisi 0,05, non-inferioritas satu sisi 0,025** (19.4.8) | — |
| P17 | Konfigurasi CPU 50% sebagai dosis ketiga | ya / tidak | **usulan pemilik 2026-10-19: tidak** (posisi pemilik 2026-10-18; 19.4.7) | pembimbing (konfirmasi) |
| P18 | Operasionalisasi Hipotesis 2 | jenis metrik = efek sinyal H2p → H3 / efek total H2 → H3 | **usulan pemilik 2026-10-19: efek sinyal, dengan dekomposisi** (19.4.2) | pembimbing (konfirmasi) |
| P19 | Level sensitivitas f | tidak ada / f = 0,7 deskriptif / uji penuh / prediksi model | **diputuskan 2026-10-19 (pemilik), diperbarui setelah *red team* v0.5 K-2: klaim bersyarat f = 0,8; f = 0,7 hanya prediksi model fluida (eksploratori), tanpa *run*** (19.3.1) | — |
| P20 | Bentuk dan durasi *run*; ekor | bentuk K1, ekor 180 s / *ramp* aman / ekor ≥ 450 s | **diputuskan 2026-10-18 (pemilik): bentuk K1 untuk kedua pola, ekor 180 s, replika-detik hanya di jendela beban, *scale-down* dicek di pilot** (19.3.10) | — |
| P21 | *Pool* untuk k6 | berbagi `infra` dengan *monitoring*, KEDA, *adapter*, dan dependensi (Part 17 R10) / *pool* `load` sendiri | **diputuskan 2026-10-19 (pemilik): `load` sendiri (*taint*), 1 × D2as_v5; cek pilot `dropped_iterations` = 0 dan *throttling* k6 ≈ 0 (gagal → D4as_v5); `infra` 2 × D4as_v5** (19.3.8) | — |
| P22 | Aturan cadangan berbasis daya | tidak ada / komponen *intersection-union* dengan daya < 0,8 menjadi estimasi | **dihapus 2026-10-19 (pemilik; *red team* v0.5 K-2): semua komponen tetap uji; tidak lolos = "tidak dapat disimpulkan" beserta daya** (19.3.7) | — |
| P23 | Jumlah blok kampanye b | 8 / 10 / 15 / 20 (tabel efek terkecil yang terdeteksi, 19.3.7) | **diputuskan 2026-10-19 (pemilik): b = 10** (280 *run*; pembenaran sumber daya + analisis sensitivitas daya, Lakens 2022) | — |

## 19.6 Langkah berikutnya

1. Konfirmasi pembimbing atas usulan pemilik P1, P9, P10, P12, P13, P14, P17, P18 (2026-10-19); keputusan P2 (terakhir).
2. Tulis skrip D1-b′ (rumus HPA, masukan *ladder*) dan model fluida (prediksi eksploratori dan δ_min *gradual*) sebagai skrip repositori, sebelum cek dijalankan.
3. Cek 19.3.5 di kind (termasuk aturan *adapter* CPU untuk H2p), lalu *ladder* singkat di platform terpilih (dengan
   persetujuan biaya). Putuskan D1 dan catat tanggalnya.
4. Register parameter dan aturan pemilihan (gerbang 2). Butir yang tidak berubah boleh berdasar kontinuitas K1
   (B-konv), kecuali butir yang menentukan ukuran efek (19.3.8). Butir Part 17 §17.12 yang sama dipakai ulang.
5. Gerbang 3 di kind: seluruh *pipeline* dan analisis ujung ke ujung.
6. Pilot penuh (19.3.6), diulang bila perlu; laporan efek terkecil yang terdeteksi diperbarui dengan σ pilot terpool (batas atas 80%), tanpa mengubah b.
7. Pembekuan (gerbang 5), tinjauan *red team* gerbang 6 bersama data pilot, lalu peluncuran.

**Tugas pendamping:**
- Sumber bahwa layanan yang dibatasi slot memang ada di praktik: **sebagian terverifikasi 2026-10-19** — dokumentasi
  Resilience4j *Bulkhead* (`maxConcurrentCalls` bawaan 25) dan HikariCP (`maximumPoolSize` bawaan 10). Masih [BD]: Nygard,
  *Release It!* (pola *bulkhead*), batas *thread pool* server aplikasi (mis. Tomcat `maxThreads`), dan rujukan AWS
  Builders' Library tentang *load shedding* (tinjauan *red team* m-8).
- Cek sumber daya menganggur di Azure Cost Management: September, dengan AKS berhenti sebulan, tagihannya IDR 888.752
  (±US$53 per bulan) dari *load balancer* dan VM yang tetap berjalan [F, Part 08 §8.15]. Anggaran bukan batasan, tetapi
  biaya yang tidak terpakai sebaiknya dihentikan.

## 19.7 Titik rawan bersama (dari pra-mortem Part 17 §17.22)

| # | Titik rawan | Pemeriksaan di bagian ini | Bila gagal |
|---|---|---|---|
| PM2 | Satu *pod* kewalahan di menit pertama *spike*, atau runtuh pada λp, sehingga penghitung, *scrape*, dan *probe* buta | 19.3.5 (d); λp ≤ 0,8 × laju runtuh | turunkan r sebelum pembekuan |
| PM3 | Laju kedatangan sebagai titik tunggal (H3, K1, Hipotesis 1–2, hipotesis kalibrasi) | kueri gabungan diuji di kind terhadap jadwal k6; pemeriksaan pemicu 19.3.1 | tanpa sinyal laju yang lolos, tidak ada kampanye |
| PM4 | Pemicu tidak setara (kini empat konfigurasi: H2, H2p, H3, K1) | pemeriksaan rasio ≈ 1 pada L\* (19.3.1) | kalibrasi ulang sebelum pembekuan |
| PM5 | Lonjakan *login* awal mencemari HPA CPU *auth* | *runner* K1 sudah melakukan *login* awal saat *reset*, sebelum *autoscaler* diterapkan (BAB 4.2.3); dipertahankan | perbaiki urutan *runner* |
| PM6 | Pipa metrik putus di tengah *run*, tercampur dengan mekanisme lambat; *prometheus-adapter* kini dipakai H2p dan H3 sekaligus | *watcher* mencatat kondisi HPA (`AbleToScale`, `ScalingActive`, `ScalingLimited`) dan *event* `FailedGet*Metric` | *run* diulang; kegagalan *scrape* pada λp dilaporkan (19.3.4) |
| PM7 | M mengikat, atau *node* untuk layanan uji kurang | 19.3.2: M = 100; `sut` ≥ 2 × replika tertinggi pilot; `ScalingLimited` beralasan `TooManyReplicas` dan *Pending* dicek per *run* (DQ7) | tambah *node* `sut` sebelum pembekuan |
| PM8 | N untuk B2 tidak cukup karena kapasitas tidak linear | N diukur langsung (19.2) | N + 1 |

## 19.8 Pemetaan tinjauan *red team* (Part 17, 2026-10-18) ke v0.1–v0.2

| Temuan | Status |
|---|---|
| K-1 biaya menolak menghapus efek H1 pada *spike* | diterapkan: aturan D1 (19.3.5), pola utama *gradual* (19.4.1) |
| K-2 hipotesis kesetaraan tidak dapat diputuskan; efek lantai *gradual* | diterapkan: tidak ada hipotesis TOST; "kompetitif" lewat non-inferioritas atau deskriptif; efek lantai ditulis (19.4.1) |
| K-3 anggaran dan jadwal | sebagian tidak berlaku (anggaran bukan batasan); cek biaya tetap dan jumlah *node* tetap ada (19.6, 19.3.2) |
| M-1 MC1 gagal pada data K1 | diterapkan: cek *auth* lewat *throttling* dan plato *goodput* (19.3.5 c) |
| M-2 ketergantungan pada aturan SLO | diterapkan: urutan aturan (19.3.3) |
| M-3 perancu antar-layanan | diterapkan: dua konstruk, inferensi di dalam layanan, r sama (19.4.5, 19.3.3) |
| M-4 kontras CPU → laju adalah paket | diterapkan: H2p memisahkan jalur dari sinyal (v0.2; 19.4.6) |
| M-5 keluaran primer | diterapkan: catatan redundansi, komposisi, lantai (19.3.8); pilihan tetap P7 |
| M-6 *intersection-union* dan keluarga | diterapkan: 19.4.8 |
| M-7 pemblokan tidak terbukti mengurangi varians | diterapkan: blok kecil, daya dengan sebaran tak berpasangan (19.3.7) |
| M-8 satu pola | diterapkan: dua pola dengan pola utama per hipotesis; klaim bersyarat; *oscillating* K1 sebagai pembanding (19.2) |
| M-9 parameter penentu efek | diterapkan: aturan pemilihan dibekukan di gerbang 2; catatan sensitivitas (19.3.8) |
| m-1 versi AKS | diterapkan: 19.3.5 (f) |
| m-2 nuansa KEDA | diterapkan: `useCachedMetrics: false` eksplisit (19.3.5 f) |
| m-3 aturan Object | tidak berlaku (tipe Pods seperti K1); kueri kedatangan dan aturan CPU H2p diuji di kind |
| m-4 inkonsistensi R63/DQ8 | tidak berlaku (khusus Part 17) |
| m-5 batas runtuh *auth* | diterapkan: 19.3.5 (d) |
| m-6 SENS-f | tidak dipakai sejak v0 |
| m-7 penghitung di proses yang sama | diterapkan: aturan pelaporan kegagalan *scrape* (19.3.4) |
| m-8 rujukan belum diverifikasi | tugas pendamping (19.6) |
| O1 KEDA | sebagian: KEDA tetap di kampanye sebagai estimasi (judul), ditambah uji langkah (19.3.5 e) |
| O2 CPU lewat Prometheus ke inti | diterapkan di v0.2: H2p |
| O3 non-inferioritas vs ST-N ditolak | sesuai sejak v0: estimasi terhadap B2 (19.4.3) |
| O4 bekukan aturan di gerbang 2 | diterapkan (19.3.8) |
| O5 penamaan | sebagian: label konfigurasi K1 dipertahankan demi kontinuitas, H2p ditambahkan tanpa menomori ulang; konvensi tertulis di kepala bagian ini |
| Jalur 1′ (*shipping* K1 tidak diubah, H1 prediksi terhitung) | berbeda: *shipping* didesain ulang bersyarat; jalur 1′ menjadi cabang gagal D1 |

## 19.9 Sumber

- K1: Part 08 (§8.5, §8.10–8.13, §8.15); `experiment-results-openloop/analysis/ladder.json`; `analysis/part12/report.md`
  (X1, X5); `analysis/cache/*.npz` (data mentah per permintaan; hitung ulang 2026-10-18); Thesis-2.3 BAB 3–4, Lampiran E
  dan H.
- Part 15 (kontrafaktual); Part 17 (§17.3, §17.12, §17.16, §17.22, §17.23); tinjauan *red team*
  [17-review-redteam-ringan-v0.md](17-review-redteam-ringan-v0.md) (termasuk Lampiran A.4 dan B.1).
- Kode: `backend/services/*/internal/middleware/admission_control.py` (`http_requests_shed_total`), `app/main.py` (urutan
  *middleware*); `infrastructure/kubernetes/load-testing/k6-openloop-pilot.yaml` (`rateStages`, bentuk beban K1).
- Fraksi pemicu dan cadangan (19.3.1, dicek 2026-10-18): GKE *Best practices for cost optimization* (target "70% or 80%"
  sebagai cadangan selama replika baru menyala); Google Cloud Architecture Center *Best practices for running
  cost-optimized Kubernetes applications on GKE* (target 70% = cadangan 30%; cadangan cukup untuk dua–tiga menit saat
  *spike*). SLO (19.3.3, dicek 2026-10-18): J. Nielsen, *Usability Engineering* (1993), dikutip di NN/g "Response Times:
  The 3 Important Limits"; Google SRE Book bab 4 *Service Level Objectives* ("Choosing Targets"). Ekor dan *scale-down*
  (19.3.10): tinjauan *red team* Part 14 F4 ([14-review-redteam-v0.md](14-review-redteam-v0.md)). Statistik (19.3.7, 19.4.8, dicek
  2026-10-19): Bender & Lange (2001), *J Clin Epidemiol* 54:343–349; Berger (1982), *Technometrics* 24(4):295–300; ICH E9 (EMA, CPMP/ICH/363/96, §3.3.2 dan §5.5, teks asli dicek);
  Hollander & Wolfe, *Nonparametric Statistical Methods*; Browne (1995), *Stat Med* 14:1933–1940; Lakens (2022),
  *Collabra: Psychology* 8(1), doi 10.1525/collabra.33267; Montgomery,
  *Design and Analysis of Experiments*. maxReplicas dan *node*
  (19.3.2, dicek 2026-10-19): KEDA 2.17 *ScaledObject specification* (`maxReplicaCount`, bawaan 100); Microsoft Learn
  *Concepts - IP address planning in AKS* (*maximum pods per node*); `infrastructure/kubernetes/auth/deployment.yaml` dan
  `shipping/deployment.yaml` (*request*, dependensi). Rancangan *shipping* baru (19.3.5, dicek 2026-10-19): dokumentasi Resilience4j *Bulkhead*
  (`maxConcurrentCalls` bawaan 25, `maxWaitDuration` bawaan 0); `backend/services/carrier-mock-service/internal/service/carrier_service.py`
  (jeda *carrier*, `CARRIER_DELAY_SCALE`). Ukuran *node* (19.3.2, 19.3.8, dicek 2026-10-19): Azure Retail Prices API (Indonesia
  Central, Linux bayar per jam: D2as_v5 US$0,0972, D4as_v5 US$0,194, D16as_v5 US$0,778); Microsoft Learn *Use system node
  pools in AKS* (minimum *pool* sistem dan *pool user*).
- Dokumentasi: Kubernetes HPA (*behavior* bawaan, kondisi status HPA, perlakuan *pod* baru untuk CPU); referensi API HPA
  v2 (bawaan 80% bila metrik tidak diisi, dicek 2026-10-18); tutorial HPA (`--cpu=50%`, dicek 2026-10-18); KEDA 2.17
  *ScaledObject specification* (`pollingInterval`, `useCachedMetrics`); FAQ *metrics-server*; AKS *Supported Kubernetes
  versions* (dicek 2026-10-18).
- Resolusi *metrics-server* (19.3.9, dicek 2026-10-18): FAQ, `manifests/base/deployment.yaml`, dan `values.yaml` *Helm
  chart* di kubernetes-sigs/metrics-server; Microsoft Learn *Configure Metrics Server VPA in AKS*; Microsoft Q&A 571261
  (perilaku *add-on* Reconcile); dokumentasi EKS *Metrics Server*, *Community add-ons*, dan *field management*; dokumentasi
  GKE *Horizontal Pod autoscaling* (konsep, konfigurasi, *troubleshooting*), *release notes* (Performance HPA profile),
  referensi REST `HPAProfile`, dan blog Google Cloud "Rearchitected GKE HPA improves scaling performance" (2025-01-18).

## 19.10 Catatan perubahan

| Tanggal | Versi | Perubahan | Pemicu |
|---|---|---|---|
| 2026-10-18 | v0 | usulan pemilik ditulis: perubahan dari K1, tujuh butir yang tetap harus berubah, hipotesis, keputusan P1–P11 | permintaan pemilik |
| 2026-10-18 | v0.1 | aturan D1 desain ulang *shipping* bersyarat; operasionalisasi Hipotesis 1 (CPU = H1); pola utama per hipotesis; aturan keputusan dan keluarga uji (*intersection-union*, dua sisi); cek *auth* lewat *throttling*, batas runtuh kedua layanan, uji langkah KEDA, cek platform; urutan aturan SLO; blok kecil dan daya dengan sebaran tak berpasangan; aturan δ_min 15 s; catatan keluaran primer; aturan pemilihan parameter di gerbang 2; titik rawan bersama (19.7); pemetaan tinjauan *red team* (19.8); keputusan P12–P16 | permintaan pemilik: terapkan temuan *red team* yang berlaku |
| 2026-10-18 | v0.2 | konfigurasi H2p (CPU lewat Prometheus dan *adapter*, pemicu setara) masuk inti; rantai kontras satu perubahan per langkah (19.0); Hipotesis 2 dioperasionalkan sebagai efek jenis sinyal H2p → H3 dengan dekomposisi jalur + sinyal (19.4.2); tabel mekanisme per langkah (19.4.6); keluarga dekomposisi (19.4.8); cek aturan *adapter* CPU (19.3.5 g); blok tujuh konfigurasi dan pilot 56 *run*; catatan daya efek sinyal; P11 diputuskan; P17 (CPU 50%) dan P18 (operasionalisasi Hipotesis 2) ditambahkan | permintaan pemilik: tambah konfigurasi di antara H2 dan H3 |
| 2026-10-18 | v0.3 | resolusi *metrics-server* per platform dan arti H2 (19.3.9); P2 diperjelas; sumber dokumentasi ditambahkan; perbaikan naskah K1 dicatat di Part 20 | permintaan pemilik: cek apakah resolusi bisa diubah di AKS, EKS, GKE |
| 2026-10-18 | v0.4 | f = 0,8 usulan pemilik dengan dasar, alternatif, dan sensitivitas (19.3.1; contoh maxReplicas 19.3.2 disesuaikan); bentuk dan durasi *run* K1 untuk kedua pola, ekor 180 s, replika-detik hanya di jendela beban, cek *scale-down* di pilot (19.3.10); estimasi pilot ±19 jam mesin (19.3.6); posisi pemilik tentang CPU 50% dan sensitivitas K (19.4.7); P4 diputuskan pemilik (f = 0,8, B-konv; alasan: nilai bawaan HPA, angka *auth* hanya akibat), P17 diperbarui, P19 (level sensitivitas f) dan P20 (diputuskan) ditambahkan; P6 diputuskan: SLO 1.000 ms untuk kedua layanan (Nielsen, B-konv), lantai *auth* dan sensitivitas 1.500 ms eksploratori (19.3.3); λ0 = 0,2 × C_SLO untuk kedua layanan (B-konv), cek pilot tanpa penskalaan sebelum t = 120 s, perbaikan `setup()` *auth* (19.3.3); P5 diputuskan: r = min(0,8 × λ_runtuh / C_SLO) antar-layanan (B-rumus), *ladder* kelebihan beban sampai runtuh (19.3.5 d), *ladder* baru sebagai sumber angka beserta syaratnya (19.3.3); paket D1 diputuskan: c_D1 = rata-rata + 2 SD < 200m, model D1-b = model fluida *red team* dengan *back-test* K1 dan b ≤ 10, ambang *auth* = uji naik *limit* rasio ≥ 1,5 dengan *shipping* baru sebagai kontrol negatif (19.3.5); P12 diperbarui | keputusan pemilik dalam diskusi f, durasi *gradual*, ekor, SLO, λ0, r, dan paket D1 |
| 2026-10-19 | v0.5 | maxReplicas M = 100 untuk semua konfigurasi (bawaan KEDA, B-konv); *pool* `sut` D4as_v5, pilot 4 *node*, kapasitas ≥ 2 × replika tertinggi pilot, `--max-pods` eksplisit, cek `ScalingLimited` dan *Pending* per *run* (19.3.2); isi klaster hanya layanan uji + *auth-db* + *carrier-mock* (19.3.8); ringkasan 19.0 dan PM7 diperbarui; P21 diputuskan: *pool* `load` sendiri 1 × D2as_v5 dengan cek pilot, `infra` 2 × D4as_v5, tabel tata letak *pool* (19.3.8); rancangan *shipping* baru: T_svc lewat `CARRIER_DELAY_SCALE` agar p95 bawaan ≈ *auth* pada λ0, C = C terbesar yang lolos D1-a dan D1-b, W = bulat(C × T̄_svc), beserta urutan ukurnya (19.3.5); `sut` diganti 1 × D16as_v5 (harga sama dengan 4 × D4as_v5, penempatan identik; kurang → D32as_v5) dan dasar `infra` 2 × D4as_v5 dicatat (minimum *pool* sistem AKS) (19.3.2, 19.3.8); langkah per *run* (paket minimal): `EXPORT_WAIT` 180 → 30 s dan *pre-pull* dengan *digest* + `IfNotPresent`, *reset*/*stabilize* tetap K1, hasil pemeriksaan risiko dan pekerjaan wajib (19.3.10); estimasi pilot ±16,5–17,5 jam (19.3.6); P3 diputuskan (kedatangan) dan P7 diputuskan (fraksi permintaan buruk, komponen deskriptif, O1 sekunder); P19 diputuskan (klaim bersyarat f = 0,8, prediksi model untuk 0,7, SENS-f setelah pilot dengan aturan presisi); P8, P15, P16 diputuskan setelah pemeriksaan ulang (*signed-rank* eksak + HL, aturan n berbasis α, aturan 15 s dengan turunan, keluarga per hipotesis dengan sitasi) dan P22 (aturan cadangan berbasis daya) ditambahkan (19.3.7, 19.4.1, 19.4.8); P1, P9, P10, P12, P13, P14, P17, P18 ditetapkan sebagai usulan pemilik, menunggu konfirmasi pembimbing (19.5) | keputusan pemilik dalam diskusi M, *node*, rancangan *shipping*, *overhead*, P3, P7, P19, P8, P15, P16, P22, dan butir pembimbing |
| 2026-10-19 | v0.6 | tindak lanjut tinjauan *red team* v0.5 (19.11): K-1 diterapkan (langkah *ladder* N *pod*, aturan terima rasio metrik/target 1,0 ± 0,1, cadangan g(N), D1-a pada N = 2–3, `lscpu` per *node*; 19.3.1, 19.3.3, 19.3.5); K-2 diterapkan (b ditetapkan sebelum pilot dengan analisis sensitivitas daya dan tabel efek terkecil yang terdeteksi, P23 baru; P22 dihapus; non-inferioritas *auth* tetap uji; SENS-f hanya prediksi model; pilot untuk gladi dan cek konstruk, σ pilot terpool dengan batas atas 80% hanya untuk laporan; 19.3.1, 19.3.6, 19.3.7, 19.4.1, 19.4.8); catatan tinjauan di 19.1; P23 diputuskan: b = 10 (280 *run*), D1-b memakai b = 10 (19.3.5, 19.3.6, 19.3.7); M-4 (S > |E| lewat D1/D2), M-5 (`ScalingLimited` hanya `TooManyReplicas`), M-6 (§19.3.11 aturan mutu data), M-11 (K = C_SLO × SLO, semantik *bulkhead*), M-12 (label δ_min), N-2 (tingkat putusan), N-3 (disk OS *Managed*) diterapkan; M-1 (dasar praktik *bulkhead*, klaim bersyarat rasio, alasan P13), M-2 (H2p hanya *pod* Ready, *recording rule*), M-3 (D1-b′ mekanisme, model fluida eksploratori), M-7 (*request* DEC), M-8 (cek konstruk (e)), M-9 (klaster tidak dihentikan), M-10 (*pool* `deps`), N-1 (penundaan acak U(0, 15) s) diterapkan; m-1 sampai m-10 diterapkan (jangkar *scale* 0,5 × SLO, T̄_svc laju rendah tetap, SD c_D1, c_tolak di bawah *limit*, klaim efisiensi "selama jendela beban", daftar DaemonSet, cek sisa antar-*run*, waktu blok, ICH E9 terverifikasi); ilustrasi K di 19.3.3 dan urutan *shipping* di 19.3.5 diselaraskan dengan K = C_SLO × SLO | keputusan pemilik atas semua temuan tinjauan *red team* v0.5 |
| 2026-10-19 | v0.6.1 | pemeriksaan ulang menyeluruh (*triple check*) atas semua keputusan tindak lanjut *red team*: sumber, kode, dan simulasi dicek ulang; fakta baru dicatat (disk OS K1 *Managed* Premium SSD dari label *node*, 19.3.8; batas daya kontras D2 Hipotesis 2, 19.3.7); teks usang diperbaiki (alasan *pool* k6, ringkasan langkah per *run* dan penundaan acak); lima penyempurnaan diterapkan: H2p hanya *pod* yang Ready sepanjang 60 s + asimetri *scale-down* dicatat (19.3.1, 19.3.5 g), pelaporan *run* ulang per konfigurasi + sensitivitas percobaan pertama (19.3.11), acuan pergeseran B2 = median B2 pilot dengan σ = max(SD K1, SD pilot) (19.3.11), aturan konvergensi K (19.3.3), `lscpu` per *run* (19.3.3, 19.3.8, 19.3.11) | permintaan pemilik: verifikasi ulang semua keputusan |

## 19.11 Tindak lanjut tinjauan *red team* atas v0.5 (2026-10-19)

Sumber: [19-review-redteam-k1-diperbaiki-v0.5.md](19-review-redteam-k1-diperbaiki-v0.5.md) (tinjauan independen dua fase, skor 6/10;
validitas internal 5 setelah fase 2). Status per temuan:

| Temuan | Status | Tempat |
|---|---|---|
| K-1 kesetaraan pemicu dan kurva CPU hanya pada 1 *pod* | **diterapkan v0.6**: langkah *ladder* N *pod*, aturan terima rasio 1,0 ± 0,1, cadangan g(N), D1-a pada N = 2–3, `lscpu` per *node* | 19.3.1, 19.3.3, 19.3.5 |
| K-2 b, SENS-f, P22 dari σ pilot n = 2 | **diterapkan v0.6**: b = 10 ditetapkan sebelum pilot dengan analisis sensitivitas daya (P23), P22 dihapus, non-inferioritas *auth* tetap uji, SENS-f hanya prediksi model, σ pilot hanya untuk laporan efek terkecil | 19.3.1, 19.3.6, 19.3.7, 19.4.1 |
| M-1 konstruk "dibatasi slot" direkayasa; P13 | **diterapkan v0.6**: dasar praktik (Resilience4j 25, HikariCP 10), klaim bersyarat rasio CPU(C)/*request* < 0,88, alasan P13 berbasis konstruk, H2/H2p selalu dilaporkan bersama H1 | 19.2, 19.4.1, 19.6 |
| M-2 H2 → H2p juga beda perlakuan *pod* baru; OOM *adapter* | **diterapkan v0.6**: deret H2p hanya *pod* Ready (HPA menghitung *pod* tanpa metrik 0% saat *scale-up*), diuji di kind; *recording rule* terbatas untuk *adapter*; cadangan: kontras ditulis paket | 19.3.1, 19.3.5 (g) |
| M-3 validasi model D1-b lemah | **diterapkan v0.6**: D1-b diganti D1-b′ (Δt ≥ 15 s, tanpa model); model fluida hanya untuk prediksi eksploratori dan δ_min *gradual*, dengan kurva fraksi buruk terukur | 19.3.5 |
| M-4 aturan keputusan Hipotesis 2 tidak operasional | **diterapkan v0.6**: S > |E| lewat D1 = H2p − K1 dan D2 = H2p + K1 − 2 × H3, satu sisi 0,025, kedua layanan | 19.4.2, 19.4.8 |
| M-5 cek `ScalingLimited` salah baca (`ScaleUpLimit`) | **diterapkan v0.6**: hanya `TooManyReplicas` dan *Pending* (DQ7); `ScaleUpLimit` keluaran mekanisme | 19.3.2, 19.3.11 |
| M-6 aturan mutu data, pengulangan, penghentian, pergeseran B2 | **diterapkan v0.6**: tabel DQ1–DQ7, pengulangan, penghentian sesi, kovariat | 19.3.11 |
| M-7 *request*/*limit* 250m/500m berlabel kontinuitas | **diterapkan v0.6**: DEC; klaim lewat rasio CPU(C)/*request*; sensitivitas di model | 19.3.8, 19.4.1 |
| M-8 uji langkah (e) mengukur kontras tesis | **diterapkan v0.6**: (e) menjadi cek konstruk jeda metrik, tanpa estimasi selisih *scale-up* | 19.3.5 (e) |
| M-9 Dasv5 heterogen antar-sesi | **diterapkan v0.6**: klaster tidak dihentikan selama *ladder* sampai kampanye, `lscpu` per *run*, aturan henti (19.3.11) | 19.3.3, 19.3.8, 19.3.11 |
| M-10 `infra` dipakai bersama dependensi dan monitoring | **diterapkan v0.6**: *pool* `deps` ber-*taint* (1 × D4as_v5) untuk *auth-db* dan *carrier-mock* | 19.3.8 |
| M-11 aturan K berbeda dengan Part 17; semantik *bulkhead* | **diterapkan v0.6**: K = C_SLO × SLO untuk kedua layanan (sama dengan Part 17 R25), semantik *bulkhead* ditulis, c_tolak pada K dan 1,5 × K di *ladder* | 19.3.3, 19.4.7 |
| M-12 label δ_min | **diterapkan v0.6**: B-konv (turunan B-rumus), sensitivitas ½ × dan 2 × δ_min | 19.3.7 |
| N-1 fase *tick* HPA terkunci terhadap onset | **diterapkan v0.6**: penundaan acak U(0, 15) s per *run*, fase sebagai kovariat | 19.3.10, 19.3.5 (e) |
| N-2 uji arah tanpa syarat efek minimum | **diterapkan v0.6**: tingkat putusan bermakna / kecil / tidak dapat disimpulkan / berlawanan | 19.4.8 |
| N-3 disk OS *ephemeral* tidak didukung Dasv5 | **diterapkan v0.6**: `--node-osdisk-type Managed`, dicatat per *run* | 19.3.8 |
| m-1 sampai m-10 | **diterapkan v0.6**: m-1 jangkar *scale* = p95 bawaan *shipping* 0,5 × SLO; m-2 T̄_svc pada laju rendah tetap; m-3 definisi SD c_D1; m-4 c_tolak di bawah *limit* (angka K1 = batas atas); m-5 klaim efisiensi "selama jendela beban"; m-6 tertutup oleh penghapusan P22; m-7 daftar DaemonSet `sut`, tanpa Loki/promtail; m-8 cek sisa antar-*run* eksploratori; m-9 waktu blok ±2,1 jam; m-10 ICH E9 diverifikasi dari teks asli | 19.3.5, 19.3.7, 19.3.11, 19.4.3, 19.4.8 |
