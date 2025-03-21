"""
AI-Powered Interactive Story Game Engine
----------------------------------------
This module implements a multi-agent framework for generating interactive storytelling experiences.
The system uses LLM API calls to create dynamic narratives with character interactions and player choices.

Author: [Your Name]
GitHub: [Your GitHub Username]
"""

import re
import time
from typing import Dict, List, Tuple, Optional, Any, Union
from openai import OpenAI

# ==========================================================
# API CONFIGURATION
# ==========================================================

# Configure the client to use either OpenAI or Deepseek APIs

"""
OpenAI API(GPT)
"""
# Initialize the OpenAI client with your API key
# Use your OpenAI API key to replace "sk-proj-xxx" below
# client = OpenAI(api_key="sk-proj-xxx")

"""
Deepseek
"""
client = OpenAI(
    # Use your Aliyun API Key to replace "sk-xxx" below
    api_key="sk-xxx",
    base_url="https://dashscope.aliyuncs.com/compatible-mode/v1"
)

# Model selection
model = "deepseek-r1"
# Alternate options:
# model = "gpt-4o-mini"  # For OpenAI

# ==========================================================
# AGENT DEFINITIONS
# ==========================================================

# Define agents with specific roles and system prompts
agents = {
    "world_manager": {
        "system_prompt": """You are a story constructor. You will write a story based on some keywords, including as many details as possible. The story's beginning should end with at least two characters appearing, with one of them being the protagonist. End with the scene of their meeting.
                        
                        Output the character names at the end in the following format, with the first character always being the protagonist, for example:
                        Character List:
                        1. Ami
                        2. Qinghe""", 
        "history": []
    },
    "character_maker": {
        "system_prompt": "You are a character creator. Based on the input provided, you will craft a concise character backstory.", 
        "history": []
    }
}

def add_agent(agent_name: str, system_prompt: str) -> None:
    """
    Add a new agent to the system.
    
    Args:
        agent_name: Name of the new agent
        system_prompt: System prompt that defines the agent's behavior
    """
    agents[agent_name] = {"system_prompt": system_prompt, "history": []}

# ==========================================================
# RESPONSE VALIDATION
# ==========================================================

class ResponseValidator:
    """
    Validates responses from different AI agents in the story game.
    Ensures that outputs follow expected formats and contain necessary elements.
    """
    
    def validate_world_manager_init(self, response: str) -> Tuple[bool, Optional[str], List[str]]:
        """
        Validates the initial story from the world_manager agent.
        
        Args:
            response: The response from the world_manager
            
        Returns:
            Tuple containing:
                - Boolean indicating if validation passed
                - Error message if validation failed
                - List of extracted character names if validation passed
        """
        # Check if response is not empty
        if not response or len(response.strip()) < 100:
            return False, "Response is too short or empty", []
        
        # Check if there's a story narrative
        if len(response.split('\n\n')) < 2:
            return False, "Response does not contain a proper narrative", []
        
        # Check for character list
        character_list_match = re.search(r"Character List:[\s\S]*?\d+\.\s*.+", response)
        if not character_list_match:
            return False, "Response does not contain a Character List", []
        
        # Improved character list extraction logic
        # Step 1: Locate the character list section
        char_section = re.search(
            r"(?i)\*{0,2}Character List:\*{0,2}(.*?)(?=\n\n|\Z)", 
            response, 
            re.DOTALL
        )
        
        if not char_section:
            return False, "Response does not contain a Character List", []
        
        # Step 2: Extract all numbered character entries
        matches = re.findall(r"\d+\.\s*([^\n$$]+)", char_section.group(1))
        
        # Clean data: Remove parenthetical notes after character names
        characters = [name.split('(')[0].strip() for name in matches]
        
        # Verify at least two characters
        if len(characters) < 2:
            return False, "Response does not contain at least two character names", []
        
        return True, None, characters[:2]
    
    def validate_character_background(self, response: str) -> Tuple[bool, Optional[str]]:
        """
        Validates the character background from the character_maker agent.
        
        Args:
            response: The response from the character_maker
            
        Returns:
            Tuple containing:
                - Boolean indicating if validation passed
                - Error message if validation failed
        """
        # Check if response is not empty
        if not response or len(response.strip()) < 100:
            return False, "Character background is too short or empty"
        
        # Check for background section
        if "Background" not in response:
            return False, "Response does not contain a Background section"
        
        # Check for personality section
        if "Personality" not in response:
            return False, "Response does not contain a Personality section"
        
        return True, None
    
    def validate_character_dialogue(self, response: str) -> Tuple[bool, Optional[str], Dict[str, str]]:
        """
        Validates the dialogue and options from a character agent.
        
        Args:
            response: The response from the character agent
            
        Returns:
            Tuple containing:
                - Boolean indicating if validation passed
                - Error message if validation failed
                - Dictionary of options {A, B, C} -> option text
        """
        # Check if response is not empty
        if not response or len(response.strip()) < 50:
            return False, "Dialogue response is too short or empty", {}
        
        # Split by option markers
        parts = re.split(r'\n\s*([A-C])\.\s+', response)
        
        # The first element is the text before any option
        options_dict = {}
        
        # Process parts - they will be in format [pre-text, A, A-text, B, B-text, C, C-text]
        for i in range(1, len(parts), 2):
            if i+1 < len(parts):
                letter = parts[i]
                option_text = parts[i+1]
                options_dict[letter] = option_text
        
        # Check if we have exactly 3 options: A, B, and C
        if set(options_dict.keys()) != {'A', 'B', 'C'}:
            return False, f"Response does not contain all required options (found {options_dict.keys()})", {}
        
        return True, None, options_dict
    
    def validate_story_continuation(self, response: str) -> Tuple[bool, Optional[str]]:
        """
        Validates the story continuation from the world_manager agent.
        
        Args:
            response: The response from the world_manager
            
        Returns:
            Tuple containing:
                - Boolean indicating if validation passed
                - Error message if validation failed
        """
        # Check if response is not empty
        if not response or len(response.strip()) < 200:
            return False, "Story continuation is too short or empty"
        
        # Check for narrative elements (paragraphs)
        paragraphs = response.split('\n\n')
        if len(paragraphs) < 3:
            return False, "Story continuation does not have enough paragraphs"
        
        # Check for dialogue (presence of quotation marks)
        if not re.search(r'"([^"]*)"', response):
            return False, "Story continuation does not contain any dialogue"
        
        # Look for character interactions
        if not re.search(r'([A-Z][a-z]+)\s+(?:said|replied|asked|shouted|whispered)', response):
            return False, "Story continuation does not show character interactions"
        
        # Updated character list should be present
        character_list_match = re.search(r"Character List:[\s\S]*?\d+\.\s*.+", response)
        if not character_list_match:
            return False, "Story continuation does not contain an updated Character List", []
        
        return True, None

# ==========================================================
# VALIDATION AND RETRY LOGIC
# ==========================================================

def validate_and_retry(agent_name: str, validator: ResponseValidator, 
                       chat_func, prompt: str, max_attempts: int = 3) -> Dict[str, Any]:
    """
    Attempts to get a valid response from an agent, retrying if validation fails.
    
    Args:
        agent_name: Name of the agent to chat with
        validator: ResponseValidator instance
        chat_func: Function to call for chatting with the agent
        prompt: The prompt to send to the agent
        max_attempts: Maximum number of retry attempts
        
    Returns:
        Dictionary containing:
            - success: Boolean indicating if a valid response was obtained
            - response: The validated response (if success is True)
            - error: Error message (if success is False)
            - additional data (e.g., characters, options) if applicable
    """
    attempt = 0
    result = {"success": False, "response": None, "error": None}
    
    while attempt < max_attempts:
        attempt += 1
        
        try:
            response = chat_func(agent_name, prompt)
            
            # Apply the appropriate validation based on agent type and context
            if agent_name == "world_manager" and "initial story" in prompt.lower():
                valid, error, characters = validator.validate_world_manager_init(response)
                if valid:
                    result = {"success": True, "response": response, "characters": characters}
                    break
            
            elif agent_name == "character_maker":
                valid, error = validator.validate_character_background(response)
                if valid:
                    result = {"success": True, "response": response}
                    break
            
            elif agent_name == "world_manager" and "continue" in prompt.lower():
                valid, error = validator.validate_story_continuation(response)
                if valid:
                    result = {"success": True, "response": response}
                    break
            
            elif "options" in prompt.lower() or any(option in prompt for option in ["A", "B", "C"]):
                valid, error, options = validator.validate_character_dialogue(response)
                if valid:
                    result = {"success": True, "response": response, "options": options}
                    break
            
            else:
                # Default validation - just check if response is not empty
                if response and len(response.strip()) > 0:
                    result = {"success": True, "response": response}
                    break
                else:
                    error = "Empty response"
            
            # If we get here, validation failed - prepare for retry
            retry_prompt = prompt + "\n\nThe previous response was invalid because: " + error + ". Please try again and ensure your response includes all required elements."
            prompt = retry_prompt
            
        except Exception as e:
            # Handle API errors or other exceptions
            error = f"Error communicating with the agent: {str(e)}"
            
            # For API errors, we might want to retry with exponential backoff
            time.sleep(2 ** attempt)  # Exponential backoff: 2, 4, 8 seconds
    
    if not result["success"]:
        result["error"] = f"Failed to get valid response after {max_attempts} attempts. Last error: {error}"
    
    return result

# ==========================================================
# UTILITY FUNCTIONS
# ==========================================================

def extract_characters_from_story(response: str) -> List[str]:
    """
    Extract character names from a story response.
    
    Args:
        response: The story text from world_manager
        
    Returns:
        List of character names
        
    Raises:
        ValueError: If character extraction fails
    """
    validator = ResponseValidator()
    valid, error, characters = validator.validate_world_manager_init(response)
    if valid:
        return characters
    else:
        raise ValueError(f"Cannot extract characters: {error}")


def extract_options_from_dialogue(response: str) -> Dict[str, str]:
    """
    Extract the three options (A, B, C) from a dialogue response.
    
    Args:
        response: The dialogue text from character agent
        
    Returns:
        Dictionary mapping option letters to option text
        
    Raises:
        ValueError: If option extraction fails
    """
    validator = ResponseValidator()
    valid, error, options = validator.validate_character_dialogue(response)
    if valid:
        return options
    else:
        raise ValueError(f"Cannot extract options: {error}")

# ==========================================================
# AGENT COMMUNICATION
# ==========================================================

def chat_with_agent(agent_name: str, user_prompt: str, validate: bool = True) -> str:
    """
    Enhanced function to chat with an agent with validation.
    
    Args:
        agent_name: The name of the agent to chat with
        user_prompt: The prompt to send to the agent
        validate: Whether to validate the response
        
    Returns:
        The agent's response if validate=False or validation passes
        
    Raises:
        ValueError: If agent not found or validation fails
    """
    if agent_name not in agents:
        raise ValueError(f"Agent '{agent_name}' not found.")
    
    # Get agent information
    agent_info = agents[agent_name]
    
    # Combine system setting and history into a message list
    messages = [{"role": "system", "content": agent_info["system_prompt"]}] + agent_info["history"] + [{"role": "user", "content": user_prompt}]
    
    # Call API to get response
    response = client.chat.completions.create(
        model=model,
        messages=messages
    )
    
    # Extract assistant's reply
    reply = response.choices[0].message.content
    
    # Add user's question and assistant's reply to history
    agent_info["history"].append({"role": "user", "content": f"user_prompt:<{user_prompt}>"})
    agent_info["history"].append({"role": "assistant", "content": reply})
    
    # Validate the response if requested
    if validate:
        validator = ResponseValidator()
        
        # Determine which validation to use based on agent and prompt
        if agent_name == "world_manager" and "story beginning" in user_prompt.lower():
            valid, error, _ = validator.validate_world_manager_init(reply)
            if not valid:
                raise ValueError(f"World manager response validation failed: {error}")
                
        elif agent_name == "character_maker" and "Background and Personality" in user_prompt:
            valid, error = validator.validate_character_background(reply)
            if not valid:
                raise ValueError(f"Character background validation failed: {error}")
                
        elif "provide 3 possible replies" in user_prompt.lower():
            valid, error, _ = validator.validate_character_dialogue(reply)
            if not valid:
                raise ValueError(f"Dialogue options validation failed: {error}")
                
        elif agent_name == "world_manager" and "continue writing the story" in user_prompt.lower():
            valid, error = validator.validate_story_continuation(reply)
            if not valid:
                raise ValueError(f"Story continuation validation failed: {error}")
    
    return reply

# ==========================================================
# GAME ENGINE CORE FUNCTIONS
# ==========================================================

# Store conversation history
chats = []
History = ""

def generate_world(theme: str, max_attempts: int = 3) -> Tuple[Optional[str], Optional[List]]:
    """
    Generate an initial story world with characters based on a theme.
    
    Args:
        theme: Theme for the story
        max_attempts: Maximum retry attempts
        
    Returns:
        Tuple of (story_text, character_list) or (None, None) if generation fails
    """
    attempt = 0
    while attempt < max_attempts:
        try:
            user_prompt = f"Please help me write a story beginning with the theme of '{theme} Story'"
            world_overview = chat_with_agent("world_manager", user_prompt)

            validator = ResponseValidator()
            valid, error, characters = validator.validate_world_manager_init(world_overview)

            if not valid or not characters or len(characters) < 2:
                raise ValueError(f"Failed to extract character names: {error}")
            
            return world_overview, characters
        except Exception as e:
            attempt += 1
            print(f"Attempt {attempt} failed: {str(e)}")
    print("Max attempts reached. Unable to generate initial story.")
    return None, None

def generate_character_background(world_overview: str, character_name: str, max_attempts: int = 3) -> Optional[str]:
    """
    Generate a background for a character in the story.
    
    Args:
        world_overview: The story context
        character_name: Name of the character to generate background for
        max_attempts: Maximum retry attempts
        
    Returns:
        Character background text or None if generation fails
    """
    attempt = 0
    while attempt < max_attempts:
        try:
            user_prompt = world_overview + f"\n\nHelp me write a Background and Personality for {character_name}"
            character_overview = chat_with_agent("character_maker", user_prompt)
            return character_overview
        except Exception as e:
            attempt += 1
            print(f"Attempt {attempt} failed: {str(e)}")
    print("Max attempts reached. Unable to generate character background.")
    return None

def add_character_agent(character_name: str) -> None:
    """
    Add a new agent for a character in the story.
    
    Args:
        character_name: Name of the character to add as an agent
    """
    try:
        add_agent(character_name, f"You will play the specified character '{character_name}' based on the received information.")
    except Exception as e:
        print(f"Failed to add character agent: {str(e)}")

def generate_dialogue(world_overview: str, character_overview: str, characters: List, max_attempts: int = 3) -> Optional[str]:
    """
    Generate a dialogue scene between characters with player choice options.
    
    Args:
        world_overview: Story context
        character_overview: Background of the non-player character
        characters: List of character names in the story
        max_attempts: Maximum retry attempts
        
    Returns:
        Dialogue text with options or None if generation fails
    """
    attempt = 0
    while attempt < max_attempts:
        try:
            user_prompt = (f"{world_overview}{character_overview}\n\nNow you will play a dialogue between {characters[1]} and {characters[0]},"
                           f" your task is to develop the story through questions and answers. \n\n"
                           f"'Focus on storytelling' by using specific expressions to drive the story forward.\n"
                           f"The protagonist and you will take turns speaking. Provide responses and 3 possible replies strictly formatted as follows:\n\n"
                           f"A. **\"First option text here\"**\n"
                           f"B. **\"Second option text here\"**\n"
                           f"C. **\"Third option text here\"**\n\n"
                           f"These options should genuinely change the story's direction and be labeled as shown above."
                           f"I will tell you which answer the protagonist chooses.")
            chats.append(chat_with_agent(characters[1], user_prompt))
            print("The conversation is as follows:\n", chats[-1])
            return chats[-1]
        except Exception as e:
            attempt += 1
            print(f"Attempt {attempt} failed: {str(e)}")
    print("Max attempts reached. Unable to generate dialogue.")
    return None

def process_player_choice(character_name: str, choice: str) -> Optional[str]:
    """
    Process a player's choice from the options and generate the next story segment.
    
    Args:
        character_name: The character agent to respond to the choice
        choice: Player's choice (A, B, or C)
        
    Returns:
        Next dialogue text or None if processing fails
    """
    if choice not in ["A", "B", "C"]:
        print("Invalid choice. Please choose A, B, or C.")
        return None

    result = validate_and_retry(
        agent_name=character_name,
        validator=ResponseValidator(),
        chat_func=chat_with_agent,
        prompt=choice,
        max_attempts=3
    )

    if result["success"]:
        next_dialogue = result["response"]
        print("The conversation continues:\n", next_dialogue)
        return next_dialogue
    else:
        raise Exception(f"Failed to process choice: {result['error']}")

# ==========================================================
# MAIN GAME FLOW
# ==========================================================

def safe_story_progression(max_attempts: int = 3, theme: str = "Town Suspense") -> Optional[Dict]:
    """
    Run the complete story generation process safely with error handling.
    
    Args:
        max_attempts: Maximum retry attempts for each step
        theme: Theme for the story
        
    Returns:
        Dictionary with story components or None if generation fails
    """
    # Step 1: Generate world and characters
    world_overview, characters = generate_world(theme, max_attempts)
    if not world_overview or not characters:
        return None
    print(world_overview)

    # Step 2: Generate character background
    character_overview = generate_character_background(world_overview, characters[1], max_attempts)
    if not character_overview:
        return None

    # Step 3: Add character agent
    add_character_agent(characters[1])

    # Step 4: Generate initial dialogue
    dialogue = generate_dialogue(world_overview, character_overview, characters, max_attempts)
    if not dialogue:
        return None

    # Return all generated story components
    return {
        "world_overview": world_overview,
        "characters": characters,
        "character_overview": character_overview,
        "chats": chats
    }

# ==========================================================
# EXECUTION
# ==========================================================

# Run the story progression
if __name__ == "__main__":
    # Generate the initial story
    result = safe_story_progression()
    
    if result:
        # Process player's first choice
        process_player_choice(result["characters"][1], "A")

    # Add more choices here to continue the story
    # Example:
    # process_player_choice(result["characters"][1], "B")
    # process_player_choice(result["characters"][1], "C")
    # ...