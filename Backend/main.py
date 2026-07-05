import json
import asyncio
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse
from pydantic import BaseModel
from agent import agent


app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class ChatRequest(BaseModel):
    message: str
    history: list = []

@app.post("/api/chat")
async def chat_endpoint(request: ChatRequest):
    formatted_history = []
    for msg in request.history:
        formatted_history.append({"role": msg["role"], "content": msg["content"]})
    formatted_history.append({"role": "user", "content": request.message})

    async def event_generator():
        try:
            # 1. Initial Processing Signal
            yield f"data: {json.dumps({'type': 'status', 'text': '🧠 MedOS Mind mapping intent...'})}\n\n"
            await asyncio.sleep(0.1)

            # 2. Stream events straight from the LangGraph graph execution
            async for event in agent.astream_events({"messages": formatted_history}, version="v2"):
                kind = event["event"]
                name = event["name"]

                # Triggers when any tool begins execution
                if kind == "on_tool_start":
                    tool_input = event['data'].get('input', {})
                    
                    if name == "hospital_sql":
                        query = tool_input.get('sql_query', 'records')
                        yield f"data: {json.dumps({'type': 'status', 'text': f'🗄️ Querying system tables...'})}\n\n"
                    elif name == "book_appointment":
                        patient = tool_input.get('patient_name', 'Patient')
                        yield f"data: {json.dumps({'type': 'status', 'text': f'📅 Accessing schedule ledger for {patient}...'})}\n\n"
                    elif name == "get_table_schema":
                        table = tool_input.get('table_name', 'database')
                        yield f"data: {json.dumps({'type': 'status', 'text': f'🔍 Inspecting structure definitions for `{table}`...'})}\n\n"
                    else:
                        yield f"data: {json.dumps({'type': 'status', 'text': f'⚙️ Activating tool: {name}...'})}\n\n"

                # Triggers when a tool returns its structural output
                elif kind == "on_tool_end":
                    yield f"data: {json.dumps({'type': 'status', 'text': '✅ Core analytics retrieved. Processing layout...'})}\n\n"

                # Triggers token-by-token text generation from your LLM model
                elif kind == "on_chat_model_stream":
                    content = event["data"]["chunk"].content
                    if content:
                        yield f"data: {json.dumps({'type': 'token', 'text': content})}\n\n"

        except Exception as e:
            yield f"data: {json.dumps({'type': 'error', 'text': f'System Exception: {str(e)}'})}\n\n"

    return StreamingResponse(event_generator(), media_type="text/event-stream")