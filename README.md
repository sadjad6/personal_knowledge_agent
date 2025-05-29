# Personal Knowledge Management AI Assistant

A powerful, self-hosted AI assistant for managing and querying your personal knowledge base using natural language. Built with FastAPI, LangChain, Qdrant, and Streamlit, with a local Gemma 3B model for privacy and offline use.

## ✨ Features

- **📝 Multi-format Support**: Ingest notes from Markdown, Notion exports, and Obsidian vaults
- **🔍 Semantic Search**: Find information using natural language queries
- **🤖 RAG-Powered Q&A**: Get accurate answers from your knowledge base using Retrieval-Augmented Generation
- **📅 Automated Summaries**: Daily summaries of new or updated notes
- **🔒 Privacy-First**: Runs locally with Ollama and Qdrant, keeping your data private
- **🌐 Web Interface**: User-friendly Streamlit frontend
- **🐳 Docker Support**: Easy deployment with Docker Compose
- **⏰ Scheduled Tasks**: Automatic processing of new content

## 🚀 Quick Start

### Prerequisites

- Docker and Docker Compose
- At least 8GB RAM (16GB recommended)
- Ollama with Gemma 3B model installed

### Installation

1. **Clone the repository**
   ```bash
   git clone https://github.com/yourusername/personal-knowledge-assistant.git
   cd personal-knowledge-assistant
   ```

2. **Set up environment variables**
   ```bash
   cp .env.example .env
   ```
   Edit the `.env` file to configure your settings.

3. **Add your notes**
   Place your Markdown, Notion, or Obsidian notes in the `data/notes` directory.

4. **Start the services**
   ```bash
   docker-compose up --build
   ```

5. **Access the application**
   - Frontend: http://localhost:8501
   - API Docs: http://localhost:8000/docs

## 🏗️ Project Structure

```
personal-ai-agent/
├── backend/                  # FastAPI backend
│   ├── api/                  # API endpoints and routes
│   ├── services/             # Core business logic
│   ├── rag/                  # RAG pipeline components
│   ├── main.py               # FastAPI application entry point
│   └── config.py             # Application configuration
├── frontend/                 # Streamlit frontend
│   ├── app.py                # Main application
│   └── utils.py              # Utility functions
├── data/                     # Data directory
│   ├── notes/                # Your personal notes go here
│   └── summaries/            # Generated summaries are stored here
├── tests/                    # Unit and integration tests
├── .env.example              # Example environment variables
├── docker-compose.yml        # Docker Compose configuration
├── Dockerfile                # Backend Dockerfile
└── README.md                # This file
```

## 🔧 Configuration

Edit the `.env` file to customize the application:

```env
# API Configuration
APP_NAME=Personal Knowledge Assistant
ENVIRONMENT=development
DEBUG=True

# Server
HOST=0.0.0.0
PORT=8000

# Qdrant
QDRANT_URL=http://qdrant:6333
QDRANT_COLLECTION=personal_knowledge

# LLM
OLLAMA_BASE_URL=http://host.docker.internal:11434
MODEL_NAME=gemma:3b

# Paths
DATA_DIR=./data
SUMMARIES_DIR=./data/summaries
NOTES_DIR=./data/notes

# Scheduler
SUMMARY_SCHEDULE="0 20 * * *"  # Daily at 8 PM
```

## 🛠️ Development

### Prerequisites

- Python 3.10+
- Poetry (for dependency management)
- Node.js and npm (for frontend development)

### Setup

1. **Install Python dependencies**
   ```bash
   pip install -r requirements.txt
   ```

2. **Install frontend dependencies**
   ```bash
   cd frontend
   npm install
   ```

3. **Run the backend**
   ```bash
   cd backend
   uvicorn main:app --reload
   ```

4. **Run the frontend**
   ```bash
   cd frontend
   streamlit run app.py
   ```

### Running Tests

```bash
# Run all tests
pytest

# Run tests with coverage
pytest --cov=backend --cov-report=term-missing
```

## 🤖 API Endpoints

- `GET /api/v1/ask?q=your+question` - Get an answer to a question
- `POST /api/v1/summarize` - Manually trigger summary generation
- `GET /api/v1/status` - Get system status
- `POST /api/v1/ingest` - Manually trigger note ingestion

## 🌐 Frontend

The Streamlit frontend provides a user-friendly interface for interacting with your knowledge base:

- **Chat Interface**: Ask questions about your notes
- **Recent Updates**: View recently added or modified notes
- **Knowledge Base Status**: Monitor system health and statistics
- **Manual Controls**: Trigger actions like reindexing and summary generation

## 🔄 Scheduled Tasks

The application includes a scheduler that runs the following tasks:

- **Daily Summary**: Generates a summary of new or updated notes (runs at 8 PM by default)

## 🐳 Docker Deployment

### Prerequisites

- Docker and Docker Compose
- Ollama running with the Gemma 3B model

### Steps

1. **Start Ollama** (if not already running)
   ```bash
   ollama serve
   ```

2. **Pull the Gemma 3B model**
   ```bash
   ollama pull gemma:3b
   ```

3. **Build and start the application**
   ```bash
   docker-compose up --build -d
   ```

4. **Access the application**
   - Frontend: http://localhost:8501
   - API Docs: http://localhost:8000/docs

## 📚 Supported File Formats

- Markdown (`.md`, `.markdown`)
- Text files (`.txt`)
- PDF (`.pdf`)
- Microsoft Word (`.docx`)
- PowerPoint (`.pptx`)
- CSV (`.csv`)

## 🤝 Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- [FastAPI](https://fastapi.tiangolo.com/) - Modern, fast web framework
- [LangChain](https://python.langchain.com/) - Framework for developing LLM applications
- [Qdrant](https://qdrant.tech/) - Vector similarity search engine
- [Streamlit](https://streamlit.io/) - For the web interface
- [Ollama](https://ollama.ai/) - For running LLMs locally
- [Gemma](https://ai.google.dev/gemma) - Open LLM by Google
