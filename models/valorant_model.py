from pydantic import BaseModel
from typing import Optional, List


class Weapon(BaseModel):
    weapon_name: str
    weapon_type: str
    weapon_silhouette_url: str
    weapon_accuracy: List[str]
    weapon_kills: int


class MapStats(BaseModel):
    map_name: str
    map_win_percentage: str
    map_matches: str
    map_image_url: str


class Role(BaseModel):
    role_name: str
    role_win_rate: str
    role_kda: float
    role_wins: int
    role_losses: int
    role_kills: int
    role_deaths: int
    role_assists: int
    role_image_url: str


class ValorantPlayerStats(BaseModel):
    username: str
    platform: str
    season: Optional[str] = None
    current_rank: Optional[str] = None
    current_rank_image_url: Optional[str] = None
    peak_rank: Optional[str] = None
    peak_rank_image_url: Optional[str] = None
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
