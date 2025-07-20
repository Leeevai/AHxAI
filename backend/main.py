from fastapi import FastAPI, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse
from pydantic import BaseModel
from typing import List, Optional, Dict, Any
import google.generativeai as genai
import os
from datetime import datetime
import uuid
import json
from contextlib import asynccontextmanager

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from langchain.chat_models import init_chat_model
from langchain_core.messages import SystemMessage, HumanMessage
from dotenv import load_dotenv

from structured_outputs import Lib, CodeTextSep
from llm_tools import scrap_docs, scrap_snippets
from models.api_models import CodeRequest, ChatMessage, Chat, CodeResponse, ChatResponse, QueryRequest
from fastapi.middleware.cors import CORSMiddleware
from postgres_api import postgres_router

load_dotenv()

# Database models (using in-memory storage for simplicity)
# In production, use PostgreSQL, MongoDB, etc.
chats_db = {}
messages_db = {}

# Pydantic models imported from models.api_models

def llm_hints(kind: str, libs: dict):

    public_prompt = f"{kind.upper()} LIBS:\n"

    for k, v in libs.items():
        public_prompt += f"use {k} for {v}\n"
    
    return public_prompt

llm = init_chat_model("gpt-4.1", model_provider="openai")
lib_extractor_llm = llm.with_structured_output(Lib)

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],  # or ["*"] to allow all (not recommended in prod)
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include PostgreSQL database router
app.include_router(postgres_router)

memory = []

@app.post("/execute-query")
async def execute_query(request: QueryRequest):
    query = request.query
    system_prompt = request.system_prompt

    try:
        def execute_llm(llm, query: str, system_promt: str):
            tools_registry = {
                "scrap_docs": scrap_docs,
                "scrap_snippets": scrap_snippets
            }
    
            tools = [scrap_docs, scrap_snippets]
            llm_with_tools = llm.bind_tools(tools)

            messages = [
                SystemMessage(system_promt),
                HumanMessage(query),
            ]

            memory.extend(messages)
    
            useful_libs = lib_extractor_llm.invoke(query)
            public_libs = useful_libs.to_dict_public()
            private_libs = useful_libs.to_dict_private()

            public_prompt = llm_hints("public", public_libs)
            private_prompt = llm_hints("private", private_libs)

            libs_text = f"{public_prompt}\n\n{private_prompt}"
    
            next_prompt = f"get the docs and search for the topics of the following libraries\n{libs_text}"
    
            ai_message = llm_with_tools.invoke(next_prompt)
            messages.append(ai_message)
            memory.append(ai_message)

            tool_calls = ai_message.tool_calls
    
            for tool_call in tool_calls:
                selected_tool = tools_registry[tool_call['name']]
                tool_msg = selected_tool.invoke(tool_call)
                messages.append(tool_msg)
                memory.append(tool_msg)
    
            output = llm_with_tools.invoke(memory)

            print(memory)

            return (output, messages, tool_calls)
        
        result, full_messages, tool_calls = execute_llm(llm, query, system_prompt)
        return {"result": result, "full_messages": full_messages, "tool_calls": tool_calls}
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

def create_analysis_prompt(code: str, language: str, context: str) -> str:
    return f"""
    You are an expert code analyst. Analyze the following {language} code and provide:
    
    1. CORRECTED_CODE: Improved version of the code with best practices
    2. EXPLANATION: Clear explanation of what the code does and improvements made
    3. VISUALIZATION_HTML: HTML/CSS visualization that represents the code's functionality, data structures, or algorithm flow
    4. SUGGESTIONS: List of specific improvement suggestions
    5. WARNINGS: List of potential issues or performance concerns
    
    Context: {context}
    
    Code to analyze:
    ```{language}
    {code}
    ```
    
    Please format your response as JSON with the following structure:
    {{
        "corrected_code": "improved code here",
        "explanation": "detailed explanation here",
        "visualization_html": "complete HTML with embedded CSS for visualization",
        "suggestions": ["suggestion 1", "suggestion 2", ...],
        "warnings": ["warning 1", "warning 2", ...]
    }}
    """

async def analyze_code_with_gemini(code: str, language: str, context: str) -> CodeResponse:
    try:
        prompt = create_analysis_prompt(code, language, context)
        response = llm.invoke(prompt)
        
        # Parse JSON response
        try:
            result = json.loads(response.text)
        except json.JSONDecodeError:
            # Fallback if JSON parsing fails
            result = {
                "corrected_code": code,
                "explanation": response.text,
                "visualization_html": "<div>Visualization not available</div>",
                "suggestions": [],
                "warnings": []
            }
        
        return CodeResponse(**result)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error analyzing code: {str(e)}")

@app.get("/")
async def root():
    return {"message": "Coding AI Agent API is running"}

@app.get("/health")
async def health_check():
    return {"status": "healthy", "timestamp": datetime.now()}

@app.post("/api/chats", response_model=Chat)
async def create_chat():
    """Create a new chat session"""
    chat_id = str(uuid.uuid4())
    chat = Chat(
        id=chat_id,
        title="New Chat",
        created_at=datetime.now(),
        updated_at=datetime.now()
    )
    chats_db[chat_id] = chat
    return chat

@app.get("/api/chats", response_model=List[Chat])
async def get_chats():
    """Get all chat sessions"""
    return list(chats_db.values())

@app.get("/api/chats/{chat_id}", response_model=Chat)
async def get_chat(chat_id: str):
    """Get a specific chat session"""
    if chat_id not in chats_db:
        raise HTTPException(status_code=404, detail="Chat not found")
    
    chat = chats_db[chat_id]
    # Add messages to chat
    chat.messages = [msg for msg in messages_db.values() if msg.chat_id == chat_id]
    return chat

@app.delete("/api/chats/{chat_id}")
async def delete_chat(chat_id: str):
    """Delete a chat session"""
    if chat_id not in chats_db:
        raise HTTPException(status_code=404, detail="Chat not found")
    
    # Delete chat and its messages
    del chats_db[chat_id]
    messages_to_delete = [msg_id for msg_id, msg in messages_db.items() if msg.chat_id == chat_id]
    for msg_id in messages_to_delete:
        del messages_db[msg_id]
    
    return {"message": "Chat deleted successfully"}

@app.post("/api/analyze", response_model=ChatResponse)
async def analyze_code(request: CodeRequest):
    """Analyze code and return results"""
    
    # Create or get chat
    chat_id = request.chat_id
    if not chat_id:
        chat = await create_chat()
        chat_id = chat.id
    elif chat_id not in chats_db:
        raise HTTPException(status_code=404, detail="Chat not found")
    
    # Create user message
    user_msg_id = str(uuid.uuid4())
    user_message = ChatMessage(
        id=user_msg_id,
        chat_id=chat_id,
        content=f"Analyze this {request.language} code: {request.code[:100]}...",
        is_user=True,
        timestamp=datetime.now(),
        metadata={"code": request.code, "language": request.language, "context": request.context}
    )
    messages_db[user_msg_id] = user_message
    
    # Analyze code with Gemini
    ai_response = await analyze_code_with_gemini(request.code, request.language, request.context)
    
    # Create AI response message
    ai_msg_id = str(uuid.uuid4())
    ai_message = ChatMessage(
        id=ai_msg_id,
        chat_id=chat_id,
        content="I've analyzed your code and provided improvements, explanations, and visualizations.",
        is_user=False,
        timestamp=datetime.now(),
        metadata=ai_response.dict()
    )
    messages_db[ai_msg_id] = ai_message
    
    # Update chat title and timestamp
    if chat_id in chats_db:
        chats_db[chat_id].title = f"Code Analysis - {request.language}"
        chats_db[chat_id].updated_at = datetime.now()
    
    return ChatResponse(
        chat_id=chat_id,
        message=ai_message,
        ai_response=ai_response
    )

@app.get("/api/chats/{chat_id}/messages", response_model=List[ChatMessage])
async def get_chat_messages(chat_id: str):
    """Get messages for a specific chat"""
    if chat_id not in chats_db:
        raise HTTPException(status_code=404, detail="Chat not found")
    
    messages = [msg for msg in messages_db.values() if msg.chat_id == chat_id]
    return sorted(messages, key=lambda x: x.timestamp)

@app.get("/api/visualization/{message_id}", response_class=HTMLResponse)
async def get_visualization(message_id: str):
    """Get HTML visualization for a specific message"""
    if message_id not in messages_db:
        raise HTTPException(status_code=404, detail="Message not found")
    
    message = messages_db[message_id]
    if not message.metadata or "visualization_html" not in message.metadata:
        raise HTTPException(status_code=404, detail="Visualization not found")
    
    return HTMLResponse(content=message.metadata["visualization_html"])

@app.post("/api/chats/{chat_id}/messages", response_model=ChatMessage)
async def send_message(chat_id: str, message: dict):
    """Send a message to a chat"""
    if chat_id not in chats_db:
        raise HTTPException(status_code=404, detail="Chat not found")
    
    msg_id = str(uuid.uuid4())
    chat_message = ChatMessage(
        id=msg_id,
        chat_id=chat_id,
        content=message["content"],
        is_user=message.get("is_user", True),
        timestamp=datetime.now()
    )
    messages_db[msg_id] = chat_message
    
    # Update chat timestamp
    chats_db[chat_id].updated_at = datetime.now()
    
    return chat_message

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)