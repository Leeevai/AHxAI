"""
Example usage of the Enhanced Coding AI Agent API
"""
import requests
import json

# API base URL
BASE_URL = "http://localhost:8000"

def test_basic_code_analysis():
    """Test the basic code analysis endpoint"""
    print("Testing basic code analysis...")
    
    code_request = {
        "code": """
def bubble_sort(arr):
    n = len(arr)
    for i in range(n):
        for j in range(0, n-i-1):
            if arr[j] > arr[j+1]:
                arr[j], arr[j+1] = arr[j+1], arr[j]
    return arr

# Example usage
numbers = [64, 34, 25, 12, 22, 11, 90]
sorted_numbers = bubble_sort(numbers)
print(sorted_numbers)
        """,
        "language": "python",
        "context": "Looking for performance improvements and best practices"
    }
    
    response = requests.post(f"{BASE_URL}/api/analyze", json=code_request)
    if response.status_code == 200:
        result = response.json()
        print(f"Chat ID: {result['chat_id']}")
        print(f"Analysis: {result['ai_response']['explanation']}")
        print(f"Suggestions: {result['ai_response']['suggestions']}")
    else:
        print(f"Error: {response.status_code} - {response.text}")

def test_advanced_query():
    """Test the advanced query endpoint with LangChain"""
    print("\nTesting advanced query...")
    
    query_request = {
        "query": "How can I optimize a FastAPI application for better performance? I need help with database connections, caching, and async operations.",
        "system_prompt": "You are an expert Python developer specializing in FastAPI and performance optimization. Provide detailed, actionable advice with code examples."
    }
    
    response = requests.post(f"{BASE_URL}/api/query", json=query_request)
    if response.status_code == 200:
        result = response.json()
        print(f"Chat ID: {result['chat_id']}")
        print(f"Result: {result['result']}")
        print(f"Tool calls: {result['tool_calls']}")
    else:
        print(f"Error: {response.status_code} - {response.text}")

def test_chat_management():
    """Test chat management endpoints"""
    print("\nTesting chat management...")
    
    # Create a new chat
    response = requests.post(f"{BASE_URL}/api/chats")
    if response.status_code == 200:
        chat = response.json()
        chat_id = chat['id']
        print(f"Created chat: {chat_id}")
        
        # Send a message to the chat
        message_request = {
            "content": "Hello, I need help with React hooks",
            "is_user": True
        }
        
        response = requests.post(f"{BASE_URL}/api/chats/{chat_id}/messages", json=message_request)
        if response.status_code == 200:
            message = response.json()
            print(f"Sent message: {message['content']}")
        
        # Get chat messages
        response = requests.get(f"{BASE_URL}/api/chats/{chat_id}/messages")
        if response.status_code == 200:
            messages = response.json()
            print(f"Chat has {len(messages)} messages")
        
        # Get all chats
        response = requests.get(f"{BASE_URL}/api/chats")
        if response.status_code == 200:
            chats = response.json()
            print(f"Total chats: {len(chats)}")

def test_health_check():
    """Test the health check endpoint"""
    print("\nTesting health check...")
    
    response = requests.get(f"{BASE_URL}/health")
    if response.status_code == 200:
        health = response.json()
        print(f"API Status: {health['status']}")
        print(f"Timestamp: {health['timestamp']}")
    else:
        print(f"Health check failed: {response.status_code}")

def test_react_component_analysis():
    """Test React component analysis"""
    print("\nTesting React component analysis...")
    
    react_code = """
import React, { useState, useEffect } from 'react';

const UserProfile = ({ userId }) => {
    const [user, setUser] = useState(null);
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState(null);

    useEffect(() => {
        fetchUser();
    }, [userId]);

    const fetchUser = async () => {
        try {
            setLoading(true);
            const response = await fetch(`/api/users/${userId}`);
            const userData = await response.json();
            setUser(userData);
        } catch (err) {
            setError(err.message);
        } finally {
            setLoading(false);
        }
    };

    if (loading) return <div>Loading...</div>;
    if (error) return <div>Error: {error}</div>;
    if (!user) return <div>User not found</div>;

    return (
        <div className="user-profile">
            <h2>{user.name}</h2>
            <p>{user.email}</p>
            <p>Joined: {new Date(user.createdAt).toLocaleDateString()}</p>
        </div>
    );
};

export default UserProfile;
    """
    
    code_request = {
        "code": react_code,
        "language": "javascript",
        "context": "React component for user profile display with API integration"
    }
    
    response = requests.post(f"{BASE_URL}/api/analyze", json=code_request)
    if response.status_code == 200:
        result = response.json()
        print("React Component Analysis:")
        print(f"Explanation: {result['ai_response']['explanation']}")
        print(f"Suggestions: {result['ai_response']['suggestions']}")
        print(f"Warnings: {result['ai_response']['warnings']}")
    else:
        print(f"Error: {response.status_code} - {response.text}")

def test_complex_query():
    """Test complex query with multiple technologies"""
    print("\nTesting complex query...")
    
    query_request = {
        "query": "I'm building a full-stack application with React frontend, FastAPI backend, and PostgreSQL database. I need help with user authentication, real-time updates using WebSockets, and deployment strategies. Can you provide a comprehensive guide?",
        "system_prompt": "You are a senior full-stack developer with expertise in React, FastAPI, PostgreSQL, and modern deployment practices. Provide detailed architectural guidance and code examples."
    }
    
    response = requests.post(f"{BASE_URL}/api/query", json=query_request)
    if response.status_code == 200:
        result = response.json()
        print("Complex Query Result:")
        print(f"Result: {result['result'][:500]}...")  # Show first 500 chars
        print(f"Tool calls made: {len(result['tool_calls'])}")
    else:
        print(f"Error: {response.status_code} - {response.text}")

if __name__ == "__main__":
    print("Enhanced Coding AI Agent API - Example Usage")
    print("=" * 50)
    
    try:
        # Test health check first
        test_health_check()
        
        # Test basic functionality
        test_basic_code_analysis()
        
        # Test advanced query
        test_advanced_query()
        
        # Test chat management
        test_chat_management()
        
        # Test React component analysis
        test_react_component_analysis()
        
        # Test complex query
        test_complex_query()
        
        print("\n" + "=" * 50)
        print("All tests completed!")
        
    except requests.exceptions.ConnectionError:
        print("Error: Could not connect to the API server.")
        print("Make sure the FastAPI server is running on http://localhost:8000")
        print("Run: python main.py")
    except Exception as e:
        print(f"Unexpected error: {e}")