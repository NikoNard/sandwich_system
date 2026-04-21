# Sandwich System Project - Session Reflection Notes

**Date:** April 21, 2026  
**Project:** Sandwich Order System - OOP to Streamlit Web App Conversion  
**Participants:** Niko Nardulli (Steering), GitHub Copilot (Programming)

---

## 🎯 What Went Well

### 1. **Clear Project Scope & Requirements**
- ✅ User provided detailed specifications upfront (UI/UX, session management, features)
- ✅ Steering/driving partnership was clearly defined before development began
- ✅ Requirements covered: multi-select options, order history, running totals, visual enhancements

### 2. **Systematic Problem-Solving**
- ✅ Created test files to validate components before integration
- ✅ Tested imports, menu loading, and order creation separately
- ✅ Identified and fixed path issues early with absolute paths
- ✅ Used `importlib` for clean, error-free dynamic imports

### 3. **Proper Version Control**
- ✅ Git configured with user credentials at session start
- ✅ Regular, descriptive commits after each major change
- ✅ Cleaned up unnecessary test/config files before final push
- ✅ Multiple iterations pushed successfully to GitHub

### 4. **Object-Oriented Code Reuse**
- ✅ Leveraged existing OOP classes (`Menu`, `SandwichOrder`, `OrderSystem`)
- ✅ No modifications needed to existing code - clean integration
- ✅ Maintained separation of concerns between OOP logic and UI

### 5. **Error Resolution**
- ✅ Methodically addressed each error:
  - Import resolution errors → Fixed with `importlib`
  - StreamlitAPIException → Removed problematic session state resets
  - Missing navigation → Added View Cart and Checkout buttons

---

## 🔧 What Could Be Better

### 1. **Initial Testing Strategy**
- ⚠️ Could have created and run a Streamlit test earlier
- 💡 **Next time:** Run app in test mode before final fixes

### 2. **Session State Management**
- ⚠️ Tried to manually reset form fields (caused StreamlitAPIException)
- 💡 **Next time:** Understand Streamlit's automatic form reset on `st.rerun()` first

### 3. **Navigation Flow**
- ⚠️ Initially missed the navigation buttons between pages
- 💡 **Next time:** Map out all page transitions on paper/whiteboard before coding

### 4. **File Path Handling**
- ⚠️ First attempted relative paths, then hardcoded paths
- 💡 **Next time:** Use `os.path` with `__file__` from the start for dynamic paths

---

## 📋 Requirements Met

- ✅ Linear workflow (customer info → place order → manage orders → checkout)
- ✅ Streamlit `session_state` for session persistence
- ✅ Multi-select options for sandwich components
- ✅ Past order viewing from `order_history.txt`
- ✅ Running total/cart display
- ✅ Order receipt/preview
- ✅ Order confirmation notifications
- ✅ File persistence to `order_history.txt`
- ✅ Menu loaded dynamically from `menu.txt`

---

## 🚀 Workflow Notes for Next Session

### For the Steering (User):
1. **Start with clear requirements** - List all must-haves and nice-to-haves
2. **Ask for clarification early** - Better to ask than assume
3. **Test as you go** - Don't wait until the end to see the app working
4. **Provide error messages directly** - Paste full error traces for faster fixes

### For GitHub Copilot (Programmer):
1. **Always ask before assuming** - Even if it seems obvious, clarify with user
2. **Create test files to validate** - Don't rely solely on linting
3. **Map out page flows** - Document state transitions before coding
4. **Use proper dynamic imports** - `importlib` over `sys.path` manipulation
5. **Understand framework quirks** - For Streamlit: widget resets on `st.rerun()`, no manual session state for new keys
6. **Read file structure first** - Understand the full codebase before integrating
7. **Test locally when possible** - Run scripts to verify logic works
8. **Clean up before final push** - Remove test files, restore configs, ensure working tree is clean

---

## 📦 Project Structure Reference

```
sandwich_system/
├── streamlit_app.py           # Main Streamlit web app
├── OOP_copy/
│   ├── OOPsandwich_system.py  # Original CLI system (reference)
│   ├── sandwich_order.py       # SandwichOrder class
│   ├── menu.py                 # Menu class
│   ├── menu.txt                # Menu data (dynamically loaded)
│   └── order_history.txt       # Persisted orders
├── README.md
└── SESSION_NOTES.md            # This file

```

---

## 🔮 Future Enhancements to Consider

1. **Database Integration** - Replace `order_history.txt` with SQLite/PostgreSQL
2. **User Accounts** - Login system to track individual customer histories
3. **Admin Dashboard** - View sales statistics, popular items
4. **Payment Integration** - Add Stripe/PayPal for online payments
5. **Order Status** - Track order status (placed, preparing, ready)
6. **Customizable Menu** - Admin interface to modify menu items/prices
7. **Order Scheduling** - Allow customers to schedule orders for pickup
8. **Ratings & Reviews** - Customer feedback on sandwiches

---

## 💡 Key Learnings

- **Streamlit's state management** requires understanding of reruns and automatic widget resets
- **Dynamic imports** with `importlib` are cleaner than `sys.path` manipulation
- **Test incrementally** - small, focused tests catch issues early
- **Clear communication** between steering and driver prevents rework
- **Git workflow discipline** keeps history clean and makes debugging easier

---

## 🎓 Educational Value

This project demonstrates:
- OOP design principles (separation of concerns)
- Web framework integration with existing code
- Streamlit best practices
- Git workflows in collaborative settings
- Error handling and debugging methodology
- File I/O and dynamic module loading

---

**Next Session:** Review this document, check GitHub for latest code, then continue with enhancements or bug fixes as needed.

**Status:** ✅ Core functionality complete and working. Ready for testing/deployment.
