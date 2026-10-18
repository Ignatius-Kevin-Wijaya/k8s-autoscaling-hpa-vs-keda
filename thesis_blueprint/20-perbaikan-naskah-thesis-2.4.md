# Thesis Blueprint — Part 20: Daftar perbaikan naskah untuk Thesis-2.4

> Dibuat 2026-10-18. Satu tempat untuk perbaikan **teks** yang akan masuk ke Thesis-2.4, dibangun di atas
> `Thesis-2.3-bersih.docx` (salinan yang akan dikirim). Bagian ini hanya mencatat; belum ada yang diterapkan ke naskah.
> Lokasi merujuk ke subbab, tabel, atau paragraf Thesis-2.3. Berkas ini di-*commit* 2026-10-19 atas permintaan pemilik, setelah
> pemeriksaan item privat: rujukan ke catatan pemilik di luar repo ditulis "rujukan privat #n", dan isinya tidak ditulis di sini.
>
> **Sumber butir:**
> - **[E]** tinjauan eksternal atas Thesis-2.3 yang ditempel pemilik (sumber tidak diketahui), diverifikasi butir per butir
>   oleh sesi utama terhadap naskah, data, dan repositori pada 2026-10-16 (hanya butir yang terbukti benar dicatat);
> - **[M]** temuan resolusi *metrics-server* per platform, dicek di dokumentasi resmi 2026-10-18 (Part 19 §19.3.9);
> - **[R]** temuan tinjauan *red team* atas Thesis-1.7 dan Thesis-2.2 yang masih terbuka (status di
>   [13-review-redteam-thesis-1.7.md](13-review-redteam-thesis-1.7.md) dan
>   [15-review-redteam-thesis-2.2.md](15-review-redteam-thesis-2.2.md)); tidak diulang satu per satu di sini.
>
> **Catatan:** perbaikan yang bergantung pada keputusan Eksperimen 2 (Part 17 atau Part 19), judul, atau rumusan masalah
> tidak dicatat di sini; itu ditentukan setelah keputusan pembimbing.

## 20.1 Teks saja, dapat langsung dikerjakan

| # | Lokasi | Masalah | Perbaikan | Sumber |
|---|---|---|---|---|
| T1 | 5.1 paragraf penutup; abstrak (kedua bahasa) | menyatakan efek jenis metrik "telah dipisahkan" / H3 "memisahkan efek metrik dari efek mesin", bertentangan dengan 4.6.4 dan 5.2.2 butir 3, 4, 9 | tulis sebagai efek paket (sinyal beserta jalur ukur dan titik pemicu); seragamkan istilah "jalur metrik" (*adapter* vs KEDA) dan "jalur pengukuran" (*metrics-server* vs Prometheus) | [E], [R] M-2 |
| T2 | 5.1 | "menghemat kapasitas yang dicadangkan (41,1–87,0% replika-detik B2)" terbaca sebagai hemat 41,1–87,0% | "memakai 41,1–87,0% replika-detik B2 (hemat 13,0–58,9%)" | [E] |
| T3 | 5.1 | "kecil pada pola *oscillating* (4,0–61,5%)" mencampur dua layanan | pisahkan: *auth* 4,0–32,0%, *shipping* 23,1–61,5% (seperti 4.5.1) | [E] |
| T4 | 5.1 penutup | "dua jenis layanan" | "dua layanan" (premis jenis layanan tidak terwujud) | [E] |
| T5 | 5.1, Hipotesis 1 (*shipping*) | *oscillating* ditulis "tidak unggul", padahal arahnya berbalik | "berbalik arah (+40 detik), tidak signifikan" | [E] |
| T6 | 5.1 (RM1 dan ringkasan SLO) | "H1 terendah pada *oscillating*" tanpa menyebut bahwa sel *shipping oscillating* H1 gagal G6 pada repetisi 1–2 dan H1 vs H2 tidak signifikan | tambahkan kedua keterangan; nyatakan bahwa ini dibaca dari median | [E] |
| T7 | 5.1 RM2; abstrak | signifikansi efek metrik tidak membawa catatan bahwa tidak ada uji yang signifikan bila Holm dihitung atas 12 uji (p terkecil 0,0952) atau 36 uji (0,2857) | bawa catatan 4.6.4 ke 5.1 dan abstrak | [E], [R] M-4 |
| T8 | 5.2.1 (a), (b), (d), (e) | saran tanpa syarat | (a) berlaku untuk layanan dengan *load shedding*; (b) H1 berbeda pada target **dan** jendela; (d) 17–19 detik spesifik klaster dan *image* ini; (e) harga *load shedding* berupa 503 yang tercatat sebagai *error* | [E], [R] m-14 |
| T9 | 3.2.4 paragraf penutup; kalimat pengantar Tabel 3.11; judul Tabel 3.11; 3.3.3 kalimat pembuka | SLO disebut "disepakati lebih dahulu" / "ditetapkan sebelum kampanye", padahal SLO *shipping* 1.000 ms ditetapkan setelah data | keluarkan SLO dari klaim "lebih dahulu" atau tambahkan keterangan aturan SLO 11 Oktober 2026 (3.3.6) | [E] |
| T10 | 3.3.3, 3.3.6, 4.3.2 | "target 70% diubah menjadi 80% sebelum ada hasil H1 pada target tersebut" dan "keduanya dilakukan sebelum ada data yang terdampak" tidak akurat: dua *run* H1 sudah berjalan pada 70% | tulis apa adanya (diubah setelah dua *run* H1 pada 70%, demi validitas konstruk: H1 = HPA bawaan); laporkan hasil kedua *run* yang digantikan di lampiran | [E] |
| T11 | Tabel 2.4 baris "Detik di atas SLO" | definisi tidak menyebut *bin* 10 detik dan bahwa permintaan gagal dihitung sebagai latensi tak hingga | samakan dengan Tabel 3.12 (rujukan privat #6) | [E], [R] M-5 |
| T12 | 2.2.2 | kata "praktisi" masih ada (rujukan privat #2) | ganti rumusannya | [E] |
| T13 | 1.2 (RQ1); paragraf setelah Tabel 2.4 (2.3) | "*error rate*" tegak dua kali, satu-satunya kebocoran huruf miring di BAB 1–5 menurut pemindaian 2026-10-16 (rujukan privat #1); "port" dapat dipertimbangkan | miringkan | [E] |
| T14 | 4.5.2 dan keterangan Tabel H.2 | interval Hodges–Lehmann 96,8% tidak dijelaskan | jelaskan: tingkat terdekat ≥ 95% yang dapat dicapai untuk n = m = 5, yaitu 1 − 2 × 4/252 | [E] |
| T15 | BAB 4 | koreksi *bin* O1 (10 Oktober 2026) hanya disebut di 3.3.6 dan 3.3.7 | sebut satu kalimat di BAB 4 (misalnya 4.4.1) | [E] |
| T16 | 4.3.1 | kalimat *ladder* berbelit | pecah menjadi dua atau tiga kalimat | [E] |
| T17 | 3.2.4 | "sebelum generator beban diperbaiki (penggunaan ulang koneksi)" ambigu terhadap `noConnectionReuse: true` di 3.3.3 | "… diperbaiki agar setiap permintaan membuka koneksi baru (koneksi yang dipakai ulang membuat beban tidak tersebar ke *pod* baru)" | [E] |
| T18 | 3.3.4 | cara penentuan waktu O4 (`lastScaleTime`) ditetapkan setelah seluruh data, tetapi 3.3.4 hanya menyebut "O4 ditetapkan sebelum repetisi 3–5" | samakan dengan 3.3.7 | [E] |
| T19 | 3.3.2, Tabel 3.9 | Service CIDR 10.0.0.0/16 sama dengan rentang `ecommerce-vm-vnet`, ditulis berdampingan | satu kalimat penjelas (Service CIDR adalah alamat virtual di dalam klaster; tumpang tindih hanya bermasalah bila kedua jaringan terhubung), setelah dicek apakah kedua VNet di-*peering* | [E] |
| T20 | Tabel 4.3 baris "Semua" | hash kode tertulis sebagai "overlay …", sedangkan 4.2.2 menyebut hash kode | beri label "hash kode *overlay*" | [E] (catatan sesi utama) |
| T21 | Tabel 4.20; Lampiran H | median waktu tiga *pod Ready* K1 dan H1 (68,8 dan 113,1 detik) tidak ada di tabel mana pun | tambahkan median per konfigurasi ke Tabel H.1 (sumber: `analysis/part12/report.md`) | [E] |
| T22 | 4.6.2 | "waktu tunggu mendominasi latensi" tanpa angka | tambahkan hitungan: CPU *shipping* ±7 ms per permintaan (125m pada 17,9 req/s, Tabel H.3) vs penundaan *carrier* paling lambat 464–929 ms (ketiga *carrier* dipanggil paralel) | [E] |
| T23 | 3.3.5 (ketentuan 12 Oktober) | dibingkai sebagai "ketentuan yang ditambahkan setelah seluruh hasil terlihat" | tulis sebagai fakta bertanggal: pemeriksaan manipulasi gagal, jadi Hipotesis 1 tidak dapat dinilai sebagaimana dirumuskan | [E] |
| T24 | 3.3.5–3.3.7 | keputusan sebelum dan sesudah data tersebar di beberapa paragraf | satu tabel kronologi "keputusan sebelum vs sesudah data" | [E], [R] m-8 |

## 20.2 Resolusi *metrics-server* (temuan baru, 2026-10-18)

**Masalah [M].** Naskah menulis bahwa *metrics-server* "secara bawaan" memperbarui nilainya setiap 60 detik. Itu benar untuk
bawaan program (FAQ *metrics-server*) dan untuk AKS (K1 mengukur ±61 detik), tetapi manifest resmi dan *Helm chart* resmi
upstream menyetel `--metric-resolution=15s`. Di AKS resolusinya tidak dapat diubah (*add-on* terkelola); di EKS
*metrics-server* dipasang sendiri dan resolusinya dapat diatur; di GKE ada Performance HPA profile yang mengirim metrik
CPU/memori lewat `gke-metrics-agent` untuk penskalaan yang lebih cepat. Keterlambatan CPU sekitar satu menit di K1 karena
itu adalah sifat *metrics-server* terkelola AKS, dan itu batas generalisasi (rincian dan sumber: Part 19 §19.3.9).

| # | Lokasi | Perbaikan |
|---|---|---|
| M1 | 1.1 (kalimat jalur pengukuran) | "pada AKS, *metrics-server* terkelola memperbarui metrik sumber daya kira-kira sekali per menit (resolusi bawaan program 60 detik, tidak dapat diubah di AKS)" |
| M2 | 2.2.1 (paragraf HPA) dan Tabel 2.3 baris "Sumber metrik bawaan" | sebut bahwa resolusi bawaan program 60 detik, manifest resmi upstream 15 detik, dan nilainya bergantung pada cara pemasangan atau penyedia |
| M3 | 3.3.3 butir a | "*metrics-server* terkelola AKS, yang memakai resolusi bawaan 60 detik dan tidak dapat diubah" |
| M4 | 4.1 dan 4.4.3 | selang terukur 61,2 detik "sesuai dengan resolusi bawaan program 60 detik yang dipakai *metrics-server* terkelola AKS" |
| M5 | Tabel 4.21 baris "HPA berbasis CPU" dan 5.2.1 (c) | syarat: "pada klaster yang *metrics-server*-nya beresolusi 60 detik, seperti AKS" |
| M6 | 4.6.4 (generalisasi) | tambahkan: keunggulan laju yang berasal dari jalur ukur CPU bergantung pada kesegaran CPU di platform (EKS dengan pemasangan standar ±15 detik; GKE dengan Performance HPA profile) |
| M7 | 5.2.2 butir 4 | tambahkan bahwa di AKS resolusi tidak dapat diubah, sehingga CPU yang lebih segar hanya dapat diperoleh lewat Prometheus dan *adapter* (metrik kustom) |
| M8 | 2.4.1 dan Tabel 2.5 (Nguyen et al., 2020) | cek ulang apakah "bawaan 60 detik" di sana menggambarkan pengaturan studi Nguyen et al.; bila ya, biarkan dan bedakan dari bawaan manifest upstream saat ini |

Rujukan baru yang dibutuhkan: FAQ dan manifest *metrics-server* (kubernetes-sigs), Microsoft Learn *Configure Metrics
Server VPA in AKS*, dokumentasi EKS *Metrics Server*, dokumentasi GKE *Horizontal Pod autoscaling* dan *release notes*
(Performance HPA profile). Gaya APA 6 seperti rujukan dokumentasi lain di naskah.

## 20.3 Butuh bahan atau keputusan sebelum ditulis

| # | Butir | Yang dibutuhkan | Sumber |
|---|---|---|---|
| B1 | Subbab teori eksperimen kuantitatif (rujukan privat #3 dan #8): faktor, randomisasi dan blok, replikasi, ancaman validitas | rujukan yang dicek (kandidat: Montgomery, *Design and Analysis of Experiments*; Wohlin et al., *Experimentation in Software Engineering*; Jain 1991 sudah dirujuk) | [E] |
| B2 | Standar internasional untuk KPI (rujukan privat #5) | rujukan yang dicek (kandidat: ISO/IEC 25010 *performance efficiency*, belum diverifikasi) | [E] |
| B3 | Hasil dua *run* H1 70% yang digantikan (lampiran) | angka dari `experiment-results-openloop/superseded-h1-70pct/`, dihitung dengan skrip yang sama | [E], T10 |
| B4 | Riwayat Hidup | teks dari pemilik | [E] |
| B5 | Penyelarasan judul, rumusan masalah, dan hipotesis dengan apa yang diukur (mesin = jalur metrik; premis jenis layanan) | keputusan pembimbing | [R] K-1, M-1 |

## 20.4 Cara kerja saat menerapkan

- Diterapkan sebagai *tracked changes* di atas `Thesis-2.3.docx` (penulis "Ignatius Kevin Wijaya"), lalu salinan bersih
  dibuat, mengikuti alur Thesis-1.x sampai 2.3 (`tools/thesis-docx/`).
- Nomor halaman daftar isi diukur ulang dari tata letak Word setelah perubahan teks (`measure_pages.ps1`, `toc_match.py`).
- Setiap butir yang selesai ditandai di tabel ini dengan versi naskahnya.
