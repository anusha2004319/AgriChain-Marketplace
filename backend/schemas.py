from pydantic import BaseModel, Field
from typing import List, Optional
from datetime import datetime
from datetime import datetime, timezone
class UserAuth(BaseModel):
    name: str
    mobile: str
    username: str
    password: str
    role: str
class UserLogin(BaseModel):
    username: str
    password: str
    role: str
class HarvestInput(BaseModel):
    seller_name: str
    crop_category: str
    harvest_date: str
    volume_kg: float
    discount_ratio: float
    current_market_price: float
    image_data: Optional[str] = None
class CartItem(BaseModel):
    crop_category: str
    seller_name: str
    price_per_kg: float
    quantity: int
class OrderCreate(BaseModel):
    consumer_username: str
    items: List[CartItem]
    total_price: float
    delivery_address: str  
    status: str="Pending"   
    payment_method: str
    razorpay_order_id: Optional[str] = None
    razorpay_payment_id: Optional[str] = None
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
class OrderStatusUpdate(BaseModel):
    status: str 
class BankAccountInfo(BaseModel):
    username: str
    account_holder_name: str
    bank_name: str
    account_number: str
    ifsc_code: str
class Notification(BaseModel):
    recipient_username: Optional[str] = None  
    recipient_role: str                      
    title: str
    message: str
    is_read: bool = False
    related_id: Optional[str] = None          
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
class NotificationUpdate(BaseModel):
    is_read: bool    
    