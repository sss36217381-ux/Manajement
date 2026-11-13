"""
SIGTEMBAKAU - GeoJSON & Peta Router
Menyediakan layer GeoJSON untuk peta Leaflet.js.
"""
from fastapi import APIRouter, Request, Query
from fastapi.responses import JSONResponse
from database import get_db
import json

router = APIRouter(prefix="/api/geojson", tags=["GeoJSON Peta"])


@router.get("/wilayah")
async def geojson_wilayah(tingkat: str = Query("kabupaten")):
    """GeoJSON batas wilayah sentra tembakau dengan data produksi untuk choropleth."""
    conn = get_db()
    rows = conn.execute("""
        SELECT w.id_wilayah, w.nama_wilayah, w.tingkat, w.lat, w.lng,
               w.luas_potensi_ha, w.geom_geojson,
               COUNT(DISTINCT l.id_lahan) AS jumlah_lahan,
               COALESCE(SUM(l.luas_ha), 0) AS total_lahan_ha,
               COALESCE(SUM(p.jumlah_ton), 0) AS total_produksi_ton
        FROM wilayah w
        LEFT JOIN lahan l ON l.id_wilayah = w.id_wilayah AND l.status_verifikasi = 'terverifikasi'
        LEFT JOIN musim_tanam mt ON mt.id_lahan = l.id_lahan AND mt.tahun = strftime('%Y', 'now')
        LEFT JOIN produksi p ON p.id_musim = mt.id_musim
        WHERE w.tingkat = ?
        GROUP BY w.id_wilayah
    """, (tingkat,)).fetchall()
    conn.close()

    features = []
    for r in rows:
        geom = json.loads(r["geom_geojson"]) if r["geom_geojson"] else {"type": "Point", "coordinates": [r["lng"], r["lat"]]}
        features.append({
            "type": "Feature",
            "geometry": geom,
            "properties": {
                "id": r["id_wilayah"],
                "nama": r["nama_wilayah"],
                "tingkat": r["tingkat"],
                "lat": r["lat"],
                "lng": r["lng"],
                "luas_potensi_ha": r["luas_potensi_ha"],
                "jumlah_lahan": r["jumlah_lahan"],
                "total_lahan_ha": round(r["total_lahan_ha"], 2),
                "total_produksi_ton": round(r["total_produksi_ton"], 2)
            }
        })
    return {"type": "FeatureCollection", "features": features}


@router.get("/lahan")
async def geojson_lahan(
    id_wilayah: int = Query(None),
    status: str = Query(None),
    tahun: int = Query(None)
):
    """GeoJSON poligon lahan tembakau dengan info petani & produksi."""
    conn = get_db()
    q = """
        SELECT l.*, pt.nama_petani, pt.no_hp AS petani_hp,
               w.nama_wilayah,
               v.nama_varietas, v.tipe AS tipe_varietas,
               mt.tahun, mt.musim, mt.tgl_tanam, mt.luas_tanam_ha,
               p.jumlah_ton, p.produktivitas, p.grade_mutu, p.tgl_panen
        FROM lahan l
        JOIN petani pt ON pt.id_petani = l.id_petani
        JOIN wilayah w ON w.id_wilayah = l.id_wilayah
        LEFT JOIN musim_tanam mt ON mt.id_lahan = l.id_lahan
            AND mt.tahun = COALESCE(?, strftime('%Y', 'now'))
        LEFT JOIN varietas v ON v.id_varietas = mt.id_varietas
        LEFT JOIN produksi p ON p.id_musim = mt.id_musim
        WHERE 1=1
    """
    params = [tahun]
    if id_wilayah:
        q += " AND l.id_wilayah = ?"
        params.append(id_wilayah)
    if status:
        q += " AND l.status_verifikasi = ?"
        params.append(status)

    rows = conn.execute(q, params).fetchall()
    conn.close()

    features = []
    for r in rows:
        geom = json.loads(r["geom_geojson"]) if r["geom_geojson"] else None
        if not geom:
            continue
        
        # Color by status verifikasi
        color_map = {
            "terverifikasi": "#22c55e",
            "diajukan": "#f59e0b",
            "ditolak": "#ef4444",
            "draft": "#94a3b8"
        }

        features.append({
            "type": "Feature",
            "geometry": geom,
            "properties": {
                "id": r["id_lahan"],
                "kode": r["kode_lahan"],
                "petani": r["nama_petani"],
                "petani_hp": r["petani_hp"],
                "wilayah": r["nama_wilayah"],
                "luas_ha": r["luas_ha"],
                "ketinggian_mdpl": r["ketinggian_mdpl"],
                "jenis_tanah": r["jenis_tanah"],
                "kepemilikan": r["status_kepemilikan"],
                "status": r["status_verifikasi"],
                "color": color_map.get(r["status_verifikasi"], "#94a3b8"),
                "varietas": r["nama_varietas"],
                "tipe_varietas": r["tipe_varietas"],
                "tahun_tanam": r["tahun"],
                "musim": r["musim"],
                "tgl_tanam": r["tgl_tanam"],
                "luas_tanam_ha": r["luas_tanam_ha"],
                "produksi_ton": r["jumlah_ton"],
                "produktivitas": r["produktivitas"],
                "grade_mutu": r["grade_mutu"],
                "tgl_panen": r["tgl_panen"],
                "centroid_lat": r["centroid_lat"],
                "centroid_lng": r["centroid_lng"]
            }
        })
    return {"type": "FeatureCollection", "features": features}


@router.get("/gudang")
async def geojson_gudang(id_wilayah: int = Query(None), jenis: str = Query(None)):
    """GeoJSON titik gudang, pabrik, pengepul, pasar tembakau."""
    conn = get_db()
    q = """
        SELECT g.*, w.nama_wilayah,
               (SELECT h.harga_per_kg
                FROM harga h
                WHERE h.id_gudang = g.id_gudang AND h.grade_mutu = 'A'
                ORDER BY h.tanggal DESC LIMIT 1) AS harga_terakhir_A,
               (SELECT h.tanggal
                FROM harga h
                WHERE h.id_gudang = g.id_gudang
                ORDER BY h.tanggal DESC LIMIT 1) AS tgl_update_harga
        FROM gudang g
        JOIN wilayah w ON w.id_wilayah = g.id_wilayah
        WHERE 1=1
    """
    params = []
    if id_wilayah:
        q += " AND g.id_wilayah = ?"
        params.append(id_wilayah)
    if jenis:
        q += " AND g.jenis = ?"
        params.append(jenis)

    rows = conn.execute(q, params).fetchall()
    conn.close()

    icon_map = {
        "pabrik rokok": "🏭",
        "pengepul": "🏪",
        "koperasi": "🤝",
        "pasar": "🛒"
    }

    features = []
    for r in rows:
        features.append({
            "type": "Feature",
            "geometry": {"type": "Point", "coordinates": [r["lng"], r["lat"]]},
            "properties": {
                "id": r["id_gudang"],
                "nama": r["nama_gudang"],
                "jenis": r["jenis"],
                "icon": icon_map.get(r["jenis"], "📦"),
                "wilayah": r["nama_wilayah"],
                "kapasitas_ton": r["kapasitas_ton"],
                "alamat": r["alamat"],
                "kontak": r["kontak"],
                "harga_terakhir_A": r["harga_terakhir_A"],
                "tgl_update_harga": r["tgl_update_harga"],
                "status": r["status_verifikasi"]
            }
        })
    return {"type": "FeatureCollection", "features": features}


@router.get("/opt")
async def geojson_opt(status: str = Query(None), id_wilayah: int = Query(None)):
    """GeoJSON titik sebaran laporan OPT (Organisme Pengganggu Tumbuhan)."""
    conn = get_db()
    q = """
        SELECT lo.*, jo.nama_opt, jo.kategori,
               u.nama_lengkap AS pelapor,
               l.kode_lahan
        FROM laporan_opt lo
        JOIN jenis_opt jo ON jo.id_jenis_opt = lo.id_jenis_opt
        JOIN users u ON u.id_user = lo.id_user
        LEFT JOIN lahan l ON l.id_lahan = lo.id_lahan
        WHERE 1=1
    """
    params = []
    if status:
        q += " AND lo.status = ?"
        params.append(status)

    rows = conn.execute(q, params).fetchall()
    conn.close()

    color_map = {
        "baru": "#ef4444",
        "ditindaklanjuti": "#f59e0b",
        "selesai": "#22c55e"
    }
    icon_map = {
        "hama": "🐛",
        "penyakit": "🦠",
        "bencana": "⛈️"
    }
    serangan_color = {
        "ringan": "#fef08a",
        "sedang": "#fb923c",
        "berat": "#dc2626"
    }

    features = []
    for r in rows:
        features.append({
            "type": "Feature",
            "geometry": {"type": "Point", "coordinates": [r["lng"], r["lat"]]},
            "properties": {
                "id": r["id_laporan"],
                "nama_opt": r["nama_opt"],
                "kategori": r["kategori"],
                "icon": icon_map.get(r["kategori"], "⚠️"),
                "wilayah_nama": r["wilayah_nama"],
                "kode_lahan": r["kode_lahan"],
                "pelapor": r["pelapor"],
                "tanggal": r["tanggal_lapor"],
                "tingkat_serangan": r["tingkat_serangan"],
                "luas_terserang_ha": r["luas_terserang_ha"],
                "deskripsi": r["deskripsi"],
                "foto_url": r["foto_url"],
                "status": r["status"],
                "status_color": color_map.get(r["status"], "#94a3b8"),
                "serangan_color": serangan_color.get(r["tingkat_serangan"], "#94a3b8")
            }
        })
    return {"type": "FeatureCollection", "features": features}

