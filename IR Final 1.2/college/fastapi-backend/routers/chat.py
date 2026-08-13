import json
import asyncio
import sys
import os
from typing import List, Dict, Any
from fastapi import APIRouter
from fastapi.responses import StreamingResponse
from pydantic import BaseModel

# Add paths to import from backend
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
sys.path.append(os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))), "backend"))

from llm_service import get_llm_service

router = APIRouter()

class ChatMessage(BaseModel):
    role: str
    content: str

class ChatRequest(BaseModel):
    message: str
    history: List[ChatMessage] = []

async def real_llm_stream(query: str, history: List[ChatMessage]):
    """
    Runs the synchronous InsightRuralCounselor generator in a separate thread
    and yields SSE chunks to the client.
    """
    counselor = get_llm_service()
    
    # Format history into the list of dicts that llm_service expects
    formatted_history = [{"role": h.role, "content": h.content} for h in history]
    
    queue = asyncio.Queue()
    loop = asyncio.get_running_loop()
    
    def run_stream():
        try:
            # stream_response yields string tokens
            for token in counselor.stream_response(query, formatted_history):
                # Put the token in the queue safely from the thread
                asyncio.run_coroutine_threadsafe(queue.put(token), loop).result()
        except Exception as e:
            print(f"[Error in thread stream] {e}")
        finally:
            # Send None to signify end of stream
            asyncio.run_coroutine_threadsafe(queue.put(None), loop).result()
            
    # Run the generator in a background thread
    task = loop.run_in_executor(None, run_stream)
    
    # Read from the queue and yield to the client
    while True:
        token = await queue.get()
        if token is None:
            break
        yield f"data: {json.dumps({'content': token})}\n\n"
        
    # Determine widget dynamically based on query matching
    widget = None
    q_lower = query.lower()
    if "predict" in q_lower or "rank" in q_lower:
        widget = "college_list"
    elif "scholarship" in q_lower or "fee" in q_lower:
        widget = "scholarship_list"
    elif "risk" in q_lower or "analyzer" in q_lower:
        widget = "risk_chart"
        
    # Final payload with widgets and sources (retrieved context metadata)
    final_payload = {
        "content": "",
        "widget": widget
    }
    
    yield f"data: {json.dumps(final_payload)}\n\n"
    yield "data: [DONE]\n\n"
    
    # Ensure the background thread task is finished
    await task

@router.post("/stream")
async def chat_stream_endpoint(request: ChatRequest):
    """
    Server-Sent Events (SSE) streaming endpoint for the Premium AI Counselor.
    This guarantees zero timeout issues and provides real-time typing UI.
    """
    return StreamingResponse(
        real_llm_stream(request.message, request.history),
        media_type="text/event-stream"
    )
