"""
Sandwich Order System - Streamlit Web App
A user-friendly interface for ordering custom sandwiches with order history
"""

import streamlit as st
import sys
import os
import importlib.util
from datetime import datetime
from pathlib import Path

# Add OOP_copy to path so we can import our classes
current_dir = os.path.dirname(os.path.abspath(__file__))
oop_path = os.path.join(current_dir, 'OOP_copy')

# Dynamically import menu.py
menu_spec = importlib.util.spec_from_file_location("menu", os.path.join(oop_path, "menu.py"))
menu_module = importlib.util.module_from_spec(menu_spec)
menu_spec.loader.exec_module(menu_module)
Menu = menu_module.Menu

# Dynamically import sandwich_order.py
sandwich_spec = importlib.util.spec_from_file_location("sandwich_order", os.path.join(oop_path, "sandwich_order.py"))
sandwich_module = importlib.util.module_from_spec(sandwich_spec)
sandwich_spec.loader.exec_module(sandwich_module)
SandwichOrder = sandwich_module.SandwichOrder

# File paths
MENU_PATH = os.path.join(current_dir, 'OOP_copy', 'menu.txt')
HISTORY_PATH = os.path.join(current_dir, 'OOP_copy', 'order_history.txt')

# ===== PAGE CONFIG =====
st.set_page_config(
    page_title="Sandwich Order System",
    page_icon="🥪",
    layout="wide",
    initial_sidebar_state="expanded"
)

st.title("🥪 Sandwich Order System")

# ===== INITIALIZE SESSION STATE =====
if 'customer_name' not in st.session_state:
    st.session_state.customer_name = ""
if 'customer_phone' not in st.session_state:
    st.session_state.customer_phone = ""
if 'session_orders' not in st.session_state:
    st.session_state.session_orders = []
if 'menu' not in st.session_state:
    st.session_state.menu = Menu(MENU_PATH)
if 'sizes_prices' not in st.session_state:
    # Extract size-to-price mapping
    sizes = st.session_state.menu.get_category("SIZES")
    prices = st.session_state.menu.get_category("PRICES")
    st.session_state.sizes_prices = dict(zip(sizes, prices)) if sizes and prices else {}
if 'current_page' not in st.session_state:
    st.session_state.current_page = "customer_info"
if 'order_confirmation' not in st.session_state:
    st.session_state.order_confirmation = None

# ===== HELPER FUNCTIONS =====
def load_order_history():
    """Load all past orders from file."""
    if not os.path.exists(HISTORY_PATH):
        return []
    
    orders = []
    current_order = {}
    
    try:
        with open(HISTORY_PATH, 'r') as f:
            for line in f:
                line = line.strip()
                if line.startswith("="):
                    if current_order:
                        orders.append(current_order)
                    current_order = {}
                elif ": " in line:
                    key, value = line.split(": ", 1)
                    current_order[key] = value
            if current_order:
                orders.append(current_order)
    except Exception as e:
        st.error(f"Error reading order history: {e}")
    
    return orders

def calculate_session_total():
    """Calculate total price of all orders in session."""
    return sum(order.get_price() for order in st.session_state.session_orders)

def save_orders_to_file(customer_name, customer_phone):
    """Save all session orders to file."""
    for order in st.session_state.session_orders:
        order.save_to_file(HISTORY_PATH, customer_name, customer_phone)

# ===== PAGE 1: CUSTOMER INFORMATION =====
def page_customer_info():
    st.header("📋 Customer Information")
    
    col1, col2 = st.columns(2)
    
    with col1:
        fname = st.text_input(
            "First Name",
            value=st.session_state.customer_name.split()[0] if st.session_state.customer_name else "",
            key="fname_input"
        )
    
    with col2:
        lname = st.text_input(
            "Last Name",
            value=st.session_state.customer_name.split()[1] if len(st.session_state.customer_name.split()) > 1 else "",
            key="lname_input"
        )
    
    phone = st.text_input(
        "Phone Number",
        value=st.session_state.customer_phone,
        key="phone_input"
    )
    
    if st.button("✓ Continue to Ordering", type="primary", use_container_width=True):
        if fname.strip() and lname.strip() and phone.strip():
            st.session_state.customer_name = f"{fname.strip().title()} {lname.strip().title()}"
            st.session_state.customer_phone = phone.strip()
            st.session_state.current_page = "place_order"
            st.rerun()
        else:
            st.error("Please fill in all fields")

# ===== PAGE 2: PLACE ORDER =====
def page_place_order():
    st.header("🥖 Build Your Sandwich")
    
    col1, col2 = st.columns([3, 1])
    
    with col1:
        st.write(f"**Customer:** {st.session_state.customer_name}")
    with col2:
        if st.button("← Back"):
            st.session_state.current_page = "customer_info"
            st.rerun()
    
    # Create new sandwich order
    st.subheader("Customize Your Sandwich")
    
    # Size selection
    sizes = st.session_state.menu.get_category("SIZES")
    selected_size = st.selectbox("Select Size", sizes, key="size_select")
    
    # Bread selection (multi-select)
    breads = st.session_state.menu.get_category("BREAD")
    selected_breads = st.multiselect("Select Bread", breads, max_selections=1, key="bread_select")
    
    # Protein selection (multi-select)
    proteins = st.session_state.menu.get_category("PROTEIN")
    selected_proteins = st.multiselect("Select Protein", proteins, max_selections=1, key="protein_select")
    
    # Cheese selection (multi-select)
    cheeses = st.session_state.menu.get_category("CHEESE")
    selected_cheeses = st.multiselect("Select Cheese", cheeses, max_selections=1, key="cheese_select")
    
    # Toppings selection (multi-select - can select multiple)
    toppings = st.session_state.menu.get_category("TOPPINGS")
    selected_toppings = st.multiselect("Select Toppings", toppings, key="toppings_select")
    
    # Validate toppings: cannot select "None" with other options
    if selected_toppings and "None" in selected_toppings and len(selected_toppings) > 1:
        st.warning("⚠️ Cannot select 'None' with other toppings. Please choose either 'None' or specific toppings.")
        selected_toppings = [t for t in selected_toppings if t != "None"]
        # Force the state to update
        st.session_state.toppings_select = selected_toppings
    
    # Sauce selection (multi-select)
    sauces = st.session_state.menu.get_category("SAUCES")
    selected_sauces = st.multiselect("Select Sauce", sauces, max_selections=1, key="sauce_select")
    
    # Order preview
    st.divider()
    st.subheader("📦 Order Preview")
    
    if (selected_size and selected_breads and selected_proteins and 
        selected_cheeses and selected_toppings and selected_sauces):
        
        # Create order object
        order = SandwichOrder()
        order.set_size(selected_size)
        order.set_bread(selected_breads[0])
        order.set_protein(selected_proteins[0])
        order.set_cheese(selected_cheeses[0])
        order.set_topping(", ".join(selected_toppings))
        order.set_sauce(selected_sauces[0])
        order.calculate_total(st.session_state.sizes_prices)
        
        # Display preview
        col1, col2 = st.columns([2, 1])
        
        with col1:
            st.write(f"**Size:** {order.get_size()}")
            st.write(f"**Bread:** {order.get_bread()}")
            st.write(f"**Protein:** {order.get_protein()}")
            st.write(f"**Cheese:** {order.get_cheese()}")
            st.write(f"**Toppings:** {order.get_topping()}")
            st.write(f"**Sauce:** {order.get_sauce()}")
        
        with col2:
            st.metric("Price", f"${order.get_price():.2f}")
        
        # Add to cart button
        if st.button("➕ Add to Cart", type="primary", use_container_width=True):
            st.session_state.session_orders.append(order)
            st.session_state.order_confirmation = f"✓ Added {order.get_size()} sandwich to cart!"
            st.success("Order added to cart!")
            st.rerun()
    else:
        st.info("Please select all sandwich components")
    
    # Navigation buttons
    st.divider()
    col1, col2, col3 = st.columns(3)
    
    with col1:
        if st.button("← Back", use_container_width=True):
            st.session_state.current_page = "customer_info"
            st.rerun()
    
    with col2:
        if st.session_state.session_orders:
            if st.button("🛒 View Cart", type="secondary", use_container_width=True):
                st.session_state.current_page = "manage_orders"
                st.rerun()
    
    with col3:
        if st.button("✓ Checkout", type="secondary", use_container_width=True):
            if st.session_state.session_orders:
                st.session_state.current_page = "checkout"
                st.rerun()
            else:
                st.error("Add items to cart before checkout!")

# ===== PAGE 3: MANAGE ORDERS =====
def page_manage_orders():
    st.header("🛒 Your Cart")
    
    col1, col2, col3 = st.columns([2, 1, 1])
    
    with col1:
        st.write(f"**Customer:** {st.session_state.customer_name}")
    with col2:
        if st.button("➕ Add More"):
            st.session_state.current_page = "place_order"
            st.rerun()
    with col3:
        if st.button("← Back"):
            st.session_state.current_page = "place_order"
            st.rerun()
    
    if not st.session_state.session_orders:
        st.info("Your cart is empty. Add some sandwiches!")
        return
    
    # Display cart items
    st.subheader("📋 Current Orders")
    
    for idx, order in enumerate(st.session_state.session_orders, 1):
        with st.container(border=True):
            col1, col2, col3 = st.columns([3, 1, 1])
            
            with col1:
                st.write(f"**Order #{idx}:** {order.display_summary()}")
            
            with col2:
                st.metric("Price", f"${order.get_price():.2f}")
            
            with col3:
                if st.button("🗑️ Delete", key=f"delete_{idx}"):
                    st.session_state.session_orders.pop(idx - 1)
                    st.rerun()
    
    # Cart total
    st.divider()
    total = calculate_session_total()
    st.metric("🛒 Session Total", f"${total:.2f}")
    
    # Checkout button
    if st.button("✓ Proceed to Checkout", type="primary", use_container_width=True):
        st.session_state.current_page = "checkout"
        st.rerun()

# ===== PAGE 4: CHECKOUT =====
def page_checkout():
    st.header("💳 Checkout")
    
    col1, col2 = st.columns([3, 1])
    
    with col1:
        st.write(f"**Customer:** {st.session_state.customer_name}")
        st.write(f"**Phone:** {st.session_state.customer_phone}")
    with col2:
        if st.button("← Back"):
            st.session_state.current_page = "manage_orders"
            st.rerun()
    
    st.divider()
    st.subheader("📦 Final Receipt")
    
    # Display all orders
    total = 0.0
    for idx, order in enumerate(st.session_state.session_orders, 1):
        with st.container(border=True):
            st.write(f"**Sandwich #{idx}**")
            col1, col2 = st.columns([3, 1])
            
            with col1:
                st.write(f"Size: {order.get_size()}")
                st.write(f"Bread: {order.get_bread()}")
                st.write(f"Protein: {order.get_protein()}")
                st.write(f"Cheese: {order.get_cheese()}")
                st.write(f"Toppings: {order.get_topping()}")
                st.write(f"Sauce: {order.get_sauce()}")
            
            with col2:
                st.metric("Price", f"${order.get_price():.2f}")
            
            total += order.get_price()
    
    st.divider()
    st.metric("💰 Total", f"${total:.2f}", delta=None)
    
    # Confirm order button
    if st.button("✓ Confirm Order", type="primary", use_container_width=True):
        save_orders_to_file(st.session_state.customer_name, st.session_state.customer_phone)
        st.success("✓ Order confirmed and saved!")
        st.balloons()
        
        # Reset session
        st.session_state.session_orders = []
        st.session_state.customer_name = ""
        st.session_state.customer_phone = ""
        st.session_state.current_page = "customer_info"
        
        st.info("Thank you for your order! Starting new session...")
        st.rerun()

# ===== SIDEBAR: PAST ORDERS & NAVIGATION =====
with st.sidebar:
    st.header("📜 Past Orders")
    
    history = load_order_history()
    
    if history:
        with st.expander(f"View {len(history)} past orders"):
            for idx, order in enumerate(history, 1):
                st.write(f"**Order #{idx}**")
                for key, value in order.items():
                    st.write(f"{key}: {value}")
                st.divider()
    else:
        st.info("No past orders yet")
    
    st.divider()
    st.write("**Current Session**")
    if st.session_state.session_orders:
        st.metric("Orders in Cart", len(st.session_state.session_orders))
        st.metric("Session Total", f"${calculate_session_total():.2f}")

# ===== MAIN APP NAVIGATION =====
if st.session_state.current_page == "customer_info":
    page_customer_info()
elif st.session_state.current_page == "place_order":
    page_place_order()
elif st.session_state.current_page == "manage_orders":
    page_manage_orders()
elif st.session_state.current_page == "checkout":
    page_checkout()
