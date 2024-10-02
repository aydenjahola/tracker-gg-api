from pydantic import BaseModel
from typing import Optional

class PlayerStats(BaseModel):
    username: str
    platform: str
    season: Optional[str] = None
    kills: Optional[int] = None
    wins: Optional[int] = None
    matches_played: Optional[int] = None
    kd_ratio: Optional[float] = None
    current_rank: Optional[str] = None
    peak_rank: Optional[str] = None
    headshot_percentage: Optional[float] = None
    win_percentage: Optional[float] = None
    hours_played: Optional[float] = None
    tracker_score: Optional[int] = None