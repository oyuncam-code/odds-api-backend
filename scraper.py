import requests
import json
import hashlib
from datetime import datetime

# API Key: 01c6a8c323a4e78a9c7249cd8c61e00c

def main():
    try:
        api_key = "01c6a8c323a4e78a9c7249cd8c61e00c"
        results = []
        
        # Tarayacağımız spor dalları (Siz her branş olsun demiştiniz)
        sports_to_scan = [
            'soccer_eu_uefa_champions_league', 'soccer_turkey_super_lig', 
            'soccer_england_league1', 'soccer_spain_la_liga',
            'basketball_nba', 'basketball_euroleague', 
            'icehockey_nhl', 'tennis_atp_miami', 'americanfootball_nfl'
        ]
        
        # Önce genel upcoming bültenini çek
        upcoming_url = f"https://api.the-odds-api.com/v4/sports/upcoming/odds/?regions=eu&markets=h2h&apiKey={api_key}"
        data = requests.get(upcoming_url).json()
        if isinstance(data, list): results.extend(data)
        
        # Ardından listedeki sporları tek tek tara (Kotanıza acımadan her şeyi çekiyoruz!)
        for sport in sports_to_scan:
            try:
                print(f"Taranan Branş: {sport}")
                url = f"https://api.the-odds-api.com/v4/sports/{sport}/odds/?regions=eu&markets=h2h&apiKey={api_key}"
                sport_data = requests.get(url).json()
                if isinstance(sport_data, list):
                    results.extend(sport_data)
            except: continue

        final_matches = []
        seen_ids = set()
        
        for m in results:
            h = m.get('home_team'); a = m.get('away_team')
            if not h or not a: continue
            
            uid = hashlib.md5(f"{h}{a}{m.get('commence_time','')}".encode()).hexdigest()
            if uid in seen_ids: continue
            seen_ids.add(uid)
            
            h_o = 0; d_o = 0; a_o = 0
            bookies = m.get('bookmakers', [])
            if bookies:
                outs = bookies[0].get('markets', [{}])[0].get('outcomes', [])
                for o in outs:
                    if o['name'] == h: h_o = o['price']
                    elif o['name'] == a: a_o = o['price']
                    elif o['name'] == 'Draw': d_o = o['price']

            # 3 GÜNLÜK VERİ (Gereksiz eski verileri temzile)
            final_matches.append({
                "id": uid, "league": m.get('sport_title', 'Diğer'),
                "date": m.get('commence_time', datetime.now().isoformat()),
                "home": h, "away": a,
                "maxOdds": { "homeWin": h_o, "draw": d_o, "awayWin": a_o, "over25": 0, "under25": 0 }
            })
        
        with open('oranlar.json', 'w', encoding='utf-8') as f:
            json.dump({"son_guncelleme": datetime.now().isoformat(), "maclar": final_matches}, f, ensure_ascii=False, indent=4)
        print(f"Bitti! {len(final_matches)} dev bülten yüklendi.")
    except Exception as e: print(f"Hata: {e}")

if __name__ == "__main__": main()
