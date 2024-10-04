# models/tft_model.py

from pydantic import BaseModel
from typing import Optional


class TFTPlayerStats(BaseModel):
    username: str
    platform: str
    current_rank: Optional[str] = None
    lp: Optional[int] = None
    wins: Optional[int] = None
    losses: Optional[int] = None
    win_percentage: Optional[float] = None
    matches_played: Optional[int] = None
