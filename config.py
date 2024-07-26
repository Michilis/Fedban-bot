from dotenv import load_dotenv
import os

load_dotenv()

BOT_TOKEN = os.getenv("BOT_TOKEN")
LOG_GROUP_ID = os.getenv("LOG_GROUP_ID")
DATABASE_URL = os.getenv("DATABASE_URL")
DEBUGGING = os.getenv("DEBUGGING", "False").lower() in ("true", "1", "t")
