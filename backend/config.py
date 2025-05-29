from pathlib import Path
from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    # Application
    APP_NAME: str = "Personal Knowledge Assistant"
    ENVIRONMENT: str = "development"
    DEBUG: bool = True
    
    # Server
    HOST: str = "0.0.0.0"
    PORT: int = 8000
    
    # Qdrant
    QDRANT_URL: str = "http://qdrant:6333"
    QDRANT_COLLECTION: str = "personal_knowledge"
    
    # LLM
    OLLAMA_BASE_URL: str = "http://host.docker.internal:11434"
    MODEL_NAME: str = "gemma:3b"
    
    # Paths
    BASE_DIR: Path = Path(__file__).parent.parent
    DATA_DIR: Path = BASE_DIR / "data"
    SUMMARIES_DIR: Path = DATA_DIR / "summaries"
    NOTES_DIR: Path = DATA_DIR / "notes"
    
    # Scheduler
    SUMMARY_SCHEDULE: str = "0 20 * * *"  # Daily at 8 PM
    
    # Model Config
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")
    
    def setup_dirs(self) -> None:
        """Create necessary directories if they don't exist."""
        self.DATA_DIR.mkdir(exist_ok=True)
        self.SUMMARIES_DIR.mkdir(exist_ok=True)
        self.NOTES_DIR.mkdir(exist_ok=True)

# Initialize settings
settings = Settings()
settings.setup_dirs()
