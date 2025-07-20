# 🤖 AHxAI - Advanced LLM Context Enhancement Platform

A sophisticated AI-powered coding assistant that enhances Large Language Models (LLMs) by providing dynamic context, documentation, and code snippets from both public and private libraries.

## ✨ What is AHxAI?

AHxAI is an intelligent layer built on top of LLMs that dramatically improves their effectiveness by:

- **Dynamic Context Retrieval**: Automatically fetches relevant documentation and code snippets
- **Smart Library Detection**: Identifies and separates public vs private libraries from user queries
- **Vector Database Integration**: Leverages Pinecone for private codebase knowledge
- **Multi-LLM Support**: Combines OpenAI GPT-4 and Google Gemini for optimal results
- **Real-time Code Analysis**: Provides instant feedback and suggestions

## 🛠 Technology Stack

### Backend
- **FastAPI** - High-performance API framework
- **LangChain** - LLM orchestration and chaining
- **OpenAI GPT-4** - Primary language model
- **Google Gemini AI** - Code analysis and secondary LLM
- **Pinecone** - Vector database for code snippets
- **PostgreSQL** - Persistent data storage
- **Pydantic** - Data validation and structured outputs

### Frontend
- **React 18.3** - Modern UI framework
- **Vite** - Lightning-fast build tool
- **Tailwind CSS** - Utility-first styling
- **Lucide React** - Beautiful icons
- **React Syntax Highlighter** - Code display
- **Recharts** - Data visualization
- **Three.js & D3.js** - Advanced 3D and interactive visualizations

## 🚀 Quick Start

### Prerequisites
- Node.js 18+ and npm
- Python 3.8+
- PostgreSQL database
- OpenAI API key
- Google AI API key
- Pinecone API key

### Backend Setup

1. **Navigate to backend directory**:
   ```bash
   cd backend
   ```

2. **Install Python dependencies**:
   ```bash
   pip install fastapi uvicorn langchain openai google-generativeai pinecone-client psycopg2-binary pydantic requests python-dotenv
   ```

3. **Set up environment variables**:
   Create a `.env` file in the backend directory:
   ```env
   OPENAI_API_KEY=your_openai_api_key
   GOOGLE_API_KEY=your_google_ai_api_key
   PINECONE_API_KEY=your_pinecone_api_key
   DATABASE_URL=postgresql://username:password@localhost/database_name
   ```

4. **Start the backend server**:
   ```bash
   uvicorn main:app --reload --port 8000
   ```

### Frontend Setup

1. **Navigate to frontend directory**:
   ```bash
   cd frontend
   ```

2. **Install dependencies**:
   ```bash
   npm install
   ```

3. **Start the development server**:
   ```bash
   npm run dev
   ```

The application will be available at:
- **Frontend**: http://localhost:5173
- **Backend API**: http://localhost:8000
- **API Documentation**: http://localhost:8000/docs

## 🎯 Key Features

### Smart Context Enhancement
- **Library Detection**: Automatically identifies relevant libraries from user queries
- **Documentation Scraping**: Fetches real-time docs from external sources
- **Code Snippet Retrieval**: Accesses private codebases via Pinecone vector search
- **Context Assembly**: Combines user input with relevant documentation and examples

### Interactive UI
- **Tabbed Interface**: Code, Explanation, and Visualization views
- **Real-time Chat**: Persistent conversation with context memory
- **Code Editor**: Syntax highlighting and formatting
- **Collapsible Panels**: Customizable workspace layout

### Advanced Analysis
- **Multi-LLM Processing**: Leverages both GPT-4 and Gemini strengths
- **Structured Outputs**: Organized responses with clear sections
- **Visual Representations**: Charts, graphs, and 3D visualizations
- **Code Improvement**: Automated suggestions and optimizations

## 📁 Project Structure

```
AHxAI/
├── backend/
│   ├── main.py              # FastAPI application entry point
│   ├── structured_outputs.py # Pydantic models and LLM structures
│   ├── llm_tools.py         # Documentation and snippet retrieval
│   └── requirements.txt     # Python dependencies
├── frontend/
│   ├── src/
│   │   ├── components/
│   │   │   └── CodingAIAgent.jsx # Main React component
│   │   ├── App.jsx          # React app root
│   │   └── main.jsx         # Vite entry point
│   ├── package.json         # Node.js dependencies
│   ├── tailwind.config.js   # Tailwind configuration
│   └── vite.config.js       # Vite build configuration
└── README.md               # This file
```

## 🔧 API Endpoints

### Core Endpoints
- `POST /execute-query` - Main LLM processing with context enhancement
- `POST /api/analyze` - Code analysis using Gemini AI
- `GET /api/chats` - Retrieve chat history
- `POST /api/chats` - Create new chat session
- `GET /api/visualization/{message_id}` - Generate HTML visualizations

### Health & Monitoring
- `GET /health` - Application health check
- `GET /docs` - Interactive API documentation

## 🌟 How It Works

1. **Query Analysis**: User input is analyzed to extract relevant libraries and concepts
2. **Context Retrieval**: System fetches documentation from external sources and vector database
3. **Context Enhancement**: User query is enriched with relevant documentation and code examples
4. **LLM Processing**: Enhanced context is sent to appropriate LLM (GPT-4 or Gemini)
5. **Structured Response**: Results are formatted and presented with code, explanations, and visualizations

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## 📝 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- OpenAI for GPT-4 API
- Google for Gemini AI
- Pinecone for vector database capabilities
- The open-source community for the amazing tools and libraries

---

**Built with ❤️ by the AHxAI Team**