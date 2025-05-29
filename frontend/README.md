# Personal Knowledge Assistant - Frontend

This is the Streamlit-based frontend for the Personal Knowledge Management AI Assistant.

## Features

- 💬 Chat interface for asking questions about your notes
- 📅 View recent updates and changes to your knowledge base
- 📊 Monitor system status and collection statistics
- 🔄 Manually trigger note reindexing and summary generation

## Prerequisites

- Python 3.10+
- Backend service running (see main README for setup)
- Required Python packages (install with `pip install -r requirements.txt`)

## Installation

1. Clone the repository
2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
3. Copy `.env.example` to `.env` and configure:
   ```
   API_BASE_URL=http://localhost:8000  # URL of your backend service
   ```

## Running the Frontend

Start the Streamlit app with:

```bash
streamlit run app.py
```

The app will be available at `http://localhost:8501` by default.

## Development

### Project Structure

- `app.py`: Main Streamlit application
- `utils.py`: Utility functions for API communication
- `requirements.txt`: Python dependencies

### Environment Variables

- `API_BASE_URL`: Base URL of the backend API (default: `http://localhost:8000`)

## License

MIT
