import requests
import json
import os
from typing import Optional

def call_claude_model(prompt: str) -> str:
    """
    Call Claude Sonnet model with a prompt and return the response
    
    Args:
        prompt: The text prompt to send to Claude
    
    Returns:
        The model's response as a string
    """
    
    # Get API key from parameter or environment
    api_key = os.environ['ANTHROPIC_API_KEY']
    if not api_key:
        raise ValueError("API key must be provided or set in ANTHROPIC_API_KEY environment variable")
    
    # API endpoint
    url = "https://api.anthropic.com/v1/messages"
    
    # Headers
    headers = {
        "Content-Type": "application/json",
        "x-api-key": api_key,
        "anthropic-version": "2023-06-01"
    }
    
    # Request payload
    payload = {
        "model": "claude-sonnet-4-20250514",  # Latest Sonnet model
        "max_tokens": 1000,
        "messages": [
            {
                "role": "user",
                "content": prompt
            }
        ]
    }
    
    try:
        # Make the API request
        response = requests.post(url, headers=headers, json=payload)
        response.raise_for_status()  # Raise exception for bad status codes
        
        # Parse response
        response_data = response.json()
        
        # Extract the text content from the response
        if 'content' in response_data and len(response_data['content']) > 0:
            return response_data['content'][0]['text']
        else:
            return "No response content received"
            
    except requests.exceptions.RequestException as e:
        return f"API request failed: {str(e)}"
    except json.JSONDecodeError as e:
        return f"Failed to parse response JSON: {str(e)}"
    except KeyError as e:
        return f"Unexpected response format: {str(e)}"
    except Exception as e:
        return f"Unexpected error: {str(e)}"


def call_claude_with_fallback(prompt: str) -> str:
    """
    Call Claude with fallback to mock response if API fails
    Useful for development/testing when API key isn't available
    """
    try:
        return call_claude_model(prompt)
    except (ValueError, Exception) as e:
        # Fallback to mock response for development
        print(f"API call failed ({e}), using mock response")
        return "Mock response: -1.0,2.00,10"  # Example format for economic analysis


def call_model(prompt: str, model_type: str = "claude") -> str:
    """
    Universal model client - wrapper for different model providers
    
    Args:
        prompt: The text prompt to send to the model
        api_key: API key for the model provider
        model_type: Which model provider to use ("claude", "openai", etc.)
    
    Returns:
        The model's response as a string
    """
    
    if model_type.lower() == "claude":
        return call_claude_model(prompt)
    else:
        # Future: Add other model providers here
        # elif model_type.lower() == "openai":
        #     return call_openai_model(prompt, api_key)
        # elif model_type.lower() == "openrouter":
        #     return call_openrouter_model(prompt, api_key)
        
        raise ValueError(f"Unsupported model type: {model_type}. Currently only 'claude' is supported.")