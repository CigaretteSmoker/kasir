#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Aplikasi Kasir Warung - Siap Pakai
Fitur:
- Kasir cepat (cari, tambah ke keranjang, checkout)
- Manajemen produk (CRUD, stok otomatis)
- Riwayat transaksi + cetak struk TXT
- Database SQLite lokal (kasir_warung.db)
- Tanpa dependency eksternal (hanya tkinter, sqlite3)
"""

import tkinter as tk
from tkinter import ttk, messagebox
import sqlite3
from datetime import datetime
import os
from pathlib import Path

DB_FILE = "kasir_warung.db"
RECEIPT_DIR = Path("struk")
RECEIPT_DIR.mkdir(exist_ok=True)

def rp(amount):
    return f"Rp {amount:,.0f}".replace(",", ".")

class Database:
    def __init__(self):
        self.conn = sqlite3.connect(DB_FILE)
        self.create_tables()
        self.seed_if_empty()

    def create_tables(self):
        c = self.conn.cursor()
        c.execute("""CREATE TABLE IF NOT EXISTS products (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nama TEXT NOT NULL UNIQUE,
            harga INTEGER NOT NULL,
            stok INTEGER NOT NULL
        )""")
        c.execute("""CREATE TABLE IF NOT EXISTS transactions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            waktu TEXT NOT NULL,
            total INTEGER NOT NULL,
            bayar INTEGER NOT NULL,
            kembalian INTEGER NOT NULL
        )""")
        c.execute("""CREATE TABLE IF NOT EXISTS transaction_items (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            transaction_id INTEGER,
            product_id INTEGER,
            nama TEXT,
            harga INTEGER,
            qty INTEGER,
            subtotal INTEGER,
            FOREIGN KEY(transaction_id) REFERENCES transactions(id)
        )""")
        self.conn.commit()

    def seed_if_empty(self):
        c = self.conn.cursor()
        c.execute("SELECT COUNT(*) FROM products")
        if c.fetchone()[0] == 0:
            sample = [
                ("Indomie Goreng", 3500, 50),
                ("Aqua 600ml", 4000, 30),
                ("Kopi Kapal Api", 2000, 40),
                ("Beras 1kg", 14000, 20),
                ("Minyak Goreng 1L", 18000, 15),
                ("Gula 1kg", 16000, 25),
                ("Telur 1kg", 28000, 10),
                ("Roti Tawar", 15000, 12),
            ]
            c.executemany("INSERT INTO products (nama,harga,stok) VALUES (?,?,?)", sample)
            self.conn.commit()

class KasirApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Kasir Warung - Siap Pakai")
        self.geometry("1100x700")
        self.db = Database()
        self.cart = []

        self.style = ttk.Style(self)
        try:
            self.style.theme_use("clam")
        except:
            pass

        self.notebook = ttk.Notebook(self)
        self.notebook.pack(fill="both", expand=True, padx=10, pady=10)

        self.tab_kasir = ttk.Frame(self.notebook)
        self.tab_produk = ttk.Frame(self.notebook)
        self.tab_riwayat = ttk.Frame(self.notebook)

        self.notebook.add(self.tab_kasir, text=" 🛒 Kasir ")
        self.notebook.add(self.tab_produk, text=" 📦 Produk ")
        self.notebook.add(self.tab_riwayat, text=" 🧾 Riwayat ")

        self.build_kasir()
        self.build_produk()
        self.build_riwayat()

        self.load_products_kasir()
        self.load_products_manage()

    # ===== KASIR =====
    def build_kasir(self):
        left = ttk.Frame(self.tab_kasir)
        right = ttk.Frame(self.tab_kasir)
        left.pack(side="left", fill="both", expand=True, padx=(0,5))
        right.pack(side="right", fill="y", padx=(5,0))

        search_frame = ttk.Frame(left)
        search_frame.pack(fill="x", pady=5)
        ttk.Label(search_frame, text="Cari Produk:").pack(side="left")
        self.search_var = tk.StringVar()
        self.search_var.trace_add("write", lambda *a: self.load_products_kasir())
        ttk.Entry(search_frame, textvariable=self.search_var).pack(side="left", fill="x", expand=True, padx=5)

        cols = ("id","nama","harga","stok")
        self.tree_produk = ttk.Treeview(left, columns=cols, show="headings", height=20)
        for c,w in zip(cols, [50,250,100,70]):
            self.tree_produk.heading(c, text=c.upper())
            self.tree_produk.column(c, width=w, anchor="center" if c!="nama" else "w")
        self.tree_produk.pack(fill="both", expand=True)
        self.tree_produk.bind("<Double-1>", lambda e: self.add_to_cart())

        btn_frame = ttk.Frame(left)
        btn_frame.pack(fill="x", pady=5)
        ttk.Button(btn_frame, text="Tambah ke Keranjang (Enter)", command=self.add_to_cart).pack(side="left")
        ttk.Label(btn_frame, text="Qty:").pack(side="left", padx=(10,2))
        self.qty_var = tk.IntVar(value=1)
        ttk.Spinbox(btn_frame, from_=1, to=999, textvariable=self.qty_var, width=5).pack(side="left")

        ttk.Label(right, text="Keranjang", font=("Segoe UI", 12, "bold")).pack()
        cart_cols = ("nama","harga","qty","subtotal")
        self.tree_cart = ttk.Treeview(right, columns=cart_cols, show="headings", height=15)
        for c,w in zip(cart_cols, [180,90,50,100]):
            self.tree_cart.heading(c, text=c.upper())
            self.tree_cart.column(c, width=w, anchor="center" if c!="nama" else "w")
        self.tree_cart.pack(pady=5)

        btn_cart = ttk.Frame(right)
        btn_cart.pack(fill="x")
        ttk.Button(btn_cart, text="Hapus Item", command=self.remove_from_cart).pack(side="left", padx=2)
        ttk.Button(btn_cart, text="Kosongkan", command=self.clear_cart).pack(side="left", padx=2)

        total_frame = ttk.LabelFrame(right, text="Pembayaran")
        total_frame.pack(fill="x", pady=10, padx=2)
        self.total_var = tk.StringVar(value=rp(0))
        ttk.Label(total_frame, text="TOTAL:").grid(row=0,column=0, sticky="w", padx=5, pady=2)
        ttk.Label(total_frame, textvariable=self.total_var, font=("Segoe UI", 16, "bold")).grid(row=0,column=1, sticky="e")

        ttk.Label(total_frame, text="Bayar:").grid(row=1,column=0, sticky="w", padx=5)
        self.bayar_var = tk.StringVar()
        ttk.Entry(total_frame, textvariable=self.bayar_var, font=("Segoe UI", 12)).grid(row=1,column=1, pady=2)
        self.bayar_var.trace_add("write", self.update_kembalian)

        ttk.Label(total_frame, text="Kembalian:").grid(row=2,column=0, sticky="w", padx=5)
        self.kembali_var = tk.StringVar(value=rp(0))
        ttk.Label(total_frame, textvariable=self.kembali_var).grid(row=2,column=1, sticky="e")

        ttk.Button(total_frame, text="CHECKOUT (F12)", command=self.checkout).grid(row=3,column=0,columnspan=2, sticky="ew", pady=10, padx=5)

        self.bind("<Return>", lambda e: self.add_to_cart())
        self.bind("<F12>", lambda e: self.checkout())

    def load_products_kasir(self):
        q = self.search_var.get().lower()
        cur = self.db.conn.cursor()
        if q:
            cur.execute("SELECT id,nama,harga,stok FROM products WHERE lower(nama) LIKE ? ORDER BY nama", (f"%{q}%",))
        else:
            cur.execute("SELECT id,nama,harga,stok FROM products ORDER BY nama")
        rows = cur.fetchall()
        self.tree_produk.delete(*self.tree_produk.get_children())
        for r in rows:
            self.tree_produk.insert("", "end", values=(r[0], r[1], rp(r[2]), r[3]))

    def add_to_cart(self):
        sel = self.tree_produk.selection()
        if not sel:
            return
        item = self.tree_produk.item(sel[0])["values"]
        pid, nama, harga_str, stok = item[0], item[1], item[2], int(item[3])
        harga = int(harga_str.replace("Rp ","").replace(".",""))
        qty = self.qty_var.get()
        if qty > stok:
            messagebox.showwarning("Stok", f"Stok {nama} hanya {stok}")
            return
        for c in self.cart:
            if c["id"] == pid:
                if c["qty"] + qty > stok:
                    messagebox.showwarning("Stok", "Melebihi stok")
                    return
                c["qty"] += qty
                break
        else:
            self.cart.append({"id":pid, "nama":nama, "harga":harga, "qty":qty, "stok":stok})
        self.refresh_cart()

    def refresh_cart(self):
        self.tree_cart.delete(*self.tree_cart.get_children())
        total = 0
        for c in self.cart:
            sub = c["harga"] * c["qty"]
            total += sub
            self.tree_cart.insert("", "end", values=(c["nama"], rp(c["harga"]), c["qty"], rp(sub)))
        self.total_var.set(rp(total))
        self.update_kembalian()

    def remove_from_cart(self):
        sel = self.tree_cart.selection()
        if not sel: return
        idx = self.tree_cart.index(sel[0])
        del self.cart[idx]
        self.refresh_cart()

    def clear_cart(self):
        self.cart = []
        self.refresh_cart()

    def update_kembalian(self, *args):
        try:
            total = int(self.total_var.get().replace("Rp ","").replace(".",""))
            bayar = int(self.bayar_var.get().replace(".","").replace(",","") or 0)
            kembali = bayar - total
            self.kembali_var.set(rp(kembali if kembali>0 else 0))
        except:
            self.kembali_var.set(rp(0))

    def checkout(self):
        if not self.cart:
            messagebox.showinfo("Kosong", "Keranjang masih kosong")
            return
        try:
            total = int(self.total_var.get().replace("Rp ","").replace(".",""))
            bayar = int(self.bayar_var.get())
        except:
            messagebox.showerror("Error", "Masukkan nominal bayar yang valid")
            return
        if bayar < total:
            messagebox.showwarning("Kurang", "Uang bayar kurang")
            return
        kembali = bayar - total
        waktu = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        cur = self.db.conn.cursor()
        cur.execute("INSERT INTO transactions (waktu,total,bayar,kembalian) VALUES (?,?,?,?)",
                    (waktu, total, bayar, kembali))
        trans_id = cur.lastrowid
        for c in self.cart:
            sub = c["harga"]*c["qty"]
            cur.execute("INSERT INTO transaction_items (transaction_id,product_id,nama,harga,qty,subtotal) VALUES (?,?,?,?,?,?)",
                        (trans_id, c["id"], c["nama"], c["harga"], c["qty"], sub))
            cur.execute("UPDATE products SET stok = stok - ? WHERE id = ?", (c["qty"], c["id"]))
        self.db.conn.commit()

        struk_path = RECEIPT_DIR / f"struk_{trans_id}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt"
        with open(struk_path, "w", encoding="utf-8") as f:
            f.write("===== WARUNG KITA =====\n")
            f.write(f"{waktu}\n")
            f.write("------------------------\n")
            for c in self.cart:
                f.write(f"{c['nama']} x{c['qty']}  {rp(c['harga']*c['qty'])}\n")
            f.write("------------------------\n")
            f.write(f"TOTAL: {rp(total)}\n")
            f.write(f"BAYAR: {rp(bayar)}\n")
            f.write(f"KEMBALI: {rp(kembali)}\n")
            f.write("Terima kasih!\n")
        
        messagebox.showinfo("Sukses", f"Transaksi berhasil!\nKembalian: {rp(kembali)}\nStruk: {struk_path.name}")
        self.clear_cart()
        self.bayar_var.set("")
        self.load_products_kasir()
        self.load_products_manage()
        self.load_riwayat()

    # ===== PRODUK =====
    def build_produk(self):
        top = ttk.Frame(self.tab_produk)
        top.pack(fill="x", pady=5, padx=5)
        ttk.Button(top, text="Tambah Produk", command=self.produk_add).pack(side="left", padx=2)
        ttk.Button(top, text="Edit", command=self.produk_edit).pack(side="left", padx=2)
        ttk.Button(top, text="Hapus", command=self.produk_delete).pack(side="left", padx=2)
        ttk.Button(top, text="Refresh", command=self.load_products_manage).pack(side="left", padx=2)

        cols = ("id","nama","harga","stok")
        self.tree_manage = ttk.Treeview(self.tab_produk, columns=cols, show="headings")
        for c,w in zip(cols, [50,300,120,80]):
            self.tree_manage.heading(c, text=c.upper())
            self.tree_manage.column(c, width=w, anchor="center" if c!="nama" else "w")
        self.tree_manage.pack(fill="both", expand=True, padx=5, pady=5)

    def load_products_manage(self):
        cur = self.db.conn.cursor()
        cur.execute("SELECT id,nama,harga,stok FROM products ORDER BY id DESC")
        self.tree_manage.delete(*self.tree_manage.get_children())
        for r in cur.fetchall():
            self.tree_manage.insert("", "end", values=(r[0], r[1], rp(r[2]), r[3]))

    def produk_add(self):
        self.produk_form("Tambah")

    def produk_edit(self):
        sel = self.tree_manage.selection()
        if not sel: return
        vals = self.tree_manage.item(sel[0])["values"]
        self.produk_form("Edit", vals)

    def produk_form(self, mode, data=None):
        win = tk.Toplevel(self)
        win.title(f"{mode} Produk")
        win.grab_set()
        ttk.Label(win, text="Nama:").grid(row=0,column=0, padx=5,pady=5, sticky="w")
        nama = ttk.Entry(win, width=30)
        nama.grid(row=0,column=1, padx=5,pady=5)
        ttk.Label(win, text="Harga:").grid(row=1,column=0, padx=5,pady=5, sticky="w")
        harga = ttk.Entry(win)
        harga.grid(row=1,column=1, padx=5,pady=5)
        ttk.Label(win, text="Stok:").grid(row=2,column=0, padx=5,pady=5, sticky="w")
        stok = ttk.Entry(win)
        stok.grid(row=2,column=1, padx=5,pady=5)

        if data:
            nama.insert(0, data[1])
            harga.insert(0, str(data[2]).replace("Rp ","").replace(".",""))
            stok.insert(0, data[3])

        def save():
            try:
                n = nama.get().strip()
                h = int(harga.get())
                s = int(stok.get())
                if not n: raise ValueError
            except:
                messagebox.showerror("Error", "Isi dengan benar")
                return
            cur = self.db.conn.cursor()
            if mode=="Tambah":
                try:
                    cur.execute("INSERT INTO products (nama,harga,stok) VALUES (?,?,?)", (n,h,s))
                except sqlite3.IntegrityError:
                    messagebox.showerror("Error", "Nama produk sudah ada")
                    return
            else:
                cur.execute("UPDATE products SET nama=?,harga=?,stok=? WHERE id=?", (n,h,s,data[0]))
            self.db.conn.commit()
            self.load_products_manage()
            self.load_products_kasir()
            win.destroy()

        ttk.Button(win, text="Simpan", command=save).grid(row=3,column=0,columnspan=2, pady=10)

    def produk_delete(self):
        sel = self.tree_manage.selection()
        if not sel: return
        vals = self.tree_manage.item(sel[0])["values"]
        if messagebox.askyesno("Hapus", f"Hapus {vals[1]}?"):
            cur = self.db.conn.cursor()
            cur.execute("DELETE FROM products WHERE id=?", (vals[0],))
            self.db.conn.commit()
            self.load_products_manage()
            self.load_products_kasir()

    # ===== RIWAYAT =====
    def build_riwayat(self):
        top = ttk.Frame(self.tab_riwayat)
        top.pack(fill="x", pady=5)
        ttk.Button(top, text="Refresh", command=self.load_riwayat).pack(side="left", padx=5)
        ttk.Button(top, text="Lihat Detail", command=self.riwayat_detail).pack(side="left", padx=5)

        cols = ("id","waktu","total","bayar","kembalian")
        self.tree_riwayat = ttk.Treeview(self.tab_riwayat, columns=cols, show="headings")
        for c,w in zip(cols, [50,180,120,120,120]):
            self.tree_riwayat.heading(c, text=c.upper())
            self.tree_riwayat.column(c, width=w, anchor="center")
        self.tree_riwayat.pack(fill="both", expand=True, padx=5, pady=5)
        self.tree_riwayat.bind("<Double-1>", lambda e: self.riwayat_detail())
        self.load_riwayat()

    def load_riwayat(self):
        cur = self.db.conn.cursor()
        cur.execute("SELECT id,waktu,total,bayar,kembalian FROM transactions ORDER BY id DESC LIMIT 200")
        self.tree_riwayat.delete(*self.tree_riwayat.get_children())
        for r in cur.fetchall():
            self.tree_riwayat.insert("", "end", values=(r[0], r[1], rp(r[2]), rp(r[3]), rp(r[4])))

    def riwayat_detail(self):
        sel = self.tree_riwayat.selection()
        if not sel: return
        tid = self.tree_riwayat.item(sel[0])["values"][0]
        cur = self.db.conn.cursor()
        cur.execute("SELECT nama,harga,qty,subtotal FROM transaction_items WHERE transaction_id=?", (tid,))
        items = cur.fetchall()
        detail = "\n".join([f"{i[0]} x{i[2]} = {rp(i[3])}" for i in items])
        messagebox.showinfo(f"Transaksi #{tid}", detail or "Tidak ada item")

if __name__ == "__main__":
    app = KasirApp()
    app.mainloop()
py
