from fastapi import FastAPI, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse
from pydantic import BaseModel
from typing import List, Optional, Dict, Any
from langchain.chat_models import init_chat_model
from langchain_core.messages import SystemMessage, HumanMessage
import os
from datetime import datetime
import uuid
import json
from contextlib import asynccontextmanager
from dotenv import load_dotenv

from structured_outputs import Lib, CodeAnalysis
from outputs.llm_tools import scrap_docs, scrap_snippets
from libs import libs, lib_names, private_libs

load_dotenv()

# Database models (using in-memory storage for simplicity)
# In production, use PostgreSQL, MongoDB, etc.
chats_db = {}
messages_db = {}

# Pydantic models
class CodeRequest(BaseModel):
    code: str
    language: str = "javascript"
    context: str = ""
    chat_id: Optional[str] = None

class QueryRequest(BaseModel):
    query: str
    system_prompt: str = "you are a smart coding assistant"
    chat_id: Optional[str] = None

class ChatMessage(BaseModel):
    id: str
    chat_id: str
    content: str
    is_user: bool
    timestamp: datetime
    metadata: Optional[Dict[str, Any]] = None

class Chat(BaseModel):
    id: str
    title: str
    created_at: datetime
    updated_at: datetime
    messages: List[ChatMessage] = []

class CodeResponse(BaseModel):
    corrected_code: str
    explanation: str
    visualization_html: str
    suggestions: List[str]
    warnings: List[str]

class QueryResponse(BaseModel):
    content: str
    metadata: Optional[Dict[str, Any]] = None

class LLMQueryResponse(BaseModel):
    result: QueryResponse
    tool_calls: Optional[List[Dict[str, Any]]] = None
    full_messages: Optional[List[Dict[str, Any]]] = None

class ChatResponse(BaseModel):
    chat_id: str
    message: ChatMessage
    ai_response: Optional[CodeResponse] = None

class SendMessageRequest(BaseModel):
    content: str
    is_user: bool = True

# Initialize OpenAI LLM
@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    # OpenAI API key is loaded from environment variables by langchain
    yield
    # Shutdown
    pass

app = FastAPI(
    title="Coding AI Agent API",
    description="Backend API for AI-powered coding assistant",
    version="1.0.0",
    lifespan=lifespan
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://localhost:5173", "http://localhost:5174"],  # Add your frontend URLs
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Helper function for LLM hints
def llm_hints(kind: str, libs: dict):
    public_prompt = f"{kind.upper()} LIBS:\n"

    for k, v in libs.items():
        public_prompt += f"use {k} for {v}\n"
    
    return public_prompt

# Initialize OpenAI LLM
llm = init_chat_model("gpt-4", model_provider="openai")
lib_extractor_llm = llm.with_structured_output(Lib)
code_analyzer_llm = llm.with_structured_output(CodeAnalysis)

# Memory for conversation history
memory = []

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

def create_query_prompt(query: str, system_prompt: str) -> str:
    return f"""
    System: {system_prompt}
    
    User Query: {query}
    
    Please provide a helpful and detailed response to the user's query.
    """

async def analyze_code_with_openai(code: str, language: str, context: str) -> CodeResponse:
    try:
        # Create system message with analysis instructions
        system_prompt = f"You are an expert code analyst. Analyze the following {language} code and provide improvements, explanations, and visualizations."
        
        # Create human message with code to analyze
        human_prompt = f"Code to analyze:\n```{language}\n{code}\n```\n\nContext: {context}"
        
        # Create messages for LLM
        messages = [
            SystemMessage(system_prompt),
            HumanMessage(human_prompt),
        ]
        
        # Use structured output for code analysis
        analysis = code_analyzer_llm.invoke(messages)
        
        # Create visualization HTML
        visualization_html = f"<div class='code-visualization'>\n<h3>Code Visualization</h3>\n<pre><code class='{language}'>\n{analysis.corrected_code}\n</code></pre>\n<div class='explanation'>{analysis.explanation}</div>\n</div>"
        
        # Create response
        result = {
            "corrected_code": analysis.corrected_code,
            "explanation": analysis.explanation,
            "visualization_html": visualization_html,
            "suggestions": analysis.suggestions,
            "warnings": analysis.warnings
        }
        
        return CodeResponse(**result)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error analyzing code: {str(e)}")

async def query_openai(query: str, system_prompt: str) -> LLMQueryResponse:
    try:
        def execute_llm(llm, query: str, system_prompt: str):
            tools_registry = {
                "scrap_docs": scrap_docs,
                "scrap_snippets": scrap_snippets
            }
    
            tools = [scrap_docs, scrap_snippets]
            llm_with_tools = llm.bind_tools(tools)

            messages = [
                SystemMessage(system_prompt),
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

            tool_calls = ai_message.tool_calls if hasattr(ai_message, 'tool_calls') else []
    
            for tool_call in tool_calls:
                selected_tool = tools_registry[tool_call['name']]
                tool_msg = selected_tool.invoke(tool_call)
                messages.append(tool_msg)
                memory.append(tool_msg)
    
            output = llm_with_tools.invoke(memory)

            return (output, messages, tool_calls)
        
        result, full_messages, tool_calls = execute_llm(llm, query, system_prompt)
        
        # Convert to expected response format
        result_content = result.content if hasattr(result, 'content') else str(result)
        
        query_response = QueryResponse(
            content=result_content,
            metadata={"model": "gpt-4", "system_prompt": system_prompt}
        )
        
        # Convert messages to expected format
        formatted_messages = []
        for msg in full_messages:
            if hasattr(msg, 'to_dict'):
                msg_dict = msg.to_dict()
                formatted_messages.append({
                    "role": msg_dict.get("type", "unknown"),
                    "content": msg_dict.get("content", "")
                })
            else:
                formatted_messages.append({
                    "role": "unknown",
                    "content": str(msg)
                })
        
        return LLMQueryResponse(
            result=query_response,
            tool_calls=tool_calls,
            full_messages=formatted_messages
        )
    except Exception as e:
        error_detail = f"OpenAI API failed to respond: {str(e)}"
        print(f"Error in query_openai: {error_detail}")
        raise HTTPException(status_code=502, detail=error_detail)

async def create_chat_internal() -> Chat:
    """Internal function to create a new chat"""
    chat_id = str(uuid.uuid4())
    chat = Chat(
        id=chat_id,
        title="New Chat",
        created_at=datetime.now(),
        updated_at=datetime.now()
    )
    chats_db[chat_id] = chat
    return chat

@app.get("/")
async def root():
    return {"message": "Coding AI Agent API is running"}

@app.get("/health")
async def health_check():
    return {"status": "healthy", "timestamp": datetime.now()}

@app.post("/api/chats", response_model=Chat)
async def create_chat():
    """Create a new chat session"""
    return await create_chat_internal()

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
        chat = await create_chat_internal()
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
    
    # Analyze code with OpenAI
    ai_response = await analyze_code_with_openai(request.code, request.language, request.context)
    
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

@app.post("/api/query", response_model=LLMQueryResponse)
async def query_llm(request: QueryRequest):
    """Query the LLM with a general question"""
    
    # Create or get chat
    chat_id = request.chat_id
    if not chat_id:
        chat = await create_chat_internal()
        chat_id = chat.id
    elif chat_id not in chats_db:
        raise HTTPException(status_code=404, detail="Chat not found")
    
    # Create user message
    user_msg_id = str(uuid.uuid4())
    user_message = ChatMessage(
        id=user_msg_id,
        chat_id=chat_id,
        content=request.query,
        is_user=True,
        timestamp=datetime.now(),
        metadata={"query_type": "general", "system_prompt": request.system_prompt}
    )
    messages_db[user_msg_id] = user_message
    
    # Query OpenAI
    try:
        llm_response = await query_openai(request.query, request.system_prompt)
    except Exception as e:
        # Provide more detailed error information for debugging
        error_detail = f"OpenAI API failed to respond: {str(e)}"
        print(f"Error in /api/query endpoint: {error_detail}")
        raise HTTPException(status_code=502, detail=error_detail)

    
    # Create AI response message
    ai_msg_id = str(uuid.uuid4())
    ai_message = ChatMessage(
        id=ai_msg_id,
        chat_id=chat_id,
        content=llm_response.result.content,
        is_user=False,
        timestamp=datetime.now(),
        metadata={
            "query_type": "general",
            "system_prompt": request.system_prompt,
            "tool_calls": llm_response.tool_calls,
            "full_messages": llm_response.full_messages
        }
    )
    messages_db[ai_msg_id] = ai_message
    
    # Update chat title and timestamp
    if chat_id in chats_db:
        chats_db[chat_id].title = f"Query - {request.query[:30]}..."
        chats_db[chat_id].updated_at = datetime.now()
    
    return llm_response

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
async def send_message(chat_id: str, message: SendMessageRequest):
    """Send a message to a chat"""
    if chat_id not in chats_db:
        raise HTTPException(status_code=404, detail="Chat not found")
    
    msg_id = str(uuid.uuid4())
    chat_message = ChatMessage(
        id=msg_id,
        chat_id=chat_id,
        content=message.content,
        is_user=message.is_user,
        timestamp=datetime.now()
    )
    messages_db[msg_id] = chat_message
    
    # Update chat timestamp
    chats_db[chat_id].updated_at = datetime.now()
    
    return chat_message

# Additional utility endpoints

@app.get("/api/stats")
async def get_stats():
    """Get API statistics"""
    return {
        "total_chats": len(chats_db),
        "total_messages": len(messages_db),
        "api_version": "1.0.0",
        "status": "healthy"
    }

@app.post("/api/chats/{chat_id}/clear")
async def clear_chat(chat_id: str):
    """Clear all messages in a chat"""
    if chat_id not in chats_db:
        raise HTTPException(status_code=404, detail="Chat not found")
    
    # Delete all messages for this chat
    messages_to_delete = [msg_id for msg_id, msg in messages_db.items() if msg.chat_id == chat_id]
    for msg_id in messages_to_delete:
        del messages_db[msg_id]
    
    # Update chat timestamp
    chats_db[chat_id].updated_at = datetime.now()
    
    return {"message": "Chat cleared successfully"}

@app.patch("/api/chats/{chat_id}")
async def update_chat(chat_id: str, update_data: dict):
    """Update chat metadata (like title)"""
    if chat_id not in chats_db:
        raise HTTPException(status_code=404, detail="Chat not found")
    
    chat = chats_db[chat_id]
    
    if "title" in update_data:
        chat.title = update_data["title"]
    
    chat.updated_at = datetime.now()
    
    return chat

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)