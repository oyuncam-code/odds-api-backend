import json
import hashlib
from datetime import datetime
from soccerapi.api import ApiUnibet

def main():
    try:
        api = ApiUnibet()
        comps = api.competitions()
        target_urls = []
        favorite_countries = ['England', 'Spain', 'Italy', 'Germany', 'France', 'Turkey']
        for country, leagues in comps.items():
            for league_name, url in leagues.items():
                if country in favorite_countries or len(target_urls) < 15:
                    target_urls.append((f"{country} - {league_name}", url))
        results = []
        for label, url in target_urls:
            try:
                odds_data = api.odds(url)
                for event in odds_data:
                    home = event.get('home_team')
                    away = event.get('away_team')
                    if not home or not away: continue
                    uid = hashlib.md5(f"{home}{away}{event.get('time','')}".encode()).hexdigest()
                    ft = event.get('full_time_result') or event.get('full_time_resut') or {}
                    processed = {
                        "id": uid, "league": label, "date": event.get('time', datetime.now().isoformat()),
                        "home": home, "away": away,
                        "maxOdds": { "homeWin": ft.get('1', 0)/1000, "draw": ft.get('X', 0)/1000, "awayWin": ft.get('2', 0)/1000 }
                    }
                    if processed["maxOdds"]["homeWin"] > 0: results.append(processed)
            except: continue
        with open('oranlar.json', 'w', encoding='utf-8') as f:
            json.dump({"son_guncelleme": datetime.now().isoformat(), "maclar": results}, f, ensure_ascii=False, indent=4)
    except Exception as e: print(f"Hata: {e}")

if __name__ == "__main__":
    main()
