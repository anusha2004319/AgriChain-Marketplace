import streamlit as st
import requests
import base64
from fpdf import FPDF
import datetime
import time
from config import API_URL
def create_invoice_pdf(order_id, cart_items, total_price, address):
    pdf = FPDF(orientation='P', unit='mm', format='A4')
    pdf.add_page()
    pdf.set_font("Arial", 'B', 16)
    pdf.cell(0, 8, txt="Tax Invoice", ln=True, align='C')
    pdf.set_font("Arial", '', 10)
    pdf.cell(0, 5, txt="Original For Recipient", ln=True, align='C')
    pdf.ln(8)
    pdf.set_font("Arial", 'B', 10)
    pdf.cell(95, 5, txt="BILL TO / SHIP TO:", ln=False)
    pdf.cell(95, 5, txt="ORDER DETAILS:", ln=True)
    pdf.set_font("Arial", '', 9)
    start_x = pdf.get_x()
    start_y = pdf.get_y()
    clean_address = str(address).replace('\n', ', ')
    username = st.session_state.get('username', 'Guest User')
    pdf.multi_cell(90, 5, txt=f"{username}\n{clean_address}")
    pdf.set_xy(start_x + 95, start_y)
    pdf.cell(35, 5, txt="Order Number:", ln=False)
    pdf.cell(50, 5, txt=str(order_id), ln=True) 
    pdf.set_x(start_x + 95)
    pdf.cell(35, 5, txt="Order Date:", ln=False)
    pdf.cell(50, 5, txt=datetime.datetime.now().strftime('%d-%m-%Y %H:%M:%S'), ln=True)
    pdf.set_x(start_x + 95)
    pdf.cell(35, 5, txt="Invoice Number:", ln=False)
    safe_order_id = str(order_id)
    pdf.cell(50, 5, txt=f"AGRI-INV-{safe_order_id[-6:]}", ln=True)
    pdf.set_x(start_x + 95)
    pdf.cell(35, 5, txt="Invoice Date:", ln=False)
    pdf.cell(50, 5, txt=datetime.datetime.now().strftime('%d-%m-%Y %H:%M:%S'), ln=True)
    pdf.ln(10)
    pdf.set_font("Arial", 'B', 8)
    pdf.cell(8, 8, "SN.", border=1, align='C')
    pdf.cell(52, 8, "Description", border=1, align='C')
    pdf.cell(12, 8, "Qty.", border=1, align='C')
    pdf.cell(22, 8, "Gross Amt", border=1, align='C')
    pdf.cell(16, 8, "Discount", border=1, align='C')
    pdf.cell(25, 8, "Taxable Value", border=1, align='C')
    pdf.cell(32, 8, "Taxes", border=1, align='C')
    pdf.cell(23, 8, "Total", border=1, align='C', ln=True)
    pdf.set_font("Arial", '', 8)
    total_tax = 0.0
    total_taxable = 0.0
    for idx, item in enumerate(cart_items, 1):
        qty = item.get('quantity', 1)
        price_per_kg = item['price_per_kg']
        gross = price_per_kg * qty
        taxable = gross / 1.05
        tax = gross - taxable
        total_tax += tax
        total_taxable += taxable
        pdf.cell(8, 8, str(idx), border=1, align='C')
        seller = item.get('seller_name', 'Verified Farmer')
        desc = f"{item['crop_category']} ({seller})"
        pdf.cell(52, 8, desc[:35], border=1) 
        pdf.cell(12, 8, str(qty), border=1, align='C')
        pdf.cell(22, 8, f"Rs.{gross:.2f}", border=1, align='R')
        pdf.cell(16, 8, "Rs.0.00", border=1, align='R')
        pdf.cell(25, 8, f"Rs.{taxable:.2f}", border=1, align='R')
        pdf.cell(32, 8, f"IGST @5%: Rs.{tax:.2f}", border=1, align='L')
        pdf.cell(23, 8, f"Rs.{gross:.2f}", border=1, align='R', ln=True)
    pdf.set_font("Arial", 'B', 8)
    pdf.cell(135, 8, "Total", border=1, align='R')
    pdf.cell(32, 8, f"Rs.{total_tax:.2f}", border=1, align='L')
    pdf.cell(23, 8, f"Rs.{total_price:.2f}", border=1, align='R', ln=True)
    pdf.ln(10)
    pdf.set_font("Arial", 'B', 9)
    pdf.cell(0, 5, "Terms & Conditions:", ln=True)
    pdf.set_font("Arial", '', 8)
    pdf.multi_cell(0, 4, "Sold by: Multiple Verified Sellers via AgriChain Marketplace\nTax is not payable on reverse charge basis.\nThis is a computer generated invoice and does not require signature.")
    return bytes(pdf.output(dest='S'))

CROP_IMAGES = {
    "Tomatoes": "https://images.pexels.com/photos/533280/pexels-photo-533280.jpeg?auto=compress&cs=tinysrgb&w=500",
    "Onions": "https://images.pexels.com/photos/4197439/pexels-photo-4197439.jpeg?auto=compress&cs=tinysrgb&w=500",
    "Potatoes": "https://images.pexels.com/photos/144248/potatoes-vegetables-erdfrucht-bio-144248.jpeg?auto=compress&cs=tinysrgb&w=500",
    "Apples": "https://images.pexels.com/photos/206959/pexels-photo-206959.jpeg?auto=compress&cs=tinysrgb&w=500",
    "Default": "https://images.pexels.com/photos/1367243/pexels-photo-1367243.jpeg?auto=compress&cs=tinysrgb&w=500"
}

def get_marketplace_items():
    headers = {"Authorization": f"Bearer {st.session_state.get('token', '')}"}
    try:
        response = requests.get(f"http://127.0.0.1:8000/api/market_listings", headers=headers)
        if response.status_code == 200:
            return response.json().get("listings", [])
        return []
    except Exception as e:
        return []

def fetch_user_orders(username):
    headers = {"Authorization": f"Bearer {st.session_state.get('token', '')}"}
    try:
        response = requests.get(f"http://127.0.0.1:8000/api/orders/{username}", headers=headers)
        if response.status_code == 200:
            return response.json().get("orders", [])
        return []
    except Exception as e:
        return []
        
def fetch_recommendations(username):
    headers = {"Authorization": f"Bearer {st.session_state.get('token', '')}"}
    try:
        response = requests.get(f"http://127.0.0.1:8000/api/recommendations/{username}", headers=headers)
        if response.status_code == 200:
            return response.json().get("recommendations", [])
        return []
    except:
        return []
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
def consumer_storefront():
    st.markdown("""
    <style>
    .stApp { background-color: #f4f6f8 !important; }
    [data-testid="stSidebar"] { background-color: #ffffff !important; box-shadow: 2px 0px 10px rgba(0,0,0,0.05); }
    [data-testid="stSidebar"] .st-emotion-cache-1wmy9hl { gap: 0rem !important; }
    [data-testid="stImage"] img { height: 140px !important; width: 100% !important; object-fit: cover !important; border-radius: 6px !important; }
    [data-testid="stVerticalBlockBorderWrapper"] { border: 1px solid #f0f0f0 !important; border-radius: 8px !important; transition: box-shadow 0.2s ease-in-out !important; background-color: white !important; padding: 10px !important; }
    [data-testid="stVerticalBlockBorderWrapper"]:hover { box-shadow: 0px 4px 15px rgba(0, 0, 0, 0.1) !important; border: 1px solid #e0e0e0 !important; }
    .stButton > button { background-color: #ff9f00 !important; color: white !important; border: none !important; font-weight: bold !important; border-radius: 4px !important; padding: 4px 10px !important; }
    .stButton > button:hover { background-color: #f39c12 !important; box-shadow: 0px 2px 5px rgba(0,0,0,0.2) !important; }
    </style>
    """, unsafe_allow_html=True)

    if 'cart' not in st.session_state:
        st.session_state.cart = []
    all_items = get_marketplace_items()
    latest_item = all_items[-1]['crop_category'] if all_items else "New Harvest"
    user_orders = fetch_user_orders(st.session_state.username)
    has_active_order = len(user_orders) > 0
    otp_code = "8421"
    header_left, header_empty, header_right = st.columns([6, 1, 1.5])
    
    with header_left:
        st.title("🛒 AgriChain Marketplace")
        st.markdown("Fresh produce directly from verified farmers.")
        
    with header_right:
        st.markdown("<br>", unsafe_allow_html=True) 
        notifications = fetch_notifications("consumer", st.session_state.username)
        unread_count = len([n for n in notifications if not n.get('is_read')])
        
        with st.popover(f"🔔 ({unread_count})"):
            if not notifications:
                st.info("No new notifications right now.")
            else:
                for note in notifications:
                    bg_color = "success" if not note.get('is_read') else "info"
                    
                    if bg_color == "success":
                        st.success(f"**{note.get('title', 'Alert')}**\n\n{note.get('message', '')}")
                    else:
                        st.info(f"**{note.get('title', 'Alert')}**\n\n{note.get('message', '')}")
    tab1, tab2 = st.tabs(["🛍️ Shop Marketplace", "📦 My Orders & AI Picks"])

    with tab1:
        with st.sidebar:
            st.sidebar.title("🛒 Consumer Dashboard")
            user_name = st.session_state.username.split('@')[0].capitalize() if st.session_state.username else "Guest"
            st.markdown(f"### 👋 Welcome, {user_name}!")
            st.markdown("<hr style='margin: 10px 0px; padding: 0;'>", unsafe_allow_html=True)
            st.markdown("### 🔍 Filter Products") 
            search_query = st.text_input("Search for crops", placeholder="e.g. Tomato")
            st.markdown("<hr style='margin: 10px 0px; padding: 0;'>", unsafe_allow_html=True)
            price_range = st.slider("Price Range (₹/kg)", 0, 500, (0, 500)) 
            st.markdown("<hr style='margin: 10px 0px; padding: 0;'>", unsafe_allow_html=True)
            sort_by = st.selectbox("Sort By", ["Newest First", "Price: Low to High", "Price: High to Low"])
            st.markdown("<hr style='margin: 10px 0px; padding: 0;'>", unsafe_allow_html=True)
            st.markdown("### 🛍️ Your Cart")
            if not st.session_state.cart:
                st.info("Your cart is empty.")
            else:
                st.success(f"Items in cart: **{len(st.session_state.cart)}**")
                
                # Update Cart Estimate to show rounded number
                raw_est = sum(item['price_per_kg'] * item.get('quantity', 1) for item in st.session_state.cart)
                total_est = round(raw_est)
                st.write(f"Estimated Total: **₹{total_est}.00**")
                
                if st.button("Clear Cart", use_container_width=True):
                    st.session_state.cart = []
                    st.rerun()
                if st.button("Go to Checkout ➔", type="primary", use_container_width=True):
                    st.session_state.auth_step = "checkout" 
                    st.rerun()
            
            st.markdown("<hr style='margin: 10px 0px; padding: 0;'>", unsafe_allow_html=True)
            if st.button("🚪 Log Out", use_container_width=True):
                st.session_state.clear()
                st.rerun()

        all_crops = get_marketplace_items()
        filtered_crops = [crop for crop in all_crops if search_query.lower() in crop['crop_category'].lower() and price_range[0] <= crop['price_per_kg'] <= price_range[1]]

        if sort_by == "Price: Low to High":
            filtered_crops.sort(key=lambda x: x['price_per_kg'])
        elif sort_by == "Price: High to Low":
            filtered_crops.sort(key=lambda x: x['price_per_kg'], reverse=True)
        elif sort_by == "Newest First":
            filtered_crops.reverse()

        if not filtered_crops:
            st.warning("No crops found matching your search criteria.")
        else:
            cols = st.columns(4) 
            for i, crop in enumerate(filtered_crops):
                with cols[i % 4]: 
                    with st.container(border=True):
                        if crop.get('image_data'):
                            try:
                                img_bytes = base64.b64decode(crop['image_data'])
                                st.image(img_bytes, use_container_width=True)
                            except:
                                st.image(CROP_IMAGES.get(crop['crop_category'], CROP_IMAGES["Default"]), use_container_width=True)
                        else:
                            st.image(CROP_IMAGES.get(crop['crop_category'], CROP_IMAGES["Default"]), use_container_width=True)
                        
                        seller_name = crop.get('seller_name', 'Verified Farmer')
                        original_price = crop.get('original_price_per_kg')
                        current_price = crop['price_per_kg']
                        
                        if original_price and original_price > current_price:
                            discount_pct = int(((original_price - current_price) / original_price) * 100)
                            price_display = f'<div style="font-size: 13px; color: #e74c3c; text-decoration: line-through; margin-bottom: -2px;">₹{original_price:.2f}</div><div style="font-size: 18px; font-weight: bold; margin-bottom: 2px;">₹{current_price:.2f}<span style="font-size:12px; font-weight:normal; color:gray;">/kg</span> <span style="color: #2e7d32; font-size: 14px; font-weight: 800; background-color: #e8f5e9; padding: 2px 6px; border-radius: 4px; margin-left: 5px;">{discount_pct}% OFF</span></div>'
                        else:
                            price_display = f'<div style="font-size: 18px; font-weight: bold; margin-bottom: 2px; margin-top: 15px;">₹{current_price:.2f}<span style="font-size:12px; font-weight:normal; color:gray;">/kg</span></div>'
                        
                        st.markdown(f'<div style="line-height: 1.2; margin-top: -10px;"><div style="font-size: 16px; font-weight: bold; margin-bottom: 4px;">{crop["crop_category"]}</div><div style="font-size: 11px; color: gray; white-space: nowrap; overflow: hidden; text-overflow: ellipsis; margin-bottom: 4px;">📍 {seller_name}</div>{price_display}</div>', unsafe_allow_html=True)
                        
                        selected_qty = st.number_input("Qty (kg)", min_value=0.5, max_value=100.0, value=1.0, step=0.5, key=f"qty_main_{i}")
                        
                        if st.button(f"🛒 Add to Cart", key=f"btn_{i}", use_container_width=True):
                            cart_item = crop.copy()
                            cart_item['quantity'] = selected_qty
                            st.session_state.cart.append(cart_item)
                            st.toast(f"Added {selected_qty}kg of {crop['crop_category']} to cart!", icon="✅")
                            st.rerun()

    with tab2:
        st.header("🤖 Personalized Recommendations")
        recs = fetch_recommendations(st.session_state.username)
        if not recs:
            st.info("Make your first purchase to get AI recommendations!")
        else:
            rec_cols = st.columns(len(recs) if 0 < len(recs) < 4 else 4)
            for i, crop in enumerate(recs[:4]):
                with rec_cols[i % 4]:
                    with st.container(border=True):
                        st.image(CROP_IMAGES.get(crop['crop_category'], CROP_IMAGES["Default"]), use_container_width=True)
                        st.markdown(f"**{crop['crop_category']}**")
                        st.markdown(f"₹{crop['price_per_kg']}/kg")
                        
                        rec_qty = st.number_input("Qty (kg)", min_value=0.5, max_value=100.0, value=1.0, step=0.5, key=f"qty_rec_{i}")
                        if st.button("🛒 Add", key=f"rec_btn_{i}", use_container_width=True):
                            cart_item = crop.copy()
                            cart_item['quantity'] = rec_qty
                            st.session_state.cart.append(cart_item)
                            st.toast(f"Added {rec_qty}kg to cart!", icon="✅")
                            st.rerun()

        st.divider()
        st.header("📦 My Order History")
        orders = fetch_user_orders(st.session_state.username)
        if not orders:
            st.warning("You haven't placed any orders yet.")
        else:
            for order in orders:
                with st.container(border=True):
                    st.markdown(f"**Order placed on:** {order.get('order_date', 'N/A')}")
                    st.markdown(f"**Status:** {order.get('status', 'Processing')} | **Total:** ₹{order.get('total_price', 0):.2f}")
                    items_str = ", ".join([f"{item.get('quantity', 1)}kg {item['crop_category']}" for item in order.get('items', [])])
                    st.caption(f"Items: {items_str}")
def consumer_checkout():
    st.title("💳 Secure Checkout")
    
    if 'cart' not in st.session_state or not st.session_state.cart:
        st.warning("Your cart is empty!")
        if st.button("← Back to Shop"):
            st.session_state.auth_step = "marketplace" 
            st.rerun()
        return

    col1, col2 = st.columns([2, 1])
    with col2:
        with st.container(border=True):
            st.subheader("🛒 Order Summary")
            raw_total = sum(item['price_per_kg'] * item.get('quantity', 1) for item in st.session_state.cart)
            
            for item in st.session_state.cart:
                qty = item.get('quantity', 1)
                item_total = item['price_per_kg'] * qty
                st.write(f"• {qty}kg {item['crop_category']} - **₹{item_total:.2f}**")
                st.caption(f"Sold by: {item.get('seller_name', 'Verified Farmer')}")
                
            st.divider()
            st.markdown(f"### Total Payable: ₹{raw_total:.2f}")
            st.caption("(Note: Cash on Delivery orders will be rounded to the nearest Rupee)")
    with col1:
        with st.container(border=True):
            st.subheader("📍 Shipping Details")
            address = st.text_area("Delivery Address", placeholder="Enter your full address...")
            delivery_days = 3
            est_date = datetime.datetime.now() + datetime.timedelta(days=delivery_days)
            st.success(f"🚚 **Estimated Delivery:** {est_date.strftime('%d %b %Y')} (in {delivery_days} days)")
            payment_method = st.radio("Payment Method", ["Cash on Delivery", "UPI", "Credit/Debit Card"])
            
            upi_id = ""
            
            if payment_method == "UPI":
                with st.container(border=True):
                    st.info("📲 Pay using GPay, PhonePe, or Paytm.")
                    upi_id = st.text_input("Enter your UPI ID", placeholder="e.g. username@okhdfcbank")
            elif payment_method == "Credit/Debit Card":
                with st.container(border=True):
                    st.info("💳 Enter your card details securely.")
                    st.text_input("Card Number", placeholder="XXXX XXXX XXXX XXXX", max_chars=19)
                    c1, c2 = st.columns(2)
                    c1.text_input("Expiry Date", placeholder="MM/YY", max_chars=5)
                    c2.text_input("CVV", type="password", placeholder="•••", max_chars=3)
            
            st.markdown("<br>", unsafe_allow_html=True)
            
            btn_text = " Pay & Place Order" if payment_method != "Cash on Delivery" else "✅ Place Order (COD)"
            valid_upi_handles = [
                "ybl", "ibl", "axl", "paytm", "okaxis", "okhdfcbank", 
                "okicici", "oksbi", "sbi", "icici", "kotak", "amazonpay", 
                "apl", "upi", "idfcbank", "postbank", "freecharge"
            ]
            
            if st.button(btn_text, type="primary", use_container_width=True):
                if not address:
                    st.error("Please enter a delivery address.")
                
                elif payment_method == "UPI" and (not upi_id or "@" not in upi_id):
                    st.error("Please enter a valid UPI ID format (e.g., name@bank).")
                
                elif payment_method == "UPI" and upi_id.split("@")[-1].lower() not in valid_upi_handles:
                    invalid_handle = upi_id.split("@")[-1]
                    st.error(f" Invalid or unsupported UPI provider '(@{invalid_handle})'. Please use a verified handle like @ybl, @ibl, or @paytm.")
                
                else:
                    if payment_method == "UPI":
                        status_container = st.empty()
                        progress_bar = st.progress(0)
                        status_container.warning(f"📲 Verifying UPI ID securely...")
                        for percent_complete in range(100):
                            time.sleep(0.01) 
                            progress_bar.progress(percent_complete + 1)
                        status_container.empty()
                        progress_bar.empty()
                    
                    items_payload = []
                    for item in st.session_state.cart:
                        items_payload.append({
                            "crop_category": item['crop_category'],
                            "seller_name": item.get('seller_name', 'Unknown'),
                            "price_per_kg": item['price_per_kg'],
                            "quantity": item.get('quantity', 1) 
                        })
                    final_amount = round(raw_total) if payment_method == "Cash on Delivery" else raw_total
                    
                    payload = {
                        "consumer_username": st.session_state.username,
                        "items": items_payload,
                        "total_price": final_amount, 
                        "delivery_address": address,
                        "payment_method": payment_method
                    }
                    
                    try:
                        with st.spinner("Processing your order & connecting to gateway..."):
                            headers = {"Authorization": f"Bearer {st.session_state.get('token', '')}"}
                            response = requests.post("http://127.0.0.1:8000/api/checkout", json=payload, headers=headers)
                            
                        if response.status_code == 200:
                            res_data = response.json()
                            order_id = res_data.get("order_id", "ORD-1234")
                            payment_url = res_data.get("payment_url") 
                            
                            pdf_bytes = create_invoice_pdf(order_id, st.session_state.cart, final_amount, address)
                            st.download_button(
                                label="📄 Download Your Invoice (PDF)",
                                data=pdf_bytes,
                                file_name=f"Invoice_{order_id}.pdf",
                                mime="application/pdf"
                            )
                            
                            st.session_state.cart = [] 
                            
                            if payment_url:
                                st.success("Order recorded! Redirecting to secure payment gateway...")
                                st.markdown(f'<meta http-equiv="refresh" content="1.5;url={payment_url}">', unsafe_allow_html=True)
                            else:
                                st.success("Order recorded successfully! Your harvest is on the way.")
                                
                        else:
                            st.error(f"Backend rejected the order. Server says: {response.text}")
                    except Exception as e:
                        st.error(f"Backend offline. Could not complete checkout. Error: {e}")
            
            st.write("")
            if st.button("← Back to Marketplace"):
                st.session_state.auth_step = "marketplace" 
                st.rerun()