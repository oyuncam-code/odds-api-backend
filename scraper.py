import json
from datetime import datetime
import hashlib
from soccerapi.api import Api888Sport

def get_competitions(api):
    try:
        comps = api.competitions()
        urls = []
        favorite_countries = ['England', 'Spain', 'Italy', 'Germany', 'France', 'Turkey']
        for country, leagues in comps.items():
            if country in favorite_countries:
                for league_name, url in leagues.items():
                    urls.append((f"{country} - {league_name}", url))
        return urls[:15]
    except Exception as e:
        print(f"Competitions fetch error: {e}")
        return []

def main():
    try:
        api = Api888Sport()
        comps = get_competitions(api)
        
        results = []
        for league_name, url in comps:
            try:
                odds_data = api.odds(url)
                
                for event in odds_data:
                    home = event.get('home_team', 'Unknown')
                    away = event.get('away_team', 'Unknown')
                    match_time = event.get('time', datetime.now().isoformat())
                    
                    uid = hashlib.md5(f"{home}{away}{match_time}".encode()).hexdigest()
                    
                    ft = event.get('full_time_result', {})
                    if not ft: ft = event.get('full_time_resut', {})
                    homeWin = ft.get('1', 0) / 1000
                    draw = ft.get('X', 0) / 1000
                    awayWin = ft.get('2', 0) / 1000
                    
                    uo = event.get('under_over', {})
                    over25 = 0; under25 = 0
                    if isinstance(uo, dict):
                        over25 = uo.get('over', 0) / 1000
                        if over25 == 0:
                            line_25 = uo.get('2.5') or uo.get('2,5', {})
                            if isinstance(line_25, dict):
                                over25 = line_25.get('over', 0) / 1000
                                under25 = line_25.get('under', 0) / 1000
                        else:
                            under25 = uo.get('under', 0) / 1000

                    btts = event.get('both_teams_to_score', {})
                    bttsYes = btts.get('yes', 0) / 1000
                    bttsNo = btts.get('no', 0) / 1000
                    
                    ah = event.get('asian_handicap', {})
                    asianHandicapHome = 0; asianLine = 0
                    if isinstance(ah, dict):
                        line_0 = ah.get('0.0') or ah.get('0')
                        if line_0 and isinstance(line_0, dict):
                            asianLine = 0.0
                            asianHandicapHome = line_0.get('1', 0) / 1000

                    processed_match = {
                        "id": uid,
                        "league": league_name,
                        "date": match_time,
                        "home": home,
                        "away": away,
                        "maxOdds": {
                            "homeWin": homeWin, "draw": draw, "awayWin": awayWin,
                            "over25": over25, "under25": under25,
                            "bttsYes": bttsYes, "bttsNo": bttsNo,
                            "asianHandicapHome": asianHandicapHome, "asianLine": asianLine
                        },
                        "pinnacleOdds": { "homeWin": 0, "draw": 0, "awayWin": 0 }, 
                    }
                    if homeWin > 0:
                        results.append(processed_match)
            except Exception as e:
                print(f"[{league_name}] atlandi: {e}")
        
        data = {
            "son_guncelleme": datetime.now().isoformat(),
            "maclar": results
        }
        
        with open('oranlar.json', 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=4)
            
        print("Veriler basariyla cekildi ve oranlar.json dosyasina yazildi.")
        
    except Exception as e:
        print(f"Iletisim hatasi: {e}")

if __name__ == '__main__':
    main()
