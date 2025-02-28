import streamlit as st
import json
import random
import time
from datetime import datetime
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

# Dictionary of genre icons
genre_icons = {
    "Horror": "👻",
    "Adventure": "🏔️", 
    "Romance": "❤️",
    "Fantasy": "🧙",
    "Sci-Fi": "🚀",
    "Mystery": "🔍"
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
    # Title
    st.markdown("<h1 class='title'>Interactive Story Adventure</h1>", unsafe_allow_html=True)
    
    # Start screen - Genre selection
    if st.session_state.current_scene == "start" and not st.session_state.genre:
        st.markdown("## Choose Your Adventure Genre")
        
        # Display genre options in a grid
        genres = ["Horror", "Adventure", "Romance", "Fantasy", "Sci-Fi", "Mystery"]
        cols = st.columns(3)
        
        for i, genre in enumerate(genres):
            with cols[i % 3]:
                # Create a card with icon for each genre
                icon = genre_icons.get(genre, "📖")
                
                # Style the selected genre
                if st.button(f"{icon} {genre}", key=f"genre_{genre}"):
                    st.session_state.genre = genre
                    st.rerun()
    
    # Player name input
    elif st.session_state.current_scene == "start" and st.session_state.genre and not st.session_state.player_name:
        st.markdown(f"## {st.session_state.genre} Adventure")
        icon = genre_icons.get(st.session_state.genre, "📖")
        st.markdown(f"### {icon} What's your name, brave adventurer?")
        
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
            st.rerun()
    
    # Display current scene and choices
    elif st.session_state.current_scene in st.session_state.story_data:
        current_scene_data = st.session_state.story_data[st.session_state.current_scene]
        
        # Display choice counter and genre
        icon = genre_icons.get(st.session_state.genre, "📖")
        st.markdown(f"### {icon} {st.session_state.genre} Adventure • Choice {st.session_state.choice_count}/20")
        
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
                    st.rerun()
        else:
            # End of game options
            col1, col2 = st.columns(2)
            with col1:
                if st.button("Play Again", use_container_width=True):
                    reset_game()
                    st.rerun()
            
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
