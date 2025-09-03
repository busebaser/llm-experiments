## AI EDA Agent
This project demonstrates an AI-powered data analyst agent that automatically performs Exploratory Data Analysis (EDA) on a dataset.
It uses AutoGen to manage AI agents, with Google Gemini (OpenAI-compatible API) as the LLM backend.

## The agent:
- Loads a dataset (e.g., Gym Members Exercise Dataset from Kaggle).
- Cleans missing values and data types.
- Generates histograms and scatter plots with trendlines.
- Writes concise EDA summaries into a markdown report.
- Runs fully automated (no human input required).

##  📂 Project Structure
```bash
├── main.py              # Core AI agent runner
├── kaggle_download.py   # Helper script for dataset download
├── reports/             # Generated reports (Markdown + Figures)
│   ├── eda_report.md
│   └── figures/
└── data/                # Dataset folder
```

## Create a .env file in the project root:
```bash
GOOGLE_API_KEY=your_google_api_key
OPENAI_COMPAT_URL=https://generativelanguage.googleapis.com/v1beta/openai/
MODEL=gemini-2.0-flash
KAGGLE_USERNAME=your_kaggle_username
KAGGLE_KEY=your_kaggle_key
```

## 🚀 Usage
Download dataset (automatically via Kaggle or place manually):
```bash
python kaggle_download.py
```

Run the AI EDA agent:
```bash
python main.py
```

Check results:
- Markdown summary at reports/eda_report.md
- Figures saved under reports/figures/

## 📑 Sample Results
You can see my outputs in the reports folder.

