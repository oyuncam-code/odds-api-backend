import json
import hashlib
from datetime import datetime
from soccerapi.api import ApiUnibet

def main():
    try:
        api = ApiUnibet()
        print("Ligler taranıyor...")
        comps = api.competitions()
        target_urls = []
        
        # Favori ülkeler
        favs = ['England', 'Spain', 'Italy', 'Germany', 'France', 'Turkey']
        
        for k, v in comps.items():
            for name, url in v.items():
                if k in favs or len(target_urls) < 15:
                    target_urls.append((f"{k} - {name}", url))
        
        results = []
        for label, url in target_urls:
            try:
                print(f"Çekiliyor: {label}")
                odds = api.odds(url)
                for ev in odds:
                    h = ev.get('home_team')
                    a = ev.get('away_team')
                    if not h or not a: continue
                    
                    uid = hashlib.md5(f"{h}{a}{ev.get('time','')}".encode()).hexdigest()
                    # Mutfaktaki en önemli ayar: Yazım hatalarını (resut vs) deneme yanılma ile aş
                    ft = ev.get('full_time_result') or ev.get('full_time_resut') or {}
                    
                    processed = {
                        "id": uid,
                        "league": label,
                        "date": ev.get('time', datetime.now().isoformat()),
                        "home": h,
                        "away": a,
                        "maxOdds": {
                            "homeWin": ft.get('1', 0) / 1000,
                            "draw": ft.get('X', 0) / 1000,
                            "awayWin": ft.get('2', 0) / 1000
                        }
                    }
                    if processed["maxOdds"]["homeWin"] > 0:
                        results.append(processed)
            except: continue

        # Dosyaya kaydet
        with open('oranlar.json', 'w', encoding='utf-8') as f:
            json.dump({"son_guncelleme": datetime.now().isoformat(), "maclar": results}, f, ensure_ascii=False, indent=4)
        print(f"Bitti! {len(results)} maç kaydedildi.")
        
    except Exception as e:
        print(f"Hata: {e}")

if __name__ == "__main__":
    main()
