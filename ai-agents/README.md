🤖 AI Agent Playground

This repository is a collection of experiments and projects with LLMs and AI agent frameworks.
The goal is to explore how different models and runtimes can be combined to build intelligent, interactive, and multi-agent applications.

📂 Projects
1. 🪨📄✂ Rock-Paper-Scissors Agents

A multi-agent system built with Autogen
 and Ollama
, where agents play a game of Rock-Paper-Scissors.

Player Agents: Two agents that select moves (rock, paper, or scissors).

Game Master Agent: Coordinates the game and judges the winner using LLM reasoning.

Runtime: Message passing with SingleThreadedAgentRuntime.

👉 Demonstrates agent-to-agent communication and decision-making with local LLMs.


2. 🤖 Sidekick

Sidekick is a lightweight chatbot application built with LangGraph, LangChain, Google Gemini, and Gradio.

It provides a minimal but powerful assistant that can:

💬 Chat with you via Gemini LLM.

🔍 Search the web using DuckDuckGo (snippets only).

🧮 Calculate safe math expressions.

📲 Send push notifications to your devices (via Pushover).
