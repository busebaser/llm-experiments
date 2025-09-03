## 🎵 Music Finder & Translator

This project is a lightweight AI-powered tool that helps you identify songs from a lyric snippet and translate the lyrics into a target language.
It uses CrewAI agents and DuckDuckGo Search (via ddgs) for fetching song and translation information.

## ✨ Features

🔍 Guess the song title and artist from a given lyric snippet
🌍 Translate the provided lyric snippet into a chosen language
🤖 Powered by CrewAI agents (Lyric Finder Expert & Translation Specialist)
🛠 Fallback logic (works even if CrewAI execution fails)

## Dependencies include:

crewai

ddgs

argparse

re / json

## 🚀 Usage

Run the script with a lyric snippet:

python main.py --lyrics "zamansızdık ilk başta" --language english

Example Output
The song found: Zamansızdık - Manifest
Translation to english: We were timeless at first

⚙️ Arguments
Argument	Description	Default
```bash
--lyrics	The lyric snippet to search for	(required)
--language	Target language for translation	turkish
```

🧩 Project Structure
```bash
main.py        # Main entry point
```

Key components:

Lyric Finder Expert → finds the song and artist from lyrics

Lyrics Translation Specialist → translates the snippet into the target language

📌 Notes

The translation currently relies on web search results and may be approximate.
