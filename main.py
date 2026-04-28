import json
import os

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import List , Dict
import requests
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv

app = FastAPI()
load_dotenv()

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",
        "http://127.0.0.1:5173"
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
#this is feat
FEATURED = ["pikachu", "charizard", "mewtwo", "bulbasaur", "squirtle", "eevee"]
# AI_API_KEY = os.getenv("AI_API_KEY")

AI_URL = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-2.5-flash:generateContent?key={AI_API_KEY}"


class PokemonCard(BaseModel):
    name: str
    image: str
    types: List[str]
    stats: Dict[str,int]
    abilities: List[str]


@app.get("/featured", response_model=List[PokemonCard])
def get_featured():
    result = []

    for name in FEATURED:
        url = f"https://pokeapi.co/api/v2/pokemon/{name}"

        try:
            res = requests.get(url, timeout=5)
        except requests.exceptions.RequestException:
            raise HTTPException(status_code=500, detail="Failed to connect to Pokémon API")


        if res.status_code != 200:
            raise HTTPException(
                status_code=400,
                detail=f"Failed to fetch data for {name}"
            )

        try:
            data = res.json()
        except Exception:
            raise HTTPException(
                status_code=500,
                detail="Invalid response from Pokémon API"
            )

        result.append(PokemonCard(
            name=data["name"].capitalize(),
            image=data["sprites"]["front_default"],
            types=[t["type"]["name"] for t in data["types"]],
            stats={
                stat["stat"]["name"].replace("-","_"):stat["base_stat"]
                for stat in data["stats"]
            },
            abilities=[a["ability"]["name"] for a in data["abilities"]]
        ))

    return result


def get_ai_analysis(name,types,stats):
    prompt = f"""
    You are a Pokémon expert assistant.

    Pokemon: {name}
    Types: {types}
    Stats: {stats}

    IMPORTANT:
    - Based ONLY on official Pokémon type matchups
    - Do NOT guess

    Tasks:
    1. Explain what kind of Pokémon this is (playstyle, strength)
    2. List:
       - strong_against
       - weak_against
    3. Give a simple battle tip
    4. Mention first appearance (game or anime)

    Return ONLY JSON:
    {{
      "summary": "...",
      "strong_against": [],
      "weak_against": [],
      "battle_tip": "...",
      "first_appearance": "..."
    }}

    No markdown. No extra text.
    """

    payload = {
        "contents": [{"parts": [{"text": prompt}]}]
    }

    try:
        res = requests.post(AI_URL,json=payload,timeout=100)
        data = res.json()

        ai_text = data["candidates"][0]["content"]["parts"][0]["text"]
        ai_text = ai_text.replace("```json", "").replace("```", "").strip()

        return json.loads(ai_text)

    except Exception as e:
        print("AI_error",e)
        print("RAW:",data if 'data' in locals() else "No response")

        return {
            "summary": "AI analysis failed",
            "strong_against": [],
            "weak_against": [],
            "battle_tip": "",
            "first_appearance": ""
        }


@app.post("/analyse")
def analyze_pokemon(pokemon: PokemonCard):
    return get_ai_analysis(
        name=pokemon.name.lower(),
        types=pokemon.types,
        stats=pokemon.stats
    )