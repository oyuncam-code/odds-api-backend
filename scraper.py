import json
import hashlib
from datetime import datetime
from soccerapi.api import ApiUnibet

def main():
    try:
        api = ApiUnibet()
        print("Bülten taranıyor...")
        
        # Unibet için en popüler liglerin URL slugları
        target_leagues = [
            'england/premier_league',
            'turkey/super_lig',
            'spain/la_liga',
            'italy/serie_a',
            'germany/bundesliga',
            'france/ligue_1'
        ]
        
        results = []
        for slug in target_leagues:
            try:
                print(f"Çekiliyor: {slug}")
                # odds() fonksiyonuna doğrudan slug gönderiyoruz
                odds_data = api.odds(slug)
                for event in odds_data:
                    home = event.get('home_team')
                    away = event.get('away_team')
                    if not home or not away: continue
                    
                    uid = hashlib.md5(f"{home}{away}{event.get('time','')}".encode()).hexdigest()
                    # Unibet verisindeki yazım hatalarını (resut vs) denetle
                    ft = event.get('full_time_result') or event.get('full_time_resut') or {}
                    
                    processed = {
                        "id": uid,
                        "league": slug.upper(),
                        "date": event.get('time', datetime.now().isoformat()),
                        "home": home,
                        "away": away,
                        "maxOdds": {
                            "homeWin": ft.get('1', 0) / 1000,
                            "draw": ft.get('X', 0) / 1000,
                            "awayWin": ft.get('2', 0) / 1000,
                            "over25": 0, "under25": 0 # Gelecek sürümlerde eklenebilir
                        }
                    }
                    if processed["maxOdds"]["homeWin"] > 0:
                        results.append(processed)
            except Exception as e:
                print(f"{slug} hatası: {e}")

        # Kaydet
        data = {"son_guncelleme": datetime.now().isoformat(), "maclar": results}
        with open('oranlar.json', 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=4)
        print(f"Bitti! {len(results)} maç bulundu.")
        
    except Exception as e:
        print(f"Genel Hata: {e}")

if __name__ == "__main__":
    main()
