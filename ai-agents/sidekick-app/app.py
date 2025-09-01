# app.py
import asyncio
import gradio as gr
from langchain_core.messages import HumanMessage
from sidekick import Sidekick

# --- Create and setup Sidekick once at startup ---
sk: Sidekick | None = None

async def _ensure_sidekick():
    global sk
    if sk is None:
        sk = Sidekick()
        await sk.setup()
    return sk

# --- Chat handler (async) ---
async def chat_fn(user_message: str, chat_history: list[tuple[str, str]] | None, llm_history: list | None):
    """
    user_message: latest user input (str)
    chat_history: [(user, assistant), ...] for the visible Gradio chat
    llm_history: Sidekick's internal history (list of {role, content}) persisted across turns
    """
    if chat_history is None:
        chat_history = []
    if llm_history is None:
        llm_history = []

    sidekick = await _ensure_sidekick()

    result_history = await sidekick.run_superstep(
        message=[HumanMessage(content=user_message)],
        success_criteria="Answer clearly and correctly.",
        history=llm_history,
    )

    # Sidekick returns:
    #   ... user, assistant_reply, evaluator_feedback (3 appended items)
    # The last assistant's *visible* reply is the one before the evaluator message.
    assistant_reply = result_history[-2]["content"]

    chat_history.append((user_message, assistant_reply))
    return chat_history, result_history, ""  # clear the textbox

with gr.Blocks(title="Sidekick (Gemini + Search + Calc + Push)") as demo:
    gr.Markdown("## 🤖 Sidekick\nChat with your Gemini-powered Sidekick. Tools: DuckDuckGo search, safe calculator, push notifications.")
    chatbot = gr.Chatbot(height=480)
    msg = gr.Textbox(placeholder="Type your message... e.g., 'search: langgraph' or 'send me a push: Hello!'", label="Message")
    llm_state = gr.State([])  

    send = gr.Button("Send", variant="primary")


    msg.submit(chat_fn, inputs=[msg, chatbot, llm_state], outputs=[chatbot, llm_state, msg])
    send.click(chat_fn, inputs=[msg, chatbot, llm_state], outputs=[chatbot, llm_state, msg])

    async def _warmup():
        await _ensure_sidekick()
        return gr.update(placeholder="Ready! Try: '2 + 2*3', 'search: latest drone swarm research', or 'send me a push: Build OK'")

    demo.load(_warmup, [], [msg])


demo.queue()
if __name__ == "__main__":
    demo.launch(server_name="0.0.0.0", server_port=7860)

