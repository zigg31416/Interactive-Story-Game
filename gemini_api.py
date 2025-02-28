import json
import requests
import os
import streamlit as st

class GeminiAPI:
    """
    Client for Google's Gemini API
    """
    def __init__(self, api_key=None):
        # Use provided API key or get from streamlit secrets/environment variable
        self.api_key = api_key or st.secrets.get("GEMINI_API_KEY", os.environ.get("GEMINI_API_KEY"))
        if not self.api_key:
            raise ValueError("Gemini API key is required. Set it in Streamlit secrets or environment variable GEMINI_API_KEY.")
        
        # Gemini API endpoint
        self.api_url = "https://generativelanguage.googleapis.com/v1beta/models/gemini-pro:generateContent"
        
        # Headers for API requests
        self.headers = {
            "Content-Type": "application/json",
        }
    
    def generate_story(self, prompt, player_name, genre, max_tokens=200):
        """
        Generate story content using Gemini API
        
        Args:
            prompt: The specific story prompt
            player_name: The player's character name
            genre: The story genre
            max_tokens: Maximum number of tokens to generate
            
        Returns:
            str: Generated story text
        """
        # Format context with player and genre information
        context = f"Genre: {genre}. Character: {player_name}. "
        
        # Construct the full prompt
        full_prompt = f"{context}{prompt}"
        
        # Prepare the payload for the API
        payload = {
            "contents": [
                {
                    "parts": [
                        {"text": full_prompt}
                    ]
                }
            ],
            "generationConfig": {
                "temperature": 0.7,
                "topP": 0.9,
                "topK": 40,
                "maxOutputTokens": max_tokens
            }
        }
        
        try:
            # Make the API request with API key as query parameter
            response = requests.post(
                f"{self.api_url}?key={self.api_key}",
                headers=self.headers,
                data=json.dumps(payload)
            )
            
            # Check if the request was successful
            response.raise_for_status()
            
            # Parse the response
            result = response.json()
            
            # Extract the generated text from Gemini's response format
            generated_text = result.get("candidates", [{}])[0].get("content", {}).get("parts", [{}])[0].get("text", "")
            
            if not generated_text:
                return "The storyteller pauses, struggling to find the right words..."
                
            return generated_text
        
        except requests.exceptions.HTTPError as http_err:
            print(f"HTTP error occurred: {http_err}")
            print(f"Response content: {response.text}")
            return f"Error: {http_err}"
        except Exception as err:
            print(f"An error occurred: {err}")
            return "The storyteller pauses, gathering thoughts..."

# Example usage (for testing purposes)
if __name__ == "__main__":
    # Get API key from environment
    api_key = os.environ.get("GEMINI_API_KEY")
    
    if not api_key:
        print("Please set GEMINI_API_KEY environment variable")
        exit(1)
        
    # Initialize the API client
    gemini_client = GeminiAPI(api_key)
    
    # Generate a story
    story = gemini_client.generate_story(
        prompt="Start a horror story where the main character discovers an old book",
        player_name="Alex",
        genre="Horror"
    )
    
    print(story)
