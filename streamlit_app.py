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

# ===== ACCESSIBILITY IMPROVEMENTS =====
st.markdown("""
<style>
    /* Increase button size for accessibility */
    button {
        min-width: 50px !important;
        min-height: 44px !important;
        font-size: 16px !important;
    }
    
    /* Improve contrast and clarity */
    .stSelectbox, .stMultiSelect, .stTextInput {
        font-size: 16px !important;
    }
    
    /* Better focus indicators for keyboard navigation */
    button:focus {
        outline: 3px solid #FF4B4B !important;
        outline-offset: 2px !important;
    }
    
    /* Improve selected item visibility */
    .stMultiSelect [data-baseweb="select"] {
        border: 2px solid #1f77b4 !important;
    }
</style>
""", unsafe_allow_html=True)

# ===== INITIALIZE SESSION STATE =====
if 'customer_name' not in st.session_state:
    st.session_state.customer_name = ""
if 'customer_phone' not in st.session_state:
    st.session_state.customer_phone = ""
if 'session_orders' not in st.session_state:
    # Each item is a dict: {"order": SandwichOrder, "meta": {"special_instructions": str}}
    st.session_state.session_orders = []
if 'favorite_sandwiches' not in st.session_state:
    st.session_state.favorite_sandwiches = {}
if 'general_notes' not in st.session_state:
    st.session_state.general_notes = ""
if 'FAVS_PATH' not in st.session_state:
    st.session_state.FAVS_PATH = os.path.join(current_dir, 'OOP_copy', 'favorites.json')
    # Load persisted favorites if available
    try:
        import json
        if os.path.exists(st.session_state.FAVS_PATH):
            with open(st.session_state.FAVS_PATH, 'r') as f:
                st.session_state.favorite_sandwiches = json.load(f)
    except Exception:
        st.session_state.favorite_sandwiches = {}
if 'reorder_sandwich' not in st.session_state:
    # Stores sandwich data when user clicks reorder; separate from widget keys
    st.session_state.reorder_sandwich = None
if 'menu_mode' not in st.session_state:
    st.session_state.menu_mode = "Basic"
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
    total = 0.0
    for item in st.session_state.session_orders:
        if isinstance(item, dict):
            total += item['order'].get_price()
        else:
            # Fallback for old SandwichOrder objects (backward compat)
            total += item.get_price()
    return total

def save_orders_to_file(customer_name, customer_phone):
    """Save all session orders to file with metadata and notes."""
    import json
    try:
        with open(HISTORY_PATH, 'a') as f:
            f.write('=' * 50 + '\n')
            f.write(f'Date: {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}\n')
            f.write(f'Customer: {customer_name}\n')
            f.write(f'Phone: {customer_phone}\n')
            # Write items with special instructions
            for idx, item in enumerate(st.session_state.session_orders, 1):
                if isinstance(item, dict):
                    order = item['order']
                    meta = item.get('meta', {})
                else:
                    # Backward compat for old SandwichOrder objects
                    order = item
                    meta = {}
                f.write(f'Item {idx}: {order.display_summary()}\n')
                if meta.get('special_instructions'):
                    f.write(f'  Special Instructions: {meta.get("special_instructions")}\n')
            # General order notes
            if st.session_state.get('general_notes', '').strip():
                f.write(f'General Notes: {st.session_state.get("general_notes")}\n')
            f.write(f'Total: ${calculate_session_total():.2f}\n')
            f.write('=' * 50 + '\n\n')
        return True
    except Exception as e:
        st.error(f'Error saving order: {e}')
        return False

def save_favorite(sandwich_name, sandwich_dict):
    """Save a sandwich to favorites and persist to disk."""
    st.session_state.favorite_sandwiches[sandwich_name] = sandwich_dict
    # Persist favorites to disk
    try:
        import json
        with open(st.session_state.FAVS_PATH, 'w') as f:
            json.dump(st.session_state.favorite_sandwiches, f, indent=2)
    except Exception as e:
        st.warning(f'Could not save favorites: {e}')

def load_favorite(sandwich_name):
    """Load a favorite sandwich."""
    return st.session_state.favorite_sandwiches.get(sandwich_name, None)

def get_basic_menu_items(category):
    """Get simplified basic menu items."""
    basic_menus = {
        "SIZES": ["6 inch", "12 inch"],
        "BREAD": ["White", "Wheat"],
        "PROTEIN": ["Turkey", "Ham", "Chicken"],
        "CHEESE": ["American", "Cheddar"],
        "TOPPINGS": ["Lettuce", "Tomato", "Onion"],
        "SAUCES": ["Mayo", "Mustard"],
    }
    return basic_menus.get(category, st.session_state.menu.get_category(category))

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
    
    col1, col2, col3 = st.columns([2, 1, 1])
    
    with col1:
        st.write(f"**Customer:** {st.session_state.customer_name}")
    with col2:
        # Menu mode toggle (Improvement #3: Simplify menu)
        st.session_state.menu_mode = st.selectbox(
            "Menu Mode",
            ["Basic", "Full"],
            index=0 if st.session_state.menu_mode == "Basic" else 1,
            key="menu_mode_select",
            help="Basic: Essential options | Full: All options"
        )
    with col3:
        if st.button("← Back", help="Return to customer information"):
            st.session_state.current_page = "customer_info"
            st.session_state.reorder_sandwich = None  # Clear reorder state
            st.rerun()
    
    st.subheader("Customize Your Sandwich")
    
    # Get menu items based on mode (Improvement #3)
    menu_items = {
        "SIZES": st.session_state.menu.get_category("SIZES"),
        "BREAD": get_basic_menu_items("BREAD") if st.session_state.menu_mode == "Basic" else st.session_state.menu.get_category("BREAD"),
        "PROTEIN": get_basic_menu_items("PROTEIN") if st.session_state.menu_mode == "Basic" else st.session_state.menu.get_category("PROTEIN"),
        "CHEESE": get_basic_menu_items("CHEESE") if st.session_state.menu_mode == "Basic" else st.session_state.menu.get_category("CHEESE"),
        "TOPPINGS": get_basic_menu_items("TOPPINGS") if st.session_state.menu_mode == "Basic" else st.session_state.menu.get_category("TOPPINGS"),
        "SAUCES": get_basic_menu_items("SAUCES") if st.session_state.menu_mode == "Basic" else st.session_state.menu.get_category("SAUCES"),
    }
    
    # Load reorder data if user clicked reorder on a favorite
    reorder_data = st.session_state.reorder_sandwich
    
    # Size selection
    selected_size = st.selectbox(
        "Select Size",
        menu_items["SIZES"],
        index=menu_items["SIZES"].index(reorder_data['size']) if reorder_data and reorder_data.get('size') in menu_items["SIZES"] else 0,
        key="size_select",
        help="Choose sandwich size"
    )
    
    # Bread selection
    selected_breads = st.multiselect(
        "Select Bread [Select 1]",
        menu_items["BREAD"],
        default=[reorder_data['bread']] if reorder_data and reorder_data.get('bread') in menu_items["BREAD"] else [],
        max_selections=1,
        key="bread_select",
        help="Choose one bread type"
    )
    
    # Protein selection
    selected_proteins = st.multiselect(
        "Select Protein [Select 1]",
        menu_items["PROTEIN"],
        default=[reorder_data['protein']] if reorder_data and reorder_data.get('protein') in menu_items["PROTEIN"] else [],
        max_selections=1,
        key="protein_select",
        help="Choose one protein type"
    )
    
    # Cheese selection
    selected_cheeses = st.multiselect(
        "Select Cheese [Select 1]",
        menu_items["CHEESE"],
        default=[reorder_data['cheese']] if reorder_data and reorder_data.get('cheese') in menu_items["CHEESE"] else [],
        max_selections=1,
        key="cheese_select",
        help="Choose one cheese type"
    )
    
    # Toppings selection with validation
    toppings_label = "Select Toppings [Select Multiple]" if st.session_state.menu_mode == "Full" else "Select Toppings"
    
    def validate_toppings():
        """Prevent selecting None with other toppings"""
        current = st.session_state.toppings_select
        if current and "None" in current and len(current) > 1:
            st.session_state.toppings_select = [t for t in current if t != "None"]
            st.warning("⚠️ Cannot select 'None (skip toppings)' with other toppings.")
    
    selected_toppings = st.multiselect(
        toppings_label,
        menu_items["TOPPINGS"],
        default=[t for t in reorder_data.get('toppings', []) if t in menu_items["TOPPINGS"]] if reorder_data else [],
        key="toppings_select",
        on_change=validate_toppings,
        help="Select multiple toppings or 'None' to skip"
    )
    
    # Sauce selection
    selected_sauces = st.multiselect(
        "Select Sauce [Select 1]",
        menu_items["SAUCES"],
        default=[reorder_data['sauce']] if reorder_data and reorder_data.get('sauce') in menu_items["SAUCES"] else [],
        max_selections=1,
        key="sauce_select",
        help="Choose one sauce type"
    )
    
    # Special Instructions (Improvement #5)
    st.divider()
    st.subheader("✏️ Special Instructions (Optional)")
    special_instructions = st.text_area(
        "Any special requests?",
        value=reorder_data.get('special_instructions', '') if reorder_data else '',
        placeholder="E.g., Toast bread lightly, extra mayo, no onion...",
        max_chars=100,
        height=80,
        help="Add up to 100 characters of special instructions"
    )
    
    # Order preview and quantity (Improvements #1 & #5)
    st.divider()
    st.subheader("📦 Order Preview & Quantity")
    
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
        
        # Display preview with quantity (Improvement #1: Quantity Field)
        col1, col2, col3 = st.columns([2, 1, 1])
        
        with col1:
            st.write(f"**Size:** {order.get_size()}")
            st.write(f"**Bread:** {order.get_bread()}")
            st.write(f"**Protein:** {order.get_protein()}")
            st.write(f"**Cheese:** {order.get_cheese()}")
            st.write(f"**Toppings:** {order.get_topping() if order.get_topping() else '(None)'}")
            st.write(f"**Sauce:** {order.get_sauce()}")
            if special_instructions:
                st.write(f"**Special Instructions:** {special_instructions}")
        
        with col2:
            st.metric("Unit Price", f"${order.get_price():.2f}")
        
        with col3:
            # Quantity spinner (Improvement #1)
            quantity = st.number_input(
                "Quantity",
                min_value=1,
                max_value=10,
                value=1,
                step=1,
                key="quantity_input",
                help="Select quantity (1-10)"
            )
            subtotal = order.get_price() * quantity
            st.metric("Subtotal", f"${subtotal:.2f}")
        
        # Save as favorite button (Improvement #4)
        col1, col2, col3 = st.columns(3)
        with col1:
            favorite_name = st.text_input(
                "Save as Favorite (optional)",
                placeholder="E.g., My Regular",
                key="favorite_name",
                help="Name this sandwich for quick reorder"
            )
        
        with col2:
            if st.button("❤️ Save Favorite", help="Save this sandwich to favorites"):
                if favorite_name:
                    save_favorite(favorite_name, {
                        "size": selected_size,
                        "bread": selected_breads[0],
                        "protein": selected_proteins[0],
                        "cheese": selected_cheeses[0],
                        "toppings": selected_toppings,
                        "sauce": selected_sauces[0],
                        "special_instructions": special_instructions
                    })
                    st.success(f"✓ Saved '{favorite_name}' to favorites!")
                else:
                    st.error("Please enter a name for this favorite")
        
        # Add to cart button
        st.divider()
        if st.button("➕ Add to Cart", type="primary", use_container_width=True, help="Add sandwich(es) to your cart"):
            for _ in range(quantity):
                cart_item = {
                    "order": order,
                    "meta": {
                        "special_instructions": special_instructions
                    }
                }
                st.session_state.session_orders.append(cart_item)
            st.session_state.reorder_sandwich = None  # Clear reorder state
            st.success(f"✓ Added {quantity} sandwich(es) to cart!")
            st.rerun()
    else:
        st.info("Please select all sandwich components")
    
    # Navigation buttons
    st.divider()
    col1, col2, col3 = st.columns(3)
    
    with col1:
        if st.button("← Back", use_container_width=True, help="Return to customer info"):
            st.session_state.current_page = "customer_info"
            st.rerun()
    
    with col2:
        if st.session_state.session_orders:
            if st.button("🛒 View Cart", type="secondary", use_container_width=True, help="Review your order"):
                st.session_state.current_page = "manage_orders"
                st.rerun()
    
    with col3:
        if st.button("✓ Checkout", type="secondary", use_container_width=True, help="Proceed to payment"):
            if st.session_state.session_orders:
                st.session_state.current_page = "checkout"
                st.rerun()
            else:
                st.error("Add items to cart before checkout!")
    
    # Favorites section (Improvement #4)
    if st.session_state.favorite_sandwiches:
        st.divider()
        st.subheader("⭐ Your Favorite Sandwiches")
        
        favorite_cols = st.columns(min(3, len(st.session_state.favorite_sandwiches)))
        for idx, (name, sandwich) in enumerate(st.session_state.favorite_sandwiches.items()):
            with favorite_cols[idx % len(favorite_cols)]:
                st.write(f"**{name}**")
                st.write(f"Size: {sandwich['size']}")
                st.write(f"Bread: {sandwich['bread']}")
                
                col1, col2 = st.columns(2)
                with col1:
                    if st.button(f"🔄 Reorder", key=f"reorder_{name}", use_container_width=True, help="Reorder this favorite"):
                        # Store sandwich data in reorder_sandwich (don't set widget keys directly)
                        st.session_state.reorder_sandwich = sandwich
                        st.rerun()
                
                with col2:
                    if st.button(f"🗑️", key=f"delete_fav_{name}", use_container_width=True, help="Delete this favorite"):
                        del st.session_state.favorite_sandwiches[name]
                        # Persist deletion to disk
                        try:
                            import json
                            with open(st.session_state.FAVS_PATH, 'w') as f:
                                json.dump(st.session_state.favorite_sandwiches, f, indent=2)
                        except Exception:
                            pass
                        st.success(f"✓ Deleted '{name}' from favorites")
                        st.rerun()

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
    
    # Display cart items with grouping by sandwich type
    st.subheader("📋 Current Orders")
    
    # Group identical orders
    order_groups = {}
    for idx, item in enumerate(st.session_state.session_orders):
        # Extract order object from dict or use directly if old format
        order = item['order'] if isinstance(item, dict) else item
        meta = item.get('meta', {}) if isinstance(item, dict) else {}
        summary = order.display_summary()
        if summary not in order_groups:
            order_groups[summary] = {'indices': [], 'order': order, 'meta': meta}
        order_groups[summary]['indices'].append(idx)
    
    # Display grouped orders
    for group_num, (summary, group_data) in enumerate(order_groups.items(), 1):
        order = group_data['order']
        indices = group_data['indices']
        meta = group_data['meta']
        quantity = len(indices)
        
        with st.container(border=True):
            col1, col2, col3, col4 = st.columns([2, 1, 1, 1])
            
            with col1:
                st.write(f"**Order #{group_num}:** {summary}")
                # Show special instructions if available
                if meta.get('special_instructions'):
                    st.caption(f"📝 Notes: {meta.get('special_instructions')}")
            
            with col2:
                st.metric("Qty", quantity)
            
            with col3:
                st.metric("Price", f"${order.get_price() * quantity:.2f}")
            
            with col4:
                if st.button("🗑️ Delete", key=f"delete_group_{group_num}"):
                    # Delete all instances of this order
                    for idx in sorted(indices, reverse=True):
                        st.session_state.session_orders.pop(idx)
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
    
    # Group orders for display
    order_groups = {}
    for idx, item in enumerate(st.session_state.session_orders):
        # Extract order object from dict or use directly if old format
        order = item['order'] if isinstance(item, dict) else item
        meta = item.get('meta', {}) if isinstance(item, dict) else {}
        summary = order.display_summary()
        if summary not in order_groups:
            order_groups[summary] = {'indices': [], 'order': order, 'meta': meta}
        order_groups[summary]['indices'].append(idx)
    
    # Display grouped orders
    total = 0.0
    for group_num, (summary, group_data) in enumerate(order_groups.items(), 1):
        order = group_data['order']
        indices = group_data['indices']
        meta = group_data['meta']
        quantity = len(indices)
        subtotal = order.get_price() * quantity
        total += subtotal
        
        with st.container(border=True):
            st.write(f"**Sandwich #{group_num}** (Qty: {quantity})")
            col1, col2 = st.columns([3, 1])
            
            with col1:
                st.write(f"Size: {order.get_size()}")
                st.write(f"Bread: {order.get_bread()}")
                st.write(f"Protein: {order.get_protein()}")
                st.write(f"Cheese: {order.get_cheese()}")
                st.write(f"Toppings: {order.get_topping()}")
                st.write(f"Sauce: {order.get_sauce()}")
                
                # Show special instructions if available
                if meta.get('special_instructions'):
                    st.caption(f"📝 Special Instructions: {meta.get('special_instructions')}")
            
            with col2:
                st.metric("Subtotal", f"${subtotal:.2f}")
    
    # General order notes section
    st.divider()
    st.subheader("📝 Order Notes")
    st.session_state.general_notes = st.text_area(
        "General Order Notes (Optional)",
        value=st.session_state.general_notes,
        placeholder="E.g., Deliver by 2pm, Left side of building, Call upon arrival...",
        max_chars=200,
        help="Add any special delivery or preparation instructions for the entire order"
    )
    
    st.divider()
    st.metric("💰 Total", f"${total:.2f}", delta=None)
    
    # Confirm order button
    if st.button("✓ Confirm Order", type="primary", use_container_width=True):
        save_orders_to_file(st.session_state.customer_name, st.session_state.customer_phone)
        st.success("✓ Order confirmed and saved!")
        st.balloons()
        
        # Reset session
        st.session_state.session_orders = []
        st.session_state.general_notes = ""
        st.session_state.customer_name = ""
        st.session_state.customer_phone = ""
        st.session_state.reorder_sandwich = None
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
