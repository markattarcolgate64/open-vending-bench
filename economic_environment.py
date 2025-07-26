import json
import requests
from typing import Dict, List, Tuple

class EconomicEnvironment:
    def __init__(self, api_key=None):
        self.api_key = api_key
        self.base_url = "https://api.anthropic.com/v1/messages"
        
    def analyze_single_item(self, item_name: str, item_price: float, item_size: str, context: str = "") -> Tuple[float, float, int]:
        """
        Analyze a single item and return (price_elasticity, reference_price, base_sales)
        """
        prompt = self._create_single_item_prompt(item_name, item_price, item_size, context)
        response = self._call_claude_api(prompt)
        return self._parse_single_item_response(response, item_price)
    
    def generate_customer_behavior(self, vending_machine_items: Dict, context: str = "") -> Dict:
        """
        Generate customer behavior metrics for each item in the vending machine
        Returns: Dict with item_name -> {price_elasticity, reference_price, base_sales}
        """
        behavior_data = {}
        
        for slot_id, item_data in vending_machine_items.items():
            item_name = item_data['item']
            if item_name not in behavior_data:  # Avoid duplicates if same item in multiple slots
                price_elasticity, reference_price, base_sales = self.analyze_single_item(
                    item_name, item_data['price'], item_data['size'], context
                )
                behavior_data[item_name] = {
                    "price_elasticity": price_elasticity,
                    "reference_price": reference_price,
                    "base_sales": base_sales
                }
        
        return behavior_data
    
    def _create_single_item_prompt(self, item_name: str, item_price: float, item_size: str, context: str) -> str:
        """Create prompt for analyzing a single item"""
        
        prompt = f"""You are an economics expert analyzing customer behavior for a vending machine item.

CONTEXT: {context if context else "Standard office building vending machine"}

ITEM TO ANALYZE:
- Name: {item_name}
- Current Price: ${item_price}
- Size Category: {item_size}

Calculate these three values for this specific item:

1. PRICE_ELASTICITY: How sensitive customers are to price changes (-2.0 to -0.1, more negative = more sensitive)
2. REFERENCE_PRICE: What customers expect to pay for this item (in dollars)  
3. BASE_SALES: Daily sales volume at reference price (units per day, realistic numbers)

Consider factors like:
- Item type and necessity
- Location context  
- Competitive alternatives
- Price sensitivity of typical customers

Return ONLY three numbers separated by commas in this format:
price_elasticity,reference_price,base_sales

Example: -1.2,2.50,15

Response:"""
        
        return prompt
    
    def _call_claude_api(self, prompt: str) -> str:
        """Call Claude API to get behavior analysis"""
        
        # Mock response for now - TODO: Implement actual API call
        return "-1.0,2.00,10"
    
    def _parse_single_item_response(self, response: str, fallback_price: float) -> Tuple[float, float, int]:
        """Parse Claude's response for a single item"""
        try:
            parts = response.strip().split(',')
            price_elasticity = float(parts[0])
            reference_price = float(parts[1])
            base_sales = int(parts[2])
            return price_elasticity, reference_price, base_sales
        except (ValueError, IndexError):
            # Fallback to defaults if parsing fails
            return -1.0, fallback_price, 10
    
    def calculate_daily_sales(self, item_name: str, current_price: float, behavior_metrics: Dict) -> int:
        """Calculate expected daily sales based on current price and behavior metrics"""
        if item_name not in behavior_metrics:
            return 0
        
        metrics = behavior_metrics[item_name]
        price_elasticity = metrics['price_elasticity']
        reference_price = metrics['reference_price']
        base_sales = metrics['base_sales']
        
        # Calculate percentage difference from reference price
        percentage_diff = (current_price - reference_price) / reference_price
        
        # Create sales impact factor using price elasticity
        # Impact = 1 + (elasticity * percentage_difference)
        sales_impact_factor = 1 + (price_elasticity * percentage_diff)
        
        # Apply impact factor to base sales
        expected_sales = base_sales * sales_impact_factor
        
        # Return as integer (can't sell fractional items)
        return max(0, int(round(expected_sales)))