import requests
import json
import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

class MistralAPI:
    """
    Client for Mistral AI API
    """
    def __init__(self, api_key=None):
        # Use provided API key or get from environment variable
        self.api_key = api_key or os.environ.get("MISTRAL_API_KEY")
        if not self.api_key:
            raise ValueError("Mistral API key is required. Set it as an environment variable MISTRAL_API_KEY or pass it directly.")
        
        # Mistral API endpoint for Mistral-7B-Instruct model
        self.api_url = "https://api.mistral.ai/v1/chat/completions"
        
        # Headers for API requests
        self.headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {self.api_key}"
        }
    
    def generate_story(self, prompt, player_name, genre, max_tokens=200):
        """
        Generate story content using Mistral API
        
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
            "model": "mistral-7b-instruct", # or "open-mistral-7b" depending on API provider
            "messages": [
                {"role": "user", "content": full_prompt}
            ],
            "max_tokens": max_tokens,
            "temperature": 0.7,
            "top_p": 0.9
        }
        
        try:
            # Make the API request
            response = requests.post(
                self.api_url,
                headers=self.headers,
                data=json.dumps(payload)
            )
            
            # Check if the request was successful
            response.raise_for_status()
            
            # Parse the response
            result = response.json()
            
            # Extract the generated text
            generated_text = result["choices"][0]["message"]["content"]
            
            return generated_text
        
        except requests.exceptions.HTTPError as http_err:
            print(f"HTTP error occurred: {http_err}")
            return f"Error: {http_err}"
        except Exception as err:
            print(f"An error occurred: {err}")
            return "The storyteller pauses, gathering thoughts..."
