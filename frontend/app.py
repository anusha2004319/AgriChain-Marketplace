import streamlit as st
import requests
st.set_page_config(page_title="AgriChain Marketplace", page_icon="🌾", layout="wide")
from config import CLIENT_ID, CLIENT_SECRET, REDIRECT_URI, API_URL
from views.landing_page import show_landing_page 
from views.auth_ui import login_page, register_page, forgot_password_page
from styles import page_bg_css
from views.seller_ui import seller_dashboard
from views.consumer_ui import consumer_storefront, consumer_checkout
from views.admin_ui import admin_dashboard

st.markdown(page_bg_css, unsafe_allow_html=True)
if "logged_in" not in st.session_state: st.session_state.logged_in = False
if "user_role" not in st.session_state: st.session_state.user_role = None  
if "username" not in st.session_state: st.session_state.username = ""
if "auth_step" not in st.session_state: st.session_state.auth_step = "role_selection" 
if "cart" not in st.session_state: st.session_state.cart = []
if "code" in st.query_params:
    auth_code = st.query_params["code"]
    returned_role = st.query_params.get("state", "consumer")
    st.query_params.clear() 
    
    token_data = {
        "code": auth_code, "client_id": CLIENT_ID, "client_secret": CLIENT_SECRET,
        "redirect_uri": REDIRECT_URI, "grant_type": "authorization_code"
    }
    token_r = requests.post("https://oauth2.googleapis.com/token", data=token_data)
    
    if token_r.status_code == 200:
        access_token = token_r.json().get("access_token")
        user_r = requests.get("https://www.googleapis.com/oauth2/v2/userinfo", headers={"Authorization": f"Bearer {access_token}"})
        if user_r.status_code == 200:
            google_email = user_r.json().get("email")
            st.session_state.update({"logged_in": True, "username": google_email, "user_role": returned_role, "auth_step": "authenticated"})
            try:
                requests.post(f"{API_URL}/register", json={"username": google_email, "password": "GOOGLE_OAUTH_SECURE", "role": returned_role})
            except: pass
            st.rerun()
if not st.session_state.logged_in:
    if st.session_state.auth_step == "role_selection" and st.session_state.user_role is None:
        show_landing_page()
    elif st.session_state.auth_step == "role_selection" and st.session_state.user_role is not None:
        from views.auth_ui import landing_page as show_bridge_page
        show_bridge_page() 
    elif st.session_state.auth_step == "login": 
        login_page()
    elif st.session_state.auth_step == "register": 
        register_page()
    elif st.session_state.auth_step == "forgot_password": 
        forgot_password_page()
else:
    current_role = str(st.session_state.user_role).lower()
    
    if current_role == "admin":
        admin_dashboard()
    elif current_role == "seller": 
        seller_dashboard()
    elif current_role == "consumer":
        if st.session_state.get("auth_step") == "checkout":
            consumer_checkout()
        else:
            consumer_storefront()