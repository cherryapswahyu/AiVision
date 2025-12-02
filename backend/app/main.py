# /app/main.py
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from . import models
from .core.database import engine, Base
from .api.v1.router import router

# Buat tabel di database (dipanggil saat aplikasi pertama kali dijalankan)
Base.metadata.create_all(bind=engine)

app = FastAPI(title="AI CCTV Restaurant Backend", version="1.0.0")

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