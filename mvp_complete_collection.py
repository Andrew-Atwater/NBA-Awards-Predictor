import pandas as pd
from pymongo import MongoClient
from datetime import datetime

df = pd.read_csv("mvp_complete_stats.csv")

client = MongoClient("mongodb://localhost:27017")
db = client["nba_mvp"]
candidates = db["mvp_candidates"]

docs = []

for _, row in df.iterrows():
    season_label = row["Season"]
    start_year = int(season_label.split("-")[0])
    end_year = start_year + 1

    doc = {
        "player": row["Player"],
        "season": {"label": season_label, "start_year": start_year, "end_year": end_year},
        "voting": {"mvpPoints": float(row["MVP_Points"])},
        "stats": {
            "gp": row.get("gp"),
            "mpg": row.get("mpg"),
            "pts": row.get("pts"),
            "reb": row.get("reb"),
            "ast": row.get("ast"),
            "stl": row.get("stl"),
            "blk": row.get("blk"),
            "fgPct": row.get("fgPct"),
            "fg3Pct": row.get("fg3Pct"),
            "ftPct": row.get("ftPct"),
            "team": {
                "abbr": row.get("TEAM"),
                "record": row.get("TEAM_RECORD"),
                "winPct": row.get("TEAM_WIN_PCT"),
            },
            "gameScore": row.get("GAME_SCORE"),
            "simplePER": row.get("SIMPLE_PER"),
            "impactScore": row.get("IMPACT_SCORE"),
        },
        "flags": {"pastmvpwinner": bool(row["PAST_MVP_WINNER"])},
    }

    docs.append(doc)

if docs:
    candidates.insert_many(docs)
