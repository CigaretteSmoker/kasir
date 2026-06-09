# 🛒 Aplikasi Kasir Warung (Siap Pakai)

Aplikasi kasir (Point of Sale) sederhana, cepat, dan ringan berbasis desktop yang dirancang khusus untuk manajemen warung atau toko kelontong skala kecil hingga menengah. Dibangun menggunakan **Python** dengan antarmuka grafis (**Tkinter**) dan penyimpanan lokal (**SQLite3**), aplikasi ini bersifat *standalone* tanpa memerlukan instalasi *third-party dependency* tambahan.

---

## ✨ Fitur Utama

* **🛒 Kasir Cepat (Point of Sale):** * Pencarian produk secara *real-time* saat mengetik.
    * Sistem keranjang belanja interaktif (Tambah/Hapus/Kosongkan).
    * Kalkulasi otomatis untuk total belanja dan uang kembalian.
    * Mendukung *shortcut* cepat menggunakan keyboard (`Enter` untuk tambah barang, `F12` untuk *checkout*).
* **📦 Manajemen Produk (CRUD):**
    * Tambah, edit, dan hapus data produk langsung dari aplikasi.
    * Validasi proteksi nama produk ganda (*unique constraint*).
    * Sistem manajemen stok otomatis yang berkurang setiap kali transaksi berhasil dilakukan.
* **🧾 Riwayat Transaksi & Cetak Struk:**
    * Pencatatan riwayat transaksi yang rapi dan terurut berdasarkan waktu.
    * Fitur detail transaksi untuk melihat item apa saja yang terjual.
    * *Auto-generate* cetak struk fisik dalam format file teks (`.txt`) di dalam folder khusus.
* **💾 Database Lokal:**
    * Menggunakan SQLite3 yang terintegrasi langsung.
    * Fitur *Auto-seed data* (otomatis mengisi beberapa contoh produk jika database masih kosong saat pertama kali dijalankan).

---

## 🛠️ Persyaratan Sistem

Aplikasi ini dirancang untuk berjalan tanpa ketergantungan pada pustaka eksternal (*zero external dependencies*). Anda hanya membutuhkan:
* **Python 3.x** (Sudah termasuk modul bawaan `tkinter` dan `sqlite3`).

---

## 🚀 Cara Menjalankan Aplikasi

1.  **Clone Repositori:**
    ```bash
    git clone [https://github.com/username-anda/nama-repo.git](https://github.com/username-anda/nama-repo.git)
    cd nama-repo
    ```

2.  **Jalankan Script:**
    Eksekusi file utama menggunakan Python di terminal atau command prompt Anda:
    ```bash
    python kasir.py
    ```

---

## 📂 Struktur File & Folder Utama

Setelah aplikasi dijalankan pertama kali, sistem akan otomatis membentuk struktur direktori berikut:

```text
├── kasir.py             # File kode utama aplikasi (Tkinter GUI & Logika)
├── kasir_warung.db      # File database SQLite3 (otomatis terbuat)
└── struk/               # Folder tempat penyimpanan file struk belanja (.txt)

⌨️ Pintasan Keyboard (Shortcuts)
Untuk mempercepat pelayanan di kasir, gunakan tombol pintasan berikut:

Double-Click / Enter : Menambahkan produk yang dipilih dari tabel ke dalam keranjang.

F12 : Memproses pembayaran langsung (Checkout).

Lisensi: Bebas digunakan dan dimodifikasi untuk kebutuhan personal maupun komersial skala kecil.
