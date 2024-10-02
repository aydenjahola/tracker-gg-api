# Valorant Player Stats API

This API allows you to fetch statistics for Valorant players, including current and all-time statistics. The API is built using FastAPI and utilizes web scraping to gather player data from [Tracker.gg](https://tracker.gg/).

## Table of Contents

- [Features](#features)
- [Getting Started](#getting-started)
  - [Prerequisites](#prerequisites)
  - [Installation](#installation)
  - [Environment Variables](#environment-variables)
- [API Endpoints](#api-endpoints)
  - [Get Current Act Stats](#get-current-act-stats)
  - [Get All Seasons Stats](#get-all-seasons-stats)
- [Response Model](#response-model)
- [Error Handling](#error-handling)
- [License](#license)

## Features

- Fetch current act statistics for a given Valorant player.
- Fetch all-time statistics across seasons for a given Valorant player.
- API key authentication for secure access.

## Getting Started

### Prerequisites

- Python 3.7 or higher
- An active internet connection

### Installation

1. Clone the repository:

```bash
git@github.com:aydenjahola/tracker-gg-api.git
cd valorant-stats-api
```

2. Install the required packages:

```bash
pip install -r requirements.txt
```

### Environment Variables

Create a `.env` file in the root of the project directory and add your API keys:

```env
API_KEYS=your_api_key1,your_api_key2
```

Make sure to replace `your_api_key1,your_api_key2` with your actual API keys.

## API Endpoints

### Get Current Act Stats

**Endpoint:** `GET /player/{username}/current`

**Description:** Fetch the current act statistics for a given Valorant player.

**Parameters:**

- `username`: The Riot username of the player (eg. Shitter#1234).
- `X-API-Key`: Your API key (header).

**Response:**

```json
{
  "username": "player_username",
  "platform": "valorant",
  "season": "Current Act",
  "kills": 150,
  "wins": 75,
  "matches_played": 100,
  "kd_ratio": 1.5,
  "current_rank": "Gold",
  "peak_rank": "Platinum",
  "headshot_percentage": 30.0,
  "win_percentage": 75.0,
  "hours_played": 50.0,
  "tracker_score": 1000
}
```

### Get All Seasons Stats

**Endpoint:** `GET /player/{username}/all`

**Description:** Fetch all seasons' statistics for a given Valorant player.

**Parameters:**

- `username`: The Riot username of the player (eg. Shitter#1234).
- `X-API-Key`: Your API key (header).

**Response:**

Similar to the "Get Current Act Stats" response, but the `season` field will be set to `"All Acts"`.

## Response Model

The response for both endpoints follows the `PlayerStats` model, defined as:

```python
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
```

## Error Handling

- **403 Forbidden:** If the API key is invalid.
- **404 Not Found:** If the player's stats cannot be found.

## License

This project is licensed under the [GNU GENERAL PUBLIC LICENSE Version 3License ](./LICENSE). See the LICENSE file for details.

---

Feel free to reach out for any questions or contributions to the project!
