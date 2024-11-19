import os
import random
import string
from fastapi import FastAPI, HTTPException, Depends, Header
from fastapi.security import APIKeyHeader
from fastapi_limiter import FastAPILimiter
from fastapi_limiter.depends import RateLimiter
import redis.asyncio as redis
from contextlib import asynccontextmanager
from sqlalchemy.orm import Session
from databases import Database

from scrapers.valorant_scraper import fetch_valorant_player_stats
from scrapers.cs2_scraper import fetch_cs2_player_stats
from models.valorant_model import ValorantPlayerStats
from models.cs2_model import CS2PlayerStats
from scrapers.tft_scraper import fetch_tft_player_stats
from models.tft_model import TFTPlayerStats

from models.db import create_db, add_api_key, SessionLocal, APIKey

from dotenv import load_dotenv


load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL", "Please set DATABASE_URL environment variable")
database = Database(DATABASE_URL)

API_KEY_HEADER = "X-API-Key"
api_key_header = APIKeyHeader(name=API_KEY_HEADER)


def get_session_local():
    yield SessionLocal()


# Fetch API keys from the database
def get_api_keys_from_db(db: Session):
    keys = db.query(APIKey.key).all()
    return {key[0] for key in keys}


# Dependency to validate the API key using SQLAlchemy ORM
async def get_api_key(
    api_key: str = Depends(api_key_header), db: Session = Depends(get_session_local)
):
    db_api_key = db.query(APIKey).filter(APIKey.key == api_key).first()

    if not db_api_key:
        raise HTTPException(status_code=403, detail="Invalid API Key")

    return api_key


# Function to generate a random API key
def generate_random_api_key() -> str:
    """Generates a random 32-character API key."""
    return "".join(random.choices(string.ascii_letters + string.digits, k=32))


# Check if the app is running for the first time (no API keys)
def check_first_run(db: Session) -> bool:
    count = db.query(APIKey).count()
    return count == 0


async def add_admin_key(admin_key: str, db: Session):
    """Adds an admin API key to the database and prints it."""
    # Create an admin key with the permission 'admin'
    add_api_key(db, admin_key, user="admin", permission="admin")
    print(f"Admin API key generated: {admin_key}")


# Define a lifespan function for managing startup and shutdown
@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Context manager to manage app lifecycle events.
    """

    redis_url = os.getenv("REDIS_URL", "redis://localhost:6379")
    redis_client = redis.from_url(redis_url, encoding="utf-8", decode_responses=True)

    await FastAPILimiter.init(redis_client)

    await database.connect()

    create_db()

    db = SessionLocal()
    if check_first_run(db):
        admin_key = generate_random_api_key()
        await add_admin_key(admin_key, db)
    db.close()

    yield

    await redis_client.close()
    await database.disconnect()


app = FastAPI(lifespan=lifespan)


@app.get(
    "/valorant/player/{username}/current",
    response_model=ValorantPlayerStats,
    dependencies=[Depends(RateLimiter(times=10, seconds=60))],
)
async def get_valorant_current_act_stats(
    username: str, api_key: str = Depends(get_api_key)
):
    player_stats = await fetch_valorant_player_stats(
        username=username, season="current"
    )
    if player_stats is None:
        raise HTTPException(
            status_code=404, detail=f"Player stats not found for username: {username}."
        )
    player_stats.season = "Current Act"
    return player_stats


@app.get(
    "/valorant/player/{username}/all",
    response_model=ValorantPlayerStats,
    dependencies=[Depends(RateLimiter(times=10, seconds=60))],
)
async def get_valorant_all_seasons_stats(
    username: str, api_key: str = Depends(get_api_key)
):
    player_stats = await fetch_valorant_player_stats(username=username, season="all")
    if player_stats is None:
        raise HTTPException(
            status_code=404, detail=f"Player stats not found for username: {username}."
        )
    player_stats.season = "All Acts"
    return player_stats


@app.get(
    "/cs2/player/{steam_id}",
    response_model=CS2PlayerStats,
    dependencies=[Depends(RateLimiter(times=10, seconds=60))],
)
async def get_cs2_stats(steam_id: str, api_key: str = Depends(get_api_key)):
    player_stats = await fetch_cs2_player_stats(steam_id=steam_id)
    if player_stats is None:
        raise HTTPException(
            status_code=404, detail=f"Player stats not found for steam_id: {steam_id}."
        )
    return player_stats


@app.get(
    "/tft/player/{username}",
    response_model=TFTPlayerStats,
    dependencies=[Depends(RateLimiter(times=10, seconds=60))],
)
async def get_tft_player_stats(username: str, api_key: str = Depends(get_api_key)):
    player_stats = await fetch_tft_player_stats(username=username)
    if player_stats is None:
        raise HTTPException(
            status_code=404, detail=f"Player stats not found for username: {username}."
        )
    return player_stats


@app.get("/status", summary="API Health Check")
async def status():
    return {"status": "ok"}


@app.post(
    "/admin/create-api-key",
    summary="Create a new API Key",
)
async def create_new_api_key(
    user: str,
    new_api_key: str = Header(None, include_in_schema=False),
    permission: str = "normal",
    api_key: str = Depends(get_api_key),
    db: Session = Depends(get_session_local),
):
    """
    Create a new API key, but only accessible to users with 'admin' permissions.
    """
    db_api_key = db.query(APIKey).filter(APIKey.key == api_key).first()

    if not db_api_key:
        raise HTTPException(status_code=403, detail="Invalid API Key")

    # Check if the user has admin privileges
    if db_api_key.permission != "admin":
        raise HTTPException(
            status_code=403,
            detail="You must have 'admin' permissions to create new API keys.",
        )

    # Check for valid permission level in the request
    if permission not in ["normal", "admin"]:
        raise HTTPException(status_code=400, detail="Invalid permission level.")

    # If no API key is provided, generate a random one
    if not new_api_key:
        new_api_key = generate_random_api_key()

    try:
        # Call function to add the new API key to the database
        add_api_key(db, new_api_key, user, permission)
        return {
            "message": f"API Key '{new_api_key}' created successfully for user '{user}' with permission '{permission}'."
        }
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))
