# sidekick.py
from typing import Annotated, List, Any, Optional, Dict
from typing_extensions import TypedDict
from datetime import datetime
import uuid
import asyncio
from dotenv import load_dotenv
from pydantic import BaseModel, Field
from langgraph.graph import StateGraph, START, END
from langgraph.graph.message import add_messages
from langgraph.prebuilt import ToolNode
from langgraph.checkpoint.memory import MemorySaver
from langchain_core.messages import AIMessage, HumanMessage, SystemMessage
from langchain_google_genai import ChatGoogleGenerativeAI

from sidekick_tools import minimal_tools

load_dotenv(override=True)


# Graph State and Evaluator schema
class State(TypedDict):
    messages: Annotated[List[Any], add_messages]
    success_criteria: str
    feedback_on_work: Optional[str]
    success_criteria_met: bool
    user_input_needed: bool

class EvaluatorOutput(BaseModel):
    feedback: str = Field(description="Feedback on the assistant's response")
    success_criteria_met: bool = Field(description="Whether the success criteria have been met")
    user_input_needed: bool = Field(
        description="True if more input is needed from the user, or clarifications, or the assistant is stuck"
    )

# Sidekick
class Sidekick:
    """
    Minimal Sidekick:
    - LLM: Gemini
    - Tools: send_push_notification, search (DuckDuckGo), calculate
    """

    def __init__(self):
        self.worker_llm_with_tools = None
        self.evaluator_llm_with_output = None
        self.tools = None
        self.llm_with_tools = None
        self.graph = None
        self.sidekick_id = str(uuid.uuid4())
        self.memory = MemorySaver()

    async def setup(self):
        # Tools
        self.tools = minimal_tools()

        # Worker Gemini model
        worker_llm = ChatGoogleGenerativeAI(model="gemini-2.5-flash-preview-05-20")  
        self.worker_llm_with_tools = worker_llm.bind_tools(self.tools)

        # Evaluator Gemini model with structured output
        evaluator_llm = ChatGoogleGenerativeAI(model="gemini-2.5-flash-preview-05-20")
        self.evaluator_llm_with_output = evaluator_llm.with_structured_output(EvaluatorOutput)

        await self.build_graph()


    # Worker node
    def worker(self, state: State) -> Dict[str, Any]:
        system_message = f"""You are a helpful assistant with access to exactly three tools:
1) search — DuckDuckGo search that returns result snippets only (no browsing).
2) calculate — a safe calculator for arithmetic expressions.
3) send_push_notification — sends a push notification to the user.

Rules:
- ONLY call send_push_notification if the user explicitly asks for a push/notification.
- If external info is needed, use 'search'. If math is needed, use 'calculate'.

Current date and time: {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}

Success criteria:
{state["success_criteria"]}

Reply with a direct answer, or ask a clear question if you truly need clarification.
"""

        if state.get("feedback_on_work"):
            system_message += f"""

Previously you attempted a final answer but it was rejected.
Feedback:
{state["feedback_on_work"]}

Use this feedback to continue and meet the success criteria (or ask a clarifying question if necessary).
"""

    
        messages = state["messages"]
        found_system_message = False
        for m in messages:
            if isinstance(m, SystemMessage):
                m.content = system_message
                found_system_message = True
        if not found_system_message:
            messages = [SystemMessage(content=system_message)] + messages

        response = self.worker_llm_with_tools.invoke(messages)
        return {"messages": [response]}

    def worker_router(self, state: State) -> str:
        last = state["messages"][-1]
        if hasattr(last, "tool_calls") and last.tool_calls:
            return "tools"
        return "evaluator"


    # Evaluator node
    def format_conversation(self, messages: List[Any]) -> str:
        convo = "Conversation history:\n\n"
        for msg in messages:
            if isinstance(msg, HumanMessage):
                convo += f"User: {msg.content}\n"
            elif isinstance(msg, AIMessage):
                convo += f"Assistant: {(msg.content or '[Tools use]')}\n"
        return convo

    def evaluator(self, state: State) -> State:
        last_response = state["messages"][-1].content
        system_message = (
            "You are an evaluator that decides if the Assistant satisfied the success criteria. "
            "Provide succinct feedback. Say if criteria are met, and whether user input is needed."
        )
        user_message = f"""
{self.format_conversation(state["messages"])}

Success criteria:
{state["success_criteria"]}

Last Assistant response:
{last_response}
"""
        eval_messages = [SystemMessage(content=system_message), HumanMessage(content=user_message)]
        eval_result = self.evaluator_llm_with_output.invoke(eval_messages)

        new_state = {
            "messages": [
                {"role": "assistant", "content": f"Evaluator Feedback: {eval_result.feedback}"}
            ],
            "feedback_on_work": eval_result.feedback,
            "success_criteria_met": eval_result.success_criteria_met,
            "user_input_needed": eval_result.user_input_needed,
        }
        return new_state

    def route_based_on_evaluation(self, state: State) -> str:
        return "END" if (state["success_criteria_met"] or state["user_input_needed"]) else "worker"

    # Graph wiring
    async def build_graph(self):
        graph_builder = StateGraph(State)
        graph_builder.add_node("worker", self.worker)
        graph_builder.add_node("tools", ToolNode(tools=self.tools))
        graph_builder.add_node("evaluator", self.evaluator)

        graph_builder.add_conditional_edges("worker", self.worker_router, {"tools": "tools", "evaluator": "evaluator"})
        graph_builder.add_edge("tools", "worker")
        graph_builder.add_conditional_edges("evaluator", self.route_based_on_evaluation, {"worker": "worker", "END": END})
        graph_builder.add_edge(START, "worker")

        self.graph = graph_builder.compile(checkpointer=self.memory)


    # Public runner
    async def run_superstep(self, message, success_criteria, history):
        config = {"configurable": {"thread_id": self.sidekick_id}}
        state = {
            "messages": message,
            "success_criteria": success_criteria or "The answer should be clear and accurate.",
            "feedback_on_work": None,
            "success_criteria_met": False,
            "user_input_needed": False,
        }
        result = await self.graph.ainvoke(state, config=config)
        user = {"role": "user", "content": message}
        reply = {"role": "assistant", "content": result["messages"][-2].content}
        feedback = {"role": "assistant", "content": result["messages"][-1].content}
        return history + [user, reply, feedback]

    def cleanup(self):
        try:
            loop = asyncio.get_running_loop()
            if loop.is_running():
                return
        except RuntimeError:
            return

