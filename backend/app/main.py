from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager # 🚨 IMPORT BARU
from sqlalchemy.orm import Session # 🚨 IMPORT BARU
from .core.database import engine, Base, SessionLocal # 🚨 PERLU IMPORT SessionLocal
from . import models, crud # 🚨 PERLU IMPORT CRUD
from .api.v1.router import router
import asyncio # 🚨 IMPORT BARU

# --- FUNGSI BACKGROUND CHECK ---
async def heartbeat_check_task():
    """Loop asynchronous yang menjalankan pengecekan setiap 60 detik."""
    while True:
        # Panggil fungsi CRUD dalam sesi database terpisah
        db: Session = SessionLocal()
        try:
            crud.check_camera_heartbeats(db)
        finally:
            db.close()
        
        # Tunggu 60 detik sebelum pengecekan berikutnya
        await asyncio.sleep(60)

# --- LIFESPAN MANAGER BARU ---
@asynccontextmanager
async def lifespan(app: FastAPI):
    # 1. Buat tabel di database saat aplikasi start
    print("Membuat tabel-tabel di database...")
    Base.metadata.create_all(bind=engine)
    print("✅ Tabel-tabel siap digunakan!")
    
    # 2. Start Background Task
    task = asyncio.create_task(heartbeat_check_task())
    
    # 3. Yield (Aplikasi berjalan)
    yield
    
    # 4. Shutdown (Hentikan Task saat aplikasi dimatikan)
    task.cancel()

# Ubah inisialisasi FastAPI untuk menggunakan lifespan
app = FastAPI(
    title="AI CCTV Restaurant Backend", 
    version="1.0.0",
    lifespan=lifespan # 🚨 TAMBAHAN LIFESPAN
)

# 🚨 PENTING: Middleware CORS untuk koneksi dengan Frontend React
origins = [
    "http://localhost:3000",  # Ganti dengan alamat frontend Anda
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Masukkan semua router API
app.include_router(router)

# Endpoint Health Check
@app.get("/")
def read_root():
    return {"status": "Backend running", "version": "v1"}