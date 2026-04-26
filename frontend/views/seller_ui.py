import streamlit as st
import pandas as pd
import datetime
import requests
import base64  
from config import API_URL
from views.consumer_ui import fetch_user_orders
import plotly.express as px

def fetch_bank_details(username):
    try:
        response = requests.get(f"http://127.0.0.1:8000/api/seller/bank/{username}")
        if response.status_code == 200 and response.json().get("status") == "success":
            return response.json().get("data")
        return None
    except:
        return None

def get_marketplace_items():
    headers = {"Authorization": f"Bearer {st.session_state.get('token', '')}"}
    try:
        response = requests.get("http://127.0.0.1:8000/api/market_listings", headers=headers)
        if response.status_code == 200:
            return response.json().get("listings", [])
        return []
    except Exception as e:
        return []

def fetch_seller_orders(username):
    headers = {"Authorization": f"Bearer {st.session_state.get('token', '')}"}
    try:
        response = requests.get(f"http://127.0.0.1:8000/api/seller_orders/{username}", headers=headers)
        if response.status_code == 200:
            return response.json().get("orders", []) 
        return []
    except Exception as e:
        return []

def get_analytics_data(username):
    headers = {"Authorization": f"Bearer {st.session_state.get('token', '')}"}
    try:
        response = requests.get(f"http://127.0.0.1:8000/api/seller_orders/{username}", headers=headers)
        if response.status_code == 200:
            orders = response.json().get("orders", [])
            all_items = []
            for order in orders:
                for item in order.get('items', []):
                    if item.get('seller_name') == username:
                        all_items.append({
                            "Crop": item['crop_category'],
                            "Revenue": item['price_per_kg'] * item.get('quantity', 1),
                            "Volume": item.get('quantity', 1)
                        })
            return pd.DataFrame(all_items)
        return pd.DataFrame()
    except:
        return pd.DataFrame()            

def fetch_notifications(role, username):
    endpoint = f"http://127.0.0.1:8000/api/notifications/{username}?role={role}"
        
    headers = {"Authorization": f"Bearer {st.session_state.get('token', '')}"}
    try:
        response = requests.get(endpoint, headers=headers)
        if response.status_code == 200:
            return response.json().get("notifications", [])
        return []
    except Exception as e:
        return []

def seller_dashboard():
    st.markdown("""
    <style>
    /* --- NEW: Professional Background Colors --- */
    .stApp {
        background-color: #f4f6f8 !important; /* Soft dashboard gray */
    }
    [data-testid="stSidebar"] {
        background-color: #ffffff !important; /* Crisp white sidebar */
        box-shadow: 2px 0px 10px rgba(0,0,0,0.05); /* Subtle shadow */
    }
    
    /* Hide Streamlit Branding */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}
    
    /* Make Tabs 'pop' down when clicked */
    button[data-baseweb="tab"] {
        transition: all 0.15s ease !important;
    }
    button[data-baseweb="tab"]:active {
        transform: scale(0.95) translateY(2px) !important;
    }
    </style>
    """, unsafe_allow_html=True)
    seller_orders = fetch_seller_orders(st.session_state.username) 
    new_order_count = len([o for o in seller_orders if o.get('status') == 'Pending'])
    header_left, header_empty, header_right = st.columns([6, 2, 1.2])
    
    with header_left:
        st.title("🧑‍🌾 Seller Dashboard")
        st.markdown("Manage your farm inventory and orders.")
        
    with header_right:
        st.markdown("<br>", unsafe_allow_html=True)
        notifications = fetch_notifications("seller", st.session_state.username) 
        unread_count = len([n for n in notifications if not n.get('is_read')])
        
        with st.popover(f"🔔 ({unread_count})"):
            if not notifications:
                st.write("No new seller notifications at this time.")
            else:
                for note in notifications:
                    if not note.get('is_read'):
                        st.success(f"**{note.get('title', 'Alert')}**\n\n{note.get('message', '')}")
                    else:
                        st.info(f"**{note.get('title', 'Alert')}**\n\n{note.get('message', '')}")
                    
    st.sidebar.title("🌾 Seller Portal")
    st.sidebar.write(f"Welcome, **{st.session_state.username}**")
    if st.sidebar.button("Log Out"):
        st.session_state.logged_in = False
        st.session_state.auth_step = "role_selection"
        st.session_state.user_role = None
        st.session_state.token = None # Clear token on logout
        st.rerun()
        
    tab1, tab2, tab3, tab4 = st.tabs(["📊 Analytics Dashboard", "🛒 List a Crop", "💰 My Sales", "🏦 Bank Details"])
    with tab1:
        st.markdown("### 📊 Farm Analytics & Market Trends")
        
        real_df = get_analytics_data(st.session_state.username)
        
        if not real_df.empty:
            total_rev = real_df['Revenue'].sum()
            total_vol = real_df['Volume'].sum()
            
            kpi1, kpi2, kpi3 = st.columns(3)
            kpi1.metric(label="Total Revenue", value=f"₹{total_rev:,.2f}")
            kpi2.metric(label="Total Volume Sold", value=f"{total_vol} kg")
            kpi3.metric(label="Top Crop", value=real_df.groupby('Crop')['Revenue'].sum().idxmax())

            st.markdown("**📦 Sales by Crop Category**")
            chart_data = real_df.groupby('Crop')['Volume'].sum().reset_index()
            fig_bar = px.bar(chart_data, x="Crop", y="Volume", color="Crop")
            st.plotly_chart(fig_bar, use_container_width=True)
        else:
            st.warning("No sales data available yet to generate analytics.")
    with tab2:
        st.header("🛒 Demand Forecasting & Listing")
        st.info("Run your AI pipeline here. Your crop will instantly be listed on the consumer market!")
        
        with st.form("prediction_form"):
            crop_dropdown = st.selectbox(
                "Crop Category", 
                ["Tomatoes", "Onions", "Potatoes", "Apples", "✨ Add Custom Crop..."]
            )
            custom_crop = None
            if crop_dropdown == "✨ Add Custom Crop...":
                custom_crop = st.text_input(
                    "Type your product name here:", 
                    placeholder="e.g., Carrots, Mangoes, Wheat"
                )
            uploaded_image = st.file_uploader("Upload a picture of your crop (Optional)", type=["jpg", "jpeg", "png"])
            
            harvest_date = st.date_input("Expected Harvest Date", datetime.date.today() + datetime.timedelta(days=7))
            current_price = st.number_input("Current Local Market Price (₹/kg)", min_value=1.0, value=20.0, step=1.0)
            volume_kg = st.number_input("Estimated Volume (KG)", min_value=100, step=100, value=1000)
            apply_discount = st.slider("Discount Optimization Ratio (%)", 0, 30, 5)
            
            submit_button = st.form_submit_button("Generate AI Pricing & List on Market")

        if submit_button:
            final_crop_name = crop_dropdown
            if crop_dropdown == "✨ Add Custom Crop...":
                if custom_crop:
                    final_crop_name = custom_crop.strip().title()
                else:
                    st.error("Please type a name for your custom crop before submitting.")
                    st.stop() 
            img_str = ""
            if uploaded_image is not None:
                img_bytes = uploaded_image.getvalue()
                img_str = base64.b64encode(img_bytes).decode("utf-8")

            payload = {
                "seller_name": st.session_state.username, 
                "crop_category": final_crop_name, 
                "harvest_date": str(harvest_date), 
                "volume_kg": float(volume_kg), 
                "discount_ratio": float(apply_discount), 
                "current_market_price": float(current_price), 
                "image_data": img_str 
            }
            
            try:
                with st.spinner(f"AI is pricing your {final_crop_name} and listing it..."):
                    headers = {"Authorization": f"Bearer {st.session_state.get('token', '')}"}
                    response = requests.post("http://127.0.0.1:8000/api/predict_demand", json=payload, headers=headers)
                
                if response.status_code == 200:
                    data = response.json()["predictions"]
                    st.toast(f"Successfully listed {final_crop_name}!", icon="✅") 
                    st.success(f"AI Pricing Applied! {final_crop_name} listed for ₹{data['optimal_price_per_kg']}/kg.")
                    
                    if "forecast_trend" in data:
                        st.markdown("### 📊 7-Day Market Trend Forecast")
                        
                        if data["forecast_trend"]: 
                            if isinstance(data["forecast_trend"], dict):
                                df_chart = pd.DataFrame(list(data["forecast_trend"].items()), columns=["Date", "Predicted Price (₹)"])
                            else: 
                                df_chart = pd.DataFrame(data["forecast_trend"])
                            
                            df_chart.set_index("Date", inplace=True)
                            st.line_chart(df_chart, color="#22c55e") 
                            max_price = df_chart["Predicted Price (₹)"].max()
                            min_price = df_chart["Predicted Price (₹)"].min()
                            current_price = df_chart.iloc[0]["Predicted Price (₹)"]
                            
                            max_date = df_chart["Predicted Price (₹)"].idxmax()
                            
                            max_increase = (max_price - current_price) / current_price
                            max_decrease = (current_price - min_price) / current_price
                            
                            if max_increase > 0.01:
                                st.success(f"💡 AI Insight: Prices will peak at **₹{max_price:.2f}** around **{max_date}**. Consider holding stock to maximize profit!")
                            elif max_decrease > 0.01:
                                st.warning(f"💡 AI Insight: Prices are volatile and may drop to **₹{min_price:.2f}**. We recommend selling your harvest immediately.")
                            else:
                                st.info(f"💡 AI Insight: The market is predicted to remain stable around ₹{current_price:.2f} next week. Good time to list!")
                else:
                    st.error(f"Failed to list item: {response.text}")
            except Exception as e:
                st.error(f"Backend offline or Error: {e}")
    with tab3:
        st.header("📦 Recent Orders")
        st.markdown("Track what customers have bought from you.")
        
        orders = fetch_seller_orders(st.session_state.username)
        
        if not orders:
            st.info("No sales yet. Keep listing fresh crops!")
        else:
            for order in orders:
                with st.container(border=True):
                    col1, col2 = st.columns([3, 1])
                    
                    with col1:
                        order_id = order.get('_id', 'Unknown')
                        st.markdown(f"**Order ID:** {order_id[:8]}")
                        st.markdown(f"**Customer:** {order.get('consumer_username', 'Guest')}")
                        st.markdown(f"**Delivery Address:** {order.get('delivery_address', 'N/A')}")
                        st.markdown(f"**Payment Method:** {order.get('payment_method', 'N/A')}")
                        
                        st.write("**Items to Pack:**")
                        my_items = [item for item in order.get('items', []) if item.get('seller_name') == st.session_state.username]
                        
                        revenue_for_this_order = 0
                        for item in my_items:
                            qty = item.get('quantity', 1)
                            price = item.get('price_per_kg', 0)
                            subtotal = qty * price
                            revenue_for_this_order += subtotal
                            st.markdown(f"- {qty}kg **{item['crop_category']}** (₹{price}/kg)")
                            
                    with col2:
                        status = order.get('status', 'Processing')
                        st.success(f"Status: {status}")
                        st.markdown(f"### Total Earned:")
                        st.markdown(f"<h2 style='color:#2e7d32; margin-top:0px;'>₹{revenue_for_this_order:.2f}</h2>", unsafe_allow_html=True)
                        
                        if status != "Shipped" and order_id != 'Unknown':
                            if st.button("Mark as Shipped", key=f"ship_{order_id}"):
                                headers = {"Authorization": f"Bearer {st.session_state.get('token', '')}"}
                                response = requests.put(f"http://127.0.0.1:8000/api/orders/{order_id}/status", json={"status": "Shipped"}, headers=headers)
                                
                                if response.status_code == 200:
                                    st.success("Status updated to Shipped!")
                                    st.rerun()
                                else:
                                    st.error(f"🚨 Update Failed ({response.status_code}): {response.text}")
    with tab4:
        st.header("🏦 Bank Account Details")
        st.markdown("Register your bank account to receive payments from buyers.")

        existing_bank = fetch_bank_details(st.session_state.username)
        
        with st.container(border=True):
            acc_name = st.text_input("Account Holder Name", value=existing_bank['account_holder_name'] if existing_bank else "")
            default_bank_name = existing_bank['bank_name'] if existing_bank else "State Bank of India (SBI)"
            bank_options = [
                "🏦 State Bank of India (SBI)",
                "🏦 HDFC Bank",
                "🏦 ICICI Bank",
                "🏦 Axis Bank",
                "🏦 Kotak Mahindra Bank",
                "🏦 Punjab National Bank (PNB)",
                "🏦 Bank of Baroda",
                "➕ Other..."
            ]
            if existing_bank and existing_bank['bank_name'] not in [b.replace("🏦 ", "").replace("➕ ", "") for b in bank_options]:
                start_index = len(bank_options) - 1 # Set to "Other..."
            else:
                try:
                    match = [b for b in bank_options if default_bank_name in b][0]
                    start_index = bank_options.index(match)
                except:
                    start_index = 0

            selected_bank = st.selectbox("Select Bank", bank_options, index=start_index)
            final_bank_name = selected_bank.replace("🏦 ", "").replace("➕ ", "")
            
            if selected_bank == "➕ Other...":
                final_bank_name = st.text_input("Type your Custom Bank Name", value=existing_bank['bank_name'] if existing_bank and start_index == len(bank_options)-1 else "")
            
            acc_num = st.text_input("Account Number", type="password", value=existing_bank['account_number'] if existing_bank else "")
            ifsc = st.text_input("IFSC Code", placeholder="e.g., SBIN0001234", value=existing_bank['ifsc_code'] if existing_bank else "")
            
            confirm = st.checkbox("I confirm that these bank details are correct.")
            submit_bank = st.button("Save Bank Details", use_container_width=True, type="primary")
            
            if submit_bank:
                if not confirm:
                    st.error("Please confirm your details by checking the box.")
                elif not all([acc_name, final_bank_name, acc_num, ifsc]):
                    st.error("All fields are required!")
                else:
                    payload = {
                        "username": st.session_state.username,
                        "account_holder_name": acc_name,
                        "bank_name": final_bank_name,
                        "account_number": acc_num,
                        "ifsc_code": ifsc
                    }
                    try:
                        with st.spinner("Saving bank details..."):
                            res = requests.post("http://127.0.0.1:8000/api/seller/bank", json=payload)
                            
                        if res.status_code == 200 and res.json().get("status") == "success":
                            st.success(res.json().get("message"))
                            st.rerun()
                        else:
                            st.error("Failed to save bank details.")
                    except Exception as e:
                        st.error(f"Connection Error: {e}")
        if existing_bank:
            st.info(f"Active Bank Account: **{existing_bank['bank_name']}** ending in **{existing_bank['account_number'][-4:]}**")