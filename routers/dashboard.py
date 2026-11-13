"""
SIGTEMBAKAU - Dashboard & Statistik Router
Agregasi data untuk homepage, grafik produksi, ringkasan wilayah.
"""
from fastapi import APIRouter, Request, Query
from fastapi.responses import JSONResponse
from database import get_db

router = APIRouter(prefix="/api/dashboard", tags=["Dashboard"])


@router.get("/ringkasan")
async def ringkasan():
    """Kartu KPI utama untuk dashboard."""
    conn = get_db()

    total_lahan = conn.execute(
        "SELECT COUNT(*), COALESCE(SUM(luas_ha), 0) FROM lahan WHERE status_verifikasi = 'terverifikasi'"
    ).fetchone()

    total_produksi = conn.execute(
        """SELECT COALESCE(SUM(p.jumlah_ton), 0), COALESCE(AVG(p.produktivitas), 0)
           FROM produksi p
           JOIN musim_tanam mt ON mt.id_musim = p.id_musim
           WHERE mt.tahun = strftime('%Y', 'now')"""
    ).fetchone()

    total_petani = conn.execute("SELECT COUNT(*) FROM petani").fetchone()
    total_gudang = conn.execute("SELECT COUNT(*) FROM gudang").fetchone()
    total_wilayah = conn.execute("SELECT COUNT(*) FROM wilayah WHERE tingkat = 'kabupaten'").fetchone()

    opt_aktif = conn.execute(
        "SELECT COUNT(*) FROM laporan_opt WHERE status IN ('baru', 'ditindaklanjuti')"
    ).fetchone()

    harga_tertinggi = conn.execute(
        """SELECT v.nama_varietas, g.nama_gudang, h.harga_per_kg, h.grade_mutu, h.tanggal
           FROM harga h
           JOIN gudang g ON g.id_gudang = h.id_gudang
           JOIN varietas v ON v.id_varietas = h.id_varietas
           WHERE h.grade_mutu = 'A'
           ORDER BY h.harga_per_kg DESC LIMIT 1"""
    ).fetchone()

    lahan_diajukan = conn.execute(
        "SELECT COUNT(*) FROM lahan WHERE status_verifikasi = 'diajukan'"
    ).fetchone()

    conn.close()

    return {
        "total_lahan_petak": total_lahan[0],
        "total_lahan_ha": round(total_lahan[1], 2),
        "total_produksi_ton": round(total_produksi[0], 2),
        "rata_produktivitas": round(total_produksi[1], 2),
        "total_petani": total_petani[0],
        "total_gudang": total_gudang[0],
        "total_wilayah_sentra": total_wilayah[0],
        "opt_aktif": opt_aktif[0],
        "lahan_diajukan": lahan_diajukan[0],
        "harga_tertinggi": dict(harga_tertinggi) if harga_tertinggi else None
    }


@router.get("/produksi-per-wilayah")
async def produksi_per_wilayah(tahun: int = Query(None)):
    conn = get_db()
    rows = conn.execute("""
        SELECT w.nama_wilayah,
               COALESCE(SUM(p.jumlah_ton), 0) AS total_ton,
               COALESCE(SUM(l.luas_ha), 0) AS total_ha,
               COALESCE(AVG(p.produktivitas), 0) AS avg_produktivitas,
               COUNT(DISTINCT l.id_lahan) AS jumlah_lahan
        FROM wilayah w
        LEFT JOIN lahan l ON l.id_wilayah = w.id_wilayah AND l.status_verifikasi = 'terverifikasi'
        LEFT JOIN musim_tanam mt ON mt.id_lahan = l.id_lahan
            AND mt.tahun = COALESCE(?, strftime('%Y', 'now'))
        LEFT JOIN produksi p ON p.id_musim = mt.id_musim
        WHERE w.tingkat = 'kabupaten'
        GROUP BY w.id_wilayah
        ORDER BY total_ton DESC
    """, (tahun,)).fetchall()
    conn.close()
    return [dict(r) for r in rows]


@router.get("/produksi-per-varietas")
async def produksi_per_varietas(tahun: int = Query(None)):
    conn = get_db()
    rows = conn.execute("""
        SELECT v.nama_varietas, v.tipe,
               COALESCE(SUM(p.jumlah_ton), 0) AS total_ton,
               COALESCE(AVG(p.produktivitas), 0) AS avg_produktivitas,
               COUNT(DISTINCT mt.id_musim) AS jumlah_musim
        FROM varietas v
        LEFT JOIN musim_tanam mt ON mt.id_varietas = v.id_varietas
            AND mt.tahun = COALESCE(?, strftime('%Y', 'now'))
        LEFT JOIN produksi p ON p.id_musim = mt.id_musim
        GROUP BY v.id_varietas
        ORDER BY total_ton DESC
    """, (tahun,)).fetchall()
    conn.close()
    return [dict(r) for r in rows]


@router.get("/tren-harga")
async def tren_harga(id_varietas: int = Query(1), grade: str = Query("A")):
    """Tren harga dalam 30 hari terakhir untuk varietas dan grade tertentu."""
    conn = get_db()
    rows = conn.execute("""
        SELECT h.tanggal, AVG(h.harga_per_kg) AS rata_harga,
               MIN(h.harga_per_kg) AS min_harga, MAX(h.harga_per_kg) AS max_harga,
               v.nama_varietas
        FROM harga h
        JOIN varietas v ON v.id_varietas = h.id_varietas
        WHERE h.id_varietas = ? AND h.grade_mutu = ?
            AND h.tanggal >= date('now', '-30 days')
        GROUP BY h.tanggal
        ORDER BY h.tanggal ASC
    """, (id_varietas, grade)).fetchall()
    conn.close()
    return [dict(r) for r in rows]


@router.get("/opt-rekap")
async def opt_rekap():
    """Rekapitulasi OPT per kategori dan status."""
    conn = get_db()
    per_kategori = conn.execute("""
        SELECT jo.kategori, COUNT(*) AS jumlah, 
               COALESCE(SUM(lo.luas_terserang_ha), 0) AS total_ha
        FROM laporan_opt lo
        JOIN jenis_opt jo ON jo.id_jenis_opt = lo.id_jenis_opt
        GROUP BY jo.kategori
    """).fetchall()

    per_status = conn.execute("""
        SELECT lo.status, COUNT(*) AS jumlah
        FROM laporan_opt lo
        GROUP BY lo.status
    """).fetchall()

    per_tingkat = conn.execute("""
        SELECT lo.tingkat_serangan, COUNT(*) AS jumlah,
               COALESCE(SUM(lo.luas_terserang_ha), 0) AS total_ha
        FROM laporan_opt lo
        GROUP BY lo.tingkat_serangan
    """).fetchall()

    conn.close()
    return {
        "per_kategori": [dict(r) for r in per_kategori],
        "per_status": [dict(r) for r in per_status],
        "per_tingkat": [dict(r) for r in per_tingkat]
    }

