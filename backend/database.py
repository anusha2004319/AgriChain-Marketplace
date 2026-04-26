from pymongo import MongoClient
import os # <-- Required to read environment variables

try:
    MONGO_URL = os.getenv("MONGO_URL", "mongodb://localhost:27017/")
    client = MongoClient(MONGO_URL, serverSelectionTimeoutMS=5000)
    db = client["agrichain_db"]
    users_collection = db["users"]
    listings_collection = db["market_listings"] 
    orders_collection = db["orders"]
    notifications_collection = db["notifications"]
    bank_accounts_collection = db["bank_accounts"]
    client.server_info() 
    print("MongoDB Connected Successfully!")
except Exception as e:
    print(f"Could not connect to MongoDB. Error: {e}")