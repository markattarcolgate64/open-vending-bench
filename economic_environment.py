import json
import requests
import math
from typing import Dict, List, Tuple
from model_client import call_model
from weather import get_weather_sales_multiplier
from functools import cache
from vending_machine import VendingMachine, Item

def analyze_single_item(item_name: str, item_price: float, item_size: str, quantity: int, context: str = "") -> Tuple[float, float, int]:
    """
    Analyze a single item and return (price_elasticity, reference_price, base_sales)
    """
    prompt = create_single_item_prompt(item_name, item_price, item_size, quantity, context)
    response = call_model(prompt)
    return parse_single_item_response(response, item_price)

def generate_customer_behavior(vending_machine_slots: Dict, context: str = "") -> Dict:
    """
    Generate customer behavior metrics for each item in the vending machine
    Returns: Dict with item_name -> {price_elasticity, reference_price, base_sales}
    """
    behavior_data = {}
    
    for _, slot in vending_machine_slots.items():
        item_data = slot['item']
        if item_data is None:
            continue
        item_name = item_data.name  
        if item_name not in behavior_data:  # Avoid duplicates if same item in multiple slots
            price_elasticity, reference_price, base_sales = analyze_single_item(
                item_name, item_data.price, item_data.size, slot['quantity'], context
            )
            behavior_data[item_name] = {
                "price_elasticity": price_elasticity,
                "reference_price": reference_price,
                "base_sales": base_sales
            }
    
    return behavior_data

def create_single_item_prompt(item_name: str, item_price: float, item_size: str, quantity: int, context: str) -> str:
    """Create prompt for analyzing a single item"""
    
    prompt = f"""You are an economics expert analyzing customer behavior for a vending machine item.

CONTEXT: {context if context else "Standard office building vending machine"}

ITEM TO ANALYZE:
- Name: {item_name}
- Current Price: ${item_price}
- Size Category: {item_size}
- Available Quantity: {quantity} units in stock

Calculate these three values for this specific item:

1. PRICE_ELASTICITY: How sensitive customers are to price changes (-2.0 to -0.1, more negative = more sensitive)
2. REFERENCE_PRICE: What customers expect to pay for this item (in dollars)  
3. BASE_SALES: Daily sales volume at reference price (units per day, realistic numbers)

Consider factors like:
- Item type and necessity
- Location context  
- Competitive alternatives
- Price sensitivity of typical customers
- Available quantity (sales cannot exceed {quantity} units per day)

Return ONLY three numbers separated by commas in this format:
price_elasticity,reference_price,base_sales

Example: -1.2,2.50,15

Response:"""
    
    return prompt

def parse_single_item_response(response: str, fallback_price: float) -> Tuple[float, float, int]:
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

def calculate_item_sales(item_name: str, current_price: float, behavior_metrics: Dict) -> int:
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

@cache 
def calculate_choice_multiplier(num_products: int) -> float:
    """
    Calculate choice multiplier using sigmoid function
    Optimal variety is around 10 products, with diminishing returns beyond that
    Floor is 0.5, punishment for too little or too much variety
    """
    if num_products == 0:
        return 0.5
    
    # Sigmoid function: f(x) = 1 / (1 + e^(-k*(x - x0)))
    # Where x0 is the inflection point (optimal variety = 10)
    # k controls the steepness of the curve
    x0 = 10.0  # Optimal number of products
    k = 0.5    # Steepness factor
    
    # Apply sigmoid centered at x0
    sigmoid = 1 / (1 + math.exp(-k * (num_products - x0)))
    
    # Scale to have max around 1.0 at optimal point
    # And apply punishment for extremes
    if num_products <= x0:
        # For low variety, scale from 0.5 to 1.0
        multiplier = 0.5 + 0.5 * sigmoid
    else:
        # For high variety, diminishing returns from 1.0 downward
        excess_penalty = math.exp(-0.1 * (num_products - x0))
        multiplier = sigmoid * excess_penalty
    
    # Ensure floor of 0.5
    return max(0.5, multiplier)

@cache 
def get_month_multiplier(month: int) -> float:
    """
    Get sales multiplier based on month (1-12)
    Higher sales in summer months, lower in winter
    """
    multipliers = {
        1: 0.80,   # January - post-holiday slump
        2: 0.85,   # February - still winter
        3: 0.95,   # March - spring pickup
        4: 1.05,   # April - nice weather begins
        5: 1.10,   # May - pleasant weather
        6: 1.15,   # June - summer begins
        7: 1.20,   # July - peak summer
        8: 1.20,   # August - peak summer
        9: 1.10,   # September - back to school/work
        10: 1.00,  # October - baseline fall
        11: 0.90,  # November - cooling down
        12: 0.95   # December - holiday season but cold
    }
    return multipliers.get(month, 1.00)

@cache 
def get_day_of_week_multiplier(day_of_week: int) -> float:
    """
    Get sales multiplier based on day of week (0=Monday, 6=Sunday)
    Higher sales on weekends, lower on Mondays
    """
    multipliers = {
        0: 0.85,   # Monday - slow start
        1: 0.95,   # Tuesday - picking up
        2: 1.00,   # Wednesday - midweek baseline
        3: 1.05,   # Thursday - almost weekend
        4: 1.15,   # Friday - TGIF energy
        5: 1.25,   # Saturday - peak weekend
        6: 1.20    # Sunday - weekend but preparing for week
    }
    return multipliers.get(day_of_week, 1.00)

def calculate_item_final_sales(item_data: Item, behavior_metrics: Dict, unique_products: int, weather: str = "cloudy", month: int = 6, day_of_week: int = 2) -> int:
    """
    Calculate final sales with choice multiplier, weather, month, and day-of-week effects applied
    
    Args:
        item_name: Name of the item
        current_price: Current selling price
        behavior_metrics: Price elasticity data
        vending_machine_items: All items in the machine (for variety calculation)
        weather: Current weather state (sunny, rainy, cloudy, snowy)
        month: Month number (1-12) for seasonal effects
        day_of_week: Day of week (0=Monday, 6=Sunday) for weekly patterns
    
    Returns:
        Final expected daily sales including all multipliers
    """
    # Get base sales from price elasticity
    item_sales = calculate_item_sales(item_data.name, item_data.price, behavior_metrics)

    choice_multiplier = calculate_choice_multiplier(unique_products)
    
    # Get all multipliers
    weather_multiplier = get_weather_sales_multiplier(weather)
    month_multiplier = get_month_multiplier(month)
    day_multiplier = get_day_of_week_multiplier(day_of_week)
    
    # Apply all multipliers
    final_sales = item_sales *  choice_multiplier * weather_multiplier * month_multiplier * day_multiplier
    
    return max(0, int(round(final_sales)))

def calculate_total_sales_and_report(vending_machine: VendingMachine, weather: str = "cloudy", month: int = 6, day_of_week: int = 2) -> Tuple[int, str]:
    """
    Calculate total sales for all items in the vending machine
    """
    vending_machine_slots = vending_machine.get_inventory()
    unique_products = set()

    behavior_metrics = generate_customer_behavior(vending_machine_slots)
    report = "Total Sales Report:\n"
    for _, slot in vending_machine_slots.items():
        if slot['item'] is not None:
            unique_products.add(slot['item'].name)
    unique_products = len(unique_products)
    total_sales = 0
    for slot_id, slot in vending_machine_slots.items():
        if slot['item'] is None:
            continue
        item_data = slot['item']
        final_sales = calculate_item_final_sales(item_data, behavior_metrics, unique_products, weather, month, day_of_week)
        vending_machine.sell_item(slot_id, final_sales)
        total_sales += final_sales * item_data.price
        report += f"{item_data.name}: ${final_sales}\n"
    
    report += f"\nTotal Sales: ${total_sales}"

    return total_sales, report