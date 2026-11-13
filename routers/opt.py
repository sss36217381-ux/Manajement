"""
SIGTEMBAKAU - OPT (Organisme Pengganggu Tumbuhan) Router
Pelaporan, monitoring, dan rekomendasi penanganan OPT.
"""
from fastapi import APIRouter, Request, Depends, Query, HTTPException
from pydantic import BaseModel
from typing import Optional
from database import get_db
from routers.auth import get_current_user

router = APIRouter(prefix="/api/opt", tags=["OPT"])


class LaporanOPTCreate(BaseModel):
    id_lahan: Optional[int] = None
    id_jenis_opt: int
    wilayah_nama: Optional[str] = None
    tanggal_lapor: str
    tingkat_serangan: str   # ringan, sedang, berat
    luas_terserang_ha: float
    deskripsi: Optional[str] = None
    foto_url: Optional[str] = None
    lat: float
    lng: float


class LaporanOPTUpdate(BaseModel):
    status: Optional[str] = None  # baru, ditindaklanjuti, selesai
    deskripsi: Optional[str] = None


@router.get("")
async def list_laporan(
    status: Optional[str] = None,
    kategori: Optional[str] = None,
    tingkat: Optional[str] = None,
    limit: int = 100
):
    conn = get_db()
    q = """
        SELECT lo.*, jo.nama_opt, jo.kategori, jo.gejala, jo.rekomendasi,
               u.nama_lengkap AS pelapor, l.kode_lahan
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
    if kategori:
        q += " AND jo.kategori = ?"
        params.append(kategori)
    if tingkat:
        q += " AND lo.tingkat_serangan = ?"
        params.append(tingkat)
    q += f" ORDER BY lo.created_at DESC LIMIT {limit}"

    rows = conn.execute(q, params).fetchall()
    conn.close()
    return [dict(r) for r in rows]


@router.get("/jenis")
async def jenis_opt():
    conn = get_db()
    rows = conn.execute("SELECT * FROM jenis_opt ORDER BY kategori, nama_opt").fetchall()
    conn.close()
    return [dict(r) for r in rows]


@router.get("/{id_laporan}")
async def detail_laporan(id_laporan: int):
    conn = get_db()
    row = conn.execute("""
        SELECT lo.*, jo.nama_opt, jo.kategori, jo.gejala, jo.rekomendasi,
               u.nama_lengkap AS pelapor, l.kode_lahan, w.nama_wilayah
        FROM laporan_opt lo
        JOIN jenis_opt jo ON jo.id_jenis_opt = lo.id_jenis_opt
        JOIN users u ON u.id_user = lo.id_user
        LEFT JOIN lahan l ON l.id_lahan = lo.id_lahan
        LEFT JOIN wilayah w ON w.id_wilayah = l.id_wilayah
        WHERE lo.id_laporan = ?
    """, (id_laporan,)).fetchone()
    conn.close()
    if not row:
        raise HTTPException(status_code=404, detail="Laporan OPT tidak ditemukan.")
    return dict(row)


@router.post("")
async def buat_laporan(data: LaporanOPTCreate, request: Request, user=Depends(get_current_user)):
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("""
        INSERT INTO laporan_opt
            (id_lahan, id_jenis_opt, id_user, wilayah_nama, tanggal_lapor,
             tingkat_serangan, luas_terserang_ha, deskripsi, foto_url, lat, lng)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, (data.id_lahan, data.id_jenis_opt, user["id_user"], data.wilayah_nama,
          data.tanggal_lapor, data.tingkat_serangan, data.luas_terserang_ha,
          data.deskripsi, data.foto_url, data.lat, data.lng))

    new_id = cursor.lastrowid
    conn.execute(
        "INSERT INTO log_aktivitas (id_user, user_name, aksi, tabel_target, id_target, keterangan) VALUES (?,?,'create','laporan_opt',?,?)",
        (user["id_user"], user["nama_lengkap"], new_id,
         f"Laporan OPT baru tingkat {data.tingkat_serangan} di {data.wilayah_nama or 'lokasi'}")
    )
    conn.commit()
    conn.close()
    return {"status": "ok", "id_laporan": new_id}


@router.patch("/{id_laporan}")
async def update_laporan(id_laporan: int, data: LaporanOPTUpdate, request: Request, user=Depends(get_current_user)):
    conn = get_db()
    fields = []
    params = []
    if data.status:
        fields.append("status = ?")
        params.append(data.status)
    if data.deskripsi:
        fields.append("deskripsi = ?")
        params.append(data.deskripsi)

    if fields:
        params.append(id_laporan)
        conn.execute(f"UPDATE laporan_opt SET {', '.join(fields)} WHERE id_laporan = ?", params)
        conn.execute(
            "INSERT INTO log_aktivitas (id_user, user_name, aksi, tabel_target, id_target, keterangan) VALUES (?,?,'update','laporan_opt',?,?)",
            (user["id_user"], user["nama_lengkap"], id_laporan, f"Update laporan OPT #{id_laporan}")
        )
        conn.commit()
    conn.close()
    return {"status": "ok"}

