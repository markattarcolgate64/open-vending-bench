import random
from typing import Dict

def get_season_from_month(month: int) -> str:
    """Get season from month number (1-12)"""
    if month in [12, 1, 2]:
        return "winter"
    elif month in [3, 4, 5]:
        return "spring"
    elif month in [6, 7, 8]:
        return "summer"
    else:  # 9, 10, 11
        return "fall"

def get_weather_probabilities(season: str, previous_weather: str) -> Dict[str, float]:
    """
    Get weather transition probabilities based on season and previous weather
    
    Args:
        season: "winter", "spring", "summer", "fall"
        previous_weather: "sunny", "rainy", "cloudy", "snowy"
    
    Returns:
        Dict with weather state probabilities
    """
    
    # Base seasonal probabilities
    seasonal_base = {
        "winter": {"sunny": 0.2, "cloudy": 0.4, "rainy": 0.2, "snowy": 0.2},
        "spring": {"sunny": 0.4, "cloudy": 0.3, "rainy": 0.3, "snowy": 0.0},
        "summer": {"sunny": 0.6, "cloudy": 0.2, "rainy": 0.2, "snowy": 0.0},
        "fall": {"sunny": 0.3, "cloudy": 0.4, "rainy": 0.3, "snowy": 0.0}
    }
    
    # Weather persistence factor - same weather tends to continue
    persistence_bonus = 0.3
    
    # Start with seasonal base probabilities
    probabilities = seasonal_base[season].copy()
    
    # Apply persistence - boost probability of same weather continuing
    if previous_weather in probabilities:
        # Reduce all probabilities slightly
        for weather in probabilities:
            probabilities[weather] *= (1.0 - persistence_bonus)
        
        # Boost the previous weather
        probabilities[previous_weather] += persistence_bonus
    
    # Normalize to ensure they sum to 1.0
    total = sum(probabilities.values())
    for weather in probabilities:
        probabilities[weather] /= total
    
    return probabilities

def generate_next_weather(month: int, previous_weather: str = "sunny") -> str:
    """
    Generate next day's weather based on month and previous weather
    
    Args:
        month: Month number (1-12)
        previous_weather: Previous day's weather state
    
    Returns:
        Next day's weather state as string
    """
    season = get_season_from_month(month)
    probabilities = get_weather_probabilities(season, previous_weather)
    
    # Random selection based on probabilities
    weather_states = list(probabilities.keys())
    weights = list(probabilities.values())
    
    return random.choices(weather_states, weights=weights)[0]

def get_weather_sales_multiplier(weather: str) -> float:
    """
    Get overall sales multiplier based on weather
    
    Args:
        weather: Current weather state
    
    Returns:
        Float multiplier for overall sales (1.0 = no change)
    """
    multipliers = {
        "sunny": 1.10,    # +10% - people are out and about
        "rainy": 0.85,    # -15% - people stay indoors more
        "cloudy": 1.00,   # neutral baseline
        "snowy": 0.75     # -25% - severe weather reduces foot traffic
    }
    
    return multipliers.get(weather, 1.00)