# sidekick_tools.py
from dotenv import load_dotenv
from langchain.agents import Tool
from duckduckgo_search import DDGS
import ast
import operator as op
import os
import requests

load_dotenv(override=True)


# Push notification (Pushover)
_PUSHOVER_TOKEN = os.getenv("PUSHOVER_TOKEN")
_PUSHOVER_USER = os.getenv("PUSHOVER_USER")
_PUSHOVER_URL = "https://api.pushover.net/1/messages.json"

def _push(text: str) -> str:
    """
    Send a push notification to the user via Pushover.
    Requires PUSHOVER_TOKEN and PUSHOVER_USER in environment.
    """
    if not _PUSHOVER_TOKEN or not _PUSHOVER_USER:
        return "Error: missing PUSHOVER_TOKEN or PUSHOVER_USER."
    try:
        r = requests.post(
            _PUSHOVER_URL,
            data={"token": _PUSHOVER_TOKEN, "user": _PUSHOVER_USER, "message": text[:1024]},
            timeout=10,
        )
        if r.ok:
            return "Push sent."
        return f"Push failed: {r.status_code} {r.text[:200]}"
    except Exception as e:
        return f"Push failed: {e}"


# DuckDuckGo search
def ddg_search(query: str) -> str:
    """
    Perform a DuckDuckGo text search and return compact lines:
    index. title
       url
       snippet
    (No page fetching or browsing.)
    """
    out_lines = []
    with DDGS() as ddgs:
        for i, r in enumerate(ddgs.text(query, max_results=8)):
            title = r.get("title") or ""
            href = r.get("href") or r.get("url") or ""
            body = r.get("body") or r.get("snippet") or ""
            out_lines.append(f"{i+1}. {title}\n   {href}\n   {body}")
    return "\n".join(out_lines) if out_lines else "No results."


# Safe calculator (no code exec)
_ALLOWED_OPS = {
    ast.Add: op.add, ast.Sub: op.sub, ast.Mult: op.mul, ast.Div: op.truediv,
    ast.FloorDiv: op.floordiv, ast.Mod: op.mod, ast.Pow: op.pow,
    ast.USub: op.neg, ast.UAdd: op.pos,
}

def _eval_ast(node):
    if isinstance(node, ast.Num):
        return node.n
    if isinstance(node, ast.Constant):
        if isinstance(node.value, (int, float)):
            return node.value
        raise ValueError("Only numbers allowed.")
    if isinstance(node, ast.UnaryOp) and type(node.op) in _ALLOWED_OPS:
        return _ALLOWED_OPS[type(node.op)](_eval_ast(node.operand))
    if isinstance(node, ast.BinOp) and type(node.op) in _ALLOWED_OPS:
        return _ALLOWED_OPS[type(node.op)](_eval_ast(node.left), _eval_ast(node.right))
    if isinstance(node, ast.Expr):
        return _eval_ast(node.value)
    raise ValueError("Unsupported expression.")

def safe_calculate(expr: str) -> str:
    """
    Safely evaluate arithmetic (+ - * / // % ** and parentheses).
    No names, calls, lists, dicts, etc.
    """
    try:
        tree = ast.parse(expr, mode="eval")
        return str(_eval_ast(tree.body))
    except Exception as e:
        return f"Error: {e}"

# Tool registry
def minimal_tools():
    return [
        Tool(
            name="send_push_notification",
            func=_push,
            description="Send a push notification to the user. Input should be the exact message text."
        ),
        Tool(
            name="search",
            func=ddg_search,
            description="DuckDuckGo search: return top result snippets (title, url, snippet)."
        ),
        Tool(
            name="calculate",
            func=safe_calculate,
            description="Safely evaluate arithmetic (+ - * / // % ** and parentheses)."
        ),
    ]

