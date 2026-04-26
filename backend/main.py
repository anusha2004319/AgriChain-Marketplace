import os
import logging
import razorpay
import boto3
from dotenv import load_dotenv
from fastapi import FastAPI, Depends, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from typing import List
from database import db
# Import our new, hyper-modular routers!
from routes.auth import router as auth_router
from routes.market import router as market_router
from routes.predictions import router as predictions_router
from schemas import BankAccountInfo
from database import users_collection, listings_collection, orders_collection, bank_accounts_collection
# 1. Load the secret vault
load_dotenv()
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)
app = FastAPI(
    title="AgriChain Forecasting & Marketplace API",
    description="Backend services handling consumer checkout, seller inventory, and ML-driven sales forecasting.",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
app.include_router(auth_router, prefix="/api")
app.include_router(market_router, prefix="/api")
app.include_router(predictions_router, prefix="/api")
RAZORPAY_KEY_ID = os.getenv("RAZORPAY_KEY_ID")
RAZORPAY_KEY_SECRET = os.getenv("RAZORPAY_KEY_SECRET")
razorpay_client = razorpay.Client(auth=(RAZORPAY_KEY_ID, RAZORPAY_KEY_SECRET))
def load_ml_models():
    """Downloads models from S3 bucket on startup if not present locally"""
    s3 = boto3.client(
        's3',
        aws_access_key_id=os.getenv("AWS_ACCESS_KEY"),
        aws_secret_access_key=os.getenv("AWS_SECRET_KEY")
    )
    models = ['cb_price.cbm', 'cb_volume.cbm', 'prophet_model.pkl']
    os.makedirs("models", exist_ok=True)
    for model in models:
        local_path = f"models/{model}"
        if not os.path.exists(local_path):
            logger.info(f"Downloading {model} from S3 bucket...")
            try:
                s3.download_file('agrichain-ml-models', model, local_path)
                logger.info(f"Successfully loaded {model}")
            except Exception as e:
                logger.error(f"Failed to download {model}: {e}")
@app.on_event("startup")
async def startup_event():
    logger.info("AgriChain API starting...")
@app.get("/")
def read_root():
    return {"status": "online", "message": "AgriChain Backend is running securely!"}
@app.get("/api/admin/notifications")
async def get_admin_notifications():
    # Fetch latest listing and order using MongoDB sort
    recent_listing = await db.listings.find_one({}, sort=[("_id", -1)])
    recent_order = await db.orders.find_one({}, sort=[("_id", -1)])
    notifications = []
    if recent_listing:
        notifications.append({
            "type": "warning",
            "message": f"🌾 New Inventory: {recent_listing.get('seller_name', 'A Farmer')} added {recent_listing.get('crop_category', 'a new crop')}."
        })
    if recent_order:
        commission = recent_order.get('total_price', 0) * 0.05
        order_id = recent_order.get('order_id', 'Recent')
        notifications.append({
            "type": "success",
            "message": f"💰 Commission Obtained: ₹{commission:.2f} from Order #{order_id}."
        })
    return {"notifications": notifications}
@app.get("/api/seller/notifications/{username}")
async def get_seller_notifications(username: str):
    notifications = [{
        "type": "info",
        "message": f"🧑‍🌾 Welcome to your Seller Dashboard, {username.split('@')[0]}!"
    }]
    try:
        cursor = db.orders.find({"seller_username": username, "status": "Pending"})
        new_orders = list(db.orders.find({"seller_username": username, "status": "Pending"}))
        
        for order in new_orders:
            notifications.append({
                "type": "success",
                "message": f"📦 New Order! {order.get('consumer_username', 'A customer')} ordered {order.get('quantity', 1)}kg of {order.get('crop_category', 'produce')}."
            })
    except Exception as e:
        print(f"Database lookup skipped: {e}")
    return {"notifications": notifications}
@app.post("/api/seller/bank")
def save_bank_details(data: BankAccountInfo):
    try:
        existing = bank_accounts_collection.find_one({"username": data.username})
        bank_data = {
            "username": data.username,
            "account_holder_name": data.account_holder_name,
            "bank_name": data.bank_name,
            "account_number": data.account_number,
            "ifsc_code": data.ifsc_code.upper()
        }
        if existing:
            bank_accounts_collection.update_one({"username": data.username}, {"$set": bank_data})
            return {"status": "success", "message": "Bank details updated successfully!"}
        else:
            bank_accounts_collection.insert_one(bank_data)
            return {"status": "success", "message": "Bank details registered successfully!"}
    except Exception as e:
        return {"status": "error", "message": str(e)}
@app.get("/api/seller/bank/{username}")
def get_bank_details(username: str):
    account = bank_accounts_collection.find_one({"username": username}, {"_id": 0})
    if account:
        return {"status": "success", "data": account}
    return {"status": "not_found", "message": "No bank details found"}
@app.get("/api/consumer/notifications/{username}")
async def get_consumer_notifications(username: str):
    """
    Backend endpoint to fetch notifications for the consumer.
    The Streamlit frontend will call this API to display the bell icon.
    """
    notifications = []
    try:
        cursor = db.orders.find({"consumer_username": username}).sort("_id", -1).limit(5)
        user_orders = await cursor.to_list(length=5)
        if not user_orders:
            notifications.append({
                "type": "info",
                "message": f"Welcome {username}! Start exploring the marketplace to see updates."
            })
        for order in user_orders:
            status = order.get("status", "Processing")
            notifications.append({
                "type": "success",
                "message": f"Order #{order.get('order_id', 'N/A')} is currently {status}."
            })
    except Exception as e:
        logger.error(f"Error fetching consumer notifications: {e}")
        return {"notifications": [{"type": "warning", "message": "Could not load notifications."}]}
    return {"notifications": notifications}