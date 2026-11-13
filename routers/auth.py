"""
SIGTEMBAKAU - Auth Router
Autentikasi berbasis session sederhana (cookie-based) untuk prototype.
"""
from fastapi import APIRouter, Request, Response, Form, HTTPException, Depends
from fastapi.responses import JSONResponse, RedirectResponse
import hashlib
from database import get_db

router = APIRouter(prefix="/api/auth", tags=["Auth"])

def hash_pw(password: str) -> str:
    return hashlib.sha256(password.encode()).hexdigest()

def get_current_user(request: Request):
    user_id = request.session.get("user_id")
    if not user_id:
        raise HTTPException(status_code=401, detail="Silakan login terlebih dahulu.")
    conn = get_db()
    user = conn.execute(
        "SELECT u.*, r.nama_role FROM users u JOIN roles r ON u.id_role = r.id_role WHERE u.id_user = ?",
        (user_id,)
    ).fetchone()
    conn.close()
    if not user:
        raise HTTPException(status_code=401, detail="Sesi tidak valid.")
    return dict(user)

def get_optional_user(request: Request):
    try:
        return get_current_user(request)
    except:
        return None

@router.post("/login")
async def login(request: Request, email: str = Form(...), password: str = Form(...)):
    conn = get_db()
    user = conn.execute(
        "SELECT u.*, r.nama_role FROM users u JOIN roles r ON u.id_role = r.id_role WHERE u.email = ? AND u.status_aktif = 1",
        (email,)
    ).fetchone()
    conn.close()

    if not user or user["password_hash"] != hash_pw(password):
        raise HTTPException(status_code=401, detail="Email atau password salah.")

    request.session["user_id"] = user["id_user"]
    request.session["user_name"] = user["nama_lengkap"]
    request.session["role"] = user["nama_role"]

    # Log aktivitas
    conn = get_db()
    conn.execute(
        "INSERT INTO log_aktivitas (id_user, user_name, aksi, keterangan) VALUES (?, ?, 'login', ?)",
        (user["id_user"], user["nama_lengkap"], f"Login berhasil dari {request.client.host}")
    )
    conn.commit()
    conn.close()

    return JSONResponse({
        "status": "ok",
        "user": {
            "id": user["id_user"],
            "nama": user["nama_lengkap"],
            "email": user["email"],
            "role": user["nama_role"],
            "wilayah": user["wilayah_tugas"]
        }
    })

@router.post("/logout")
async def logout(request: Request):
    request.session.clear()
    return JSONResponse({"status": "ok", "message": "Berhasil logout."})

@router.get("/me")
async def me(request: Request):
    user = get_optional_user(request)
    if not user:
        return JSONResponse({"logged_in": False})
    return JSONResponse({
        "logged_in": True,
        "user": {
            "id": user["id_user"],
            "nama": user["nama_lengkap"],
            "email": user["email"],
            "role": user["nama_role"],
            "wilayah": user["wilayah_tugas"]
        }
    })

