"""
Script untuk membuat tabel-tabel di database
Jalankan script ini untuk membuat semua tabel yang didefinisikan di models.py
"""
from app.core.database import engine, Base
from app import models  # Import semua models agar terdaftar di Base.metadata

def init_db():
    """Membuat semua tabel di database"""
    print("Membuat tabel-tabel di database...")
    print(f"Database URL: {engine.url}")
    
    # Buat semua tabel
    Base.metadata.create_all(bind=engine)
    
    print("✅ Tabel-tabel berhasil dibuat!")
    print("\nTabel yang dibuat:")
    for table_name in Base.metadata.tables.keys():
        print(f"  - {table_name}")

if __name__ == "__main__":
    init_db()

