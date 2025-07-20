from fastapi import APIRouter, HTTPException, Depends
from typing import List, Optional, Dict, Any, Union
import psycopg2
from psycopg2.extras import RealDictCursor
import os
from datetime import datetime
import uuid
import json
from contextlib import contextmanager
from models.database_models import ChatMessageDB, ChatDB, CodeProjectDB, CodeAnalysisDB, UserSessionDB

# Database configuration
DATABASE_CONFIG = {
    "host": os.getenv("DB_HOST", "localhost"),
    "port": os.getenv("DB_PORT", "5432"),
    "database": os.getenv("DB_NAME", "postgres"),
    "user": os.getenv("DB_USER", "postgres"),
    "password": os.getenv("DB_PASSWORD", "password")
}

# Pydantic models imported from models.database_models

# Database connection manager
@contextmanager
def get_db_connection():
    conn = None
    try:
        conn = psycopg2.connect(**DATABASE_CONFIG)
        yield conn
    except psycopg2.Error as e:
        if conn:
            conn.rollback()
        raise HTTPException(status_code=500, detail=f"Database error: {str(e)}")
    finally:
        if conn:
            conn.close()

# Database initialization SQL
DATABASE_SCHEMA = """
-- Create tables for AHxAI application

-- Users table
CREATE TABLE IF NOT EXISTS users (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    username VARCHAR(255) UNIQUE NOT NULL,
    email VARCHAR(255) UNIQUE NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Chats table
CREATE TABLE IF NOT EXISTS chats (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    title VARCHAR(500) NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    user_id UUID REFERENCES users(id) ON DELETE CASCADE
);

-- Chat messages table
CREATE TABLE IF NOT EXISTS chat_messages (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    chat_id UUID REFERENCES chats(id) ON DELETE CASCADE,
    content TEXT NOT NULL,
    is_user BOOLEAN NOT NULL,
    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    metadata JSONB
);

-- Code projects table
CREATE TABLE IF NOT EXISTS code_projects (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    name VARCHAR(255) NOT NULL,
    description TEXT,
    language VARCHAR(50) NOT NULL,
    code_content TEXT NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    user_id UUID REFERENCES users(id) ON DELETE CASCADE
);

-- Code analysis table
CREATE TABLE IF NOT EXISTS code_analysis (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    project_id UUID REFERENCES code_projects(id) ON DELETE CASCADE,
    original_code TEXT NOT NULL,
    corrected_code TEXT,
    explanation TEXT,
    suggestions JSONB,
    warnings JSONB,
    analysis_type VARCHAR(50),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- User sessions table
CREATE TABLE IF NOT EXISTS user_sessions (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    session_token VARCHAR(255) UNIQUE NOT NULL,
    user_data JSONB,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    expires_at TIMESTAMP NOT NULL
);

-- Indexes for better performance
CREATE INDEX IF NOT EXISTS idx_chat_messages_chat_id ON chat_messages(chat_id);
CREATE INDEX IF NOT EXISTS idx_chat_messages_timestamp ON chat_messages(timestamp);
CREATE INDEX IF NOT EXISTS idx_code_projects_user_id ON code_projects(user_id);
CREATE INDEX IF NOT EXISTS idx_code_analysis_project_id ON code_analysis(project_id);
CREATE INDEX IF NOT EXISTS idx_user_sessions_token ON user_sessions(session_token);
CREATE INDEX IF NOT EXISTS idx_chats_user_id ON chats(user_id);
"""

# APIRouter for PostgreSQL operations
postgres_router = APIRouter(prefix="/api/db", tags=["database"])

# Database initialization endpoint
@postgres_router.post("/init")
async def initialize_database():
    """Initialize database schema"""
    try:
        with get_db_connection() as conn:
            with conn.cursor() as cursor:
                cursor.execute(DATABASE_SCHEMA)
                conn.commit()
        return {"message": "Database initialized successfully"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to initialize database: {str(e)}")

# Chat endpoints
@postgres_router.post("/chats", response_model=ChatDB)
async def create_chat(title: str, user_id: Optional[str] = None):
    """Create a new chat"""
    chat_id = str(uuid.uuid4())
    now = datetime.now()
    
    with get_db_connection() as conn:
        with conn.cursor(cursor_factory=RealDictCursor) as cursor:
            cursor.execute("""
                INSERT INTO chats (id, title, created_at, updated_at, user_id)
                VALUES (%s, %s, %s, %s, %s)
                RETURNING *
            """, (chat_id, title, now, now, user_id))
            result = cursor.fetchone()
            conn.commit()
            
    return ChatDB(**result)

@postgres_router.get("/chats", response_model=List[ChatDB])
async def get_chats(user_id: Optional[str] = None, limit: int = 50, offset: int = 0):
    """Get all chats with pagination"""
    with get_db_connection() as conn:
        with conn.cursor(cursor_factory=RealDictCursor) as cursor:
            if user_id:
                cursor.execute("""
                    SELECT * FROM chats 
                    WHERE user_id = %s 
                    ORDER BY updated_at DESC 
                    LIMIT %s OFFSET %s
                """, (user_id, limit, offset))
            else:
                cursor.execute("""
                    SELECT * FROM chats 
                    ORDER BY updated_at DESC 
                    LIMIT %s OFFSET %s
                """, (limit, offset))
            results = cursor.fetchall()
            
    return [ChatDB(**row) for row in results]

@postgres_router.get("/chats/{chat_id}", response_model=ChatDB)
async def get_chat(chat_id: str):
    """Get a specific chat by ID"""
    with get_db_connection() as conn:
        with conn.cursor(cursor_factory=RealDictCursor) as cursor:
            cursor.execute("SELECT * FROM chats WHERE id = %s", (chat_id,))
            result = cursor.fetchone()
            
    if not result:
        raise HTTPException(status_code=404, detail="Chat not found")
    return ChatDB(**result)

@postgres_router.delete("/chats/{chat_id}")
async def delete_chat(chat_id: str):
    """Delete a chat and all its messages"""
    with get_db_connection() as conn:
        with conn.cursor() as cursor:
            cursor.execute("DELETE FROM chats WHERE id = %s", (chat_id,))
            if cursor.rowcount == 0:
                raise HTTPException(status_code=404, detail="Chat not found")
            conn.commit()
    return {"message": "Chat deleted successfully"}

# Chat message endpoints
@postgres_router.post("/chats/{chat_id}/messages", response_model=ChatMessageDB)
async def create_message(chat_id: str, content: str, is_user: bool, metadata: Optional[Dict[str, Any]] = None):
    """Create a new message in a chat"""
    message_id = str(uuid.uuid4())
    now = datetime.now()
    
    with get_db_connection() as conn:
        with conn.cursor(cursor_factory=RealDictCursor) as cursor:
            cursor.execute("""
                INSERT INTO chat_messages (id, chat_id, content, is_user, timestamp, metadata)
                VALUES (%s, %s, %s, %s, %s, %s)
                RETURNING *
            """, (message_id, chat_id, content, is_user, now, json.dumps(metadata) if metadata else None))
            result = cursor.fetchone()
            
            # Update chat's updated_at timestamp
            cursor.execute("UPDATE chats SET updated_at = %s WHERE id = %s", (now, chat_id))
            conn.commit()
            
    return ChatMessageDB(**result)

@postgres_router.get("/chats/{chat_id}/messages", response_model=List[ChatMessageDB])
async def get_chat_messages(chat_id: str, limit: int = 100, offset: int = 0):
    """Get all messages for a chat"""
    with get_db_connection() as conn:
        with conn.cursor(cursor_factory=RealDictCursor) as cursor:
            cursor.execute("""
                SELECT * FROM chat_messages 
                WHERE chat_id = %s 
                ORDER BY timestamp ASC 
                LIMIT %s OFFSET %s
            """, (chat_id, limit, offset))
            results = cursor.fetchall()
            
    return [ChatMessageDB(**row) for row in results]

# Code project endpoints
@postgres_router.post("/projects", response_model=CodeProjectDB)
async def create_code_project(
    name: str, 
    language: str, 
    code_content: str, 
    description: Optional[str] = None,
    user_id: Optional[str] = None
):
    """Create a new code project"""
    project_id = str(uuid.uuid4())
    now = datetime.now()
    
    with get_db_connection() as conn:
        with conn.cursor(cursor_factory=RealDictCursor) as cursor:
            cursor.execute("""
                INSERT INTO code_projects (id, name, description, language, code_content, created_at, updated_at, user_id)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
                RETURNING *
            """, (project_id, name, description, language, code_content, now, now, user_id))
            result = cursor.fetchone()
            conn.commit()
            
    return CodeProjectDB(**result)

@postgres_router.get("/projects", response_model=List[CodeProjectDB])
async def get_code_projects(language: Optional[str] = None, user_id: Optional[str] = None, limit: int = 50):
    """Get code projects with optional filtering"""
    with get_db_connection() as conn:
        with conn.cursor(cursor_factory=RealDictCursor) as cursor:
            query = "SELECT * FROM code_projects WHERE 1=1"
            params = []
            
            if language:
                query += " AND language = %s"
                params.append(language)
            if user_id:
                query += " AND user_id = %s"
                params.append(user_id)
                
            query += " ORDER BY updated_at DESC LIMIT %s"
            params.append(limit)
            
            cursor.execute(query, params)
            results = cursor.fetchall()
            
    return [CodeProjectDB(**row) for row in results]

@postgres_router.put("/projects/{project_id}", response_model=CodeProjectDB)
async def update_code_project(project_id: str, code_content: str, name: Optional[str] = None):
    """Update a code project"""
    now = datetime.now()
    
    with get_db_connection() as conn:
        with conn.cursor(cursor_factory=RealDictCursor) as cursor:
            if name:
                cursor.execute("""
                    UPDATE code_projects 
                    SET code_content = %s, name = %s, updated_at = %s 
                    WHERE id = %s 
                    RETURNING *
                """, (code_content, name, now, project_id))
            else:
                cursor.execute("""
                    UPDATE code_projects 
                    SET code_content = %s, updated_at = %s 
                    WHERE id = %s 
                    RETURNING *
                """, (code_content, now, project_id))
                
            result = cursor.fetchone()
            if not result:
                raise HTTPException(status_code=404, detail="Project not found")
            conn.commit()
            
    return CodeProjectDB(**result)

# Code analysis endpoints
@postgres_router.post("/analysis", response_model=CodeAnalysisDB)
async def create_code_analysis(
    project_id: str,
    original_code: str,
    corrected_code: Optional[str] = None,
    explanation: Optional[str] = None,
    suggestions: Optional[List[str]] = None,
    warnings: Optional[List[str]] = None,
    analysis_type: str = "general"
):
    """Create a new code analysis"""
    analysis_id = str(uuid.uuid4())
    now = datetime.now()
    
    with get_db_connection() as conn:
        with conn.cursor(cursor_factory=RealDictCursor) as cursor:
            cursor.execute("""
                INSERT INTO code_analysis 
                (id, project_id, original_code, corrected_code, explanation, suggestions, warnings, analysis_type, created_at)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
                RETURNING *
            """, (
                analysis_id, project_id, original_code, corrected_code, explanation,
                json.dumps(suggestions) if suggestions else None,
                json.dumps(warnings) if warnings else None,
                analysis_type, now
            ))
            result = cursor.fetchone()
            conn.commit()
            
    return CodeAnalysisDB(**result)

@postgres_router.get("/analysis/project/{project_id}", response_model=List[CodeAnalysisDB])
async def get_project_analysis(project_id: str, analysis_type: Optional[str] = None):
    """Get all analysis for a project"""
    with get_db_connection() as conn:
        with conn.cursor(cursor_factory=RealDictCursor) as cursor:
            if analysis_type:
                cursor.execute("""
                    SELECT * FROM code_analysis 
                    WHERE project_id = %s AND analysis_type = %s 
                    ORDER BY created_at DESC
                """, (project_id, analysis_type))
            else:
                cursor.execute("""
                    SELECT * FROM code_analysis 
                    WHERE project_id = %s 
                    ORDER BY created_at DESC
                """, (project_id,))
            results = cursor.fetchall()
            
    return [CodeAnalysisDB(**row) for row in results]

# Advanced search and analytics endpoints
@postgres_router.get("/analytics/summary")
async def get_analytics_summary():
    """Get overall analytics summary"""
    with get_db_connection() as conn:
        with conn.cursor(cursor_factory=RealDictCursor) as cursor:
            cursor.execute("""
                SELECT 
                    (SELECT COUNT(*) FROM chats) as total_chats,
                    (SELECT COUNT(*) FROM chat_messages) as total_messages,
                    (SELECT COUNT(*) FROM code_projects) as total_projects,
                    (SELECT COUNT(*) FROM code_analysis) as total_analyses,
                    (SELECT COUNT(DISTINCT language) FROM code_projects) as unique_languages
            """)
            result = cursor.fetchone()
            
    return dict(result)

@postgres_router.get("/search/code")
async def search_code_projects(query: str, language: Optional[str] = None, limit: int = 20):
    """Search code projects by content"""
    with get_db_connection() as conn:
        with conn.cursor(cursor_factory=RealDictCursor) as cursor:
            if language:
                cursor.execute("""
                    SELECT * FROM code_projects 
                    WHERE (code_content ILIKE %s OR name ILIKE %s OR description ILIKE %s)
                    AND language = %s
                    ORDER BY updated_at DESC
                    LIMIT %s
                """, (f"%{query}%", f"%{query}%", f"%{query}%", language, limit))
            else:
                cursor.execute("""
                    SELECT * FROM code_projects 
                    WHERE code_content ILIKE %s OR name ILIKE %s OR description ILIKE %s
                    ORDER BY updated_at DESC
                    LIMIT %s
                """, (f"%{query}%", f"%{query}%", f"%{query}%", limit))
            results = cursor.fetchall()
            
    return [CodeProjectDB(**row) for row in results]

@postgres_router.get("/stats/languages")
async def get_language_stats():
    """Get statistics by programming language"""
    with get_db_connection() as conn:
        with conn.cursor(cursor_factory=RealDictCursor) as cursor:
            cursor.execute("""
                SELECT 
                    language,
                    COUNT(*) as project_count,
                    AVG(LENGTH(code_content)) as avg_code_length
                FROM code_projects 
                GROUP BY language 
                ORDER BY project_count DESC
            """)
            results = cursor.fetchall()
            
    return [dict(row) for row in results]

# Health check endpoint
@postgres_router.get("/health")
async def health_check():
    """Check database connection health"""
    try:
        with get_db_connection() as conn:
            with conn.cursor() as cursor:
                cursor.execute("SELECT 1")
                cursor.fetchone()
        return {"status": "healthy", "database": "connected"}
    except Exception as e:
        raise HTTPException(status_code=503, detail=f"Database unhealthy: {str(e)}")

# Router is imported and included in main.py