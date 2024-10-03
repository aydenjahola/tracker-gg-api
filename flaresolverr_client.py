import aiohttp
import os
from dotenv import load_dotenv

load_dotenv()

FLARESOLVERR_URL = os.getenv("FLARESOLVERR_URL")

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/85.0.4183.121 Safari/537.36",
    "Accept-Language": "en-US,en;q=0.9",
    "Referer": "https://tracker.gg/",
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
}


async def fetch_page_with_flaresolverr(url: str) -> str:
    payload = {"cmd": "request.get", "url": url, "maxTimeout": 60000}

    async with aiohttp.ClientSession() as session:
        try:
            async with session.post(FLARESOLVERR_URL, json=payload) as response:
                response.raise_for_status()
                result = await response.json()
                return result.get("solution", {}).get("response", "")
        except aiohttp.ClientResponseError as e:
            print(f"HTTP error occurred: {e.status} - {e.message}")
            return ""
        except Exception as e:
            print(f"An error occurred: {e}")
            return ""
