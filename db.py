import sqlite3
from passlib.hash import bcrypt
import os

# Veritabanı yolu
db_path = "/home/runner/recon-app/user_auth.db"

# Önceki veritabanı varsa sil
if os.path.exists(db_path):
    os.remove(db_path)

# SQLite bağlantısı
conn = sqlite3.connect(db_path)
cur = conn.cursor()

# users tablosunu oluştur
cur.execute("""
CREATE TABLE users (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    email TEXT NOT NULL UNIQUE,
    password TEXT NOT NULL
)
""")

# Örnek kullanıcı
email = "exampleemail@domain.com"
password = "password"
hashed_password = bcrypt.hash(password)

cur.execute("INSERT INTO users (email, password) VALUES (?, ?)", (email, hashed_password))
conn.commit()
conn.close()

print("Veritabanı başarıyla oluşturuldu:", db_path)