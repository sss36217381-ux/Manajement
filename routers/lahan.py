"""
SIGTEMBAKAU - Lahan Router
CRUD lahan tembakau + verifikasi oleh operator.
"""
from fastapi import APIRouter, Request, HTTPException, Depends
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from typing import Optional
from database import get_db
from routers.auth import get_current_user
import json

router = APIRouter(prefix="/api/lahan", tags=["Lahan"])


class LahanCreate(BaseModel):
    id_petani: int
    id_wilayah: int
    kode_lahan: str
    luas_ha: float
    ketinggian_mdpl: Optional[int] = 500
    jenis_tanah: Optional[str] = None
    status_kepemilikan: Optional[str] = "milik"
    geom_geojson: str   # JSON string polygon
    centroid_lat: Optional[float] = None
    centroid_lng: Optional[float] = None


class LahanVerifikasi(BaseModel):
    status_verifikasi: str  # terverifikasi / ditolak
    catatan_verifikasi: Optional[str] = None


@router.get("")
async def list_lahan(
    request: Request,
    id_wilayah: Optional[int] = None,
    status: Optional[str] = None,
    limit: int = 100
):
    conn = get_db()
    q = """
        SELECT l.*, pt.nama_petani, w.nama_wilayah,
               mt.tahun, mt.musim, mt.luas_tanam_ha,
               v.nama_varietas,
               p.jumlah_ton, p.produktivitas, p.grade_mutu
        FROM lahan l
        JOIN petani pt ON pt.id_petani = l.id_petani
        JOIN wilayah w ON w.id_wilayah = l.id_wilayah
        LEFT JOIN musim_tanam mt ON mt.id_lahan = l.id_lahan
            AND mt.tahun = strftime('%Y', 'now')
        LEFT JOIN varietas v ON v.id_varietas = mt.id_varietas
        LEFT JOIN produksi p ON p.id_musim = mt.id_musim
        WHERE 1=1
    """
    params = []
    if id_wilayah:
        q += " AND l.id_wilayah = ?"
        params.append(id_wilayah)
    if status:
        q += " AND l.status_verifikasi = ?"
        params.append(status)
    q += f" LIMIT {limit}"

    rows = conn.execute(q, params).fetchall()
    conn.close()
    return [dict(r) for r in rows]


@router.get("/{id_lahan}")
async def detail_lahan(id_lahan: int):
    conn = get_db()
    lahan = conn.execute("""
        SELECT l.*, pt.nama_petani, pt.nik, pt.no_hp AS petani_hp, pt.alamat AS petani_alamat,
               w.nama_wilayah, kp.nama_kelompok
        FROM lahan l
        JOIN petani pt ON pt.id_petani = l.id_petani
        JOIN wilayah w ON w.id_wilayah = l.id_wilayah
        LEFT JOIN kelompok_tani kp ON kp.id_kelompok = pt.id_kelompok
        WHERE l.id_lahan = ?
    """, (id_lahan,)).fetchone()

    if not lahan:
        raise HTTPException(status_code=404, detail="Lahan tidak ditemukan.")

    musim_list = conn.execute("""
        SELECT mt.*, v.nama_varietas, v.tipe,
               p.jumlah_ton, p.produktivitas, p.grade_mutu, p.tgl_panen
        FROM musim_tanam mt
        JOIN varietas v ON v.id_varietas = mt.id_varietas
        LEFT JOIN produksi p ON p.id_musim = mt.id_musim
        WHERE mt.id_lahan = ?
        ORDER BY mt.tahun DESC, mt.musim DESC
    """, (id_lahan,)).fetchall()

    conn.close()
    return {
        "lahan": dict(lahan),
        "riwayat_musim": [dict(m) for m in musim_list]
    }


@router.post("")
async def create_lahan(data: LahanCreate, request: Request, user=Depends(get_current_user)):
    conn = get_db()
    # Cek kode unik
    existing = conn.execute("SELECT id_lahan FROM lahan WHERE kode_lahan = ?", (data.kode_lahan,)).fetchone()
    if existing:
        conn.close()
        raise HTTPException(status_code=400, detail=f"Kode lahan '{data.kode_lahan}' sudah digunakan.")
    
    cursor = conn.cursor()
    cursor.execute("""
        INSERT INTO lahan (id_petani, id_wilayah, kode_lahan, luas_ha, ketinggian_mdpl,
                          jenis_tanah, status_kepemilikan, geom_geojson, centroid_lat, centroid_lng,
                          status_verifikasi)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, 'diajukan')
    """, (data.id_petani, data.id_wilayah, data.kode_lahan, data.luas_ha,
          data.ketinggian_mdpl, data.jenis_tanah, data.status_kepemilikan,
          data.geom_geojson, data.centroid_lat, data.centroid_lng))

    new_id = cursor.lastrowid
    conn.execute(
        "INSERT INTO log_aktivitas (id_user, user_name, aksi, tabel_target, id_target, keterangan) VALUES (?,?,'create','lahan',?,?)",
        (user["id_user"], user["nama_lengkap"], new_id, f"Mendaftarkan lahan baru {data.kode_lahan}")
    )
    conn.commit()
    conn.close()
    return {"status": "ok", "id_lahan": new_id, "message": f"Lahan {data.kode_lahan} berhasil didaftarkan, menunggu verifikasi."}


@router.patch("/{id_lahan}/verifikasi")
async def verifikasi_lahan(id_lahan: int, data: LahanVerifikasi, request: Request, user=Depends(get_current_user)):
    if user["nama_role"] not in ("admin", "operator"):
        raise HTTPException(status_code=403, detail="Hanya Admin/Operator yang dapat memverifikasi lahan.")

    conn = get_db()
    conn.execute("""
        UPDATE lahan SET status_verifikasi = ?, catatan_verifikasi = ?, updated_at = CURRENT_TIMESTAMP
        WHERE id_lahan = ?
    """, (data.status_verifikasi, data.catatan_verifikasi, id_lahan))
    conn.execute(
        "INSERT INTO log_aktivitas (id_user, user_name, aksi, tabel_target, id_target, keterangan) VALUES (?,?,'verify','lahan',?,?)",
        (user["id_user"], user["nama_lengkap"], id_lahan,
         f"Status diubah menjadi '{data.status_verifikasi}' - {data.catatan_verifikasi}")
    )
    conn.commit()
    conn.close()
    return {"status": "ok", "message": f"Lahan #{id_lahan} diperbarui menjadi '{data.status_verifikasi}'."}


@router.delete("/{id_lahan}")
async def delete_lahan(id_lahan: int, request: Request, user=Depends(get_current_user)):
    if user["nama_role"] != "admin":
        raise HTTPException(status_code=403, detail="Hanya Admin yang dapat menghapus data lahan.")
    conn = get_db()
    conn.execute("DELETE FROM lahan WHERE id_lahan = ?", (id_lahan,))
    conn.execute(
        "INSERT INTO log_aktivitas (id_user, user_name, aksi, tabel_target, id_target, keterangan) VALUES (?,?,'delete','lahan',?,?)",
        (user["id_user"], user["nama_lengkap"], id_lahan, f"Menghapus data lahan #{id_lahan}")
    )
    conn.commit()
    conn.close()
    return {"status": "ok", "message": f"Lahan #{id_lahan} berhasil dihapus."}

