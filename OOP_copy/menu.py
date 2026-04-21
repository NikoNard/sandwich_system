"""
Menu Class for Sandwich System
Manages menu items, categories, and pricing
"""


class Menu:
    """Represents a sandwich shop menu with categories and items."""

    def __init__(self, menu_file="menu.txt"):
        """Initialize menu from a file.
        
        Args:
            menu_file (str): Path to menu file with format CATEGORY;item1,item2,...
        """
        self.menu_data = {}
        import os
        # Handle file path - check current directory and script directory
        if not os.path.exists(menu_file):
            script_dir = os.path.dirname(os.path.abspath(__file__))
            menu_file = os.path.join(script_dir, menu_file)
        self.load_menu(menu_file)

    def load_menu(self, menu_file):
        """Load menu from file.
        
        Args:
            menu_file (str): Path to menu file
        """
        try:
            with open(menu_file, 'r') as f:
                for line in f:
                    line = line.strip()
                    if line and ';' in line:
                        category, items = line.split(';', 1)
                        self.menu_data[category] = items.split(',')
        except FileNotFoundError:
            print(f"Warning: Menu file '{menu_file}' not found.")

    def get_category(self, category):
        """Get items in a category.
        
        Args:
            category (str): Category name
            
        Returns:
            list: Items in category or empty list if not found
        """
        return self.menu_data.get(category, [])

    def get_all_categories(self):
        """Get all menu categories.
        
        Returns:
            list: All category names
        """
        return list(self.menu_data.keys())

    def display_menu(self):
        """Display entire menu."""
        print("\n--- MENU ---")
        for category, items in self.menu_data.items():
            print(f"\n{category}:")
            for item in items:
                print(f"  • {item}")

    def display_category(self, category):
        """Display items in a specific category.
        
        Args:
            category (str): Category name
        """
        items = self.get_category(category)
        if items:
            print(f"\n{category}:")
            for item in items:
                print(f"  • {item}")
        else:
            print(f"Category '{category}' not found.")


if __name__ == "__main__":
    # Demo usage
    menu = Menu("menu.txt")
    menu.display_menu()
    
    print("\n--- BREAD OPTIONS ---")
    menu.display_category("BREAD")
