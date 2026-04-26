from fastapi import APIRouter, HTTPException
import datetime
import pandas as pd
import pickle
from catboost import CatBoostRegressor
import os
import requests  #  for live API calls
from backend.schemas import HarvestInput
from backend.database import listings_collection

router = APIRouter()

# --- LOAD TRAINED ML MODELS ---
MODEL_DIR = "ml_models"

# 1. Initialize as None to prevent the "not defined" crash
prophet_model = None
cb_volume_model = None
cb_price_model = None

try:
    with open(os.path.join(MODEL_DIR, 'prophet_model.pkl'), 'rb') as f:
        prophet_model = pickle.load(f)
    cb_volume_model = CatBoostRegressor()
    cb_volume_model.load_model(os.path.join(MODEL_DIR, 'cb_volume.cbm'))
    cb_price_model = CatBoostRegressor()
    cb_price_model.load_model(os.path.join(MODEL_DIR, 'cb_price.cbm'))
    print("✅ Enterprise ML Models Loaded Successfully!")
except Exception as e:
    print(f"⚠️ Warning: Could not load models. Error: {e}")


# ==========================================================
# LIVE DATA INGESTION ENGINE
# ==========================================================
def get_live_temperature(city="Delhi"):
    """Fetches real-time weather data to feed into the AI"""
    #  PASTE OPENWEATHER API KEY HERE:
    api_key = "c2ec34e1240f00fefe8137f6fdd893db" 
    
    url = f"http://api.openweathermap.org/data/2.5/weather?q={city}&units=metric&appid={api_key}"
    try:
        res = requests.get(url).json()
        temp = res["main"]["temp"]
        print(f"🌍 Live API Success: Current temperature in {city} is {temp}°C")
        return temp
    except Exception as e:
        print(f"⚠️ Live API Failed (Fallback to historical avg): {e}")
        return 25.0  # Safe fallback so your presentation never crashes

@router.post("/predict_demand")
def predict_demand(data: HarvestInput):
    # 2. Safety Check: Ensure models are loaded before running prediction math
    if prophet_model is None or cb_volume_model is None or cb_price_model is None:
        raise HTTPException(status_code=500, detail="Machine Learning models are not loaded on the server. Please check backend logs.")

    try:
        # --- 1. DEMAND FORECASTING (Prophet Time-Series) ---
        harvest_df = pd.DataFrame({'ds': [pd.to_datetime(data.harvest_date)]})
        forecast = prophet_model.predict(harvest_df)
        harvest_trend = forecast['trend'].values[0]
        prophet_yearly = forecast['yearly'].values[0] if 'yearly' in forecast.columns else 0.0
        
        today_df = pd.DataFrame({'ds': [pd.to_datetime(datetime.date.today())]})
        today_trend = prophet_model.predict(today_df)['trend'].values[0]

        raw_trend_multiplier = harvest_trend / today_trend if today_trend > 0 else 1.0
        demand_multiplier = max(0.80, min(raw_trend_multiplier, 1.20)) 

        # --- 2. INVENTORY & CLEARANCE ALGORITHM (CatBoost) ---
        # 🚀 FETCH THE REAL WEATHER RIGHT BEFORE PREDICTING
        real_time_temp = get_live_temperature()
        
        cb_features = pd.DataFrame({
            'discount_ratio': [data.discount_ratio], 
            'temp_lag_7': [real_time_temp], # 🚀 FED DIRECTLY INTO CATBOOST!
            'prophet_trend': [harvest_trend], 
            'prophet_yearly': [prophet_yearly]
        })
        cb_volume_pred = cb_volume_model.predict(cb_features)[0]
        prophet_volume_pred = forecast['yhat'].values[0]
        
        hybrid_volume = (0.6 * cb_volume_pred) + (0.4 * prophet_volume_pred)
        scaling_factor = data.volume_kg / 1000.0
        final_sales_volume = min(hybrid_volume * scaling_factor, data.volume_kg)
        
        predicted_spoilage = max(0, data.volume_kg - final_sales_volume)
        spoilage_ratio = predicted_spoilage / data.volume_kg if data.volume_kg > 0 else 0
        inventory_multiplier = 1.0 - (spoilage_ratio * 0.30)

        # --- 3. DYNAMIC PRICING ENGINE & ENTERPRISE DISCOUNTING ---
        base_price = data.current_market_price
        algorithmic_price = base_price * demand_multiplier * inventory_multiplier

        # Strategy A: Bulk Purchasing Power (Economies of Scale)
        bulk_discount = 0.0
        if data.volume_kg >= 5000:
            bulk_discount = 0.15  # 15% auto-discount for massive wholesale
        elif data.volume_kg >= 1000:
            bulk_discount = 0.05  # 5% auto-discount for medium bulk
            
        # Strategy B: Flash Sales & Panic Buying (Urgency)
        flash_sale_discount = 0.0
        days_to_harvest = (pd.to_datetime(data.harvest_date).date() - datetime.date.today()).days
        
        # If the crop harvests in 48 hours OR 40%+ will rot, trigger a massive clearance discount
        if days_to_harvest <= 2 or spoilage_ratio > 0.40:
            flash_sale_discount = 0.25 
            
        # The engine picks the steepest competitive discount
        total_discount_ratio = max((data.discount_ratio / 100.0), bulk_discount, flash_sale_discount)
        promotional_price = algorithmic_price * (1.0 - total_discount_ratio)


        # --- 4. HUMAN GUARDRAILS (Brand Reputation Protection) ---
        MIN_PRICE_FLOOR = base_price * 0.40  # Never sell below 40% of market value
        MAX_PRICE_CEIL = base_price * 1.50   # Never sell above 150% of market value 
        final_enterprise_price = max(MIN_PRICE_FLOOR, min(promotional_price, MAX_PRICE_CEIL))


        # --- 5. CHART DATA EXTRACTION ---
        future_dates = pd.date_range(start=data.harvest_date, periods=7)
        future_df = pd.DataFrame({'ds': future_dates})
        chart_forecast = prophet_model.predict(future_df)
        chart_forecast['ds'] = chart_forecast['ds'].dt.strftime('%Y-%m-%d')
        
        # 'yhat' (the real fluctuating forecast) instead of 'trend'
        base_yhat = chart_forecast['yhat'].iloc[0]
        
        # Scale the Prophet curve so it starts exactly at your calculated final_enterprise_price
        if base_yhat > 0:
            chart_forecast['Predicted Price (₹)'] = chart_forecast['yhat'] * (final_enterprise_price / base_yhat)
        else:
            chart_forecast['Predicted Price (₹)'] = final_enterprise_price
            
        chart_forecast['Predicted Price (₹)'] = chart_forecast['Predicted Price (₹)'].round(2)
        chart_data = chart_forecast[['ds', 'Predicted Price (₹)']].rename(columns={'ds': 'Date'}).to_dict('records')


        # --- 6. SAVE TO DATABASE ---
        listing_doc = {
            "seller_name": data.seller_name,
            "crop_category": data.crop_category,
            "original_price_per_kg": round(base_price, 2),
            "price_per_kg": round(final_enterprise_price, 2),
            "available_kg": int(final_sales_volume),
            "listed_on": datetime.datetime.now().strftime("%Y-%m-%d %H:%M"),
            "image_data": data.image_data  
        }
        listings_collection.insert_one(listing_doc)


        # --- 7. RETURN FINAL PAYLOAD ---
        return {
            "status": "success", 
            "predictions": {
                "optimal_price_per_kg": round(final_enterprise_price, 2), 
                "predicted_sales_volume_kg": int(final_sales_volume), 
                "spoilage_risk_kg": int(predicted_spoilage),
                "forecast_trend": chart_data 
            }
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))