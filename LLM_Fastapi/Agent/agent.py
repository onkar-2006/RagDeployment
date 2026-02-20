import os
from typing import Annotated, List, Literal
from typing_extensions import TypedDict
from langchain_groq import ChatGroq
from langchain_core.messages import BaseMessage, AIMessage, SystemMessage
from langchain_core.tools import tool
from langgraph.graph import StateGraph, START, END
from langgraph.graph.message import add_messages
from langgraph.prebuilt import ToolNode
from Prompts.Prompt import SYSTEM_PROMPT
from VectorStore.Vector_Store import VectorStore

retriever = VectorStore().load_vectorStore()

@tool
def knowledge_base_tool(query: str) -> str:
    """Useful for searching internal documents and PDFs to answer user questions."""
    docs = retriever.invoke(query)
    formatted_docs = []
    for doc in docs:
        source = doc.metadata.get("source", "Unknown")
        content = f"Content: {doc.page_content}\nSource: {source}\n---"
        formatted_docs.append(content)
    return "\n\n".join(formatted_docs)

tools = [knowledge_base_tool]
tool_node = ToolNode(tools)

class AgentState(TypedDict):
    messages: Annotated[List[BaseMessage], add_messages]

def calling_agent(state: AgentState):

    model = ChatGroq(model="openai/gpt-oss-120b", temperature=0)
    model_with_tools = model.bind_tools(tools)

    messages = [SystemMessage(content=SYSTEM_PROMPT)] + state["messages"]
    
    response = model_with_tools.invoke(messages)
    return {"messages": [response]}

def decide_node(state: AgentState) -> Literal["tools", "__end__"]:
    last_message = state["messages"][-1]
    if isinstance(last_message, AIMessage) and last_message.tool_calls:
        return "tools"
    return "__end__"

workflow = StateGraph(AgentState)

workflow.add_node("agent", calling_agent)
workflow.add_node("tools", tool_node)

workflow.add_edge(START, "agent")
workflow.add_conditional_edges(
    "agent", 
    decide_node, 
    {
        "tools": "tools", 
        "__end__": END
    }
)
workflow.add_edge("tools", "agent")

app = workflow.compile()