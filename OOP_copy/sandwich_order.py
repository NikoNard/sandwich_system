"""
SandwichOrder Class - Blueprint for Order Management
Packs all sandwich order data into a single reusable object (Suitcase)
"""


class SandwichOrder:
    """
    Manages a complete sandwich order with all properties and operations.
    This is the 'Suitcase' that holds all order data together.
    
    UML Methods:
    - __init__: Initialize order
    - set_size: Set sandwich size
    - set_bread: Set bread type
    - set_protein: Set protein type
    - set_cheese: Set cheese type
    - set_topping: Set topping type
    - set_sauce: Set sauce type
    - get_size, get_bread, get_protein, get_cheese, get_topping, get_sauce: Getters
    - calculate_total: Compute price based on size
    - display_order: Show formatted order
    - save_to_file: Persist order data
    """
    
    def __init__(self, size="", bread="", protein="", cheese="", topping="", sauce=""):
        """Initialize sandwich order with optional parameters."""
        self.__size = size
        self.__bread = bread
        self.__protein = protein
        self.__cheese = cheese
        self.__topping = topping
        self.__sauce = sauce
        self.__price = 0.0
    
    # ===== SETTERS (Individual line-by-line editing) =====
    def set_size(self, size):
        """Set sandwich size."""
        self.__size = size
    
    def set_bread(self, bread):
        """Set bread type."""
        self.__bread = bread
    
    def set_protein(self, protein):
        """Set protein type."""
        self.__protein = protein
    
    def set_cheese(self, cheese):
        """Set cheese type."""
        self.__cheese = cheese
    
    def set_topping(self, topping):
        """Set topping type."""
        self.__topping = topping
    
    def set_sauce(self, sauce):
        """Set sauce type."""
        self.__sauce = sauce
    
    def set_price(self, price):
        """Set order price."""
        self.__price = price
    
    # ===== GETTERS =====
    def get_size(self):
        """Get sandwich size."""
        return self.__size
    
    def get_bread(self):
        """Get bread type."""
        return self.__bread
    
    def get_protein(self):
        """Get protein type."""
        return self.__protein
    
    def get_cheese(self):
        """Get cheese type."""
        return self.__cheese
    
    def get_topping(self):
        """Get topping type."""
        return self.__topping
    
    def get_sauce(self):
        """Get sauce type."""
        return self.__sauce
    
    def get_price(self):
        """Get order price."""
        return self.__price
    
    # ===== DISPLAY LOGIC (Clear numbered format) =====
    def display_order(self):
        """
        Display order in clear, numbered format.
        Shows all sandwich properties.
        """
        print("\n--- ORDER DETAILS ---")
        print(f"1. Size:     {self.__size}")
        print(f"2. Bread:    {self.__bread}")
        print(f"3. Protein:  {self.__protein}")
        print(f"4. Cheese:   {self.__cheese}")
        print(f"5. Topping:  {self.__topping}")
        print(f"6. Sauce:    {self.__sauce}")
        print(f"   Price:    ${self.__price:.2f}")
    
    def display_summary(self):
        """Display a one-line order summary."""
        return f"{self.__size} sandwich: {self.__bread}, {self.__protein}, {self.__cheese}, {self.__topping}, {self.__sauce} (${self.__price:.2f})"
    
    # ===== CALCULATION =====
    def calculate_total(self, prices_dict):
        """
        Calculate total price based on size.
        
        Args:
            prices_dict: Dictionary with size names as keys, prices as values
        
        Returns:
            float: Total price
        """
        if self.__size in prices_dict:
            self.__price = float(prices_dict[self.__size])
        return self.__price
    
    # ===== FILE PERSISTENCE =====
    def save_to_file(self, filename, customer_name, customer_phone):
        """
        Save order to file.
        
        Args:
            filename: File to append order to
            customer_name: Full customer name
            customer_phone: Customer phone number
        """
        try:
            with open(filename, 'a') as f:
                f.write("=" * 50 + "\n")
                f.write(f"Customer: {customer_name}\n")
                f.write(f"Phone: {customer_phone}\n")
                f.write(f"Size:     {self.__size}\n")
                f.write(f"Bread:    {self.__bread}\n")
                f.write(f"Protein:  {self.__protein}\n")
                f.write(f"Cheese:   {self.__cheese}\n")
                f.write(f"Topping:  {self.__topping}\n")
                f.write(f"Sauce:    {self.__sauce}\n")
                f.write(f"Total:    ${self.__price:.2f}\n")
                f.write("=" * 50 + "\n\n")
            return True
        except Exception as e:
            print(f"Error saving order: {e}")
            return False
    
    # ===== VALIDATION & HELPER =====
    def is_complete(self):
        """Check if all sandwich components are selected."""
        return all([
            self.__size,
            self.__bread,
            self.__protein,
            self.__cheese,
            self.__topping,
            self.__sauce
        ])
    
    def reset_order(self):
        """Clear all order data."""
        self.__size = ""
        self.__bread = ""
        self.__protein = ""
        self.__cheese = ""
        self.__topping = ""
        self.__sauce = ""
        self.__price = 0.0


if __name__ == "__main__":
    # Demo usage
    order = SandwichOrder()
    
    # Build order using setters
    order.set_size("6 inch")
    order.set_bread("Wheat")
    order.set_protein("Turkey")
    order.set_cheese("Swiss")
    order.set_topping("Lettuce")
    order.set_sauce("Mayo")
    order.set_price(7.50)
    
    # Display order
    order.display_order()
    print(f"\nSummary: {order.display_summary()}")
    print(f"\nOrder complete? {order.is_complete()}")
