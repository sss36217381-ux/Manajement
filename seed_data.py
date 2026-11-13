"""
SIGTEMBAKAU - Seed Data Generator
Mengisi basis data dengan data spasial awal untuk 8 sentra tembakau nasional:
1. Temanggung, 2. Wonosobo, 3. Madura (Pamekasan), 4. Jember,
5. Bojonegoro, 6. Lombok Timur, 7. Deli Serdang, 8. Garut.
"""
import sqlite3
import json
import hashlib
from datetime import datetime, date, timedelta
from database import get_db, init_db

def hash_pw(password: str) -> str:
    # simple sha256 for prototype demo
    return hashlib.sha256(password.encode()).hexdigest()

def seed_all():
    init_db()
    conn = get_db()
    cursor = conn.cursor()

    # Check if already seeded
    cursor.execute("SELECT COUNT(*) FROM roles")
    if cursor.fetchone()[0] > 0:
        print("Database already contains data. Refreshing seed...")
        cursor.execute("DELETE FROM log_aktivitas")
        cursor.execute("DELETE FROM laporan_opt")
        cursor.execute("DELETE FROM harga")
        cursor.execute("DELETE FROM gudang")
        cursor.execute("DELETE FROM produksi")
        cursor.execute("DELETE FROM musim_tanam")
        cursor.execute("DELETE FROM lahan")
        cursor.execute("DELETE FROM petani")
        cursor.execute("DELETE FROM kelompok_tani")
        cursor.execute("DELETE FROM varietas")
        cursor.execute("DELETE FROM jenis_opt")
        cursor.execute("DELETE FROM wilayah")
        cursor.execute("DELETE FROM users")
        cursor.execute("DELETE FROM roles")
        cursor.execute("DELETE FROM layer_peta")

    print("Seeding roles...")
    roles = [
        (1, 'admin', 'Administrator Sistem penuh'),
        (2, 'operator', 'Petugas Dinas Perkebunan / Operator Verifikasi'),
        (3, 'penyuluh', 'Penyuluh Pertanian Lapangan (PPL)'),
        (4, 'petani', 'Petani / Kelompok Tani Tembakau'),
        (5, 'gudang', 'Pedagang / Pengelola Gudang / Pabrik'),
        (6, 'pimpinan', 'Pimpinan / Pengambil Kebijakan'),
        (7, 'publik', 'Masyarakat Umum / Peneliti')
    ]
    cursor.executemany("INSERT INTO roles (id_role, nama_role, keterangan) VALUES (?, ?, ?)", roles)

    print("Seeding users...")
    users = [
        (1, 1, 'Budi Santoso, S.Kom', 'admin@sigtembakau.id', hash_pw('admin123'), '081234567890', 'Pusat', 1),
        (2, 2, 'Ir. Wahyu Hidayat', 'operator.tmg@sigtembakau.id', hash_pw('operator123'), '081398765432', 'Kabupaten Temanggung', 1),
        (3, 3, 'Siti Nurhaliza, S.P.', 'penyuluh.tmg@sigtembakau.id', hash_pw('penyuluh123'), '085711223344', 'Kec. Bulu & Parakan', 1),
        (4, 4, 'Pak Joko Prayitno', 'petani.pakjo@sigtembakau.id', hash_pw('petani123'), '087834567812', 'Desa Tlahab Lor, Temanggung', 1),
        (5, 5, 'Hendra Gunawan (PT Djarum)', 'gudang.djarum@sigtembakau.id', hash_pw('gudang123'), '081255667788', 'Sentra Gudang Temanggung', 1),
        (6, 6, 'Drs. H. Mulyadi, M.M.', 'pimpinan@sigtembakau.id', hash_pw('pimpinan123'), '081122334455', 'Dinas Pertanian & Perkebunan', 1),
        (7, 4, 'Haji Moh. Romli', 'petani.madura@sigtembakau.id', hash_pw('petani123'), '081938472910', 'Pamekasan, Madura', 1),
        (8, 4, 'I Made Suardana', 'petani.lombok@sigtembakau.id', hash_pw('petani123'), '087765432190', 'Sikur, Lombok Timur', 1),
        (9, 2, 'Ratna Dewi, S.Pt', 'operator.jember@sigtembakau.id', hash_pw('operator123'), '081344556677', 'Kabupaten Jember', 1),
    ]
    cursor.executemany("""
    INSERT INTO users (id_user, id_role, nama_lengkap, email, password_hash, no_hp, wilayah_tugas, status_aktif)
    VALUES (?, ?, ?, ?, ?, ?, ?, ?)
    """, users)

    print("Seeding wilayah sentra tembakau...")
    # Sentra tembakau data: coordinates, boundary approximation
    sentra_wilayah = [
        (1, '3323', 'Kabupaten Temanggung', 'kabupaten', None, -7.3167, 110.1667, 18500.0,
         json.dumps({
             "type": "Polygon",
             "coordinates": [[
                 [110.05, -7.22], [110.28, -7.20], [110.32, -7.38], [110.12, -7.42], [110.03, -7.30], [110.05, -7.22]
             ]]
         })),
        (2, '3325', 'Kabupaten Wonosobo', 'kabupaten', None, -7.3600, 109.9000, 8200.0,
         json.dumps({
             "type": "Polygon",
             "coordinates": [[
                 [109.80, -7.25], [109.98, -7.24], [110.03, -7.42], [109.85, -7.48], [109.78, -7.35], [109.80, -7.25]
             ]]
         })),
        (3, '3528', 'Kabupaten Pamekasan (Madura)', 'kabupaten', None, -7.1500, 113.4800, 31200.0,
         json.dumps({
             "type": "Polygon",
             "coordinates": [[
                 [113.38, -6.98], [113.62, -7.00], [113.60, -7.25], [113.40, -7.23], [113.38, -6.98]
             ]]
         })),
        (4, '3509', 'Kabupaten Jember', 'kabupaten', None, -8.1724, 113.7007, 14800.0,
         json.dumps({
             "type": "Polygon",
             "coordinates": [[
                 [113.45, -8.05], [113.88, -8.08], [113.92, -8.45], [113.50, -8.40], [113.45, -8.05]
             ]]
         })),
        (5, '3522', 'Kabupaten Bojonegoro', 'kabupaten', None, -7.1502, 111.8817, 11500.0,
         json.dumps({
             "type": "Polygon",
             "coordinates": [[
                 [111.60, -7.05], [112.05, -7.10], [112.02, -7.38], [111.65, -7.35], [111.60, -7.05]
             ]]
         })),
        (6, '5203', 'Kabupaten Lombok Timur', 'kabupaten', None, -8.6500, 116.5333, 22400.0,
         json.dumps({
             "type": "Polygon",
             "coordinates": [[
                 [116.40, -8.40], [116.70, -8.45], [116.72, -8.85], [116.42, -8.82], [116.40, -8.40]
             ]]
         })),
        (7, '1207', 'Kabupaten Deli Serdang', 'kabupaten', None, 3.5167, 98.7833, 6200.0,
         json.dumps({
             "type": "Polygon",
             "coordinates": [[
                 [98.50, 3.75], [99.00, 3.70], [98.95, 3.25], [98.55, 3.30], [98.50, 3.75]
             ]]
         })),
        (8, '3205', 'Kabupaten Garut', 'kabupaten', None, -7.2167, 107.9000, 7800.0,
         json.dumps({
             "type": "Polygon",
             "coordinates": [[
                 [107.70, -7.05], [108.10, -7.10], [108.05, -7.60], [107.65, -7.50], [107.70, -7.05]
             ]]
         }))
    ]
    cursor.executemany("""
    INSERT INTO wilayah (id_wilayah, kode_wilayah, nama_wilayah, tingkat, id_induk, lat, lng, luas_potensi_ha, geom_geojson)
    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, sentra_wilayah)

    print("Seeding kelompok tani...")
    poktan = [
        (1, 'Poktan Tani Makmur Bansari', 1, 'Supriyadi', 45),
        (2, 'Poktan Sindoro Asri Tlahab', 1, 'Kuncoro Joko', 38),
        (3, 'Poktan Prancak Jaya', 3, 'Haji Romli', 62),
        (4, 'Poktan Kasturi Mandiri Ajung', 4, 'Bambang Irawan', 50),
        (5, 'Poktan Sasak Rinjani Sikur', 6, 'Ahmad Fadhil', 54),
        (6, 'Poktan Garut Subur Leles', 8, 'Asep Saepuloh', 30)
    ]
    cursor.executemany("""
    INSERT INTO kelompok_tani (id_kelompok, nama_kelompok, id_wilayah, ketua, jumlah_anggota)
    VALUES (?, ?, ?, ?, ?)
    """, poktan)

    print("Seeding petani...")
    petani = [
        (1, 4, 1, '3323011508750001', 'Pak Joko Prayitno', 'RT 02 / RW 04 Ds. Tlahab Lor, Parakan, Temanggung', '087834567812'),
        (2, None, 1, '3323012003780002', 'Bapak Slamet Raharjo', 'Ds. Bansari, Kledung, Temanggung', '085223344556'),
        (3, 7, 3, '3528021004810003', 'Haji Moh. Romli', 'Ds. Guluk-Guluk, Pamekasan, Madura', '081938472910'),
        (4, None, 4, '3509051409830004', 'Drs. Subroto Basuki', 'Ds. Ajung, Jember', '081333444555'),
        (5, 8, 5, '5203022511870005', 'I Made Suardana', 'Ds. Sikur Barat, Lombok Timur', '087765432190'),
        (6, None, 6, '3205011902890006', 'Kang Asep Kurniawan', 'Ds. Salamnunggal, Leles, Garut', '082133887766')
    ]
    cursor.executemany("""
    INSERT INTO petani (id_petani, id_user, id_kelompok, nik, nama_petani, alamat, no_hp)
    VALUES (?, ?, ?, ?, ?, ?, ?)
    """, petani)

    print("Seeding varietas...")
    varietas = [
        (1, 'Kemloko / Srintil', 'rajangan',
         'Aroma khas pegunungan, kadar nikotin tinggi, rajangan lembut keemasan',
         'Lereng Sindoro-Sumbing ketinggian 700-1400 mdpl',
         'Tembakau rajangan asli Temanggung yang menjadi bahan baku utama rokok kretek premium. Varian Srintil bernilai paling tinggi karena fermentasi alami getah lamuran.'),
        (2, 'Virginia Lombok (FC)', 'Virginia',
         'Warna kuning keemasan hasil flue-cured, kadar gula tinggi, aroma manis',
         'Dataran rendah hingga menengah Lombok Timur dengan irigasi teknis',
         'Bahan baku rokok putih dan rokok mild berkadar tar rendah dengan pengeringan oven (flue curing).'),
        (3, 'Madura Prancak', 'rajangan',
         'Daun tebal, warna cokelat kemerahan, aroma gurih harum',
         'Tanah tegalan kapur / aluvial Madura dengan iklim kering',
         'Tembakau rajangan khas Madura dengan daya bakar prima, sangat diminati pabrikan kretek terkemuka.'),
        (4, 'Na-Oogst Besuki (BesNo)', 'cerutu',
         'Elastisitas daun tinggi, urat daun halus, rasa lembut',
         'Tanah vulkanik subur Jember dengan curah hujan teratur',
         'Tembakau pembungkus (wrapper) dan pengisi (filler) cerutu kualitas ekspor ke Bremen dan Eropa.'),
        (5, 'Virginia Bojonegoro', 'Virginia',
         'Kuning cerah, tekstur daun sedang, mudah diserap industri',
         'Lahan sawah bekas padi Bojonegoro saat musim kemarau',
         'Tembakau Virginia oven populer di Jawa Timur.'),
        (6, 'Deli White Burley', 'cerutu',
         'Daun lebar, abu putih bersih saat terbakar, elastis dan lembut',
         'Tanah aluvial Deli Serdang Sumatera Utara',
         'Tembakau legendaris dunia pembungkus cerutu kelas satu sejak era kolonial 1863.'),
        (7, 'Tembakau Mole Garut', 'mole',
         'Rajangan sangat halus menyerupai rambut emas, aroma wangi',
         'Dataran tinggi pegunungan Garut dan Sumedang',
         'Tembakau tingwe (linting dewe) tradisional yang terkenal wangi dan gurih.')
    ]
    cursor.executemany("""
    INSERT INTO varietas (id_varietas, nama_varietas, tipe, karakteristik, kesesuaian_lahan, deskripsi)
    VALUES (?, ?, ?, ?, ?, ?)
    """, varietas)

    print("Seeding lahan tembakau (polygons)...")
    lahan = [
        # 1. Temanggung - Lahan Pak Joko (Lereng Sumbing, Tlahab)
        (1, 1, 1, 'LHN-TMG-001', 1.45, 1150, 'Andosol', 'milik', 'terverifikasi',
         'Data telah divalidasi oleh petugas lapangan PPL Bulu, sertifikat hak milik terlampir.',
         json.dumps({
             "type": "Polygon",
             "coordinates": [[
                 [110.1250, -7.3320],
                 [110.1280, -7.3315],
                 [110.1290, -7.3340],
                 [110.1260, -7.3350],
                 [110.1250, -7.3320]
             ]]
         }), -7.3331, 110.1270),

        # 2. Temanggung - Lahan Pak Slamet (Bansari Lereng Sindoro)
        (2, 2, 1, 'LHN-TMG-002', 2.10, 1280, 'Andosol', 'milik', 'terverifikasi',
         'Lahan terasering lereng Sindoro dengan bibit Kemloko 1, mutu unggul.',
         json.dumps({
             "type": "Polygon",
             "coordinates": [[
                 [110.1020, -7.2950],
                 [110.1060, -7.2940],
                 [110.1075, -7.2975],
                 [110.1030, -7.2985],
                 [110.1020, -7.2950]
             ]]
         }), -7.2962, 110.1046),

        # 3. Temanggung - Lahan Baru Diajukan (Kledung)
        (3, 1, 1, 'LHN-TMG-003', 0.85, 1320, 'Andosol', 'sewa', 'diajukan',
         'Menunggu pengecekan batas lahan lapangan oleh operator dinas.',
         json.dumps({
             "type": "Polygon",
             "coordinates": [[
                 [110.0820, -7.3150],
                 [110.0855, -7.3142],
                 [110.0862, -7.3175],
                 [110.0830, -7.3180],
                 [110.0820, -7.3150]
             ]]
         }), -7.3161, 110.0841),

        # 4. Wonosobo - Garung
        (4, 2, 2, 'LHN-WSB-001', 1.75, 1100, 'Regosol', 'milik', 'terverifikasi',
         'Kawasan penyangga lereng Dieng Wonosobo.',
         json.dumps({
             "type": "Polygon",
             "coordinates": [[
                 [109.9120, -7.3250],
                 [109.9160, -7.3245],
                 [109.9170, -7.3280],
                 [109.9130, -7.3290],
                 [109.9120, -7.3250]
             ]]
         }), -7.3266, 109.9145),

        # 5. Madura (Pamekasan) - Haji Romli
        (5, 3, 3, 'LHN-MD-001', 3.20, 120, 'Grumosol / Mediteran', 'milik', 'terverifikasi',
         'Tembakau tegalan musim kemarau Prancak 95.',
         json.dumps({
             "type": "Polygon",
             "coordinates": [[
                 [113.4650, -7.1350],
                 [113.4720, -7.1340],
                 [113.4735, -7.1400],
                 [113.4660, -7.1410],
                 [113.4650, -7.1350]
             ]]
         }), -7.1375, 113.4691),

        # 6. Jember - Ajung (Pak Subroto)
        (6, 4, 4, 'LHN-JBR-001', 2.80, 85, 'Aluvial Vulkanik', 'bagi hasil', 'terverifikasi',
         'Kebun tembakau Na-Oogst bawah naungan jaring (waring).',
         json.dumps({
             "type": "Polygon",
             "coordinates": [[
                 [113.6750, -8.2120],
                 [113.6820, -8.2110],
                 [113.6835, -8.2165],
                 [113.6760, -8.2175],
                 [113.6750, -8.2120]
             ]]
         }), -8.2142, 113.6791),

        # 7. Bojonegoro - Sugihwaras
        (7, 2, 5, 'LHN-BJN-001', 1.90, 45, 'Aluvial', 'sewa', 'terverifikasi',
         'Lahan sawah Virginia Bojonegoro musim tanam gadu.',
         json.dumps({
             "type": "Polygon",
             "coordinates": [[
                 [111.8650, -7.2100],
                 [111.8710, -7.2090],
                 [111.8720, -7.2140],
                 [111.8660, -7.2150],
                 [111.8650, -7.2100]
             ]]
         }), -7.2120, 111.8685),

        # 8. Lombok Timur - Sikur (I Made Suardana)
        (8, 5, 6, 'LHN-LOTIM-001', 3.60, 220, 'Regosol Coklat', 'milik', 'terverifikasi',
         'Sentra tembakau Virginia FC Lombok dengan oven terintegrasi.',
         json.dumps({
             "type": "Polygon",
             "coordinates": [[
                 [116.5150, -8.6250],
                 [116.5230, -8.6235],
                 [116.5245, -8.6310],
                 [116.5165, -8.6320],
                 [116.5150, -8.6250]
             ]]
         }), -8.6278, 116.5197),

        # 9. Deli Serdang - Klambir Lima
        (9, 4, 7, 'LHN-DELI-001', 2.40, 25, 'Aluvial Tua', 'sewa', 'terverifikasi',
         'Lahan tembakau Deli pembungkus cerutu ekspor.',
         json.dumps({
             "type": "Polygon",
             "coordinates": [[
                 [98.7150, 3.5650],
                 [98.7220, 3.5640],
                 [98.7230, 3.5700],
                 [98.7160, 3.5710],
                 [98.7150, 3.5650]
             ]]
         }), 3.5675, 98.7190),

        # 10. Garut - Leles (Kang Asep)
        (10, 6, 8, 'LHN-GAR-001', 1.20, 720, 'Andosol Humus', 'milik', 'terverifikasi',
         'Tembakau Mole Garut daun kuning ranum.',
         json.dumps({
             "type": "Polygon",
             "coordinates": [[
                 [107.8820, -7.1250],
                 [107.8870, -7.1242],
                 [107.8880, -7.1285],
                 [107.8830, -7.1292],
                 [107.8820, -7.1250]
             ]]
         }), -7.1267, 107.8850)
    ]
    cursor.executemany("""
    INSERT INTO lahan (id_lahan, id_petani, id_wilayah, kode_lahan, luas_ha, ketinggian_mdpl, jenis_tanah,
                       status_kepemilikan, status_verifikasi, catatan_verifikasi, geom_geojson, centroid_lat, centroid_lng)
    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, lahan)

    print("Seeding musim tanam & produksi...")
    musim = [
        # (id_musim, id_lahan, id_varietas, tahun, musim, tgl_tanam, tgl_panen_estimasi, luas_tanam_ha)
        (1, 1, 1, 2026, 'MT1', '2026-04-15', '2026-08-20', 1.45),
        (2, 2, 1, 2026, 'MT1', '2026-04-20', '2026-08-28', 2.10),
        (3, 4, 1, 2026, 'MT1', '2026-05-02', '2026-09-05', 1.75),
        (4, 5, 3, 2026, 'MT1', '2026-05-10', '2026-09-15', 3.20),
        (5, 6, 4, 2026, 'MT1', '2026-06-01', '2026-10-10', 2.80),
        (6, 7, 5, 2026, 'MT1', '2026-05-15', '2026-09-20', 1.90),
        (7, 8, 2, 2026, 'MT1', '2026-04-25', '2026-08-30', 3.60),
        (8, 9, 6, 2026, 'MT1', '2026-03-20', '2026-07-25', 2.40),
        (9, 10, 7, 2026, 'MT1', '2026-05-05', '2026-09-10', 1.20)
    ]
    cursor.executemany("""
    INSERT INTO musim_tanam (id_musim, id_lahan, id_varietas, tahun, musim, tgl_tanam, tgl_panen_estimasi, luas_tanam_ha)
    VALUES (?, ?, ?, ?, ?, ?, ?, ?)
    """, musim)

    produksi = [
        # (id_produksi, id_musim, tgl_panen, luas_panen_ha, jumlah_ton, produktivitas, grade_mutu, catatan, status_verifikasi)
        (1, 1, '2026-08-22', 1.45, 2.90, 2.00, 'A', 'Kualitas panen tembakau srintil istimewa dengan aroma pekat', 'terverifikasi'),
        (2, 2, '2026-08-30', 2.10, 4.62, 2.20, 'A', 'Produksi optimal lereng Sindoro Bansari', 'terverifikasi'),
        (3, 3, '2026-09-08', 1.75, 3.15, 1.80, 'B', 'Kadar air rajangan pas, cuaca mendukung', 'terverifikasi'),
        (4, 4, '2026-09-18', 3.20, 5.76, 1.80, 'A', 'Rajangan Madura aroma manis gurih terbeli habis oleh gudang', 'terverifikasi'),
        (5, 5, '2026-10-12', 2.80, 5.04, 1.80, 'A', 'Daun wrapper mulus, standar ekspor cerutu Na-Oogst', 'terverifikasi'),
        (6, 6, '2026-09-22', 1.90, 3.42, 1.80, 'B', 'Tembakau Virginia oven Bojonegoro Grade B', 'terverifikasi'),
        (7, 7, '2026-09-02', 3.60, 8.28, 2.30, 'A', 'Virginia FC Lombok mutu prima serapan Djarum & Sampoerna', 'terverifikasi'),
        (8, 8, '2026-07-28', 2.40, 3.60, 1.50, 'A', 'Tembakau Deli cerutu eksklusif', 'terverifikasi'),
        (9, 9, '2026-09-12', 1.20, 2.04, 1.70, 'B', 'Tembakau Mole wangi rajangan halus Garut', 'terverifikasi')
    ]
    cursor.executemany("""
    INSERT INTO produksi (id_produksi, id_musim, tgl_panen, luas_panen_ha, jumlah_ton, produktivitas, grade_mutu, catatan, status_verifikasi)
    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, produksi)

    print("Seeding gudang & pabrik pembelian...")
    gudang = [
        # 1. Temanggung - Gudang Pembelian PT Djarum
        (1, 5, 1, 'Gudang Pembelian PT Djarum Temanggung', 'pabrik rokok', 2500.0,
         'Jl. Raya Parakan - Temanggung Km 3, Kedu', '0293-491200', -7.3155, 110.1550, 'terverifikasi'),
        # 2. Temanggung - Gudang Garam Unit Bulu
        (2, None, 1, 'Gudang Garam Unit Pembelian Bulu', 'pabrik rokok', 3000.0,
         'Jl. Raya Bulu - Parakan No. 45, Temanggung', '0293-492311', -7.3380, 110.1340, 'terverifikasi'),
        # 3. Temanggung - Koperasi Tani Tembakau Sindoro
        (3, None, 1, 'Koperasi Tani Tembakau Sindoro Sumbing', 'koperasi', 800.0,
         'Ds. Tlahab Lor, Parakan, Temanggung', '0812-7890123', -7.3295, 110.1190, 'terverifikasi'),
        # 4. Wonosobo - Pengepul Berkah Tembakau Garung
        (4, None, 2, 'Pengepul Berkah Tembakau Garung', 'pengepul', 500.0,
         'Jl. Dieng Km 7, Garung, Wonosobo', '0286-321456', -7.3310, 109.9180, 'terverifikasi'),
        # 5. Madura (Pamekasan) - Gudang PT HM Sampoerna Tbk
        (5, None, 3, 'Gudang Pembelian Sampoerna Pamekasan', 'pabrik rokok', 4000.0,
         'Jl. Raya Tlanakan No. 88, Pamekasan, Madura', '0324-322190', -7.1720, 113.4730, 'terverifikasi'),
        # 6. Madura - Gudang Wismilak Pamekasan
        (6, None, 3, 'Gudang Pembelian Wismilak Sentra Madura', 'pabrik rokok', 2200.0,
         'Jl. Trunojoyo No. 120, Pamekasan', '0324-325567', -7.1580, 113.4850, 'terverifikasi'),
        # 7. Jember - Koperasi Agrobisnis Tarutama Nusantara (TTN)
        (7, None, 4, 'Koperasi Agrobisnis TTN & Cerutu BIN Cigar', 'koperasi', 1200.0,
         'Jl. Brawijaya No. 15, Mangli, Jember', '0331-487654', -8.1890, 113.6620, 'terverifikasi'),
        # 8. Bojonegoro - Gudang Pembelian Sukowati
        (8, None, 5, 'Gudang Pembelian Tembakau Virginia Bojonegoro', 'pengepul', 1500.0,
         'Jl. Veteran No. 70, Bojonegoro', '0353-881234', -7.1620, 111.8920, 'terverifikasi'),
        # 9. Lombok Timur - Gudang Djarum Unit Selong
        (9, None, 6, 'Gudang Djarum Unit Pembelian Lombok Timur', 'pabrik rokok', 3500.0,
         'Jl. TGKH M. Zainuddin Abdul Madjid, Selong, Lotim', '0376-21890', -8.6480, 116.5410, 'terverifikasi'),
        # 10. Deli Serdang - Balai Pengolahan PTPN I Regional 1
        (10, None, 7, 'Balai Tembakau Cerutu Deli PTPN', 'pasar', 900.0,
         'Jl. Raya Tandem Hilir, Deli Serdang', '061-7951234', 3.5820, 98.7450, 'terverifikasi'),
        # 11. Garut - Pasar Tembakau Tradisional Tarogong
        (11, None, 8, 'Sentra Pengepul Tembakau Mole Tarogong', 'pasar', 600.0,
         'Jl. Raya Garut - Bandung No. 23, Tarogong Kaler, Garut', '0262-234567', -7.1950, 107.8920, 'terverifikasi')
    ]
    cursor.executemany("""
    INSERT INTO gudang (id_gudang, id_user, id_wilayah, nama_gudang, jenis, kapasitas_ton, alamat, kontak, lat, lng, status_verifikasi)
    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, gudang)

    print("Seeding harga tembakau...")
    # Seed historical and current prices across warehouses and grades
    base_dates = [
        (date.today() - timedelta(days=28)).strftime('%Y-%m-%d'),
        (date.today() - timedelta(days=21)).strftime('%Y-%m-%d'),
        (date.today() - timedelta(days=14)).strftime('%Y-%m-%d'),
        (date.today() - timedelta(days=7)).strftime('%Y-%m-%d'),
        date.today().strftime('%Y-%m-%d')
    ]
    
    harga_records = [
        # Gudang 1: Djarum Temanggung - Varietas Kemloko/Srintil
        (1, 1, 1, base_dates[0], 'A', 165000, 5, 'Pembukaan musim pembelian tembakau Srintil'),
        (2, 1, 1, base_dates[1], 'A', 175000, 5, 'Permintaan meningkat'),
        (3, 1, 1, base_dates[2], 'A', 185000, 5, 'Kualitas daun posong prima'),
        (4, 1, 1, base_dates[3], 'A', 195000, 5, 'Tren naik mendekati puncak panen'),
        (5, 1, 1, base_dates[4], 'A', 210000, 5, 'Harga rekor grade super srintil'),

        (6, 1, 1, base_dates[4], 'B', 135000, 5, 'Grade B standar rajangan pabrik'),
        (7, 1, 1, base_dates[4], 'C', 95000, 5, 'Grade C daun bawah'),
        (8, 1, 1, base_dates[4], 'D', 65000, 5, 'Grade D rajangan campur'),

        # Gudang 2: Gudang Garam Bulu - Kemloko
        (9, 2, 1, base_dates[4], 'A', 205000, 2, 'Grade A aroma tajam'),
        (10, 2, 1, base_dates[4], 'B', 130000, 2, 'Grade B'),

        # Gudang 5: Sampoerna Pamekasan - Madura Prancak
        (11, 5, 3, base_dates[0], 'A', 65000, 2, 'Awal pembelian tembakau Madura'),
        (12, 5, 3, base_dates[1], 'A', 72000, 2, 'Kualitas rajangan kering cerah'),
        (13, 5, 3, base_dates[2], 'A', 78000, 2, 'Kenaikan permintaan pabrik'),
        (14, 5, 3, base_dates[3], 'A', 82000, 2, 'Stabil tinggi'),
        (15, 5, 3, base_dates[4], 'A', 88000, 2, 'Harga tertinggi musim ini di Madura'),
        (16, 5, 3, base_dates[4], 'B', 68000, 2, 'Grade B'),
        (17, 5, 3, base_dates[4], 'C', 48000, 2, 'Grade C'),

        # Gudang 7: Jember BIN Cigar - Na-Oogst Cerutu
        (18, 7, 4, base_dates[4], 'A', 275000, 2, 'Daun pembungkus (wrapper) ekspor nomor 1'),
        (19, 7, 4, base_dates[4], 'B', 160000, 2, 'Daun pengikat (binder) cerutu'),
        (20, 7, 4, base_dates[4], 'C', 95000, 2, 'Daun pengisi (filler) cerutu'),

        # Gudang 9: Lombok Timur Djarum - Virginia FC
        (21, 9, 2, base_dates[0], 'A', 48000, 2, 'Awal panen oven'),
        (22, 9, 2, base_dates[2], 'A', 54000, 2, 'Pengeringan sempurna'),
        (23, 9, 2, base_dates[4], 'A', 59000, 2, 'Grade A oven kuning emas'),
        (24, 9, 2, base_dates[4], 'B', 46000, 2, 'Grade B'),

        # Gudang 10: Deli Serdang PTPN - Deli White Burley
        (25, 10, 6, base_dates[4], 'A', 350000, 2, 'Kualitas super wrapper pasar Eropa'),

        # Gudang 11: Garut - Tembakau Mole
        (26, 11, 7, base_dates[4], 'A', 140000, 2, 'Mole super wangi warna emas')
    ]
    cursor.executemany("""
    INSERT INTO harga (id_harga, id_gudang, id_varietas, tanggal, grade_mutu, harga_per_kg, id_user_input, catatan)
    VALUES (?, ?, ?, ?, ?, ?, ?, ?)
    """, harga_records)

    print("Seeding jenis OPT...")
    jenis_opt = [
        (1, 'Ulat Grayak (Spodoptera litura)', 'hama',
         'Daun berlubang hingga tersisa tulang daun, kotoran ulat pada ketiak daun.',
         'Sanitasi lahan, pemasangan feromon trap, semprot insektisida nabati atau insektisida piretroid selektif.'),
        (2, 'Layu Bakteri (Ralstonia solanacearum)', 'penyakit',
         'Tanaman layu mendadak saat siang hari, batang bagian dalam coklat membusuk, lendir bakteri keluar saat dicelup air.',
         'Cabut dan bakar tanaman terserang, taburkan kapur tohor / dolomit, perbaiki drainase, rotasi tanaman non-solanaceae.'),
        (3, 'Lanas / Jamur Phytophthora nicotianae', 'penyakit',
         'Bercak basah kehitaman pada pangkal batang atau daun, tanaman patah roboh dan layu basah.',
         'Gunakan fungisida berbahan aktif mankozeb atau metalaksil, atur jarak tanam agar tidak terlalu rapat.'),
        (4, 'Virus Mozaik Tembakau (TMV)', 'penyakit',
         'Daun belang hijau muda dan tua tidak rata, daun mengkerut keriting dan pertumbuhan kerdil.',
         'Gunakan bibit bersertifikat tahan TMV, kendalikan kutu daun sebagai vektor, jangan merokok di sekitar pembibitan.'),
        (5, 'Curah Hujan Ekstrem / Banjir Genangan', 'bencana',
         'Akar tanaman terendam air lebih dari 24 jam, daun menguning dan layu akibat asfiksia akar.',
         'Pembuatan parit drainase dalam cepat di sekeliling bedengan lahan tembakau.')
    ]
    cursor.executemany("""
    INSERT INTO jenis_opt (id_jenis_opt, nama_opt, kategori, gejala, rekomendasi)
    VALUES (?, ?, ?, ?, ?)
    """, jenis_opt)

    print("Seeding laporan OPT spasial...")
    laporan_opt = [
        (1, 1, 1, 3, 'Kecamatan Bulu, Temanggung', date.today().strftime('%Y-%m-%d'), 'sedang', 0.25,
         'Ditemukan serangan ulat grayak pada daun pucuk di petak utara sekitar 35 tanaman.',
         'https://images.unsplash.com/photo-1599818816942-88ec0c54117b?w=500&auto=format&fit=crop&q=60',
         'ditindaklanjuti', -7.3325, 110.1265),

        (2, 2, 2, 3, 'Kecamatan Bansari, Temanggung', (date.today() - timedelta(days=5)).strftime('%Y-%m-%d'), 'ringan', 0.10,
         'Gejala layu satu sisi pada 8 tanaman di terasering tengah.',
         'https://images.unsplash.com/photo-1591857177580-dc82b9ac4e17?w=500&auto=format&fit=crop&q=60',
         'selesai', -7.2958, 110.1038),

        (3, 5, 1, 7, 'Kecamatan Guluk-Guluk, Pamekasan', (date.today() - timedelta(days=2)).strftime('%Y-%m-%d'), 'berat', 0.80,
         'Serangan mendadak ulat grayak pasca angin timur, lebih dari 50% daun pada blok barat terserang!',
         'https://images.unsplash.com/photo-1599818816942-88ec0c54117b?w=500&auto=format&fit=crop&q=60',
         'baru', -7.1360, 113.4680),

        (4, 8, 3, 8, 'Kecamatan Sikur, Lombok Timur', (date.today() - timedelta(days=8)).strftime('%Y-%m-%d'), 'ringan', 0.15,
         'Bercak lanas pada tanaman muda setelah hujan lokal deras.',
         'https://images.unsplash.com/photo-1591857177580-dc82b9ac4e17?w=500&auto=format&fit=crop&q=60',
         'selesai', -8.6265, 116.5185),

        (5, 6, 4, 9, 'Kecamatan Ajung, Jember', (date.today() - timedelta(days=1)).strftime('%Y-%m-%d'), 'sedang', 0.40,
         'Daun mozaik kuning belang pada klon tembakau Na-Oogst pinggir kebun.',
         'https://images.unsplash.com/photo-1591857177580-dc82b9ac4e17?w=500&auto=format&fit=crop&q=60',
         'baru', -8.2135, 113.6780)
    ]
    cursor.executemany("""
    INSERT INTO laporan_opt (id_laporan, id_lahan, id_jenis_opt, id_user, wilayah_nama, tanggal_lapor,
                            tingkat_serangan, luas_terserang_ha, deskripsi, foto_url, status, lat, lng)
    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, laporan_opt)

    print("Seeding layer peta...")
    layers = [
        (1, 'Batas Wilayah Sentra (Choropleth)', 'vector', '/api/geojson/wilayah', 'publik', 1, 1),
        (2, 'Poligon Lahan Tembakau', 'vector', '/api/geojson/lahan', 'publik', 2, 1),
        (3, 'Titik Gudang & Pabrik', 'vector', '/api/geojson/gudang', 'publik', 3, 1),
        (4, 'Titik Sebaran Serangan OPT', 'vector', '/api/geojson/opt', 'publik', 4, 1),
        (5, 'Zonasi Kesesuaian Lahan (DEM/Lereng)', 'vector', '/api/geojson/kesesuaian', 'internal', 5, 0)
    ]
    cursor.executemany("""
    INSERT INTO layer_peta (id_layer, nama_layer, tipe_layer, sumber_url, akses, urutan, aktif)
    VALUES (?, ?, ?, ?, ?, ?, ?)
    """, layers)

    print("Seeding log aktivitas awal...")
    logs = [
        (1, 1, 'Budi Santoso, S.Kom', 'login', 'users', 1, 'Admin berhasil login ke sistem SIGTEMBAKAU'),
        (2, 2, 'Ir. Wahyu Hidayat', 'verify', 'lahan', 1, 'Memverifikasi poligon lahan LHN-TMG-001'),
        (3, 3, 'Siti Nurhaliza, S.P.', 'create', 'laporan_opt', 1, 'Mengirim laporan serangan OPT Ulat Grayak di Bulu'),
        (4, 5, 'Hendra Gunawan (PT Djarum)', 'create', 'harga', 5, 'Memperbarui harga harian tembakau Grade A Rp 210.000/kg'),
        (5, 4, 'Pak Joko Prayitno', 'create', 'lahan', 3, 'Mendaftarkan poligon lahan baru di Kledung (LHN-TMG-003)')
    ]
    cursor.executemany("""
    INSERT INTO log_aktivitas (id_log, id_user, user_name, aksi, tabel_target, id_target, keterangan)
    VALUES (?, ?, ?, ?, ?, ?, ?)
    """, logs)

    conn.commit()
    conn.close()
    print("Seed data completed successfully!")

if __name__ == "__main__":
    seed_all()

