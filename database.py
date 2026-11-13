"""
SIGTEMBAKAU - Database Schema & Initialization
Mengimplementasikan perancangan basis data sesuai Dokumen WebGIS Tembakau.
"""
import sqlite3
import os
import json

DB_FILE = os.path.join(os.path.dirname(__file__), "sigtembakau.db")

def get_db():
    conn = sqlite3.connect(DB_FILE)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    conn = get_db()
    cursor = conn.cursor()

    # 1. roles
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS roles (
        id_role INTEGER PRIMARY KEY AUTOINCREMENT,
        nama_role VARCHAR(30) UNIQUE NOT NULL,
        keterangan TEXT
    );
    """)

    # 2. users
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS users (
        id_user INTEGER PRIMARY KEY AUTOINCREMENT,
        id_role INTEGER NOT NULL,
        nama_lengkap VARCHAR(100) NOT NULL,
        email VARCHAR(100) UNIQUE NOT NULL,
        password_hash VARCHAR(255) NOT NULL,
        no_hp VARCHAR(20),
        wilayah_tugas VARCHAR(100),
        status_aktif BOOLEAN DEFAULT 1,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (id_role) REFERENCES roles (id_role)
    );
    """)

    # 3. wilayah (sentra kabupaten & kecamatan/desa)
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS wilayah (
        id_wilayah INTEGER PRIMARY KEY AUTOINCREMENT,
        kode_wilayah VARCHAR(15) UNIQUE NOT NULL,
        nama_wilayah VARCHAR(100) NOT NULL,
        tingkat VARCHAR(15) NOT NULL, -- provinsi, kabupaten, kecamatan, desa
        id_induk INTEGER,
        lat REAL,
        lng REAL,
        luas_potensi_ha REAL DEFAULT 0,
        geom_geojson TEXT,
        FOREIGN KEY (id_induk) REFERENCES wilayah (id_wilayah)
    );
    """)

    # 4. kelompok_tani
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS kelompok_tani (
        id_kelompok INTEGER PRIMARY KEY AUTOINCREMENT,
        nama_kelompok VARCHAR(100) NOT NULL,
        id_wilayah INTEGER NOT NULL,
        ketua VARCHAR(100),
        jumlah_anggota INTEGER DEFAULT 0,
        FOREIGN KEY (id_wilayah) REFERENCES wilayah (id_wilayah)
    );
    """)

    # 5. petani
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS petani (
        id_petani INTEGER PRIMARY KEY AUTOINCREMENT,
        id_user INTEGER,
        id_kelompok INTEGER,
        nik VARCHAR(16) UNIQUE NOT NULL,
        nama_petani VARCHAR(100) NOT NULL,
        alamat TEXT,
        no_hp VARCHAR(20),
        FOREIGN KEY (id_user) REFERENCES users (id_user),
        FOREIGN KEY (id_kelompok) REFERENCES kelompok_tani (id_kelompok)
    );
    """)

    # 6. varietas
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS varietas (
        id_varietas INTEGER PRIMARY KEY AUTOINCREMENT,
        nama_varietas VARCHAR(60) UNIQUE NOT NULL,
        tipe VARCHAR(30) NOT NULL, -- rajangan, Virginia, cerutu, mole, dll
        karakteristik TEXT,
        kesesuaian_lahan TEXT,
        deskripsi TEXT
    );
    """)

    # 7. lahan
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS lahan (
        id_lahan INTEGER PRIMARY KEY AUTOINCREMENT,
        id_petani INTEGER NOT NULL,
        id_wilayah INTEGER NOT NULL,
        kode_lahan VARCHAR(20) UNIQUE NOT NULL,
        luas_ha REAL NOT NULL,
        ketinggian_mdpl INTEGER DEFAULT 500,
        jenis_tanah VARCHAR(50),
        status_kepemilikan VARCHAR(30) DEFAULT 'milik', -- milik, sewa, bagi hasil
        status_verifikasi VARCHAR(15) DEFAULT 'diajukan', -- draft, diajukan, terverifikasi, ditolak
        catatan_verifikasi TEXT,
        geom_geojson TEXT NOT NULL,
        centroid_lat REAL,
        centroid_lng REAL,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (id_petani) REFERENCES petani (id_petani),
        FOREIGN KEY (id_wilayah) REFERENCES wilayah (id_wilayah)
    );
    """)

    # 8. musim_tanam
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS musim_tanam (
        id_musim INTEGER PRIMARY KEY AUTOINCREMENT,
        id_lahan INTEGER NOT NULL,
        id_varietas INTEGER NOT NULL,
        tahun INTEGER NOT NULL,
        musim VARCHAR(10) NOT NULL, -- MT1, MT2
        tgl_tanam DATE NOT NULL,
        tgl_panen_estimasi DATE,
        luas_tanam_ha REAL NOT NULL,
        FOREIGN KEY (id_lahan) REFERENCES lahan (id_lahan),
        FOREIGN KEY (id_varietas) REFERENCES varietas (id_varietas),
        UNIQUE (id_lahan, tahun, musim)
    );
    """)

    # 9. produksi
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS produksi (
        id_produksi INTEGER PRIMARY KEY AUTOINCREMENT,
        id_musim INTEGER NOT NULL,
        tgl_panen DATE NOT NULL,
        luas_panen_ha REAL NOT NULL,
        jumlah_ton REAL NOT NULL,
        produktivitas REAL NOT NULL, -- ton/ha
        grade_mutu VARCHAR(10) NOT NULL, -- A, B, C, D
        catatan TEXT,
        status_verifikasi VARCHAR(15) DEFAULT 'terverifikasi',
        FOREIGN KEY (id_musim) REFERENCES musim_tanam (id_musim)
    );
    """)

    # 10. gudang
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS gudang (
        id_gudang INTEGER PRIMARY KEY AUTOINCREMENT,
        id_user INTEGER,
        id_wilayah INTEGER NOT NULL,
        nama_gudang VARCHAR(100) NOT NULL,
        jenis VARCHAR(30) NOT NULL, -- pabrik rokok, pengepul, koperasi, pasar
        kapasitas_ton REAL DEFAULT 100,
        alamat TEXT,
        kontak VARCHAR(30),
        lat REAL NOT NULL,
        lng REAL NOT NULL,
        geom_geojson TEXT,
        status_verifikasi VARCHAR(15) DEFAULT 'terverifikasi',
        FOREIGN KEY (id_user) REFERENCES users (id_user),
        FOREIGN KEY (id_wilayah) REFERENCES wilayah (id_wilayah)
    );
    """)

    # 11. harga
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS harga (
        id_harga INTEGER PRIMARY KEY AUTOINCREMENT,
        id_gudang INTEGER NOT NULL,
        id_varietas INTEGER NOT NULL,
        tanggal DATE NOT NULL,
        grade_mutu VARCHAR(10) NOT NULL,
        harga_per_kg REAL NOT NULL,
        id_user_input INTEGER,
        catatan TEXT,
        FOREIGN KEY (id_gudang) REFERENCES gudang (id_gudang),
        FOREIGN KEY (id_varietas) REFERENCES varietas (id_varietas),
        FOREIGN KEY (id_user_input) REFERENCES users (id_user)
    );
    """)

    # 12. jenis_opt
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS jenis_opt (
        id_jenis_opt INTEGER PRIMARY KEY AUTOINCREMENT,
        nama_opt VARCHAR(80) UNIQUE NOT NULL,
        kategori VARCHAR(20) NOT NULL, -- hama, penyakit, bencana
        gejala TEXT,
        rekomendasi TEXT
    );
    """)

    # 13. laporan_opt
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS laporan_opt (
        id_laporan INTEGER PRIMARY KEY AUTOINCREMENT,
        id_lahan INTEGER,
        id_jenis_opt INTEGER NOT NULL,
        id_user INTEGER NOT NULL,
        wilayah_nama VARCHAR(100),
        tanggal_lapor DATE NOT NULL,
        tingkat_serangan VARCHAR(10) NOT NULL, -- ringan, sedang, berat
        luas_terserang_ha REAL NOT NULL,
        deskripsi TEXT,
        foto_url VARCHAR(255),
        status VARCHAR(15) DEFAULT 'baru', -- baru, ditindaklanjuti, selesai
        lat REAL NOT NULL,
        lng REAL NOT NULL,
        geom_geojson TEXT,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (id_lahan) REFERENCES lahan (id_lahan),
        FOREIGN KEY (id_jenis_opt) REFERENCES jenis_opt (id_jenis_opt),
        FOREIGN KEY (id_user) REFERENCES users (id_user)
    );
    """)

    # 14. layer_peta
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS layer_peta (
        id_layer INTEGER PRIMARY KEY AUTOINCREMENT,
        nama_layer VARCHAR(80) NOT NULL,
        tipe_layer VARCHAR(20) NOT NULL, -- vector, WMS, raster
        sumber_url VARCHAR(255),
        akses VARCHAR(10) DEFAULT 'publik', -- publik, internal
        urutan INTEGER DEFAULT 1,
        aktif BOOLEAN DEFAULT 1
    );
    """)

    # 15. log_aktivitas
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS log_aktivitas (
        id_log INTEGER PRIMARY KEY AUTOINCREMENT,
        id_user INTEGER,
        user_name VARCHAR(100),
        aksi VARCHAR(30) NOT NULL, -- create, update, delete, login, export, verify
        tabel_target VARCHAR(40),
        id_target INTEGER,
        keterangan TEXT,
        waktu TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    );
    """)

    conn.commit()
    conn.close()
    print("Database tables created successfully.")

if __name__ == "__main__":
    init_db()

