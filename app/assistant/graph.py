from typing import Annotated, TypedDict

from langchain_core.messages import AnyMessage, SystemMessage
from langgraph.graph import END, START, StateGraph
from langgraph.graph.message import add_messages

from app.llm import get_chat_model


# 1. State definieren
class State(TypedDict):
    messages: Annotated[list[AnyMessage], add_messages]


# 2. SystemPrompt definieren
SYSTEM_PROMPT = """
Du bist ein erfahrener Platform-Engineering-Assistent.
Du antwortest auf Deutsch, kurz und präzise.
Du unterstützt bei Cloud, Azure, Databricks,
Deployments und IT-Infrastruktur.
Wenn du etwas nicht weißt, sagst du es ehrlich.
"""


# 3. Assistant Node
def assistant(state: State) -> dict:
    model = get_chat_model()

    response = model.invoke([
        SystemMessage(content=SYSTEM_PROMPT),
        *state["messages"]
    ])

    return {"messages": [response]}


# 4. Graph erstellen und kompilieren
def build_graph(checkpointer=None):
    graph = StateGraph(State)

    graph.add_node("assistant", assistant)

    graph.add_edge(START, "assistant")
    graph.add_edge("assistant", END)

    return graph.compile(checkpointer=checkpointer)
