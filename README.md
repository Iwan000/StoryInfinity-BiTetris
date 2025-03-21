# StoryInfinity-BiTetris

# 1. StoryInfinity: AI-Powered Interactive Story Game Engine

An intelligent multi-agent framework for generating dynamic, interactive storytelling experiences. This system uses Large Language Models to create narratives with character interactions and meaningful player choices.

## 🌟 Features

- **Dynamic Story Generation**: Creates unique narratives based on themes
- **Character Development**: Builds detailed character backgrounds and personalities
- **Interactive Dialogue**: Generates realistic conversations with multiple choice options
- **Story Branching**: Player choices affect the direction of the narrative
- **Validation System**: Ensures quality and consistency in AI-generated content
- **Error Recovery**: Implements robust retry mechanisms for reliable performance

## 🚀 Getting Started

### Prerequisites

- Python 3.8+
- An API key for either OpenAI or Deepseek

### Installation

1. Clone this repository:
   ```bash
   git clone https://github.com/Iwan000/StoryInfinity-BiTetris.git
   cd ai-story-game
   ```

2. Install required packages:

3. Configure your API key in the code:
   ```python
   # In the code, update the API key
   client = OpenAI(
       api_key="your-api-key-here",
       base_url="https://dashscope.aliyuncs.com/compatible-mode/v1"  # For Deepseek
       # Remove base_url for OpenAI
   )
   ```

## 📖 Usage

```python
from story_engine import safe_story_progression, process_player_choice

# Generate a new story with a specific theme
story = safe_story_progression(theme="Space Adventure")

# Display the story beginning and first dialogue options
print(story["world_overview"])
print(story["chats"][-1])

# Process a player choice (A, B, or C)
next_dialogue = process_player_choice(story["characters"][1], "A")
```

## 🧩 How It Works

The system consists of multiple AI agents working together:

1. **World Manager**: Creates the story setting, plot, and characters
2. **Character Maker**: Develops detailed backstories for characters
3. **Character Agents**: Role-play as specific characters, generating dialogue and responses

Each agent has a specific role defined by a system prompt, and their outputs are validated to ensure quality and consistency.

## 🔍 System Architecture

```
┌─────────────────┐     ┌─────────────────┐     ┌─────────────────┐
│  World Manager  │────▶│ Character Maker │────▶│ Character Agent │
└─────────────────┘     └─────────────────┘     └─────────────────┘
        │                                               │
        └───────────────────┬───────────────────────────┘
                            ▼
                  ┌─────────────────────┐
                  │ Validation & Retry  │
                  └─────────────────────┘
                            │
                            ▼
                  ┌─────────────────────┐
                  │    Story Flow       │
                  └─────────────────────┘
```

## 🛠️ Customization

### Modifying Agent Prompts

You can customize the behavior of agents by modifying their system prompts:

```python
agents = {
    "world_manager": {
        "system_prompt": """Your custom prompt here...""", 
        "history": []
    },
    # ...
}
```

### Adding New Agents

Create specialized agents for different story roles:

```python
add_agent("detective", "You are a detective character who investigates mysteries...")
```

## 📋 Example Output

```
[Story beginning with two characters meeting...]

The conversation is as follows:
 
Detective Morgan looked at the strange symbol carved into the tree. "I've never seen anything like this before. What do you make of it, Dr. Chen?"

Dr. Chen adjusted her glasses, studying the marking carefully. "It's similar to ancient protective sigils, but there's something... different about it. Almost as if it's been modified for a specific purpose."

Morgan nodded thoughtfully. "What do you think our next move should be?"

A. **"We should take a sample and analyze it back at the lab. There might be trace elements that could tell us who carved it."**
B. **"Let's search the surrounding area. Whoever made this might have left other clues nearby."**
C. **"I think we should speak with the locals. Someone in town might recognize this symbol or know who's been in these woods recently."**
```

## 📝 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 🙏 Acknowledgments

- This project uses the OpenAI/Deepseek API for language model inference
- Inspired by interactive fiction and role-playing games

---

## 🤝 Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add some amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

