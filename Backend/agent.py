from typing import Annotated
from typing_extensions import TypedDict
from langgraph.graph import StateGraph, START, END
from langgraph.graph.message import add_messages
from langgraph.prebuilt import ToolNode, tools_condition
from langchain_openai import ChatOpenAI
from langchain_core.messages import SystemMessage
from langchain_core.tools import tool

from config import LLM_MODEL
from tools import hospital_rag, hospital_sql, weather_tool,get_table_schema,book_appointment

# 2. DEFINE THE GRAPH STATE
# This dictates exactly what memory the graph carries around.
class State(TypedDict):
    # add_messages ensures new messages are appended, not overwritten
    messages: Annotated[list, add_messages] 

# ---------------------------------------------------------
# 3. SET UP THE NODES
# ---------------------------------------------------------
tools = [hospital_rag, hospital_sql, weather_tool, book_appointment,get_table_schema]
tool_node = ToolNode(tools)

# Bind the tools to the LLM so it knows they exist
llm = ChatOpenAI(model=LLM_MODEL, temperature=0).bind_tools(tools)

def chatbot(state: State):
    """The main brain of the agent."""
    system_prompt = SystemMessage(content=(
        "You are MedOS, a helpful hospital assistant. "
        "IMPORTANT SQL RULES: The database ONLY contains the following tables: "
        "admissions, appointments, bookings, departments, doctors, medical_records, medicines, patients, prescriptions, and rooms. "
        "MANDATORY SCHEMA RULE: You do not know the column names. NEVER guess column names. "
        "BEFORE writing any SQL query, you MUST use the 'get_table_schema' tool to verify the exact columns of the table you want to query. "
        "NOTE: Newly scheduled appointments via the book_appointment tool are saved in the 'bookings' table. Check this table if the user asks to verify their booking. "
        "If the user wants to book an appointment, collect their name, department, date, and time BEFORE calling the book_appointment tool. "
        "If the user provides a name of a person which is not available in the database, ask them to provide their full name. "
        "Search the weather_tool only when user asks about the weather; otherwise, politely state that you are a hospital assistant and cannot help with that."
    ))
    
    # Prepend the system prompt to the user's history
    messages_to_process = [system_prompt] + state["messages"]
    
    # Generate the AI's response (or tool call)
    response = llm.invoke(messages_to_process)
    
    # Return the new state
    return {"messages": [response]}

# ---------------------------------------------------------
# 4. BUILD AND COMPILE THE GRAPH
# ---------------------------------------------------------
graph_builder = StateGraph(State)

# Add the nodes (the "rooms" in our flowchart)
graph_builder.add_node("chatbot", chatbot)
graph_builder.add_node("tools", tool_node)

# Add the edges (the "doors" connecting the rooms)
graph_builder.add_edge(START, "chatbot")

# Conditional edge: If the LLM decided to use a tool, go to 'tools'. Otherwise, END.
graph_builder.add_conditional_edges(
    "chatbot",
    tools_condition, 
)

# After a tool finishes running, ALWAYS go back to the chatbot to summarize the result
graph_builder.add_edge("tools", "chatbot")

# Compile the final agent
agent = graph_builder.compile()