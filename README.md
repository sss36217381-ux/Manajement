# SIGTEMBAKAU – WebGIS Tembakau Nasional

Aplikasi WebGIS (Geographic Information System) untuk monitoring lahan, produksi, harga, dan serangan OPT (Organisme Pengganggu Tumbuhan) pada sentra-sentra tembakau nasional.

## 📍 Cakupan Wilayah
8 sentra tembakau nasional:
- Kabupaten Temanggung
- Kabupaten Wonosobo
- Kabupaten Pamekasan (Madura)
- Kabupaten Jember
- Kabupaten Bojonegoro
- Kabupaten Lombok Timur
- Kabupaten Deli Serdang
- Kabupaten Garut

## 🛠 Teknologi
| Layer | Teknologi |
|---|---|
| Backend | Python 3.13 + FastAPI + Uvicorn |
| Database | SQLite3 |
| Peta | Leaflet.js + GeoJSON + OpenStreetMap |
| Grafik | Chart.js |
| Frontend | HTML5 + CSS3 + Vanilla JS |

## 🚀 Cara Menjalankan

### 1. Install dependensi
```bash
pip install fastapi uvicorn[standard] python-multipart itsdangerous
```

### 2. Inisialisasi database & seed data
```bash
python database.py
python seed_data.py
```

### 3. Jalankan server
```bash
python run.py
```
atau
```bash
uvicorn main:app --host 0.0.0.0 --port 8000 --reload
```

### 4. Buka browser
```
http://localhost:8000
```

## 🔑 Akun Demo

| Role | Email | Password |
|---|---|---|
| Admin | admin@sigtembakau.id | admin123 |
| Operator | operator.tmg@sigtembakau.id | operator123 |
| Penyuluh | penyuluh.tmg@sigtembakau.id | penyuluh123 |
| Petani | petani.pakjo@sigtembakau.id | petani123 |
| Gudang/Pabrik | gudang.djarum@sigtembakau.id | gudang123 |
| Pimpinan | pimpinan@sigtembakau.id | pimpinan123 |

## 📂 Struktur Proyek
```
Manajement/
├── main.py              # Entry point FastAPI
├── database.py          # Schema 15 tabel SQLite
├── seed_data.py         # Data awal 8 sentra
├── run.py               # Starter script
├── routers/
│   ├── auth.py          # Login/logout
│   ├── peta.py          # GeoJSON API
│   ├── dashboard.py     # Statistik & tren
│   ├── lahan.py         # CRUD + verifikasi lahan
│   ├── harga.py         # Harga tembakau
│   ├── opt.py           # Laporan OPT
│   └── admin.py         # Manajemen pengguna
└── static/
    ├── index.html       # Halaman login
    ├── dashboard.html   # Dashboard KPI & grafik
    ├── peta.html        # Peta WebGIS interaktif
    ├── lahan.html       # Data lahan
    ├── harga.html       # Monitoring harga
    ├── opt.html         # Laporan OPT
    ├── admin.html       # Panel admin
    ├── css/style.css    # Tema tembakau
    └── js/utils.js      # Helper functions
```

## 📡 API Endpoints
- `GET /api/docs` — Swagger UI dokumentasi API
- `GET /api/dashboard/ringkasan` — KPI dashboard
- `GET /api/geojson/lahan` — GeoJSON poligon lahan
- `GET /api/geojson/gudang` — GeoJSON titik gudang
- `GET /api/geojson/opt` — GeoJSON titik OPT
- `GET /api/harga/terakhir` — Harga tembakau terbaru
- `POST /api/auth/login` — Login
