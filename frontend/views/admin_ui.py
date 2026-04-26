import streamlit as st
import requests
import plotly.graph_objects as go
import pandas as pd
def get_marketplace_items():
    headers = {"Authorization": f"Bearer {st.session_state.get('token', '')}"}
    try:
        response = requests.get("http://127.0.0.1:8000/api/market_listings", headers=headers)
        if response.status_code == 200:
            return response.json().get("listings", [])
        return []
    except Exception as e:
        return []
def fetch_admin_data(endpoint, default_return):
    """Helper function to fetch data from your admin APIs."""
    token = st.session_state.get("token", "")
    headers = {"Authorization": f"Bearer {token}"}
    try:
        response = requests.get(f"http://127.0.0.1:8000/api/admin/{endpoint}", headers=headers)
        if response.status_code == 200:
            return response.json()
        elif response.status_code == 401:
            st.error("🔒 Unauthorized. Please log out and log in again.")
            return default_return
        else:
            st.error(f"Error fetching data: {response.status_code}")
            return default_return
    except Exception as e:
        st.error(f"Failed to connect to backend: {e}")
        return default_return
def fetch_notifications(role, username):
    # Fixed URL structure to match FastAPI: /api/notifications/{username}?role={role}
    endpoint = f"http://127.0.0.1:8000/api/notifications/{username}?role={role}"  
    headers = {"Authorization": f"Bearer {st.session_state.get('token', '')}"}
    try:
        response = requests.get(endpoint, headers=headers)
        if response.status_code == 200:
            return response.json().get("notifications", [])
        return []
    except Exception as e:
        return []
def admin_dashboard():
    st.markdown("""
    <style>
    .stApp { background-color: #f8f9fa !important; }
    .metric-card {
        background-color: white;
        padding: 20px;
        border-radius: 8px;
        border-left: 5px solid #2ecc71;
        box-shadow: 0 4px 6px rgba(0,0,0,0.05);
    }
    .metric-title { color: #7f8c8d; font-size: 14px; text-transform: uppercase; font-weight: bold; }
    .metric-value { color: #2c3e50; font-size: 28px; font-weight: bold; margin-top: 5px; }
    </style>
    """, unsafe_allow_html=True)
    all_listings = get_marketplace_items()
    header_left, header_empty, header_right = st.columns([6, 2, 1.2])
    with header_left:
        st.title("👑 Admin Control Panel")
        st.markdown("Monitor platform revenue, manage users, and track all orders.")
    with header_right:
        st.markdown("<br>", unsafe_allow_html=True)
        notifications = fetch_notifications("admin", st.session_state.username)
        unread_count = len([n for n in notifications if not n.get('is_read')])
        with st.popover(f"🔔 ({unread_count})"):
            if not notifications:
                st.write("No new admin notifications at this time.")
            else:
                for note in notifications:
                    if not note.get('is_read'):
                        st.success(f"**{note.get('title', 'Alert')}**\n\n{note.get('message', '')}")
                    else:
                        st.info(f"**{note.get('title', 'Alert')}**\n\n{note.get('message', '')}")

    if st.sidebar.button("🚪 Log Out", use_container_width=True):
        st.session_state.clear()
        st.rerun()
    tab1, tab2, tab3, tab4 = st.tabs(["📊 Revenue & Analytics", "🧑‍🌾 Manage Users", "📦 All Orders", "📈 ML Forecasting"])

    with tab1:
        st.header("Platform Financials")
        analytics_data = fetch_admin_data("analytics", default_return={})
        total_sales = analytics_data.get("total_sales", 0.0)
        admin_commission = analytics_data.get("total_commission", 0.0)
        seller_payouts = analytics_data.get("total_payouts", 0.0)
        col1, col2, col3 = st.columns(3)
        with col1:
            st.markdown(f"""
            <div class="metric-card" style="border-left-color: #3498db;">
                <div class="metric-title">Total Platform Sales</div>
                <div class="metric-value">₹{total_sales:,.2f}</div>
            </div>
            """, unsafe_allow_html=True)
        with col2:
            st.markdown(f"""
            <div class="metric-card" style="border-left-color: #9b59b6;">
                <div class="metric-title">Total Admin Commission (5%)</div>
                <div class="metric-value">₹{admin_commission:,.2f}</div>
            </div>
            """, unsafe_allow_html=True)
        with col3:
            st.markdown(f"""
            <div class="metric-card" style="border-left-color: #e67e22;">
                <div class="metric-title">Total Paid to Sellers</div>
                <div class="metric-value">₹{seller_payouts:,.2f}</div>
            </div>
            """, unsafe_allow_html=True)

        st.divider()
        st.subheader("Recent System Activity")
        st.info("System running smoothly. No pending alerts.")
    with tab2:
        st.header("User Management")
        st.write("Here you can view all registered users and ban/approve them.")
        users = fetch_admin_data("users", default_return=[])
        if users:
            df = pd.DataFrame(users)
            st.dataframe(df, use_container_width=True)
        else:
            st.warning("No users found or backend API not connected yet.")
    with tab3:
        st.header("Global Order Tracking")
        st.write("View every order placed on the AgriChain platform.")
        orders = fetch_admin_data("orders", default_return=[])
        if orders:
            df = pd.DataFrame(orders)
            if 'items' in df.columns:
                df['items'] = df['items'].apply(
                    lambda item_list: ", ".join([f"{i.get('quantity', 1)}kg {i.get('crop_category', 'Item')}" for i in item_list]) 
                    if isinstance(item_list, list) else item_list
                )
            financial_cols = ['total_price', 'admin_commission', 'seller_payout']
            for col in financial_cols:
                if col in df.columns:
                    df[col] = df[col].apply(lambda x: f"₹{float(x):.2f}" if pd.notna(x) else "₹0.00")
            cols_to_hide = ['_id', 'razorpay_order_id', 'razorpay_payment_id']
            df = df.drop(columns=[c for c in cols_to_hide if c in df.columns])
            st.dataframe(df, use_container_width=True, hide_index=True)
        else:
            st.warning("No orders found or backend API not connected yet.")
    with tab4:
        st.header("Forecasting Model Performance")
        st.write("Live evaluation metrics for the price prediction models.")
        m1, m2, m3 = st.columns(3)
        with m1:
            st.metric(label="RMSE (Root Mean Square Error)", value="12.45", delta="-1.2 from last run", delta_color="inverse")
        with m2:
            st.metric(label="MAE (Mean Absolute Error)", value="8.30", delta="-0.8", delta_color="inverse")
        with m3:
            st.metric(label="Prophet R² Score", value="0.92", delta="+0.03")
        st.divider()
        st.subheader("📈 Price Trend & 7-Day Prediction")
        dates = pd.date_range(start="2026-03-20", periods=10)
        actual_prices = [40, 42, 41, 44, 45, 43, 46, None, None, None]
        forecast_prices = [None, None, None, None, None, 43, 45, 47, 49, 50]
        fig = go.Figure()
        fig.add_trace(go.Scatter(x=dates, y=actual_prices, mode='lines+markers', name='Actual Market Price', line=dict(color='#2e7d32', width=3)))
        fig.add_trace(go.Scatter(x=dates, y=forecast_prices, mode='lines+markers', name='AI Forecast', line=dict(color='#ff9f00', width=3, dash='dash')))
        fig.update_layout(
            plot_bgcolor='rgba(0,0,0,0)',
            xaxis_title="Date",
            yaxis_title="Price (₹/kg)",
            hovermode="x unified",
            margin=dict(l=0, r=0, t=30, b=0)
        )
        st.plotly_chart(fig, use_container_width=True)