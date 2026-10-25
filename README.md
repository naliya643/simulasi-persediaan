Nama: Maimunah Hilaliyah Aprilia Widagdo
NIM: 2311060130
Judul Proyek: Aplikasi Simulasi Persediaan Stok Barang 

1. Deskripsi Proyek
Proyek ini mensimulasikan beberapa jumlah persediaan barang selama periode tertentu ketika permintaan harian tidak pasti.Proyek ini menggunakan metode Monte Carlo untuk mengambil permintaan harian  dari distribusi probabilitas diskret, kemudian model persediaan menghitung penjualan terpenuhi, permintaan yang tidak terpenuhi (lost sales), stok akhir, serta pemesanan ulang.
Aplikasi ini menyediakan fitur parameter yang dapat diubah – ubah serta dapat menjalankan simulasi berulang. Hasilnya adalah berupa estimas rata-rata permintaan, jumlah permintaan tidak terpenuhi dan kemungkinan terjadinya kehabisan stok.

2. Tujuan	
1. Memahami penerapan metode Monte Carlo. 
2. Memahami dampak jumlah stok awal, pemesanan ulang, jumlah pemesanan dan waktu pengadaan.
3. Mengamati hasil siumulasi pengadaan.
4. Mendokumentasi hasil simulasi.


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

