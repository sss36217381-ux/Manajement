"""
SIGTEMBAKAU - Harga Router
Monitoring & input harga tembakau harian per gudang, varietas, dan grade mutu.
"""
from fastapi import APIRouter, Request, Depends, Query, HTTPException
from pydantic import BaseModel
from typing import Optional
from database import get_db
from routers.auth import get_current_user

router = APIRouter(prefix="/api/harga", tags=["Harga"])


class HargaInput(BaseModel):
    id_gudang: int
    id_varietas: int
    tanggal: str
    grade_mutu: str
    harga_per_kg: float
    catatan: Optional[str] = None


@router.get("")
async def list_harga(
    id_gudang: Optional[int] = None,
    id_varietas: Optional[int] = None,
    grade_mutu: Optional[str] = None,
    tanggal_mulai: Optional[str] = None,
    tanggal_akhir: Optional[str] = None,
    limit: int = 200
):
    conn = get_db()
    q = """
        SELECT h.*, g.nama_gudang, g.jenis AS jenis_gudang, g.lat, g.lng,
               w.nama_wilayah,
               v.nama_varietas, v.tipe
        FROM harga h
        JOIN gudang g ON g.id_gudang = h.id_gudang
        JOIN wilayah w ON w.id_wilayah = g.id_wilayah
        JOIN varietas v ON v.id_varietas = h.id_varietas
        WHERE 1=1
    """
    params = []
    if id_gudang:
        q += " AND h.id_gudang = ?"
        params.append(id_gudang)
    if id_varietas:
        q += " AND h.id_varietas = ?"
        params.append(id_varietas)
    if grade_mutu:
        q += " AND h.grade_mutu = ?"
        params.append(grade_mutu)
    if tanggal_mulai:
        q += " AND h.tanggal >= ?"
        params.append(tanggal_mulai)
    if tanggal_akhir:
        q += " AND h.tanggal <= ?"
        params.append(tanggal_akhir)
    q += " ORDER BY h.tanggal DESC, h.harga_per_kg DESC"
    q += f" LIMIT {limit}"

    rows = conn.execute(q, params).fetchall()
    conn.close()
    return [dict(r) for r in rows]


@router.get("/terakhir")
async def harga_terakhir():
    """Harga terbaru per gudang & varietas (Grade A) untuk ditampilkan di peta."""
    conn = get_db()
    rows = conn.execute("""
        SELECT h.id_gudang, h.id_varietas, h.grade_mutu,
               h.harga_per_kg, h.tanggal, h.catatan,
               g.nama_gudang, g.jenis AS jenis_gudang, g.lat, g.lng,
               w.nama_wilayah,
               v.nama_varietas, v.tipe
        FROM harga h
        JOIN gudang g ON g.id_gudang = h.id_gudang
        JOIN wilayah w ON w.id_wilayah = g.id_wilayah
        JOIN varietas v ON v.id_varietas = h.id_varietas
        WHERE h.rowid IN (
            SELECT MAX(rowid) FROM harga
            GROUP BY id_gudang, id_varietas, grade_mutu
        )
        ORDER BY h.harga_per_kg DESC
    """).fetchall()
    conn.close()
    return [dict(r) for r in rows]


@router.post("")
async def input_harga(data: HargaInput, request: Request, user=Depends(get_current_user)):
    if user["nama_role"] not in ("admin", "operator", "gudang"):
        raise HTTPException(status_code=403, detail="Hanya Admin/Operator/Gudang yang dapat input harga.")

    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("""
        INSERT INTO harga (id_gudang, id_varietas, tanggal, grade_mutu, harga_per_kg, id_user_input, catatan)
        VALUES (?, ?, ?, ?, ?, ?, ?)
    """, (data.id_gudang, data.id_varietas, data.tanggal, data.grade_mutu,
          data.harga_per_kg, user["id_user"], data.catatan))

    new_id = cursor.lastrowid
    conn.execute(
        "INSERT INTO log_aktivitas (id_user, user_name, aksi, tabel_target, id_target, keterangan) VALUES (?,?,'create','harga',?,?)",
        (user["id_user"], user["nama_lengkap"], new_id,
         f"Input harga Grade {data.grade_mutu} Rp {data.harga_per_kg:,.0f}/kg")
    )
    conn.commit()
    conn.close()
    return {"status": "ok", "id_harga": new_id}


@router.get("/gudang-list")
async def gudang_list():
    conn = get_db()
    rows = conn.execute("""
        SELECT g.id_gudang, g.nama_gudang, g.jenis, w.nama_wilayah
        FROM gudang g JOIN wilayah w ON w.id_wilayah = g.id_wilayah
        ORDER BY w.nama_wilayah, g.nama_gudang
    """).fetchall()
    conn.close()
    return [dict(r) for r in rows]


@router.get("/varietas-list")
async def varietas_list():
    conn = get_db()
    rows = conn.execute("SELECT id_varietas, nama_varietas, tipe FROM varietas ORDER BY tipe, nama_varietas").fetchall()
    conn.close()
    return [dict(r) for r in rows]

