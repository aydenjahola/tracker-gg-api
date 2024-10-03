from pydantic import BaseModel
from typing import Optional

class CS2PlayerStats(BaseModel):
    steam_id: str
    platform: str
    current_rank: Optional[str] = None
    peak_rank: Optional[str] = None
    kd_ratio: Optional[float] = None
    matches_played: Optional[int] = None
    headshot_percentage: Optional[float] = None
    win_percentage: Optional[float] = None
    kills: Optional[int] = None
    wins: Optional[int] = None
    hours_played: Optional[float] = None
    tracker_score: Optional[int] = None
