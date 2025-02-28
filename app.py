import streamlit as st
import json
import random
import time
from datetime import datetime
import streamlit_lottie as st_lottie
import requests
import os
from dotenv import load_dotenv
from mistral_api import MistralAPI

# Load environment variables
load_dotenv()

# App configuration
st.set_page_config(
    page_title="Interactive Story Adventure",
    page_icon="📚",
    layout="centered",
    initial_sidebar_state="collapsed"
)

# Custom CSS for a modern UI
st.markdown("""
<style>
    .main {
        background-color: #f5f5f5;
    }
    .stButton>button {
        width: 100%;
        border-radius: 10px;
        height: 3em;
        font-weight: 500;
        margin-top: 1em;
    }
    .story-text {
        background-color: white;
        padding: 20px;
        border-radius: 10px;
        box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
        margin-bottom: 20px;
    }
    .choice-button {
        background-color: #4e89ae;
        color: white;
        transition: all 0.3s;
    }
    .choice-button:hover {
        background-color: #43658b;
        transform: translateY(-2px);
    }
    .title {
        text-align: center;
        color: #2a2a2a;
    }
    .genre-card {
        border: 1px solid #e0e0e0;
        border-radius: 10px;
        padding: 15px;
        margin: 5px;
        text-align: center;
        cursor: pointer;
        transition: all 0.3s;
    }
    .genre-card:hover {
        transform: translateY(-5px);
        box-shadow: 0 10px 20px rgba(0, 0, 0, 0.1);
    }
    .selected-genre {
        border: 2px solid #4e89ae;
        background-color: #e6f2ff;
    }
</style>
""", unsafe_allow_html=True)

# Function to load Lottie animations
def load_lottieurl(url):
    try:
        r = requests.get(url, timeout=10)
        if r.status_code == 200:
            return r.json()
        else:
            st.warning(f"Failed to load animation from {url}. Status code: {r.status_code}")
            # Return a simple fallback animation
            return {"v":"5.5.7","fr":60,"ip":0,"op":60,"w":100,"h":100,"nm":"Simple Animation",
                    "ddd":0,"assets":[],"layers":[{"ddd":0,"ind":1,"ty":4,"nm":"Shape Layer",
                    "sr":1,"ks":{"o":{"a":0,"k":100},"r":{"a":1,"k":[{"i":{"x":[0.833],"y":[0.833]},
                    "o":{"x":[0.167],"y":[0.167]},"t":0,"s":[0]},{"t":60,"s":[360]}]},"p":{"a":0,
                    "k":[50,50,0]},"a":{"a":0,"k":[0,0,0]},"s":{"a":0,"k":[100,100,100]}},"ao":0,
                    "shapes":[{"ty":"rc","d":1,"s":{"a":0,"k":[50,50]},"p":{"a":0,"k":[0,0]},
                    "r":{"a":0,"k":0},"nm":"Rectangle Path 1","mn":"ADBE Vector Shape - Rect",
                    "hd":false},{"ty":"fl","c":{"a":0,"k":[0.30980392156862746,0.5372549019607843,
                    0.6823529411764706,1]},"o":{"a":0,"k":100},"r":1,"bm":0,"nm":"Fill 1",
                    "mn":"ADBE Vector Graphic - Fill","hd":false}],"ip":0,"op":60,"st":0,"bm":0}]}
    except requests.exceptions.RequestException as e:
        st.warning(f"Error loading animation: {e}")
        # Return a simple fallback animation in case of any request exception
        return {"v":"5.5.7","fr":60,"ip":0,"op":60,"w":100,"h":100,"nm":"Simple Animation",
                "ddd":0,"assets":[],"layers":[{"ddd":0,"ind":1,"ty":4,"nm":"Shape Layer",
                "sr":1,"ks":{"o":{"a":0,"k":100},"r":{"a":1,"k":[{"i":{"x":[0.833],"y":[0.833]},
                "o":{"x":[0.167],"y":[0.167]},"t":0,"s":[0]},{"t":60,"s":[360]}]},"p":{"a":0,
                "k":[50,50,0]},"a":{"a":0,"k":[0,0,0]},"s":{"a":0,"k":[100,100,100]}},"ao":0,
                "shapes":[{"ty":"rc","d":1,"s":{"a":0,"k":[50,50]},"p":{"a":0,"k":[0,0]},
                "r":{"a":0,"k":0},"nm":"Rectangle Path 1","mn":"ADBE Vector Shape - Rect",
                "hd":false},{"ty":"fl","c":{"a":0,"k":[0.30980392156862746,0.5372549019607843,
                0.6823529411764706,1]},"o":{"a":0,"k":100},"r":1,"bm":0,"nm":"Fill 1",
                "mn":"ADBE Vector Graphic - Fill","hd":false}],"ip":0,"op":60,"st":0,"bm":0}]}

# Initialize session state variables if they don't exist
if 'story_data' not in st.session_state:
    st.session_state.story_data = {}
if 'current_scene' not in st.session_state:
    st.session_state.current_scene = "start"
if 'player_name' not in st.session_state:
    st.session_state.player_name = ""
if 'genre' not in st.session_state:
    st.session_state.genre = ""
if 'story_history' not in st.session_state:
    st.session_state.story_history = []
if 'choice_count' not in st.session_state:
    st.session_state.choice_count = 0
if 'game_ended' not in st.session_state:
    st.session_state.game_ended = False
if 'story_start_time' not in st.session_state:
    st.session_state.story_start_time = None

# Lottie animations for different genres
lottie_animations = {
    "Horror": "https://lottie.host/8fcea21b-0c0c-4c8e-a00d-07cd50208b15/6Aig9AUo6B.json",
    "Adventure": "https://lottie.host/6aa60fda-82ae-484c-a643-d90c89d5b93a/UEVeBwm8mr.json",
    "Romance": "https://lottie.host/24a3d573-cd22-4c2d-a1b5-a1c7e6cd7a15/J0IjWIK2nV.json",
    "Fantasy": "https://lottie.host/db619f82-6611-4989-b458-c34a29e79eda/v5s0OdvkGS.json",
    "Sci-Fi": "https://lottie.host/d0bca245-d46b-4222-82c0-0d36a2ba3c30/LZGvDOcPDn.json",
    "Mystery": "https://lottie.host/21319eb1-7767-4383-9cf5-f8ee8b6cee7e/ZVUkVDsZzt.json"
}

# Function to initialize or reset the game
def reset_game():
    st.session_state.story_data = {}
    st.session_state.current_scene = "start"
    st.session_state.player_name = ""
    st.session_state.genre = ""
    st.session_state.story_history = []
    st.session_state.choice_count = 0
    st.session_state.game_ended = False
    st.session_state.story_start_time = None

# Initialize Mistral API
@st.cache_resource
def load_mistral_api():
    """Initialize and cache the Mistral API client"""
    try:
        # Get API key from secrets or environment
        api_key = st.secrets.get("MISTRAL_API_KEY", os.environ.get("MISTRAL_API_KEY"))
        
        if not api_key:
            st.error("Mistral API key not found. Please set it in your Streamlit secrets or as an environment variable.")
            return None
            
        # Create API client
        return MistralAPI(api_key)
    except Exception as e:
        st.error(f"Failed to initialize Mistral API: {str(e)}")
        return None

# Generate story content using AI
def generate_story_content(prompt, max_length=150):
    api_client = load_mistral_api()
    if api_client:
        try:
            # Generate text via API
            return api_client.generate_story(
                prompt=prompt,
                player_name=st.session_state.player_name,
                genre=st.session_state.genre,
                max_tokens=max_length
            )
        except Exception as e:
            st.error(f"Error generating story content: {str(e)}")
            return "The story continues but the words are difficult to discern..."
    else:
        return "The storyteller pauses, gathering thoughts..."

# Function to create a new scene with AI-generated content
def create_new_scene(scene_prompt, option1_prompt, option2_prompt):
    scene_text = generate_story_content(scene_prompt, max_length=200)
    option1 = generate_story_content(option1_prompt, max_length=50)
    option2 = generate_story_content(option2_prompt, max_length=50)
    
    # Create a unique scene ID
    scene_id = f"scene_{len(st.session_state.story_data) + 1}"
    
    # Store scene data
    st.session_state.story_data[scene_id] = {
        "text": scene_text,
        "options": [
            {"text": option1, "next_scene": None},
            {"text": option2, "next_scene": None}
        ]
    }
    
    return scene_id

# Function to select a choice and proceed to the next scene
def make_choice(choice_index):
    current_scene = st.session_state.current_scene
    
    # Record current scene in history
    st.session_state.story_history.append({
        "scene": current_scene,
        "text": st.session_state.story_data[current_scene]["text"],
        "choice": choice_index,
        "choice_text": st.session_state.story_data[current_scene]["options"][choice_index]["text"]
    })
    
    # Increment choice counter
    st.session_state.choice_count += 1
    
    # Check if we've reached the maximum number of choices (ending)
    if st.session_state.choice_count >= 20:
        st.session_state.game_ended = True
        scene_prompt = f"Conclude the story with an epic ending where {st.session_state.player_name} finishes their journey."
        final_scene = create_new_scene(scene_prompt, "Play again", "Download story")
        st.session_state.current_scene = final_scene
        return
    
    # Generate the next scene based on the player's choice
    choice_text = st.session_state.story_data[current_scene]["options"][choice_index]["text"]
    
    # Create prompts for the next scene based on the choice
    scene_prompt = f"Continue the story after {st.session_state.player_name} chose to {choice_text}"
    option1_prompt = f"First possible action for {st.session_state.player_name} after this scene"
    option2_prompt = f"Second possible action for {st.session_state.player_name} after this scene, different from the first"
    
    # Create the new scene
    next_scene = create_new_scene(scene_prompt, option1_prompt, option2_prompt)
    
    # Update the current scene's option to point to the new scene
    st.session_state.story_data[current_scene]["options"][choice_index]["next_scene"] = next_scene
    
    # Move to the new scene
    st.session_state.current_scene = next_scene

# Function to compile the full story from history
def compile_story():
    story_text = f"# {st.session_state.player_name}'s {st.session_state.genre} Adventure\n\n"
    
    for i, entry in enumerate(st.session_state.story_history):
        scene_text = entry["text"]
        choice_text = entry["choice_text"]
        
        story_text += f"## Chapter {i+1}\n\n"
        story_text += f"{scene_text}\n\n"
        story_text += f"*{st.session_state.player_name} chose to {choice_text}*\n\n"
    
    # Add the final scene
    if st.session_state.game_ended and st.session_state.current_scene in st.session_state.story_data:
        final_scene = st.session_state.story_data[st.session_state.current_scene]
        story_text += f"## The End\n\n"
        story_text += final_scene["text"]
    
    # Add completion time
    if st.session_state.story_start_time:
        elapsed_time = time.time() - st.session_state.story_start_time
        minutes, seconds = divmod(elapsed_time, 60)
        story_text += f"\n\n---\n\n"
        story_text += f"Story completed in {int(minutes)} minutes and {int(seconds)} seconds.\n"
        story_text += f"Made {st.session_state.choice_count} choices in this adventure.\n"
        story_text += f"Generated on {datetime.now().strftime('%B %d, %Y')}"
    
    return story_text

# Main game flow
def main():
    # Title with animation
    st.markdown("<h1 class='title'>Interactive Story Adventure</h1>", unsafe_allow_html=True)
    
    # Start screen - Genre selection
    if st.session_state.current_scene == "start" and not st.session_state.genre:
        st.markdown("## Choose Your Adventure Genre")
        
        # Display genre options in a grid with animations
        genres = ["Horror", "Adventure", "Romance", "Fantasy", "Sci-Fi", "Mystery"]
        cols = st.columns(3)
        
        for i, genre in enumerate(genres):
            with cols[i % 3]:
                # Display Lottie animation
                lottie_url = lottie_animations.get(genre)
                if lottie_url:
                    st_lottie.st_lottie(load_lottieurl(lottie_url), height=120, key=f"lottie_{genre}")
                
                # Create a clickable card for each genre
                selected = st.session_state.genre == genre
                genre_class = "genre-card selected-genre" if selected else "genre-card"
                
                if st.button(genre, key=f"genre_{genre}"):
                    st.session_state.genre = genre
                    st.experimental_rerun()
    
    # Player name input
    elif st.session_state.current_scene == "start" and st.session_state.genre and not st.session_state.player_name:
        st.markdown(f"## {st.session_state.genre} Adventure")
        
        # Show genre-appropriate animation
        lottie_url = lottie_animations.get(st.session_state.genre)
        if lottie_url:
            st_lottie.st_lottie(load_lottieurl(lottie_url), height=200)
        
        st.markdown("### What's your name, brave adventurer?")
        player_name = st.text_input("Enter your name", key="name_input")
        
        if st.button("Begin Your Adventure") and player_name:
            st.session_state.player_name = player_name
            
            # Create the initial scene
            scene_prompt = f"Start a {st.session_state.genre} story where the main character named {player_name} begins their journey."
            option1_prompt = f"First possible action for {player_name} at the beginning of this {st.session_state.genre} story"
            option2_prompt = f"Second possible action for {player_name} at the beginning of this {st.session_state.genre} story, different from the first"
            
            initial_scene = create_new_scene(scene_prompt, option1_prompt, option2_prompt)
            st.session_state.current_scene = initial_scene
            st.session_state.story_start_time = time.time()
            st.experimental_rerun()
    
    # Display current scene and choices
    elif st.session_state.current_scene in st.session_state.story_data:
        current_scene_data = st.session_state.story_data[st.session_state.current_scene]
        
        # Display choice counter and genre
        st.markdown(f"### {st.session_state.genre} Adventure • Choice {st.session_state.choice_count}/20")
        
        # Progress bar
        progress = min(st.session_state.choice_count / 20, 1.0)
        st.progress(progress)
        
        # Display the current scene text
        st.markdown(f"<div class='story-text'>{current_scene_data['text']}</div>", unsafe_allow_html=True)
        
        # Display choices if not at the end
        if not st.session_state.game_ended:
            st.markdown("### What will you do?")
            
            # Display options as buttons
            for i, option in enumerate(current_scene_data["options"]):
                if st.button(option["text"], key=f"option_{i}", use_container_width=True):
                    make_choice(i)
                    st.experimental_rerun()
        else:
            # End of game options
            col1, col2 = st.columns(2)
            with col1:
                if st.button("Play Again", use_container_width=True):
                    reset_game()
                    st.experimental_rerun()
            
            with col2:
                # Compile story and offer download
                full_story = compile_story()
                st.download_button(
                    label="Download Your Adventure",
                    data=full_story,
                    file_name=f"{st.session_state.player_name}s_{st.session_state.genre}_adventure.md",
                    mime="text/markdown",
                    use_container_width=True
                )
            
            # Show story preview
            st.markdown("## Your Adventure Preview")
            st.markdown(full_story)

if __name__ == "__main__":
    main()
