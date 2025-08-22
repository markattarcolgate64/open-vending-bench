import os
import requests
import json
from typing import Dict, Optional


def search_perplexity(query: str) -> tuple[str, Optional[str]]:
    """
    Search using Perplexity API
    
    Args:
        query: The search query string
        
    Returns:
        tuple: (content_string, error_string) where error_string is None if successful
    """
    api_key = os.getenv("PERPLEXITY_API_KEY")
    
    if not api_key:
        return "Search unavailable - API key not configured", "PERPLEXITY_API_KEY environment variable not set"
    
    url = "https://api.perplexity.ai/chat/completions"
    
    payload = {
        "model": "sonar",
        "messages": [
            {"role": "user", "content": query}
        ]
    }
    
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json"
    }
    
    try:
        response = requests.post(url, json=payload, headers=headers, timeout=30)
        response.raise_for_status()
        
        data = response.json()
        
        if "choices" in data and len(data["choices"]) > 0:
            content = data["choices"][0]["message"]["content"]
            return content, None
        else:
            return "Search returned no results", "No response content from Perplexity API"
            
    except requests.exceptions.RequestException as e:
        return f"Search failed due to network error: {str(e)}", f"Request failed: {str(e)}"
    except json.JSONDecodeError as e:
        return "Search failed due to response parsing error", f"Failed to parse response: {str(e)}"
    except Exception as e:
        return f"Search failed: {str(e)}", f"Unexpected error: {str(e)}"


def search_suppliers(location: str = "United States", product_types: Optional[str] = None) -> tuple[str, Optional[str]]:
    """
    Search for wholesale suppliers for vending machine products
    
    Args:
        location: Geographic location to search for suppliers
        product_types: Specific product types to find suppliers for
        
    Returns:
        tuple: (content_string, error_string) where error_string is None if successful
    """
    if product_types:
        query = f"wholesale suppliers {product_types} vending machine products {location} contact information email"
    else:
        query = f"wholesale suppliers vending machine snacks drinks candy {location} contact information email"
    
    content, error = search_perplexity(query)
    return content, error


def search_product_info(product_name: str, info_type: str = "pricing") -> tuple[str, Optional[str]]:
    """
    Search for specific product information
    
    Args:
        product_name: Name of the product to research
        info_type: Type of information needed (pricing, supplier, specifications, etc.)
        
    Returns:
        tuple: (content_string, error_string) where error_string is None if successful
    """
    query = f"{product_name} wholesale {info_type} vending machine supplier cost price"
    
    content, error = search_perplexity(query)
    return content, error