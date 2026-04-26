from fastapi import APIRouter, HTTPException, Body
import datetime
from collections import Counter
from bson import ObjectId
import os
import razorpay
import uuid
from dotenv import load_dotenv
from pydantic import BaseModel
from typing import List
from schemas import OrderCreate, Notification, NotificationUpdate # <--- Added Notification schemas
from database import users_collection, listings_collection, orders_collection, notifications_collection # <--- Added notifications_collection

# --- SECURELY LOAD RAZORPAY KEYS ---
load_dotenv()
RAZORPAY_KEY_ID = os.getenv("RAZORPAY_KEY_ID")
RAZORPAY_KEY_SECRET = os.getenv("RAZORPAY_KEY_SECRET")

# Initialize Razorpay Client
if RAZORPAY_KEY_ID and RAZORPAY_KEY_SECRET:
    rzp_client = razorpay.Client(auth=(RAZORPAY_KEY_ID, RAZORPAY_KEY_SECRET))
else:
    rzp_client = None

router = APIRouter()

# --- CONSUMER MARKET ROUTES ---
@router.get("/market_listings") # Removed /api
def get_market_listings():
    listings = list(listings_collection.find({}, {"_id": 0}).sort("listed_on", -1))
    return {"listings": listings}

@router.post("/checkout") # Removed /api
def checkout_order(order: OrderCreate):
    try:
        order_dict = order.model_dump() if hasattr(order, 'model_dump') else order.dict()
        order_dict["order_date"] = datetime.datetime.now().strftime("%Y-%m-%d %H:%M")
        
        # --- NEW: Generate a clean, professional Order ID ---
        custom_order_id = f"ORD-{str(uuid.uuid4())[:8].upper()}"
        order_dict["order_id"] = custom_order_id
        
        total_price = order_dict.get("total_price", 0.0)
        admin_commission = total_price * 0.05
        seller_payout = total_price - admin_commission
        
        order_dict["admin_commission"] = admin_commission
        order_dict["seller_payout"] = seller_payout
        
        payment_method = order_dict.get("payment_method", "Cash on Delivery")
        consumer_username = order_dict.get("consumer_username", "customer@example.com")
        payment_url = None

        # ==========================================================
        # 🚀 RAZORPAY LINK GENERATION (Only for Digital Payments)
        # ==========================================================
        if payment_method in ["UPI", "Credit/Debit Card"] and rzp_client:
            amount_in_paise = int(total_price * 100) # Razorpay requires paise!
            
            link_payload = {
                "amount": amount_in_paise,
                "currency": "INR",
                "description": f"AgriChain Order {custom_order_id}",
                "customer": {
                    "name": consumer_username.split('@')[0].capitalize(),
                    "email": consumer_username
                },
                "notify": {"email": False, "sms": False} # Keep false so test emails don't spam
            }
            
            # Request the secure payment link from Razorpay
            payment_link = rzp_client.payment_link.create(link_payload)
            payment_url = payment_link.get('short_url')
        # ==========================================================

        orders_collection.insert_one(order_dict)
        
        for item in order_dict["items"]:
            listings_collection.update_one(
                {"seller_name": item["seller_name"], "crop_category": item["crop_category"]},
                {"$inc": {"available_kg": -item["quantity"]}}
            )
            
        listings_collection.delete_many({"available_kg": {"$lte": 0}})
        # ==========================================================
        # 🚀 NOTIFICATION GENERATION
        # ==========================================================
        now_utc = datetime.datetime.now(datetime.timezone.utc)
        notifications_to_insert = []

        # 1. Notify the Consumer
        notifications_to_insert.append({
            "recipient_username": consumer_username,
            "recipient_role": "consumer",
            "title": "Order Placed Successfully",
            "message": f"Your order {custom_order_id} has been placed and is pending processing.",
            "is_read": False,
            "related_id": custom_order_id,
            "created_at": now_utc
        })

        # 2. Notify the Seller(s)
        # Using a set to avoid sending duplicate notifications to the same seller for one order
        sellers_notified = set()
        for item in order_dict["items"]:
            seller = item["seller_name"]
            if seller not in sellers_notified:
                notifications_to_insert.append({
                    "recipient_username": seller,
                    "recipient_role": "seller",
                    "title": "New Order Received!",
                    "message": f"You have a new order ({custom_order_id}) for {item['crop_category']}.",
                    "is_read": False,
                    "related_id": custom_order_id,
                    "created_at": now_utc
                })
                sellers_notified.add(seller)

        # 3. Notify the Admin(s)
        notifications_to_insert.append({
            "recipient_username": None, # None means broadcast to all admins
            "recipient_role": "admin",
            "title": "New Platform Order",
            "message": f"Order {custom_order_id} was placed for ₹{total_price}.",
            "is_read": False,
            "related_id": custom_order_id,
            "created_at": now_utc
        })

        # Insert all notifications at once
        if notifications_to_insert:
            notifications_collection.insert_many(notifications_to_insert)
        # ==========================================================

        # Return the new order ID and the Razorpay link
        return {
            "status": "success", 
            "message": "Order placed successfully", 
            "order_id": custom_order_id,
            "payment_url": payment_url
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/orders/{username}") # Removed /api
def get_user_orders(username: str):
    try:
        orders = list(orders_collection.find({"consumer_username": username}).sort("order_date", -1))
        for order in orders:
            order["_id"] = str(order["_id"])
        return {"orders": orders}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))    

@router.put("/orders/{order_id}/status")
def update_order_status(order_id: str, payload: dict = Body(...)):
    try:
        new_status = payload.get("status")
        if not new_status:
            raise HTTPException(status_code=400, detail="Missing status in request body")

        result = orders_collection.update_one(
            {"_id": ObjectId(order_id)},
            {"$set": {"status": new_status}}
        )
        if result.matched_count > 0:
            # --- NEW: Notify the consumer about the status change ---
            order = orders_collection.find_one({"_id": ObjectId(order_id)})
            if order and order.get("consumer_username"):
                notifications_collection.insert_one({
                    "recipient_username": order.get("consumer_username"),
                    "recipient_role": "consumer",
                    "title": "Order Status Updated",
                    "message": f"Your order {order.get('order_id', order_id)} is now '{new_status}'.",
                    "is_read": False,
                    "related_id": order.get('order_id'),
                    "created_at": datetime.datetime.now(datetime.timezone.utc)
                })
            # --------------------------------------------------------
            return {"status": "success", "message": f"Order marked as {new_status}"}
        else:
            raise HTTPException(status_code=404, detail="Order not found in database.")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/seller_orders/{seller_name}") # Removed /api
def get_seller_orders(seller_name: str):
    try:
        orders = list(orders_collection.find({"items.seller_name": seller_name}).sort("order_date", -1))
        for order in orders:
            order["_id"] = str(order["_id"])
        return {"orders": orders}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/recommendations/{username}") # Removed /api
def get_recommendations(username: str):
    try:
        user_orders = list(orders_collection.find({"consumer_username": username}))
        all_listings = list(listings_collection.find({}, {"_id": 0}))
        
        if not all_listings:
            return {"recommendations": []}
        if not user_orders:
            return {"recommendations": all_listings[:3]}

        bought_categories = [item["crop_category"] for order in user_orders for item in order.get("items", [])]
        favorite_crop = Counter(bought_categories).most_common(1)[0][0]
        recs = [item for item in all_listings if item["crop_category"] == favorite_crop]
        
        if len(recs) < 3:
            recs += [item for item in all_listings if item not in recs]
            
        return {"recommendations": recs[:3]} 
    except Exception as e:
        return {"recommendations": []}

# --- ADMIN DASHBOARD ROUTES ---
@router.get("/admin/analytics") # Removed /api
def get_admin_analytics():
    try:
        pipeline = [
            {"$group": {
                "_id": None,
                "total_sales": {"$sum": "$total_price"},
                "total_commission": {"$sum": "$admin_commission"},
                "total_payouts": {"$sum": "$seller_payout"}
            }}
        ]
        result = list(orders_collection.aggregate(pipeline))
        if result:
            data = result[0]
            return {"total_sales": data.get("total_sales", 0.0), "total_commission": data.get("total_commission", 0.0), "total_payouts": data.get("total_payouts", 0.0)}
        return {"total_sales": 0.0, "total_commission": 0.0, "total_payouts": 0.0}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/admin/users") # Removed /api
def get_admin_users():
    try:
        users = list(users_collection.find({}, {"password": 0})) 
        for u in users:
            u["_id"] = str(u["_id"])
        return users
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/admin/orders") # Removed /api
def get_admin_orders():
    try:
        orders = list(orders_collection.find().sort("order_date", -1))
        for o in orders:
            o["_id"] = str(o["_id"])
        return orders
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
# --- NOTIFICATION ROUTES ---
@router.get("/notifications/{username}") 
def get_user_notifications(username: str, role: str):
    try:
        # If the user is an admin, fetch global admin notifications. 
        # Otherwise, fetch notifications specific to their username and role.
        if role.lower() == "admin":
            query = {"recipient_role": "admin"}
        else:
            query = {"recipient_username": username, "recipient_role": role.lower()}

        # Fetch the 50 most recent notifications
        notifs = list(notifications_collection.find(query).sort("created_at", -1).limit(50))
        
        # Convert ObjectId and datetime for JSON serialization
        for n in notifs:
            n["_id"] = str(n["_id"])
            if "created_at" in n and isinstance(n["created_at"], datetime.datetime):
                n["created_at"] = n["created_at"].isoformat()
                
        return {"notifications": notifs}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.put("/notifications/{notif_id}/read")
def mark_notification_as_read(notif_id: str):
    try:
        result = notifications_collection.update_one(
            {"_id": ObjectId(notif_id)},
            {"$set": {"is_read": True}}
        )
        if result.matched_count > 0:
            return {"status": "success", "message": "Notification marked as read"}
        else:
            raise HTTPException(status_code=404, detail="Notification not found")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))    