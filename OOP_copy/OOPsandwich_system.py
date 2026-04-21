"""
Sandwich Order System - Main Application (OOP Version)
Uses the SandwichOrder class as the blueprint for order management
"""

from sandwich_order import SandwichOrder
from menu import Menu

ORDER_HISTORY = "order_history.txt"


class OrderSystem:
    """Manages the sandwich ordering workflow and session history."""
    
    def __init__(self):
        """Initialize the order system."""
        try:
            self.menu = Menu("menu.txt")
            self.sizes_prices = self._extract_prices()
        except Exception as e:
            print(f"Warning: Menu initialization: {e}")
            self.menu = None
            self.sizes_prices = {"6 inch": "5.00", "12 inch": "8.00"}
        
        self.current_customer = None
        self.session_orders = []
    
    def _extract_prices(self):
        """Extract size-to-price mapping from menu."""
        if not self.menu:
            return {}
        sizes = self.menu.get_category("SIZES")
        prices = self.menu.get_category("PRICES")
        return dict(zip(sizes, prices)) if sizes and prices else {}
    
    def display_main_menu(self):
        """Display main menu with required options."""
        print("\n" + "=" * 50)
        print("--- Main Menu ---")
        print("1. Place a new order")
        print("2. View my orders (this session)")
        print("3. Update an order")
        print("4. Delete an order")
        print("5. Exit")
        print("=" * 50)
        choice = input("Choose an option: ").strip()
        return choice
    
    def get_customer_info(self):
        """Get customer name and phone, return as tuple."""
        fname = input("Please enter first name: ").strip().title()
        lname = input("Please enter last name: ").strip().title()
        phone = input("Please enter phone number: ").strip()
        return f"{fname} {lname}", phone
    
    def select_from_category(self, category_name):
        """Display category options and get user selection."""
        if not self.menu:
            return "Default"
        
        items = self.menu.get_category(category_name)
        if not items:
            print(f"Category '{category_name}' not found")
            return ""
        
        print(f"\n--- SELECT {category_name} ---")
        for idx, item in enumerate(items, 1):
            print(f"{idx}. {item}")
        
        try:
            choice = int(input(f"Choose (1-{len(items)}): ")) - 1
            if 0 <= choice < len(items):
                return items[choice]
            else:
                print(f"Invalid choice. Defaulting to {items[0]}")
                return items[0]
        except ValueError:
            print(f"Invalid input. Defaulting to {items[0]}")
            return items[0]
    
    def place_new_order(self):
        """Create a new sandwich order using SandwichOrder blueprint."""
        order = SandwichOrder()
        
        size = self.select_from_category("SIZES")
        order.set_size(size)
        
        order.set_bread(self.select_from_category("BREAD"))
        order.set_protein(self.select_from_category("PROTEIN"))
        order.set_cheese(self.select_from_category("CHEESE"))
        order.set_topping(self.select_from_category("TOPPINGS"))
        order.set_sauce(self.select_from_category("SAUCES"))
        
        order.calculate_total(self.sizes_prices)
        order.display_order()
        
        confirm = input("\nConfirm this order? (y/n): ").strip().lower()
        if confirm in ('y', 'yes'):
            self.session_orders.append(order)
            print(f"✓ Order #{len(self.session_orders)} added to session")
            return order
        else:
            print("Order cancelled")
            return None
    
    def view_session_orders(self):
        """Display all orders from current session."""
        if not self.session_orders:
            print("\nNo orders in this session yet")
            return
        
        print("\n" + "=" * 50)
        print("--- YOUR ORDERS (This Session) ---")
        for idx, order in enumerate(self.session_orders, 1):
            print(f"\nOrder #{idx}:")
            print(order.display_summary())
    
    def update_order(self):
        """Update an existing order using individual setters."""
        if not self.session_orders:
            print("\nNo orders to update")
            return
        
        self.view_session_orders()
        try:
            order_num = int(input("\nEnter order number to update: ")) - 1
            if 0 <= order_num < len(self.session_orders):
                order = self.session_orders[order_num]
                
                print("\nWhat would you like to update?")
                print("1. Size")
                print("2. Bread")
                print("3. Protein")
                print("4. Cheese")
                print("5. Topping")
                print("6. Sauce")
                print("0. Cancel")
                
                choice = input("Choose: ").strip()
                
                if choice == "1":
                    order.set_size(self.select_from_category("SIZES"))
                    order.calculate_total(self.sizes_prices)
                elif choice == "2":
                    order.set_bread(self.select_from_category("BREAD"))
                elif choice == "3":
                    order.set_protein(self.select_from_category("PROTEIN"))
                elif choice == "4":
                    order.set_cheese(self.select_from_category("CHEESE"))
                elif choice == "5":
                    order.set_topping(self.select_from_category("TOPPINGS"))
                elif choice == "6":
                    order.set_sauce(self.select_from_category("SAUCES"))
                elif choice == "0":
                    return
                else:
                    print("Invalid choice")
                    return
                
                print("\nUpdated order:")
                order.display_order()
            else:
                print("Invalid order number")
        except ValueError:
            print("Invalid input")
    
    def delete_order(self):
        """Delete an order from session."""
        if not self.session_orders:
            print("\nNo orders to delete")
            return
        
        self.view_session_orders()
        try:
            order_num = int(input("\nEnter order number to delete: ")) - 1
            if 0 <= order_num < len(self.session_orders):
                removed = self.session_orders.pop(order_num)
                print(f"\n✓ Order deleted: {removed.display_summary()}")
            else:
                print("Invalid order number")
        except ValueError:
            print("Invalid input")
    
    def checkout_and_save(self, customer_name, customer_phone):
        """Finalize orders and save to file.
        
        Args:
            customer_name: Full customer name
            customer_phone: Customer phone number
        """
        if not self.session_orders:
            print("\nNo orders to save")
            return
        
        print("\n" + "=" * 50)
        print("--- FINAL TICKET ---")
        print(f"Customer: {customer_name}")
        print(f"Phone: {customer_phone}")
        
        total = 0.0
        for idx, order in enumerate(self.session_orders, 1):
            print(f"\nSandwich #{idx}:")
            order.display_order()
            total += order.get_price()
            order.save_to_file(ORDER_HISTORY, customer_name, customer_phone)
        
        print(f"\n--- SESSION TOTAL: ${total:.2f} ---")
        print("✓ Orders saved to history")
        print("=" * 50)
    
    def run(self):
        """Main application loop."""
        print("\n" + "=" * 50)
        print("*** SANDWICH ORDER SYSTEM (OOP VERSION) ***")
        print("=" * 50)
        
        # Get customer info at the beginning
        print("\n--- CUSTOMER INFORMATION ---")
        customer_name, customer_phone = self.get_customer_info()
        print(f"\n✓ Welcome, {customer_name}!")
        print(f"✓ Phone: {customer_phone}\n")
        
        while True:
            choice = self.display_main_menu()
            
            if choice == "1":
                self.place_new_order()
            elif choice == "2":
                self.view_session_orders()
            elif choice == "3":
                self.update_order()
            elif choice == "4":
                self.delete_order()
            elif choice == "5":
                if self.session_orders:
                    save = input("Save orders before exiting? (y/n): ").strip().lower()
                    if save in ('y', 'yes'):
                        self.checkout_and_save(customer_name, customer_phone)
                print("\nThank you for using Sandwich Order System!")
                break
            else:
                print("Invalid choice. Try again.")


def main():
    """Entry point for the application."""
    system = OrderSystem()
    system.run()


if __name__ == "__main__":
    main()
