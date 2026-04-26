from pymongo import MongoClient
import os

MONGO_URL = os.getenv("MONGO_URL")

client = MongoClient(MONGO_URL)

db = client["agriChainDB"]

users_collection = db["users"]
listings_collection = db["market_listings"]
orders_collection = db["orders"]
notifications_collection = db["notifications"]
bank_accounts_collection = db["bank_accounts"]
print("Mongo URL exists:", MONGO_URL is not None)