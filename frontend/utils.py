import streamlit as st

def update_qty(key, delta, max_val):
    new_val = st.session_state.get(key, 1) + delta
    if 1 <= new_val <= max_val:
        st.session_state[key] = new_val

def add_to_cart(item, qty_key):
    selected_qty = st.session_state[qty_key]
    item_exists = False
    for cart_item in st.session_state.cart:
        if cart_item['crop_category'] == item['crop_category'] and cart_item['seller_name'] == item['seller_name']:
            cart_item['quantity'] += selected_qty
            item_exists = True
            break
            
    if not item_exists:
        new_item = item.copy()
        new_item['quantity'] = selected_qty
        st.session_state.cart.append(new_item)
        
    st.toast(f"Added {selected_qty}kg of {item['crop_category']} to your cart! 🛒", icon="✅") 
    st.session_state[qty_key] = 1