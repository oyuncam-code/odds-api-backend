import json
import hashlib
from datetime import datetime
from soccerapi.api import ApiUnibet # Unibet en geniş yelpazeye sahiptir

def main():
    try:
        api = ApiUnibet()
        print("TÜM DÜNYA BÜLTENİ TARANIYOR (Lütfen Bekleyin)...")
        
        # Bütün ülkeleri ve ligleri listele
        comps = api.competitions()
        
        results = []
        # Her bir ülkeyi ve o ülkedeki bütün ligleri gez
        for country, leagues in comps.items():
            for league_name, url in leagues.items():
                try:
                    print(f"Süpürülüyor: {country} - {league_name}")
                    odds_data = api.odds(url) # Doğrudan lig URL'sini (slug) süpürür
                    
                    if not odds_data: continue
                    
                    for event in odds_data:
                        h = event.get('home_team')
                        a = event.get('away_team')
                        if not h or not a: continue
                        
                        uid = hashlib.md5(f"{h}{a}{event.get('time','')}".encode()).hexdigest()
                        ft = event.get('full_time_result') or event.get('full_time_resut') or {}
                        
                        processed = {
                            "id": uid,
                            "league": f"{country} - {league_name}",
                            "date": event.get('time', datetime.now().isoformat()),
                            "home": h,
                            "away": a,
                            "maxOdds": {
                                "homeWin": ft.get('1', 0) / 1000,
                                "draw": ft.get('X', 0) / 1000,
                                "awayWin": ft.get('2', 0) / 1000,
                                "over25": 0, "under25": 0
                            }
                        }
                        if processed["maxOdds"]["homeWin"] > 0:
                            results.append(processed)
                except:
                    # Bazı liglerde timeout olması normaldir, bot engeline takılmıştır
                    continue

        # KAYDET (Devasa bülten!)
        out = {"son_guncelleme": datetime.now().isoformat(), "maclar": results}
        with open('oranlar.json', 'w', encoding='utf-8') as f:
            json.dump(out, f, ensure_ascii=False, indent=4)
        print(f"ZAFER! {len(results)} maç bültene eklendi.")
        
    except Exception as e:
        print(f"Genel Hata: {e}")

if __name__ == "__main__":
    main()
