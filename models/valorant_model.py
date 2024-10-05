from pydantic import BaseModel
from typing import Optional, List


class Weapon(BaseModel):
    name: str
    weapon_type: str
    silhouette_url: str
    accuracy: List[str]
    kills: int


class MapStats(BaseModel):
    name: str
    win_percentage: str
    matches: str


class Role(BaseModel):
    name: str
    win_rate: str
    kda: float
    wins: int
    losses: int
    kills: int
    deaths: int
    assists: int


class ValorantPlayerStats(BaseModel):
    username: str
    platform: str
    season: Optional[str] = None
    current_rank: Optional[str] = None
    peak_rank: Optional[str] = None
    peak_rank_episode: Optional[str] = None
    wins: Optional[int] = None
    matches_played: Optional[int] = None
    playtime_hours: Optional[float] = None
    kills: Optional[int] = None
    deaths: Optional[int] = None
    assists: Optional[int] = None
    kd_ratio: Optional[float] = None
    kad_ratio: Optional[float] = None
    damage_per_round: Optional[float] = None
    headshot_percentage: Optional[float] = None
    win_percentage: Optional[float] = None
    kills_per_round: Optional[float] = None
    first_bloods: Optional[int] = None
    flawless_rounds: Optional[int] = None
    aces: Optional[int] = None
    kast: Optional[float] = None
    ddr_per_round: Optional[float] = None
    acs: Optional[float] = None
    tracker_score: Optional[int] = None
    round_win_percentage: Optional[float] = None
    top_weapons: Optional[List[Weapon]] = None
    top_maps: Optional[List[MapStats]] = None
    roles: Optional[List[Role]] = None
