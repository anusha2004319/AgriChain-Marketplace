# frontend/config.py
import os

GOOGLE_CLIENT_ID = os.getenv("GOOGLE_CLIENT_ID")
GOOGLE_CLIENT_SECRET = os.getenv("GOOGLE_CLIENT_SECRET")
REDIRECT_URI = "http://localhost:8501"
BASE_URL = "https://agrichain-marketplace.onrender.com"
API_URL =BASE_URL