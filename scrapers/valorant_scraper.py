import re
from typing import Optional
from bs4 import BeautifulSoup
from urllib.parse import quote
from models.valorant_model import ValorantPlayerStats, Weapon, MapStats, Role
from flaresolverr_client import fetch_page_with_flaresolverr

BASE_URL = "https://tracker.gg/valorant/profile/riot"


async def fetch_valorant_player_stats(
    username: str, season: str = "current"
) -> Optional[ValorantPlayerStats]:
    url = f"{BASE_URL}/{quote(username)}/overview"
    if season == "all":
        url += "?season=all"

    # Fetch the page content using the centralized FlareSolverr client
    page_content = await fetch_page_with_flaresolverr(url)

    if not page_content:
        print("No page content received.")
        return None

    soup = BeautifulSoup(page_content, "html.parser")

    # Current Rank
    current_rank_section = soup.find("div", class_="rating-summary__content")
    current_rank = "Unknown"
    if current_rank_section:
        rank_info = current_rank_section.find("div", class_="rating-entry__rank-info")
        if rank_info:
            current_rank_label = rank_info.find("div", class_="label").text.strip()
            current_rank_value = rank_info.find("div", class_="value").text.strip()
            current_rank_rr = rank_info.find("span", class_="mmr")
            current_rank = (
                f"{current_rank_label} {current_rank_value}".strip()
                if current_rank_rr
                else current_rank_value
            )

    # Peak Rank
    peak_rank_section = soup.find(
        "div", class_="rating-summary__content rating-summary__content--secondary"
    )
    peak_rank = "Unknown"
    peak_rank_episode = "N/A"
    if peak_rank_section:
        peak_rank_info = peak_rank_section.find("div", class_="rating-entry__rank-info")
        if peak_rank_info:
            peak_rank_value = (
                peak_rank_info.find("div", class_="value")
                .text.replace(",", " ")
                .strip()
            )
            peak_rank = f"{peak_rank_value}".replace(",", " ").strip()
            episode_act_div = peak_rank_info.find("div", class_="subtext")
            peak_rank_episode = (
                episode_act_div.text.replace(",", " ").strip()
                if episode_act_div
                else "N/A"
            )

    # Tracker Score
    tracker_score_section = soup.find("div", class_="score__text")
    tracker_score = None
    if tracker_score_section:
        tracker_score_value = tracker_score_section.find("div", class_="value")
        tracker_score_text = (
            tracker_score_value.text.strip().split()[0] if tracker_score_value else ""
        )
        tracker_score = (
            int(tracker_score_text) if tracker_score_text.isdigit() else None
        )

    # Round Win %
    round_win_percentage = None
    tracker_win_percentage_section = soup.find(
        "div", class_="performance-score__container"
    )
    if tracker_win_percentage_section:
        stats = tracker_win_percentage_section.find_all("div", class_="stat")
        for stat in stats:
            label = stat.find("div", class_="stat__label").text.strip()
            value = stat.find("div", class_="stat__value").text.strip().replace("%", "")
            if label == "Round Win %":
                round_win_percentage = float(value) if value else None

    # Playtime and Matches Played
    title_stats = soup.find("div", class_="title-stats")
    playtime_hours = 0.0
    matches_played = 0
    if title_stats:
        playtime_span = title_stats.find("span", class_="playtime")
        if playtime_span:
            playtime_text = playtime_span.text.strip()
            match = re.search(r"([\d\.]+)h", playtime_text)
            if match:
                playtime_hours = float(match.group(1))
        matches_span = title_stats.find("span", class_="matches")
        if matches_span:
            matches_text = matches_span.text.strip()
            match = re.search(r"(\d+)", matches_text)
            if match:
                matches_played = int(match.group(1))

    # Main Stats
    stats_sections = soup.find_all("div", class_="stat")
    stats_dict = {}
    for stat in stats_sections:
        name_span = stat.find("span", class_="name")
        if not name_span:
            continue
        stat_name = name_span.get("title", "").strip()
        value_span = stat.find("span", class_="value")
        if value_span:
            value_text = value_span.text.strip().replace("%", "").replace(",", "")
            stats_dict[stat_name] = value_text

    # Wins
    wins_section = soup.find("span", string=re.compile(r"\bWins\b", re.IGNORECASE))

    if wins_section:
        wins_value = wins_section.find_next("span", class_="value")
        if wins_value:
            wins = wins_value.text.strip().replace(",", "")
            print(f"Wins found: {wins}")
        else:
            print("Wins value not found.")
            wins = "0"
    else:
        print("Wins section not found.")
        wins = "0"

    # K/D Ratio
    kd_ratio_section = soup.find("span", title="K/D Ratio")
    kd_ratio = (
        kd_ratio_section.find_next("span", class_="value").text.strip()
        if kd_ratio_section
        else "0"
    )

    # Kills
    kills_section = soup.find("span", title="Kills")
    if kills_section:
        kills_value = kills_section.find_parent("div", class_="numbers").find(
            "span", class_="value"
        )
        kills = kills_value.text.strip().replace(",", "") if kills_value else "0"
    else:
        kills = "0"

    # Headshot Percentage
    headshot_section = soup.find("span", title="Headshot %")
    headshot_percentage = (
        headshot_section.find_next("span", class_="value")
        .text.strip()
        .replace("%", "")
        .strip()
        if headshot_section
        else "0.0"
    )

    # Win Percentage
    win_section = soup.find("span", title="Win %")
    win_percentage = (
        win_section.find_next("span", class_="value")
        .text.strip()
        .replace("%", "")
        .strip()
        if win_section
        else "0.0"
    )

    # ACS (Average Combat Score)
    acs_section = soup.find("span", title="ACS")
    acs_value = (
        acs_section.find_next("span", class_="value").text.strip()
        if acs_section
        else "0.0"
    )

    # Extract individual stats
    damage_per_round = float(stats_dict.get("Damage/Round", 0.0))
    kast = float(stats_dict.get("KAST", 0.0))
    ddr_per_round = float(stats_dict.get("DDΔ/Round", 0.0))
    deaths = int(stats_dict.get("Deaths", 0))
    assists = int(stats_dict.get("Assists", 0))
    kad_ratio = float(stats_dict.get("KAD Ratio", 0.0))
    kills_per_round = float(stats_dict.get("Kills/Round", 0.0))
    first_bloods = int(stats_dict.get("First Bloods", 0))
    flawless_rounds = int(stats_dict.get("Flawless Rounds", 0))
    aces = int(stats_dict.get("Aces", 0))

    # Extract top weapons
    top_weapons = []
    weapons_section = soup.find("div", class_="top-weapons__content")
    if weapons_section:
        weapon_divs = weapons_section.find_all("div", class_="weapon")
        for weapon_div in weapon_divs:
            name_div = weapon_div.find("div", class_="weapon__name")
            type_div = weapon_div.find("div", class_="weapon__type")
            silhouette_img = weapon_div.find("img", class_="weapon__silhouette")
            accuracy_hits_div = weapon_div.find("div", class_="weapon__accuracy-hits")
            main_stat_div = weapon_div.find("div", class_="weapon__main-stat")

            if (
                name_div
                and type_div
                and silhouette_img
                and accuracy_hits_div
                and main_stat_div
            ):
                weapon_name = name_div.text.strip()
                weapon_type = type_div.text.strip()
                weapon_silhouette_url = silhouette_img["src"]
                weapon_accuracy = [
                    stat.text.strip()
                    for stat in accuracy_hits_div.find_all("span", class_="stat")
                ]
                weapon_kills = int(
                    main_stat_div.find("span", class_="value")
                    .text.replace(",", "")
                    .strip()
                )

                top_weapons.append(
                    Weapon(
                        weapon_name=weapon_name,
                        weapon_type=weapon_type,
                        weapon_silhouette_url=weapon_silhouette_url,
                        weapon_accuracy=weapon_accuracy,
                        weapon_kills=weapon_kills,
                    )
                )

    # Extract top maps
    top_maps = []
    top_maps_section = soup.find("div", class_="top-maps__maps")
    if top_maps_section:
        map_divs = top_maps_section.find_all("div", class_="top-maps__maps-map")
        for map_div in map_divs:
            name_div = map_div.find("div", class_="name")
            info_div = map_div.find("div", class_="info")
            if name_div and info_div:
                map_name = name_div.text.strip()
                map_win_percentage = (
                    info_div.find("div", class_="value").text.replace("%", "").strip()
                )
                map_matches = info_div.find("div", class_="label").text.strip()
                top_maps.append(
                    MapStats(
                        map_name=map_name,
                        map_win_percentage=map_win_percentage,
                        map_matches=map_matches,
                    )
                )

    # Extract roles
    roles = []
    roles_section = soup.find("div", class_="roles__list")
    if roles_section:
        role_divs = roles_section.find_all("div", class_="role")
        for role_div in role_divs:
            role_name = role_div.find("h5", class_="role__name").text.strip()
            role_stats = role_div.find("div", class_="role__stats")
            if role_stats:
                # Win rate
                win_rate_text = role_stats.find(
                    "span", class_="role__value"
                ).text.strip()
                role_win_rate = win_rate_text.replace("%", "").split(" ")[1]

                # Wins and Losses
                win_loss_text = role_stats.find("span", class_="role__sub").text.strip()
                role_wins, role_losses = map(
                    int, re.findall(r"(\d+)W.*?(\d+)L", win_loss_text)[0]
                )

                # KDA
                kda_text = role_stats.find_all("span", class_="role__value")[
                    1
                ].text.strip()
                role_kda = float(kda_text.split(" ")[1])

                # Kills, Deaths, and Assists
                kd_stats = role_stats.find_all("span", class_="role__sub")[
                    1
                ].text.strip()

                # Extract the numbers using regex
                kd_values = re.findall(
                    r"\d{1,3}(?:,\d{3})*", kd_stats
                )  # This will match numbers like 1,234 or 123

                # Convert to integers, removing commas
                role_kills = (
                    int(kd_values[0].replace(",", "")) if len(kd_values) > 0 else 0
                )
                role_deaths = (
                    int(kd_values[1].replace(",", "")) if len(kd_values) > 1 else 0
                )
                role_assists = (
                    int(kd_values[2].replace(",", "")) if len(kd_values) > 2 else 0
                )

                roles.append(
                    Role(
                        role_name=role_name,
                        role_win_rate=role_win_rate,
                        role_wins=role_wins,
                        role_losses=role_losses,
                        role_kda=role_kda,
                        role_kills=role_kills,
                        role_deaths=role_deaths,
                        role_assists=role_assists,
                    )
                )

    return ValorantPlayerStats(
        username=username,
        platform="valorant",
        season="All",
        current_rank=current_rank,
        peak_rank=peak_rank,
        peak_rank_episode=peak_rank_episode,
        tracker_score=tracker_score,
        round_win_percentage=round_win_percentage,
        playtime_hours=playtime_hours,
        matches_played=matches_played,
        damage_per_round=damage_per_round,
        kd_ratio=kd_ratio,
        headshot_percentage=headshot_percentage,
        win_percentage=win_percentage,
        wins=wins,
        kast=kast,
        ddr_per_round=ddr_per_round,
        kills=kills,
        deaths=deaths,
        assists=assists,
        acs=acs_value,
        kad_ratio=kad_ratio,
        kills_per_round=kills_per_round,
        first_bloods=first_bloods,
        flawless_rounds=flawless_rounds,
        aces=aces,
        top_weapons=top_weapons,
        top_maps=top_maps,
        roles=roles,
    )
