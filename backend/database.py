import os
from pymongo import MongoClient

MONGO_URL = os.getenv("MONGO_URL")

print("DEBUG MONGO_URL:", MONGO_URL)  # 👈 ADD THIS

client = MongoClient(MONGO_URL, serverSelectionTimeoutMS=5000)

try:
    client.server_info()
    print("✅ MongoDB Connected Successfully!")
except Exception as e:
    print("❌ MongoDB ERROR:", e)