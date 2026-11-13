"""
SIGTEMBAKAU - Admin Router
Manajemen pengguna, log aktivitas, dan ekspor data.
"""
from fastapi import APIRouter, Request, Depends, HTTPException, Query
from pydantic import BaseModel
from typing import Optional
import hashlib
import csv
import io
from fastapi.responses import StreamingResponse
from database import get_db
from routers.auth import get_current_user

router = APIRouter(prefix="/api/admin", tags=["Admin"])


def require_admin(user=Depends(get_current_user)):
    if user["nama_role"] != "admin":
        raise HTTPException(status_code=403, detail="Akses hanya untuk Admin.")
    return user


class UserCreate(BaseModel):
    id_role: int
    nama_lengkap: str
    email: str
    password: str
    no_hp: Optional[str] = None
    wilayah_tugas: Optional[str] = None


@router.get("/users")
async def list_users(user=Depends(require_admin)):
    conn = get_db()
    rows = conn.execute("""
        SELECT u.id_user, u.nama_lengkap, u.email, u.no_hp, u.wilayah_tugas,
               u.status_aktif, u.created_at, r.nama_role
        FROM users u JOIN roles r ON r.id_role = u.id_role
        ORDER BY r.id_role, u.nama_lengkap
    """).fetchall()
    conn.close()
    return [dict(r) for r in rows]


@router.post("/users")
async def create_user(data: UserCreate, user=Depends(require_admin)):
    conn = get_db()
    existing = conn.execute("SELECT id_user FROM users WHERE email = ?", (data.email,)).fetchone()
    if existing:
        conn.close()
        raise HTTPException(status_code=400, detail="Email sudah terdaftar.")
    pw_hash = hashlib.sha256(data.password.encode()).hexdigest()
    cursor = conn.cursor()
    cursor.execute("""
        INSERT INTO users (id_role, nama_lengkap, email, password_hash, no_hp, wilayah_tugas)
        VALUES (?, ?, ?, ?, ?, ?)
    """, (data.id_role, data.nama_lengkap, data.email, pw_hash, data.no_hp, data.wilayah_tugas))
    conn.commit()
    conn.close()
    return {"status": "ok", "id_user": cursor.lastrowid}


@router.patch("/users/{id_user}/toggle")
async def toggle_user(id_user: int, user=Depends(require_admin)):
    conn = get_db()
    target = conn.execute("SELECT status_aktif FROM users WHERE id_user = ?", (id_user,)).fetchone()
    if not target:
        conn.close()
        raise HTTPException(status_code=404, detail="User tidak ditemukan.")
    new_status = 0 if target["status_aktif"] else 1
    conn.execute("UPDATE users SET status_aktif = ? WHERE id_user = ?", (new_status, id_user))
    conn.commit()
    conn.close()
    return {"status": "ok", "status_aktif": new_status}


@router.get("/roles")
async def list_roles(user=Depends(require_admin)):
    conn = get_db()
    rows = conn.execute("SELECT * FROM roles").fetchall()
    conn.close()
    return [dict(r) for r in rows]


@router.get("/logs")
async def list_logs(
    limit: int = Query(100),
    aksi: Optional[str] = None,
    user=Depends(require_admin)
):
    conn = get_db()
    q = "SELECT * FROM log_aktivitas WHERE 1=1"
    params = []
    if aksi:
        q += " AND aksi = ?"
        params.append(aksi)
    q += f" ORDER BY waktu DESC LIMIT {limit}"
    rows = conn.execute(q, params).fetchall()
    conn.close()
    return [dict(r) for r in rows]


@router.get("/ekspor/produksi")
async def ekspor_produksi(user=Depends(require_admin)):
    """Ekspor data produksi ke CSV."""
    conn = get_db()
    rows = conn.execute("""
        SELECT l.kode_lahan, pt.nama_petani, w.nama_wilayah,
               mt.tahun, mt.musim, mt.tgl_tanam,
               v.nama_varietas, v.tipe,
               p.tgl_panen, p.luas_panen_ha, p.jumlah_ton, p.produktivitas, p.grade_mutu
        FROM produksi p
        JOIN musim_tanam mt ON mt.id_musim = p.id_musim
        JOIN lahan l ON l.id_lahan = mt.id_lahan
        JOIN petani pt ON pt.id_petani = l.id_petani
        JOIN wilayah w ON w.id_wilayah = l.id_wilayah
        JOIN varietas v ON v.id_varietas = mt.id_varietas
        ORDER BY p.tgl_panen DESC
    """).fetchall()
    conn.close()

    output = io.StringIO()
    writer = csv.writer(output)
    writer.writerow(["Kode Lahan", "Petani", "Wilayah", "Tahun", "Musim", "Tgl Tanam",
                     "Varietas", "Tipe", "Tgl Panen", "Luas Panen (Ha)",
                     "Produksi (Ton)", "Produktivitas (Ton/Ha)", "Grade Mutu"])
    for r in rows:
        writer.writerow(list(r))

    output.seek(0)
    return StreamingResponse(
        iter([output.getvalue()]),
        media_type="text/csv",
        headers={"Content-Disposition": "attachment; filename=data_produksi_tembakau.csv"}
    )

