import logging
import os
from dotenv import load_dotenv

load_dotenv()

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s [%(levelname)s] %(name)s: %(message)s',
)
logger = logging.getLogger('config')


class Config:
    SECRET_KEY = os.getenv('SECRET_KEY', 'sage-dev-secret-key-2024')
    GEMINI_API_KEY = os.getenv('GEMINI_API_KEY', '').strip()
    GEMINI_MODEL = os.getenv('GEMINI_MODEL', 'gemini-2.5-flash-lite').strip()
    DATABASE_PATH = os.getenv('DATABASE_PATH', 'mental_health.db')
    DEBUG = os.getenv('DEBUG', 'True') == 'True'


def _mask(key: str) -> str:
    if not key:
        return '<empty>'
    if len(key) <= 8:
        return '*' * len(key)
    return f'{key[:4]}...{key[-4:]}'


if Config.GEMINI_API_KEY:
    logger.info(
        'Gemini API key loaded (key=%s, length=%d, model=%s)',
        _mask(Config.GEMINI_API_KEY),
        len(Config.GEMINI_API_KEY),
        Config.GEMINI_MODEL,
    )
else:
    logger.error('GEMINI_API_KEY is not set. Add it to your .env file.')
