"""
SIGTEMBAKAU - Main FastAPI Application
Sistem Informasi Geografis (SIG) Tembakau Nasional
"""
from fastapi import FastAPI, Request
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse, JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from starlette.middleware.sessions import SessionMiddleware
import os, sys

# Tambahkan direktori root ke path agar routers bisa import database
sys.path.insert(0, os.path.dirname(__file__))

from routers import auth, peta, dashboard, lahan, harga, opt, admin
from database import init_db

# Inisialisasi DB saat startup
init_db()

app = FastAPI(
    title="SIGTEMBAKAU",
    description="Sistem Informasi Geografis Tembakau - Prototype WebGIS Nasional",
    version="1.0.0",
    docs_url="/api/docs",
    redoc_url="/api/redoc"
)

# Middleware
app.add_middleware(
    SessionMiddleware,
    secret_key="sigtembakau-secret-key-2026-rahasia",
    max_age=86400  # 24 jam
)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"]
)

# Register Routers
app.include_router(auth.router)
app.include_router(peta.router)
app.include_router(dashboard.router)
app.include_router(lahan.router)
app.include_router(harga.router)
app.include_router(opt.router)
app.include_router(admin.router)

# Serve static files (frontend)
static_dir = os.path.join(os.path.dirname(__file__), "static")
if os.path.exists(static_dir):
    app.mount("/static", StaticFiles(directory=static_dir), name="static")

# Root: arahkan ke index.html
@app.get("/", include_in_schema=False)
async def root():
    index_path = os.path.join(static_dir, "index.html")
    if os.path.exists(index_path):
        return FileResponse(index_path)
    return JSONResponse({"status": "SIGTEMBAKAU API Running", "docs": "/api/docs"})

@app.get("/{page}.html", include_in_schema=False)
async def serve_page(page: str):
    page_path = os.path.join(static_dir, f"{page}.html")
    if os.path.exists(page_path):
        return FileResponse(page_path)
    return JSONResponse({"error": "Halaman tidak ditemukan."}, status_code=404)

@app.get("/health")
async def health():
    return {"status": "ok", "app": "SIGTEMBAKAU v1.0.0"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)

