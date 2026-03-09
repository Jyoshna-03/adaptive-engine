import os
from motor.motor_asyncio import AsyncIOMotorClient
from dotenv import load_dotenv

load_dotenv()

MONGODB_URI = os.getenv("MONGODB_URI", "mongodb://localhost:27017")
DB_NAME = os.getenv("DB_NAME", "adaptive_engine")

client: AsyncIOMotorClient = None

async def connect_db():
    global client
    client = AsyncIOMotorClient(MONGODB_URI)
    print(f"✅ Connected to MongoDB: {DB_NAME}")

async def close_db():
    global client
    if client:
        client.close()
        print("🔌 MongoDB connection closed")

def get_db():
    return client[DB_NAME]