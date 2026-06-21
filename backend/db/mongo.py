from motor.motor_asyncio import AsyncIOMotorClient
from dotenv import load_dotenv
from pathlib import Path
import os

env_path = Path(__file__).resolve().parent.parent / ".env"

load_dotenv(env_path)

MONGO_URI = os.getenv("MONGO_URI")


client = AsyncIOMotorClient(MONGO_URI)

db = client.collegegpt