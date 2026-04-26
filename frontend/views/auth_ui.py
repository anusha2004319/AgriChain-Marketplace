import streamlit as st
import requests
from config import CLIENT_ID, REDIRECT_URI, API_URL
import time
def landing_page():
    """
    The Role Selection Bridge Page. 
    Optimized for a single-screen 'No-Scroll' experience.
    """
    st.markdown("""
    <style>
    [data-testid="stAppViewBlockContainer"] {
        padding-top: 2rem !important;
        padding-bottom: 2rem !important;
    }
    .role-container {
        text-align: center;
        padding-bottom: 0.5rem;
    }
    .role-container h1 { font-size: 2rem !important; margin-bottom: 0px !important; }
    .role-container h3 { font-size: 1rem !important; font-weight: 400; color: #666; margin-top: 0px !important; }
    .role-card {
        background-color: #ffffff;
        padding: 20px;
        border-radius: 12px;
        box-shadow: 0 4px 15px rgba(0,0,0,0.06);
        text-align: center;
        border: 1px solid #eee;
        transition: transform 0.3s ease;
    }
    .role-card:hover {
        transform: translateY(-5px);
        border-color: #2e7d32;
    }
    .role-icon {
        font-size: 45px;
        margin-bottom: 10px;
    }
    .role-card h2 { font-size: 1.4rem !important; margin-top: 5px !important; }
    .role-card p { font-size: 0.85rem !important; line-height: 1.3; color: gray; }
    button[kind="secondary"] {
        border: none !important;
        background: transparent !important;
        color: #bdc3c7 !important;
        box-shadow: none !important;
        padding: 0 !important;
        font-size: 0.8rem !important;
    }
    </style>
    """, unsafe_allow_html=True)
    st.markdown("""
    <div class='role-container'>
        <h1>How would you like to use AgriChain?</h1>
        <h3>Select your primary goal to continue</h3>
    </div>
    """, unsafe_allow_html=True)
    col1, col2 = st.columns(2)
    with col1:
        st.markdown("""
        <div class="role-card">
            <div class="role-icon">🛒</div>
            <h2>I want to Buy</h2>
            <p>Browse farm-fresh produce and buy directly from local farmers.</p>
        </div>
        """, unsafe_allow_html=True)
        # Sets role to 'consumer' and moves to login [cite: 9]
        if st.button("Start Shopping ➔", key="select_consumer", type="primary", use_container_width=True):
            st.session_state.user_role = "consumer"
            st.session_state.auth_step = "login"
            st.rerun()
    with col2:
        st.markdown("""
        <div class="role-card">
            <div class="role-icon">🧑‍🌾</div>
            <h2>I want to Sell</h2>
            <p>List your crops, use AI pricing, and reach thousands of buyers.</p>
        </div>
        """, unsafe_allow_html=True)
        # Sets role to 'seller' and moves to login [cite: 10]
        if st.button("Sell Produce ➔", key="select_seller", type="primary", use_container_width=True):
            st.session_state.user_role = "seller"
            st.session_state.auth_step = "login"
            st.rerun()
    st.markdown("<br>", unsafe_allow_html=True)
    f_left, f_mid, f_right = st.columns([1.5, 1, 1.5])
    
    with f_left:
        if st.button("← Back to Hero Page", key="back_home_hero", use_container_width=True):
            st.session_state.auth_step = "role_selection"
            st.session_state.user_role = None
            st.rerun()
            
    with f_right:
        if st.button("Admin Access", key="admin_footer"):
            st.session_state.user_role = "Admin"
            st.session_state.auth_step = "login"
            st.rerun()
def login_page():
    """
    Standard login page with dynamic icons based on the selected role.
    """
    if st.session_state.user_role == "Admin":
        role_display, icon = "Admin", "👑"
    elif st.session_state.user_role == "seller":
        role_display, icon = "Seller", "🧑‍🌾"
    else:
        role_display, icon = "Consumer", "🛒"
        
    st.markdown(f"<h2 style='text-align: center;'>{icon} {role_display} Login</h2>", unsafe_allow_html=True)
    b_l, b_m, b_r = st.columns([1.5, 1, 1.5])
    with b_m:
        if st.button("← Back to Selection", use_container_width=True):
            st.session_state.auth_step = "role_selection"
            # Set to a temp value so app.py knows to show bridge, not hero
            st.session_state.user_role = "selecting" 
            st.rerun()
        
    st.markdown("<div style='margin-bottom: 20px;'></div>", unsafe_allow_html=True)
    c1, c2, c3 = st.columns([1, 1.2, 1])
    with c2:
        with st.form("login_form"):
            login_user = st.text_input("Email ID", placeholder="Enter your email", label_visibility="collapsed")
            login_pass = st.text_input("Password", type="password", placeholder="Enter your password", label_visibility="collapsed")
            submitted = st.form_submit_button("Login", use_container_width=True)
            
            if submitted:
                if login_user and login_pass:
                    payload = {"username": login_user, "password": login_pass, "role": st.session_state.user_role}
                    try:
                        response = requests.post(f"{API_URL}/login", json=payload)
                        if response.status_code == 200:
                            data = response.json()
                            st.session_state.logged_in = True
                            st.session_state.username = data.get("username", login_user)
                            st.session_state.token = data.get("access_token") 
                            st.rerun()
                        else:
                            st.error("Invalid Email ID or password.")
                    except requests.exceptions.ConnectionError:
                        st.error("Backend offline.")
                else:
                    st.error("Please fill out all fields.")
        if st.session_state.user_role != "Admin":
            l1, l2 = st.columns(2)
            with l1:
                if st.button("Forgot Password?", use_container_width=True):
                    st.session_state.auth_step = "forgot_password"
                    st.rerun()
            with l2:
                if st.button("Create Account", use_container_width=True, type="primary"):
                    st.session_state.auth_step = "register"
                    st.rerun()

            st.markdown("<p style='text-align: center; color: gray; margin: 10px 0;'>OR</p>", unsafe_allow_html=True)
            current_role = st.session_state.user_role if st.session_state.user_role else "consumer"
            auth_url = f"https://accounts.google.com/o/oauth2/v2/auth?client_id={CLIENT_ID}&redirect_uri={REDIRECT_URI}&response_type=code&scope=email%20profile&state={current_role}"
            
            google_btn_html = f"""
            <a href="{auth_url}" target="_self" style="display: flex; align-items: center; justify-content: center; background-color: white; color: #444; border: 1px solid #ccc; border-radius: 8px; padding: 8px 15px; text-decoration: none; font-family: 'Segoe UI', Roboto, sans-serif; font-size: 15px; font-weight: 500; box-shadow: 0px 1px 2px rgba(0,0,0,0.05);">
                <img src="https://upload.wikimedia.org/wikipedia/commons/c/c1/Google_%22G%22_logo.svg" alt="Google logo" style="width: 20px; height: 20px; margin-right: 12px;">
                Sign in with Google
            </a>
            """
            st.markdown(google_btn_html, unsafe_allow_html=True)

def register_page():
    """
    Standard registration page.
    """
    st.markdown("<div style='margin-top: 2vh;'></div>", unsafe_allow_html=True)
    role_display = "Seller" if st.session_state.user_role == "seller" else "Consumer"
    st.markdown(f"<h3 style='text-align: center;'>Create a new {role_display} account</h3>", unsafe_allow_html=True)
    
    col1, col2, col3 = st.columns([1, 1.2, 1])
    with col2:
        with st.form("register_form"):
            new_name = st.text_input("Full Name", placeholder="Full Name", label_visibility="collapsed")
            new_mobile = st.text_input("Mobile Number", placeholder="Mobile Number", label_visibility="collapsed")
            new_email = st.text_input("Email ID", placeholder="Email ID", label_visibility="collapsed")
            new_pass = st.text_input("Password", type="password", placeholder="Password", label_visibility="collapsed")
            confirm_pass = st.text_input("Confirm Password", type="password", placeholder="Confirm Password", label_visibility="collapsed")
            submitted = st.form_submit_button("Register", use_container_width=True)
        if submitted:
            if new_pass != confirm_pass:
               st.error("Passwords do not match")
            else:
               with st.spinner("Creating your AgriChain account..."):
                   registration_data = {
                       "name": new_name,
                       "mobile": new_mobile,
                       "username": new_email,
                       "password": new_pass,
                       "role": role_display
                   }
        
                   try:
                       # This matches your Backend Entry Point
                       response = requests.post(
                           "http://127.0.0.1:8000/api/register", 
                           json=registration_data
                       )
                       
                       if response.status_code == 200:
                           st.success("Registration successful! Please log in.")
                           time.sleep(2) # Give the user time to read the success message
                           st.rerun()
                       else:
                           error_detail = response.json().get("detail", "Registration failed")
                           st.error(f"{error_detail}")
                           
                   except Exception as e:
                       st.error(f"Connection Error: {e}")
    
    b_l, b_m, b_r = st.columns([1.5, 1, 1.5])
    with b_m:
        if st.button("← Back to Login", use_container_width=True):
            st.session_state.auth_step = "login"
            st.rerun()

def forgot_password_page():
    """
    Password reset workflow.
    """
    st.markdown("<h2 style='text-align: center;'>Reset Password</h2>", unsafe_allow_html=True)
    col1, col2, col3 = st.columns([1, 1.2, 1])
    with col2:
        st.info("Enter your registered Email ID to receive a reset OTP.")
        st.text_input("Email ID", placeholder="your@email.com")
        if st.button("Send OTP", use_container_width=True, type="primary"):
            st.success("OTP sent! (Simulation mode)")
        if st.button("← Back to Login", use_container_width=True):
            st.session_state.auth_step = "login"
            st.rerun()