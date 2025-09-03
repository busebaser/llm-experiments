import os, re, subprocess, sys, textwrap, tempfile
from pathlib import Path
from dotenv import load_dotenv

load_dotenv()
api_key = os.getenv("GOOGLE_API_KEY")
base_url = os.getenv(
        "OPENAI_COMPAT_URL",
        "https://generativelanguage.googleapis.com/v1beta/openai/",
    )
assert api_key, "Set GOOGLE_API_KEY in .env"

DATA_CSV   = "your_path"
REPORT_DIR = Path("reports")
FIG_DIR    = REPORT_DIR / "figures"
REPORT_DIR.mkdir(parents=True, exist_ok=True)
FIG_DIR.mkdir(parents=True, exist_ok=True)

from autogen import AssistantAgent
import autogen 


model = os.getenv("MODEL", "gemini-2.0-flash")
api_key = os.getenv("GOOGLE_API_KEY")
base_url = os.getenv(
        "OPENAI_COMPAT_URL",
        "https://generativelanguage.googleapis.com/v1beta/openai/",
    )

config_list = [{
        "model": model,
        "api_key": api_key,
        "base_url": base_url,   # Gemini OpenAI-compatible endpoint
    }]
llm_config = {
        "config_list": config_list,
        "temperature": 0.2,
    }

analyst = AssistantAgent(
    name="Analyst",
    llm_config=llm_config,
    system_message=(
        "You are a data analyst. You will write SHORT Python code snippets "
        "that run with pandas and matplotlib to perform EDA on the dataset. "
        f"Always save figures into '{FIG_DIR}' and append summaries "
        f"to '{REPORT_DIR}/eda_report.md'. Keep code concise and runnable in isolation. "
        "Use matplotlib only (no seaborn). Do not show plots; save them."
    ),
)

user_proxy = autogen.UserProxyAgent(
    name="user_proxy",
    human_input_mode="NEVER",  # Set to "NEVER" for full automation
    max_consecutive_auto_reply=10,
    is_termination_msg=lambda x: "TERMINATE" in x.get("content", "").upper(),
    code_execution_config={"work_dir": "coding", "use_docker": False} 
)

ONE_SHOT_PROMPT = f"""
You are a data analyst. Produce ONE Python code block that:
- Loads '{DATA_CSV}'
- Cleans obvious nulls/types
- Saves histograms for age, heart_rate, duration, calories (if they exist) to '{FIG_DIR}'
- Saves scatter + trendline for (duration vs calories) and (heart_rate vs calories) if both columns exist
- Appends a concise markdown report to '{REPORT_DIR}/eda_report.md' with shape/dtypes/nulls and 2–3 bullet insights
Rules:
- Single self-contained code block (imports included), matplotlib only, save figures, no display, <= 120 lines.
"""


#  minimal local runner for code blocks 
def extract_python_blocks(text: str) -> list[str]:
    blocks = re.findall(r"```(?:python)?\s*(.*?)```", text, flags=re.S)
    if blocks:
        return [b.strip() for b in blocks]
    if "import " in text or "pd." in text or "plt." in text:
        return [text.strip()]
    return []

def run_python_block(code: str) -> tuple[int, str, str]:
    prolog = textwrap.dedent(f"""
        import os
        from pathlib import Path
        DATA_CSV = r"{DATA_CSV}"
        REPORT_DIR = Path(r"{REPORT_DIR}")
        FIG_DIR = Path(r"{FIG_DIR}")
        REPORT_DIR.mkdir(parents=True, exist_ok=True)
        FIG_DIR.mkdir(parents=True, exist_ok=True)
    """)
    full = prolog + "\n" + code
    with tempfile.TemporaryDirectory() as td:
        tf = Path(td) / "snippet.py"
        tf.write_text(full, encoding="utf-8")
        proc = subprocess.run(
            [sys.executable, str(tf)],
            capture_output=True, text=True, timeout=300
        )
    return proc.returncode, proc.stdout, proc.stderr

def ask_and_run(user_msg: str, title: str):
    """
    Initiates a chat with the analyst agent and prints the final conversation summary.
    """
    print(f"\n=== {title} ===")
    
    # Use the user_proxy to initiate the chat with the analyst.
    # The reply will contain the full conversation history.
    user_proxy.initiate_chat(analyst, message=user_msg)

    # To see the final response from the analyst, you can inspect the conversation history.
    # The last message in the chat is typically the final answer.
    # Note: AutoGen handles the code blocks and execution automatically.
    
    # The full chat history is stored in the agent's message attributes.
    # You can access the last message like this:
    print("\n--- MODEL MESSAGE ---")
    last_message = analyst._oai_messages[user_proxy][-1]["content"]
    print(last_message)
    
    
def main():
    print("🔧 Starting one-call Gemini → local runner…")
    
    # SINGLE call (reduce chance of 429)
    # The initiate_chat method handles the conversation and returns a ChatResult object.
    # The AutoGen framework also handles retries for API errors automatically.
    
    # The original loop for retries is no longer necessary as AutoGen has its own retry mechanisms.
    # We'll use a single call and let AutoGen handle the underlying communication.
    
    try:
        # Use user_proxy to initiate the chat. The initiate_chat method handles
        # the entire conversation flow, including getting the final response.
        chat_result = user_proxy.initiate_chat(analyst, message=ONE_SHOT_PROMPT)
        
    except Exception as e:
        print(f"❌ An error occurred during the chat: {e}")
        return
    
    # After the chat is complete, you can access the final message from the result object.
    content = chat_result.summary
    
    if not content:
        print("❌ Could not get a response from the model.")
        return

    print("\n--- MODEL MESSAGE ---\n", content)
    
    # AutoGen's UserProxyAgent automatically handles the execution of code blocks.
    # Your manual code to extract and run Python blocks is no longer needed.
    
    print(f"\n✅ Done. See report at {REPORT_DIR/'eda_report.md'} and figures in {FIG_DIR}/")


if __name__ == "__main__":
    main()
