import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    SECRET_KEY = os.getenv('SECRET_KEY', 'sage-dev-secret-key-2024')
    GEMINI_API_KEY = os.getenv('GEMINI_API_KEY', '')
    GEMINI_MODEL = os.getenv('GEMINI_MODEL', 'gemini-1.5-flash')
    DATABASE_PATH = os.getenv('DATABASE_PATH', 'mental_health.db')
    DEBUG = os.getenv('DEBUG', 'True') == 'True'
