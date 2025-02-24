import os
from dotenv import load_dotenv

load_dotenv()  # Load environment variables from .env file

class Config:
    API_ID = int(os.getenv("API_ID", "your_api_id"))
    API_HASH = os.getenv("API_HASH", "your_api_hash")
    BOT_TOKEN = os.getenv("BOT_TOKEN", "your_bot_token")
    DOWNLOAD_FOLDER = "downloads/"
    
    os.makedirs(DOWNLOAD_FOLDER, exist_ok=True)  # Create download folder if not exists
