import os
import json
import random
import requests
from dotenv import load_dotenv
from flask import Flask, jsonify

load_dotenv()
API_KEY = os.getenv("APISPORTS_KEY")
BASE_URL = "https://v3.football.api-sports.io"
HEADERS = {"x-apisports-key": API_KEY, "Accept": "application/json"}

PLAYER_SEASON = 2023

CLUBES_FAMOSOS = [
    "Real Madrid", "Barcelona", "Atletico Madrid",
    "Manchester City", "Manchester United", "Liverpool",
    "Arsenal", "Chelsea", "Tottenham", "Bayern Munich",
    "Borussia Dortmund", "PSG", "Juventus", "Inter",
    "AC Milan", "Roma", "Napoli"
]

# Funciones de API
def api_get(path, params=None):
    r = requests.get(f"{BASE_URL}{path}", headers=HEADERS, params=params, timeout=30)
    r.raise_for_status()
    return r.json()

def get_team_id_by_name(name: str):
    js = api_get("/teams", {"name": name})
    resp = js.get("response", []) or []
    if not resp: return None
    exact = [it for it in resp if (it.get("team") or {}).get("name", "").lower() == name.lower()]
    t = (exact[0].get("team") if exact else resp[0].get("team")) or {}
    return t.get("id")

def get_players_from_team(team_id: int, season: int):
    jugadores = []
    page = 1
    while True:
        js = api_get("/players", {"team": team_id, "season": season, "page": page})
        resp = js.get("response", []) or []
        for it in resp:
            p = it.get("player") or {}
            stats = it.get("statistics")[0] if it.get("statistics") else {}
            pos = stats.get("games", {}).get("position")
            jugadores.append({
                "id": p.get("id"),
                "name": p.get("name"),
                "age": p.get("age"),
                "nationality": p.get("nationality"),
                "position": pos,
                "team": team_id
            })
        paging = js.get("paging") or {}
        if paging.get("current") >= paging.get("total"): break
        page += 1
    return jugadores

# Endpoint serverless
def handler(request, response):
    try:
        club_random = random.choice(CLUBES_FAMOSOS)
        club_id = get_team_id_by_name(club_random)
        if not club_id:
            return response.json({"error": f"No se pudo obtener el ID del club: {club_random}"}, status=500)
        players = get_players_from_team(club_id, PLAYER_SEASON)
        if not players:
            return response.json({"error": f"No se encontraron jugadores para {club_random}"}, status=500)
        jugador = random.choice(players)
        return response.json(jugador)
    except Exception as e:
        return response.json({"error": str(e)}, status=500)
