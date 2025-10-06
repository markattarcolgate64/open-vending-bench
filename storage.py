"""
Storage system for managing backroom inventory and deliveries
"""
from typing import Dict, Optional, List, Callable
from datetime import datetime, timedelta
from vending_machine import Item


class StorageSystem:
    """Manages backroom inventory for the vending machine business"""

    def __init__(self):
        # Storage dict: {item_name: {"item": Item, "quantity": int, "avg_unit_cost": float}}
        self.items: Dict[str, Dict] = {}
        # Pending deliveries: [{arrival_time, supplier, items, reference}]
        self.pending_deliveries: List[Dict] = []

    def add_items(self, name: str, size: str, quantity: int, unit_cost: float, price: float = 0.0) -> float:
        """
        Add items to storage and calculate weighted average cost

        Args:
            name: Product name
            size: 'small' or 'large'
            quantity: Number of units to add
            unit_cost: Cost per unit for this batch
            price: Selling price (optional, can be set later)

        Returns:
            Total cost of added items (quantity * unit_cost)
        """
        if name not in self.items:
            # Create new Item and storage record
            item = Item(name, size, price, unit_cost)
            self.items[name] = {
                "item": item,
                "quantity": 0,
                "avg_unit_cost": 0.0
            }

        record = self.items[name]

        # Update weighted average cost
        total_qty = record["quantity"] + quantity
        if total_qty > 0:
            total_cost = (record["avg_unit_cost"] * record["quantity"]) + (unit_cost * quantity)
            record["avg_unit_cost"] = total_cost / total_qty

        record["quantity"] = total_qty

        # Update the Item's cost with new average
        record["item"].cost = record["avg_unit_cost"]

        return float(unit_cost) * int(quantity)

    def remove_items(self, name: str, quantity: int) -> bool:
        """
        Remove items from storage (e.g., when stocking the machine)

        Args:
            name: Product name
            quantity: Number of units to remove

        Returns:
            True if successful, False if insufficient quantity
        """
        if name not in self.items:
            return False

        record = self.items[name]
        if record["quantity"] < quantity:
            return False

        record["quantity"] -= quantity

        # Remove item from storage if quantity reaches 0
        if record["quantity"] == 0:
            del self.items[name]

        return True

    def get_quantity(self, name: str) -> int:
        """Get quantity of a specific item in storage"""
        if name not in self.items:
            return 0
        return self.items[name]["quantity"]

    def get_item(self, name: str) -> Optional[Item]:
        """Get Item object for a specific product"""
        if name not in self.items:
            return None
        return self.items[name]["item"]

    def list_all_items(self) -> List[str]:
        """Get list of all item names in storage"""
        return list(self.items.keys())

    def get_inventory_dict(self) -> Dict[str, Dict]:
        """
        Get storage inventory as dict (for backwards compatibility)
        Returns: {item_name: {"size": str, "quantity": int, "avg_unit_cost": float}}
        """
        return {
            name: {
                "size": record["item"].size,
                "quantity": record["quantity"],
                "avg_unit_cost": record["avg_unit_cost"]
            }
            for name, record in self.items.items()
        }

    def get_total_value(self) -> float:
        """Calculate total value of all items in storage"""
        return sum(record["quantity"] * record["avg_unit_cost"] for record in self.items.values())

    def is_empty(self) -> bool:
        """Check if storage is empty"""
        return len(self.items) == 0

    def get_items_by_size(self, size: str) -> List[Item]:
        """Get all Item objects of a specific size"""
        return [
            record["item"]
            for record in self.items.values()
            if record["item"].size == size
        ]

    def update_price(self, name: str, new_price: float) -> bool:
        """
        Update the selling price for an item in storage

        Args:
            name: Product name
            new_price: New selling price

        Returns:
            True if successful, False if item not found
        """
        if name not in self.items:
            return False

        self.items[name]["item"].price = new_price
        return True

    def schedule_delivery(self, current_time: datetime, items: List[Dict], days_until_delivery: int,
                          supplier: str = "Unknown Supplier", reference: Optional[str] = None) -> datetime:
        """
        Schedule a delivery to arrive in N days at 6:00 AM

        Args:
            current_time: Current simulation time
            items: List of {name, size, quantity, unit_cost}
            days_until_delivery: Number of days until arrival
            supplier: Supplier name
            reference: Optional PO/order reference

        Returns:
            Scheduled arrival datetime
        """
        # Calculate arrival time at 6:00 AM
        arrival = current_time.replace(hour=6, minute=0, second=0, microsecond=0) + timedelta(days=days_until_delivery)

        self.pending_deliveries.append({
            "arrival_time": arrival,
            "supplier": supplier,
            "items": items,
            "reference": reference,
        })

        return arrival

    def process_arrivals(self, current_time: datetime,
                        on_arrival: Optional[Callable[[str, Optional[str], str], None]] = None) -> float:
        """
        Process deliveries that have arrived by current_time

        Args:
            current_time: Current simulation time
            on_arrival: Optional callback function(supplier, reference, delivery_notice_body) to send email

        Returns:
            Total cost of all processed deliveries
        """
        if not self.pending_deliveries:
            return 0.0

        total_cost = 0.0
        remaining = []

        for delivery in self.pending_deliveries:
            if delivery["arrival_time"] <= current_time:
                supplier = delivery.get("supplier", "Supplier")
                ref = delivery.get("reference")

                # Process items and build delivery notice
                lines = []
                delivery_cost = 0.0

                for item in delivery.get("items", []):
                    name = item.get("name")
                    size = item.get("size", "small")
                    qty = int(item.get("quantity", 0))
                    unit_cost = float(item.get("unit_cost", 0.0))

                    if qty <= 0 or not name:
                        continue

                    # Add to storage
                    item_cost = self.add_items(name, size, qty, unit_cost)
                    delivery_cost += item_cost
                    lines.append(f"- {name} ({size}) x{qty} @ ${unit_cost:.2f}")

                total_cost += delivery_cost

                # Send delivery notice via callback if provided
                if on_arrival:
                    body_lines = [
                        f"Delivery has arrived from {supplier}.",
                        f"Reference: {ref}" if ref else None,
                        f"Arrival Time (UTC): {delivery['arrival_time'].strftime('%Y-%m-%d %H:%M')}",
                        "",
                        "Items:",
                        *lines,
                        "",
                        f"Total billed on delivery: ${delivery_cost:.2f}",
                    ]
                    body = "\n".join([l for l in body_lines if l is not None])
                    on_arrival(supplier, ref, body)
            else:
                remaining.append(delivery)

        self.pending_deliveries = remaining
        return total_cost

    def get_storage_report(self) -> str:
        """
        Generate agent-friendly report of current storage inventory

        Returns:
            Formatted string showing all items in storage
        """
        if self.is_empty():
            return "Storage is currently empty. No items in backroom inventory."

        report_lines = ["STORAGE INVENTORY REPORT", "=" * 50]

        # Sort items: large first, then small (alphabetically within each)
        sorted_items = sorted(
            self.items.items(),
            key=lambda x: (x[1]["item"].size == "small", x[0])  # False (large) sorts before True (small)
        )

        for item_name, record in sorted_items:
            item = record["item"]
            qty = record["quantity"]
            avg_cost = record["avg_unit_cost"]
            total_value = qty * avg_cost
            size_label = item.size.upper()

            report_lines.append(
                f"  [{size_label:5}] {item_name:20} {qty:3} units @ ${avg_cost:.2f}/unit (Value: ${total_value:.2f})"
            )

        # Summary
        report_lines.append("-" * 50)
        report_lines.append(f"Total Product Types: {len(self.items)}")
        report_lines.append(f"Total Inventory Value: ${self.get_total_value():.2f}")

        if self.pending_deliveries:
            report_lines.append(f"Pending Deliveries: {len(self.pending_deliveries)}")

        return "\n".join(report_lines)

    def __repr__(self):
        return f"StorageSystem({len(self.items)} product types, ${self.get_total_value():.2f} value, {len(self.pending_deliveries)} pending deliveries)"