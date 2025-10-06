class Item:
    def __init__(self, name, size, price, cost):
        self.name = name
        self.size = size  # 'small' or 'large'
        self.price = price  # selling price
        self.cost = cost   # cost to purchase from supplier
    
    def __repr__(self):
        return f"Item({self.name}, {self.size}, ${self.price})"


class VendingMachine:
    def __init__(self):
        # 4 rows x 3 slots = 12 total slots
        # Rows 0-1: small items, Rows 2-3: large items
        self.slots = {}
        for row in range(4):
            for slot in range(3):
                slot_id = f"{row}-{slot}"
                self.slots[slot_id] = {
                    'item': None,
                    'quantity': 0,
                    'max_capacity': 10,  # max items per slot
                    'size_type': 'small' if row < 2 else 'large'
                }
    
    def can_stock_item(self, slot_id, item):
        """Check if item can be stocked in this slot"""
        if slot_id not in self.slots:
            return False
        
        slot = self.slots[slot_id]
        
        # Check size compatibility
        if slot['size_type'] != item.size:
            return False
        
        # Check if slot is empty or has same item
        if slot['item'] is None or slot['item'].name == item.name:
            return True
        
        return False
    
    def stock_item(self, slot_id, item, quantity):
        """Stock items in a specific slot"""
        if not self.can_stock_item(slot_id, item):
            return False
        
        slot = self.slots[slot_id]
        
        # Check capacity
        if slot['quantity'] + quantity > slot['max_capacity']:
            return False
        
        # Stock the item
        slot['item'] = item
        slot['quantity'] += quantity
        return True
    
    def get_slots(self):
        """Get current inventory state"""
        return self.slots
    
    def get_available_slots(self, size_type):
        """Get available slots for a specific size type"""
        available = []
        for slot_id, slot in self.slots.items():
            if slot['size_type'] == size_type and (slot['item'] is None or slot['quantity'] < slot['max_capacity']):
                available.append(slot_id)
        return available
    
    def sell_item(self, slot_id, quantity=1):
        """Sell items from the specified slot"""
        if slot_id not in self.slots:
            return None
        
        slot = self.slots[slot_id]
        if slot['quantity'] <= 0 or slot['item'] is None:
            return None
        
        # Can't sell more than available
        actual_quantity = min(quantity, slot['quantity'])
        
        # Remove items
        slot['quantity'] -= actual_quantity
        
        # If slot is empty, clear the item
        if slot['quantity'] == 0:
            item = slot['item']
            slot['item'] = None
            return item, actual_quantity
        
        return slot['item'], actual_quantity
    
    def print_machine(self):
        """Print ASCII diagram of the vending machine"""
        print("┌─────────── VENDING MACHINE ───────────┐")
        print("│                                       │")
        
        for row in range(4):
            size_label = "SMALL ITEMS" if row < 2 else "LARGE ITEMS"
            if row == 0 or row == 2:
                print(f"│  {size_label:^33}  │")
                print("│  ┌─────────┬─────────┬─────────┐  │")
            
            # Print slot contents
            row_display = "│  │"
            for slot in range(3):
                slot_id = f"{row}-{slot}"
                slot_data = self.slots[slot_id]
                
                if slot_data['item'] is None:
                    content = "EMPTY"
                    qty = ""
                else:
                    # Truncate item name to fit
                    name = slot_data['item'].name[:7]
                    qty = f"({slot_data['quantity']})"
                    content = f"{name} {qty}"
                
                # Center content in 9-char width
                row_display += f"{content:^9}│"
            
            row_display += "  │"
            print(row_display)
            
            if row == 1 or row == 3:
                print("│  └─────────┴─────────┴─────────┘  │")
                if row == 1:
                    print("│                                       │")
        
        print("│                                       │")
        print("└───────────────────────────────────────┘")