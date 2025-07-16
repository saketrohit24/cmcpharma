import os
from dotenv import load_dotenv

# Load environment variables from .env file in the project root
load_dotenv()

class Settings:
    """Loads settings from environment variables."""
    NVIDIA_API_KEY: str = os.getenv("NVIDIA_API_KEY")
    LLM_API_KEY: str = os.getenv("LLM_API_KEY")
    DATABASE_URL: str = os.getenv("DATABASE_URL")

settings = Settings()
