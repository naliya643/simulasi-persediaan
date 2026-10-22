# Simulasi Persediaan Barang Menggunakan Metode Monte Carlo

**Mata kuliah:** Simulasi dan Pemodelan  
**Jenis proyek:** Aplikasi simulasi persediaan berbasis web  
**Bahasa:** Python

## 1. Deskripsi proyek

Proyek ini mensimulasikan perubahan persediaan satu jenis barang selama periode tertentu ketika permintaan harian tidak pasti. Metode Monte Carlo digunakan untuk mengambil permintaan harian dari distribusi probabilitas diskret, kemudian model persediaan menghitung penjualan terpenuhi, permintaan yang tidak terpenuhi (*lost sales*), stok akhir, serta pemesanan ulang.

Aplikasi menyediakan parameter yang dapat diubah pengguna dan menjalankan banyak replikasi simulasi. Hasil antar-replikasi digunakan untuk mengestimasi rata-rata permintaan, jumlah permintaan yang tidak terpenuhi, dan probabilitas terjadinya kehabisan stok selama periode simulasi.

> **Penting:** distribusi dalam `data/demand_distribution.csv` adalah data sintetis untuk demonstrasi, bukan data penjualan toko nyata. Ganti atau kalibrasi distribusi tersebut jika tersedia data observasi.

## 2. Tujuan

1. Memahami penerapan simulasi Monte Carlo pada sistem persediaan.
2. Mengamati dampak stok awal, titik pemesanan ulang, jumlah pemesanan, dan waktu pengadaan.
3. Membandingkan hasil dari beberapa pengulangan simulasi.
4. Mendokumentasikan asumsi, kode, pengujian, dan hasil melalui GitHub.

## 3. Metode dan model

### Distribusi permintaan

Contoh distribusi sintetis:

| Permintaan harian (unit) | Probabilitas |
|---:|---:|
| 0 | 0,10 |
| 2 | 0,20 |
| 4 | 0,40 |
| 6 | 0,20 |
| 8 | 0,10 |
| **Total** | **1,00** |

Pada setiap hari, satu nilai permintaan dipilih secara acak berdasarkan probabilitas tersebut.

### Persamaan persediaan

Dengan asumsi *lost sales* (permintaan yang tidak terpenuhi tidak menjadi utang pesanan):

- Penjualan terpenuhi: `min(stok tersedia, permintaan)`
- Permintaan tidak terpenuhi: `max(permintaan - stok tersedia, 0)`
- Stok akhir: `stok tersedia - penjualan terpenuhi`

Barang yang dijadwalkan tiba ditambahkan pada awal hari kedatangannya. Pemesanan baru dilakukan ketika posisi persediaan, yaitu stok tersedia ditambah jumlah pesanan yang belum tiba, sama dengan atau di bawah titik pemesanan ulang (ROP). Pesanan tiba setelah `lead_time` hari.

Monte Carlo dijalankan dengan mengulangi simulasi untuk banyak replikasi. Hasil ringkasan merupakan estimasi dari replikasi yang dijalankan, bukan kepastian untuk masa depan.

## 4. Variabel model

| Variabel | Keterangan |
|---|---|
| Stok awal | Jumlah unit tersedia pada awal simulasi |
| Permintaan harian | Nilai acak yang diambil dari distribusi |
| ROP | Titik pemesanan ulang |
| Jumlah pemesanan | Unit pada setiap pesanan |
| Lead time | Hari antara pemesanan dan kedatangan |
| Durasi | Jumlah hari dalam satu replikasi |
| Replikasi | Jumlah pengulangan simulasi Monte Carlo |

## 5. Sumber data

File `data/demand_distribution.csv` berisi **data sintetis** yang dibuat untuk demonstrasi metode. Data ini bukan catatan transaksi aktual dan tidak boleh disebut sebagai data empiris.

Jika memakai data nyata, cantumkan nama sumber, periode pengamatan, cara pengumpulan, dan langkah pengolahan datanya.

## 6. Teknologi

- Python
- Streamlit untuk antarmuka web
- Pandas untuk pengolahan tabel
- NumPy untuk pengambilan sampel acak dan pengelolaan seed
- Matplotlib tidak diperlukan pada versi ini karena grafik dasar disediakan Streamlit

## 7. Instalasi dan menjalankan aplikasi

Disarankan menggunakan Python 3.10 atau lebih baru.

### Windows

```bash
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
streamlit run app.py
```

### macOS / Linux

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
streamlit run app.py
```

Aplikasi akan menampilkan alamat lokal di terminal, biasanya `http://localhost:8501`.

## 8. Struktur folder

```text
simulasi_persediaan_monte_carlo/
├── app.py
├── simulator.py
├── requirements.txt
├── README.md
├── .gitignore
├── data/
│   └── demand_distribution.csv
└── tests/
    └── test_simulator.py
```

## 9. Pengujian

Pengujian otomatis tersedia di `tests/test_simulator.py`.

```bash
pip install pytest
pytest -q
```

Pengujian memeriksa validitas distribusi probabilitas, penolakan total probabilitas yang tidak sama dengan 1, jumlah hari hasil simulasi, dan konsistensi hasil saat seed yang sama digunakan.

## 10. Persentase keterlibatan AI

Isi bagian ini berdasarkan penggunaan AI yang benar-benar terjadi selama pengerjaan. Jangan mencantumkan angka perkiraan tanpa metode pengukuran yang disepakati dengan dosen.

Contoh format pelaporan:

- **Bagian yang dikerjakan sendiri:** [jelaskan bagian yang benar-benar dikerjakan sendiri].
- **Bantuan AI:** [jelaskan bagian yang benar-benar dibantu AI].
- **Metode perhitungan persentase:** [jelaskan metode yang diminta atau disetujui dosen].
- **Bukti:** [tautan atau tangkapan layar bukti yang relevan, sesuai ketentuan kampus].

Persentase akhir harus sesuai batas maksimal yang ditetapkan dosen. Riwayat commit GitHub menunjukkan perkembangan kode, tetapi tidak dengan sendirinya membuktikan persentase kontribusi AI.

## 11. Batasan model

- Model hanya mencakup satu jenis barang.
- Permintaan diambil dari distribusi diskret yang diasumsikan.
- Permintaan yang tidak dapat dipenuhi dicatat sebagai *lost sales*.
- Belum ada biaya pemesanan, biaya penyimpanan, kedaluwarsa, atau optimasi jumlah pesanan.
- Hasil simulasi bergantung pada parameter, distribusi, dan jumlah replikasi.

## 12. Pelaporan GitHub

Lakukan commit secara bertahap ketika mengembangkan kode, menguji model, memperbaiki dokumentasi, dan menganalisis hasil. Pastikan riwayat commit mencerminkan pekerjaan yang benar-benar dilakukan. Jangan membuat commit palsu untuk mengesankan aktivitas.
