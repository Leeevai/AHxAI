from langchain_core.tools import tool
from langchain_core.messages import ToolMessage
import requests
from bs4 import BeautifulSoup
import json
from typing import Dict, Any, List
import re
import time
import os
from dotenv import load_dotenv

load_dotenv()

@tool
def scrap_docs(lib_name: str, topic: str) -> str:
    """
    Scrape documentation from various sources based on the library and topic.
    
    Args:
        lib_name: The name of the library to search documentation for
        topic: The specific topic within the library to search for
    
    Returns:
        str: The scraped documentation content
    """
    try:
        # Import libs here to avoid circular imports
        from libs import libs
        
        # Get the base URL for the library
        if lib_name in libs:
            base_url = libs[lib_name]
            
            # Mock implementation - in production, implement actual web scraping
            return f"Documentation for {lib_name} on topic '{topic}':\n\n"\
                   f"This would fetch real documentation from {base_url} in production.\n\n"\
                   f"Example usage:\n```python\n# Example code for {lib_name} related to {topic}\n# This is mock content\n```\n\n"\
                   f"API Reference:\n- Function: example_function()\n- Class: ExampleClass\n- Method: example_method()\n"
        else:
            return f"Library '{lib_name}' not found in our documentation sources."
            
    except Exception as e:
        return f"Error scraping documentation: {str(e)}"

def get_mock_documentation(library: str, query: str) -> str:
    """
    Return mock documentation for testing purposes.
    Replace with actual web scraping in production.
    """
    mock_docs = {
        "react": {
            "hooks": """
            React Hooks Documentation:
            
            useState Hook:
            - const [state, setState] = useState(initialValue)
            - Used for managing component state
            - Returns current state and setter function
            
            useEffect Hook:
            - useEffect(() => { /* effect */ }, [dependencies])
            - Used for side effects in functional components
            - Runs after render, can return cleanup function
            
            useContext Hook:
            - const value = useContext(MyContext)
            - Used to consume context values
            - Alternative to Context.Consumer
            
            Best Practices:
            - Always include dependencies in useEffect
            - Use multiple useEffect hooks for different concerns
            - Custom hooks for reusable logic
            """,
            "components": """
            React Components Documentation:
            
            Functional Components:
            - function MyComponent(props) { return <div>{props.children}</div> }
            - Preferred approach for new components
            - Can use hooks for state and lifecycle
            
            Props:
            - Data passed down from parent components
            - Should be treated as read-only
            - Use PropTypes for type checking
            
            JSX:
            - JavaScript XML syntax extension
            - Must return single element or fragment
            - Use className instead of class
            """
        },
        "fastapi": {
            "middleware": """
            FastAPI Middleware Documentation:
            
            CORS Middleware:
            - from fastapi.middleware.cors import CORSMiddleware
            - app.add_middleware(CORSMiddleware, allow_origins=["*"])
            - Handles cross-origin requests
            
            Custom Middleware:
            - @app.middleware("http")
            - async def add_process_time_header(request: Request, call_next)
            - Must call call_next(request) and return response
            
            Security Middleware:
            - HTTPSRedirectMiddleware for HTTPS enforcement
            - TrustedHostMiddleware for host validation
            """,
            "dependencies": """
            FastAPI Dependencies Documentation:
            
            Dependency Injection:
            - def common_parameters(q: str = None): return {"q": q}
            - @app.get("/items/")
            - async def read_items(commons: dict = Depends(common_parameters))
            
            Security Dependencies:
            - oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")
            - async def get_current_user(token: str = Depends(oauth2_scheme))
            
            Database Dependencies:
            - def get_db(): ... (database session management)
            - Use with context managers for proper cleanup
            """
        },
        "python": {
            "asyncio": """
            Python Asyncio Documentation:
            
            Basic Concepts:
            - async def function_name(): (coroutine function)
            - await expression (wait for coroutine)
            - asyncio.run() to run async code
            
            Event Loop:
            - asyncio.get_event_loop() (get current loop)
            - asyncio.create_task() (schedule coroutine)
            - asyncio.gather() (run multiple coroutines)
            
            Best Practices:
            - Use async/await for I/O operations
            - Don't mix blocking and non-blocking code
            - Use asyncio.sleep() instead of time.sleep()
            """,
            "decorators": """
            Python Decorators Documentation:
            
            Function Decorators:
            - @decorator_name
            - def my_decorator(func): return wrapper
            - functools.wraps() to preserve metadata
            
            Class Decorators:
            - @classmethod, @staticmethod, @property
            - Custom class decorators possible
            
            Decorator with Arguments:
            - def decorator_factory(arg): return decorator
            - @decorator_factory("argument")
            """
        }
    }
    
    # Find relevant documentation
    if library in mock_docs:
        lib_docs = mock_docs[library]
        for topic, content in lib_docs.items():
            if topic in query.lower():
                return content
        
        # Return first available documentation if no specific match
        return list(lib_docs.values())[0]
    
    return f"Mock documentation for {library}: {query}"

@tool
def scrap_snippets(lib_name: str, topic: str) -> str:
    """
    Retrieve code snippets related to a specific library and topic.
    
    Args:
        lib_name: The name of the library to search snippets for
        topic: The specific topic within the library to search for
    
    Returns:
        str: The retrieved code snippets
    """
    try:
        # Mock implementation - in production, this would connect to a vector database
        return f"Code snippets for {lib_name} on topic '{topic}':\n\n"\
               f"```python\n# Example snippet for {lib_name} related to {topic}\n"\
               f"def example_function():\n    # This is a mock code snippet\n    print(\"Using {lib_name} for {topic}\")\n    return \"Result\"\n```\n\n"\
               f"Another example:\n```python\n# Alternative approach\nclass Example{lib_name.capitalize()}:\n    def __init__(self):\n        self.config = \"Default config\"\n        \n    def {topic.replace(' ', '_')}(self, param):\n        return f\"Processing {{param}} with {{self.config}}\"\n```"
    except Exception as e:
        return f"Error retrieving code snippets: {str(e)}"

def search_generic_docs(query: str) -> str:
    """
    Search for generic programming documentation.
    """
    generic_docs = {
        "api": """
        API Design Best Practices:
        
        RESTful APIs:
        - Use HTTP methods correctly (GET, POST, PUT, DELETE)
        - Use meaningful resource names
        - Return appropriate status codes
        
        Error Handling:
        - Consistent error response format
        - Meaningful error messages
        - Proper HTTP status codes
        
        Authentication:
        - Use HTTPS for all endpoints
        - Implement proper token validation
        - Consider rate limiting
        """,
        "database": """
        Database Best Practices:
        
        SQL Optimization:
        - Use indexes on frequently queried columns
        - Avoid N+1 queries
        - Use connection pooling
        
        NoSQL Considerations:
        - Choose appropriate data model
        - Consider eventual consistency
        - Plan for horizontal scaling
        
        Security:
        - Use parameterized queries
        - Implement proper access controls
        - Regular security audits
        """,
        "testing": """
        Testing Best Practices:
        
        Unit Testing:
        - Test individual functions/methods
        - Use mocking for external dependencies
        - Aim for high code coverage
        
        Integration Testing:
        - Test component interactions
        - Test database operations
        - Test API endpoints
        
        Test-Driven Development:
        - Write tests before implementation
        - Red-Green-Refactor cycle
        - Keep tests simple and focused
        """,
        "performance": """
        Performance Optimization:
        
        Code Optimization:
        - Profile before optimizing
        - Use appropriate data structures
        - Minimize database queries
        
        Caching Strategies:
        - In-memory caching (Redis)
        - HTTP caching headers
        - Database query caching
        
        Monitoring:
        - Application performance monitoring
        - Database performance metrics
        - Error tracking and logging
        """
    }
    
    # Search for relevant documentation
    for topic, content in generic_docs.items():
        if topic in query.lower():
            return content
    
    return f"Generic documentation for query: {query}"

@tool
def search_stack_overflow(query: str) -> str:
    """
    Search Stack Overflow for programming solutions.
    
    Args:
        query: Search query for Stack Overflow
    
    Returns:
        str: Relevant Stack Overflow content
    """
    try:
        # Mock Stack Overflow search results
        # In production, use Stack Overflow API
        return f"""
        Stack Overflow Search Results for: {query}
        
        Top Answer:
        This is a common issue that can be solved by following these steps:
        1. Check your imports and dependencies
        2. Ensure proper error handling
        3. Use appropriate design patterns
        
        Code Example:
        ```python
        try:
            # Your code here
            result = some_function()
            return result
        except Exception as e:
            logger.error(f"Error: {e}")
            raise
        ```
        
        Additional Resources:
        - Official documentation
        - Related GitHub issues
        - Community discussions
        """
    except Exception as e:
        return f"Error searching Stack Overflow: {str(e)}"

@tool
def analyze_code_structure(code: str) -> str:
    """
    Analyze code structure and provide insights.
    
    Args:
        code: The code to analyze
    
    Returns:
        str: Code structure analysis
    """
    try:
        # Basic code analysis
        lines = code.split('\n')
        non_empty_lines = [line for line in lines if line.strip()]
        
        # Count different code elements
        functions = len([line for line in non_empty_lines if 'def ' in line or 'function ' in line])
        classes = len([line for line in non_empty_lines if 'class ' in line])
        imports = len([line for line in non_empty_lines if line.strip().startswith(('import ', 'from '))])
        comments = len([line for line in non_empty_lines if line.strip().startswith('#') or line.strip().startswith('//')])
        
        # Calculate complexity indicators
        complexity_indicators = {
            'nested_blocks': code.count('    '),  # Basic indentation count
            'conditional_statements': code.count('if ') + code.count('elif ') + code.count('else:'),
            'loops': code.count('for ') + code.count('while '),
            'try_catch_blocks': code.count('try:') + code.count('except:') + code.count('catch')
        }
        
        analysis = f"""
        Code Structure Analysis:
        
        Basic Metrics:
        - Total lines: {len(lines)}
        - Non-empty lines: {len(non_empty_lines)}
        - Functions: {functions}
        - Classes: {classes}
        - Imports: {imports}
        - Comments: {comments}
        
        Complexity Indicators:
        - Nested blocks: {complexity_indicators['nested_blocks']}
        - Conditional statements: {complexity_indicators['conditional_statements']}
        - Loops: {complexity_indicators['loops']}
        - Error handling blocks: {complexity_indicators['try_catch_blocks']}
        
        Recommendations:
        - {'Consider breaking down large functions' if functions > 10 else 'Function count looks good'}
        - {'Add more comments for better readability' if comments < len(non_empty_lines) * 0.1 else 'Good comment coverage'}
        - {'Consider refactoring complex logic' if complexity_indicators['nested_blocks'] > 50 else 'Complexity looks manageable'}
        """
        
        return analysis
        
    except Exception as e:
        return f"Error analyzing code structure: {str(e)}"

@tool
def generate_code_suggestions(language: str, context: str) -> str:
    """
    Generate code suggestions based on language and context.
    
    Args:
        language: Programming language
        context: Context or specific area for suggestions
    
    Returns:
        str: Code suggestions and best practices
    """
    try:
        suggestions_db = {
            "python": {
                "fastapi": """
                FastAPI Best Practices:
                
                1. Project Structure:
                ```
                app/
                ├── main.py
                ├── models/
                ├── routers/
                ├── services/
                └── dependencies/
                ```
                
                2. Error Handling:
                ```python
                from fastapi import HTTPException
                
                @app.get("/items/{item_id}")
                async def read_item(item_id: int):
                    if item_id < 0:
                        raise HTTPException(status_code=400, detail="Invalid item ID")
                    return {"item_id": item_id}
                ```
                
                3. Dependency Injection:
                ```python
                from fastapi import Depends
                
                def get_db():
                    db = SessionLocal()
                    try:
                        yield db
                    finally:
                        db.close()
                
                @app.get("/users/")
                async def read_users(db: Session = Depends(get_db)):
                    return db.query(User).all()
                ```
                """,
                "general": """
                Python Best Practices:
                
                1. Code Style:
                - Follow PEP 8 guidelines
                - Use meaningful variable names
                - Add docstrings to functions
                
                2. Error Handling:
                - Use specific exception types
                - Provide meaningful error messages
                - Clean up resources properly
                
                3. Performance:
                - Use list comprehensions when appropriate
                - Avoid premature optimization
                - Profile your code
                """
            },
            "javascript": {
                "react": """
                React Best Practices:
                
                1. Component Structure:
                ```jsx
                import React, { useState, useEffect } from 'react';
                
                const MyComponent = ({ prop1, prop2 }) => {
                    const [state, setState] = useState(initialValue);
                    
                    useEffect(() => {
                        // Side effect logic
                    }, [dependencies]);
                    
                    return <div>{/* JSX */}</div>;
                };
                
                export default MyComponent;
                ```
                
                2. State Management:
                - Use useState for local state
                - Use useReducer for complex state logic
                - Consider context for global state
                
                3. Performance:
                - Use React.memo for expensive components
                - Optimize re-renders with useMemo/useCallback
                - Code splitting with React.lazy
                """,
                "general": """
                JavaScript Best Practices:
                
                1. Modern Syntax:
                - Use const/let instead of var
                - Use arrow functions appropriately
                - Destructuring for cleaner code
                
                2. Async Programming:
                - Use async/await over promises
                - Handle errors properly
                - Avoid callback hell
                
                3. Code Organization:
                - Use modules (import/export)
                - Separate concerns
                - Use linting tools
                """
            }
        }
        
        if language in suggestions_db:
            if context in suggestions_db[language]:
                return suggestions_db[language][context]
            else:
                return suggestions_db[language].get("general", f"General {language} suggestions")
        
        return f"Code suggestions for {language} in {context} context: Use best practices, follow style guides, and write clean, maintainable code."
        
    except Exception as e:
        return f"Error generating code suggestions: {str(e)}"

def invoke_tool(tool_call: Dict[str, Any]) -> ToolMessage:
    """
    Invoke a tool and return a ToolMessage.
    
    Args:
        tool_call: Dictionary containing tool name and arguments
    
    Returns:
        ToolMessage: The result of the tool invocation
    """
    try:
        tool_name = tool_call.get("name")
        tool_args = tool_call.get("args", {})
        tool_id = tool_call.get("id", "")
        
        # Map tool names to functions
        tool_functions = {
            "scrap_docs": scrap_docs,
            "search_stack_overflow": search_stack_overflow,
            "analyze_code_structure": analyze_code_structure,
            "generate_code_suggestions": generate_code_suggestions
        }
        
        if tool_name in tool_functions:
            result = tool_functions[tool_name].invoke(tool_args)
            return ToolMessage(content=result, tool_call_id=tool_id)
        else:
            return ToolMessage(
                content=f"Unknown tool: {tool_name}",
                tool_call_id=tool_id
            )
            
    except Exception as e:
        return ToolMessage(
            content=f"Error invoking tool: {str(e)}",
            tool_call_id=tool_call.get("id", "")
        )