import requests
import json
import os
from typing import Optional
import litellm



def call_claude_model(prompt: str, system_prompt: str = "") -> str:
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
        "system": system_prompt,
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


def call_model_litellm(prompt: str, model: str = "claude-3-5-sonnet-20241022", system_prompt: str = "") -> str:
    """
    Call model using LiteLLM unified interface
    
    Args:
        prompt: The text prompt to send to the model
        model: Model identifier (e.g., "claude-3-5-sonnet-20241022", "gpt-4", "openai/gpt-3.5-turbo")
        system_prompt: System prompt for the model
    
    Returns:
        The model's response as a string
    """
    try:
        messages = []
        if system_prompt:
            messages.append({"role": "system", "content": system_prompt})
        messages.append({"role": "user", "content": prompt})
        
        response = litellm.completion(
            model=model,
            messages=messages,
            max_tokens=1000
        )
        
        return response.choices[0].message.content
        
    except Exception as e:
        return f"LiteLLM request failed: {str(e)}"

def call_model(prompt: str, model_type: str = "claude-4-sonnet", system_prompt: str = "") -> str:
    """
    Universal model client using LiteLLM for unified interface
    
    Args:
        prompt: The text prompt to send to the model
        model_type: Which model to use ("claude", "gpt-4", "gpt-3.5", etc.)
        system_prompt: System prompt for the model
    
    Returns:
        The model's response as a string
    """
    
    # Map common model types to LiteLLM identifiers
    model_mapping = {
        "claude-4-opus": "anthropic/claude-opus-4-20250514",
        "claude-4-sonnet": "anthropic/claude-sonnet-4-20250514", 
        "grok-3-beta": "xai/grok-3-beta",
        "grok-3-mini": "xai/grok-3-mini-beta",
        "o3-mini": "openai/o3-mini",
        "o3-pro": "openai/o3-pro",
        "gpt-4o": "openai/gpt-4o",
        "gemini-2.5-pro": "vertex_ai/gemini-2.5-pro",
        "gemini-2.5-flash": "vertex_ai/gemini-2.5-flash"
    }
    
    # Use mapped model or the provided model_type directly
    litellm_model = model_mapping.get(model_type.lower(), model_type)
    
    try:
        return call_model_litellm(prompt, litellm_model, system_prompt)
    except Exception as e:
        # Fallback to direct Claude API if LiteLLM fails
        if model_type.lower() in ["claude", "claude-sonnet"]:
            print(f"LiteLLM failed ({e}), falling back to direct Claude API")
            return call_claude_model(prompt, system_prompt)
        else:
            raise ValueError(f"Model type '{model_type}' failed with LiteLLM and no fallback available: {e}")
