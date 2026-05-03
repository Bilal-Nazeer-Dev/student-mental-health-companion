import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    SECRET_KEY = os.getenv('SECRET_KEY', 'sage-dev-secret-key-2024')
    GEMINI_API_KEY = os.getenv('GEMINI_API_KEY', '').strip()
    GEMINI_MODEL = os.getenv('GEMINI_MODEL', 'gemini-flash-latest')
    DATABASE_PATH = os.getenv('DATABASE_PATH', 'mental_health.db')
    DEBUG = os.getenv('DEBUG', 'True') == 'True'

# Debug check (requested by user)
if Config.GEMINI_API_KEY:
    print(f"DEBUG: API Key loaded from .env: {Config.GEMINI_API_KEY}")
    print(f"DEBUG: Key Length: {len(Config.GEMINI_API_KEY)}")
else:
    print("ERROR: API Key NOT found in environment! Check .env file.")
