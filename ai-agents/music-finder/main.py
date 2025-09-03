import re
import json
import argparse
from typing import List, Dict, Any
from crewai import Agent, Task, Crew, Process, LLM
from ddgs import DDGS
from crewai.tools import tool

# Tiny web search helper
def web_search(query: str, max_results: int = 5) -> List[Dict[str, Any]]:
    try:
        with DDGS() as ddgs:
            return list(ddgs.text(query, max_results=max_results))
    except:
        return []

# Core logic
def _guess_song_from_lyrics(lyrics_snippet: str) -> Dict[str, str]:
    """Lyric snippet'inden şarkıyı bul"""
    query = f'"{lyrics_snippet.strip()}" lyrics'
    results = web_search(query, max_results=5)
    
    for item in results:
        title = item.get("title", "").lower()
        
        patterns = [
            r'(.*?)\s*[-–—]\s*(.*?)\s*lyrics',
            r'lyrics\s*for\s*(.*?)\s*by\s*(.*)',
            r'(.*?)\s*by\s*(.*?)\s*lyrics'
        ]
        
        for pattern in patterns:
            match = re.search(pattern, title, re.IGNORECASE)
            if match:
                song_title = match.group(1).strip().title()
                artist = match.group(2).strip().title()
                
                if song_title and artist and len(song_title) > 2 and len(artist) > 2:
                    return {"title": song_title, "artist": artist}
    
    return {"title": "Unknown", "artist": "Unknown"}

def _translate_lyrics(lyrics_snippet: str, target_language: str = "turkish") -> str:
    if not lyrics_snippet or lyrics_snippet.strip() == "":
        return "No lyrics provided for translation"
    
    query = f'translate "{lyrics_snippet}" to {target_language}'
    results = web_search(query, max_results=3)
    
    translation = f"Translation to {target_language}: "
    
    for item in results:
        body = item.get("body", "")
        if "translat" in body.lower() and target_language.lower() in body.lower():
            lines = body.split('\n')
            for line in lines:
                if target_language.lower() in line.lower() and len(line) > 20:
                    translation += line.strip()
                    break
            else:
                translation += body[:100] + "..."
            break
    else:
        translation += "Translation not found in search results"
    
    return translation

# CrewAI Tools
@tool("Guess song from lyrics")
def guess_song_from_lyrics(lyrics_snippet: str) -> str:
    """Given a lyric snippet, return JSON with song title and artist"""
    return json.dumps(_guess_song_from_lyrics(lyrics_snippet))

@tool("Translate lyrics")
def translate_lyrics(lyrics_snippet: str, target_language: str = "turkish") -> str:
    """Translate the given lyrics to the specified language"""
    return _translate_lyrics(lyrics_snippet, target_language)


# Agents & Tasks
def build_agents():
    llm = LLM(
        model="gemini/gemini-2.0-flash",
        temperature=0.1,
        max_tokens=200
    )

    lyric_scourer = Agent(
        role="Lyric Finder Expert",
        goal="Accurately identify song title and artist from lyric snippets",
        backstory="You are an expert at finding songs from lyrics using web search tools",
        allow_delegation=False,
        verbose=True,
        llm=llm,
        tools=[guess_song_from_lyrics]
    )

    translator = Agent(
        role="Lyrics Translation Specialist",
        goal="Translate song lyrics to the user's desired language",
        backstory="You specialize in translating song lyrics between different languages",
        allow_delegation=False,
        verbose=True,
        llm=llm,
        tools=[translate_lyrics]
    )
    
    return lyric_scourer, translator

def build_tasks(lyrics_input: str, target_language: str, agents):
    lyric_scourer, translator = agents

    task1 = Task(
        description=f"""Find the exact song title and artist for these lyrics: "{lyrics_input}"
        
        Use the guess_song_from_lyrics tool to search for the song.
        Return ONLY a JSON object with 'title' and 'artist' keys.
        Example: {{"title": "Song Name", "artist": "Artist Name"}}""",
        
        expected_output='A valid JSON object with title and artist',
        agent=lyric_scourer,
        tools=[guess_song_from_lyrics]
    )

    task2 = Task(
    description=f"""Take the original lyrics snippet provided by the user: "{lyrics_input}"
    Translate this lyric snippet (not the song title) into {target_language}.
    
    Use the translate_lyrics tool with the lyric snippet and target language.
    Then format the final output EXACTLY like this:
    
    The song found: [title] - [artist]
    Translation to {target_language}: [translated lyrics]
    
    Make sure to use the exact same format with two lines only.""",

    expected_output="Two-line formatted result with song found and translation",
    agent=translator,
    tools=[translate_lyrics],
    context=[task1]
)


    return task1, task2

def run_flow(lyrics: str, target_language: str = "turkish"):
    try:
        print(f"Searching for lyrics: '{lyrics}'")
        print(f"Target language: {target_language}")
        
        # CrewAI setup
        agents = build_agents()
        tasks = build_tasks(lyrics, target_language, agents)
        crew = Crew(agents=list(agents), tasks=list(tasks), process=Process.sequential)
        
        result = crew.kickoff()
        print("\n=== CREWAI RESULT ===")
        print(result)
        
    except Exception as e:
        print(f"Error in CrewAI: {e}")
        print("\n=== FALLBACK RESULT ===")
        song_info = _guess_song_from_lyrics(lyrics)
        translation = _translate_lyrics(lyrics, target_language)
        
        print(f"The song found: {song_info['title']} - {song_info['artist']}")
        print(translation)
        
if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Music Finder and Translator with AI Agents")
    parser.add_argument("--lyrics", type=str, required=True, help="Lyric snippet to search")
    parser.add_argument("--language", type=str, default="turkish", help="Target language for translation")
    args = parser.parse_args()
    run_flow(args.lyrics, args.language)