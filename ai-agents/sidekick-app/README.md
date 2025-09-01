# 🤖 Sidekick

Sidekick is a lightweight chatbot application built with **LangGraph**, **LangChain**, **Google Gemini**, and **Gradio**.  
It provides a minimal but powerful assistant that can:

- **Chat** with you via Gemini LLM.  
- **Search** the web using DuckDuckGo (snippets only, no page browsing).  
- **Calculate** safe math expressions.  
- **Send push notifications** to your devices (via [Pushover](https://pushover.net/)).  

---

## 🚀 Features

- **Gemini-powered** conversation with tool use via LangGraph.  
- **Minimal toolset** for safety and clarity:
  - 🔍 `search`: DuckDuckGo snippets  
  - 🧮 `calculate`: safe arithmetic evaluator  
  - 📲 `send_push_notification`: instant push messages  
- **Gradio web UI** for chatting in your browser.  
- **Evaluator loop**: Sidekick automatically checks whether it has met the task success criteria.  

---

## 📂 Project Structure

- ├── app.py # Gradio interface (entrypoint)
- ├── sidekick.py # Core Sidekick graph & agent logic
- ├── sidekick_tools.py # Minimal tool implementations
- └── README.md

## Environment variables

- Create a .env file in the project root:
- GOOGLE_API_KEY=your_gemini_api_key
- PUSHOVER_TOKEN=your_pushover_app_token
- PUSHOVER_USER=your_pushover_user_or_group_key

## Run
python app.py

Then open http://127.0.0.1:7860 in your browser.


