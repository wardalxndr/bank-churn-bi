# Panduan Bikin Dashboard Looker Studio

Tujuan: satu halaman yang jawab tiga hal. Siapa paling bocor, kenapa bocor, siapa yang ditelepon dulu.

## 1. Siapkan data

1. Pastikan marts sudah ada: jalankan `py pipeline/build_marts.py`
2. Bikin satu file gabungan: `py pipeline/export_pack.py`
   Hasilnya `data/dashboard_pack.xlsx` berisi 3 tab: mart_customer, mart_cohort, save_list
3. Buka Google Sheets, File lalu Import, pilih Upload, ambil file itu
4. Pilih "Replace spreadsheet". Pastikan 3 tab kebaca dengan nama sama

## 2. Sambung ke Looker Studio

1. Buka lookerstudio.google.com, login Google
2. Create lalu Report. Di panel kanan pilih Add data lalu Google Sheets
3. Pilih spreadsheet tadi, pilih tab mart_customer
4. Ulang Add data buat tab mart_cohort dan save_list
5. Satu tab jadi satu data source. Tidak perlu blend

## 3. Susun halaman dari atas ke bawah

Aturan mata: angka besar di atas, pola di tengah, aksi di bawah.

Baris KPI, 4 kartu kecil:

| Kartu | Data source | Cara hitung | Judul tile |
|---|---|---|---|
| 1 | mart_customer | Record Count | Total nasabah 10.000 |
| 2 | mart_customer | SUM(Exited) | 2.037 nasabah churn |
| 3 | mart_customer | AVG(Exited) format percent | Churn rate 20,4% |
| 4 | save_list | Record Count | Save list 500 |

Tengah, 4 grafik batang:
1. Churn rate per Geography: dimension Geography, metric AVG(Exited), sort turun
2. Churn rate per NumOfProducts: dimension NumOfProducts, metric AVG(Exited)
3. Churn rate active vs inactive: dimension IsActiveMember, metric AVG(Exited)
4. Churn rate per bucket tenure: pakai source mart_cohort, dimension tenure_bucket, metric churn_rate

Bawah, 2 tabel:
1. Top alasan: source save_list, dimension reason, metric Record Count, sort turun, top 10
2. Save list: source save_list, kolom CustomerId, Geography, Age, Balance, risk, reason. Sort risk turun. Kasih heatmap di kolom risk

Filter di strip atas halaman:
- Geography (dropdown)
- NumOfProducts (dropdown)

## 4. Rapikan biar kelihatan profesional

1. Format angka: persen satu desimal, balance pakai pemisah ribuan
2. Warna aksen satu saja, misal merah tua buat bahaya, sisanya abu
3. Judul tiap tile jadi kalimat temuan, bukan "Chart 1"
4. Footer wajib: sumber data dan tanggal update
5. Jangan semua chart. Tabel save list lebih jujur karena per orang

## 5. Bagikan link

1. Klik Share lalu Manage access
2. Ubah jadi Anyone with the link, akses Viewer
3. Copy link, taruh di README dan CV

## Catatan

- Google Sheets itu snapshot. Kalau data berubah, impor ulang lalu Refresh di Looker
- Upgrade berikutnya: load marts ke BigQuery, terus hubungkan Looker ke BigQuery. Link tetap, data hidup, tinggal jadwalkan query

## Checklist dashboard bagus

- Bisa jawab "terus gue ngapain" dalam 5 detik pertama
- Tidak perlu scroll buat lihat KPI
- Setiap angka punya periode dan sumber
- Warna tidak lebih dari tiga
- Ada tombol ekspor CSV atau XLSX
