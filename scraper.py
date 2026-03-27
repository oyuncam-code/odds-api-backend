import requests
import json
import hashlib
from datetime import datetime

# Sizin taze API Key'iniz (Önceki mesajlardan buldum)
# 01c6a8c323a4e78a9c7249cd8c61e00c

def main():
    try:
        api_key = "01c6a8c323a4e78a9c7249cd8c61e00c"
        print("Tüm Dünya Bülteni Çekiliyor...")
        
        # Bütün dünyadaki futbol liglerini tek seferde süpür
        url = f"https://api.the-odds-api.com/v4/sports/upcoming/odds/?regions=eu&markets=h2h&apiKey={api_key}"
        
        response = requests.get(url)
        data = response.json()
        
        results = []
        if isinstance(data, list):
            for m in data:
                h = m.get('home_team')
                a = m.get('away_team')
                uid = hashlib.md5(f"{h}{a}{m.get('commence_time','')}".encode()).hexdigest()
                
                # Oran bulma (İlk bookmaker - Unibet/888Sport seçilir)
                h_o = 0; d_o = 0; a_o = 0
                bookies = m.get('bookmakers', [])
                if bookies:
                    outs = bookies[0].get('markets', [{}])[0].get('outcomes', [])
                    for o in outs:
                        if o['name'] == h: h_o = o['price']
                        elif o['name'] == a: a_o = o['price']
                        elif o['name'] == 'Draw': d_o = o['price']

                results.append({
                    "id": uid, "league": f"{m.get('sport_title', 'Futbol')} (Dünya)",
                    "date": m.get('commence_time', datetime.now().isoformat()),
                    "home": h, "away": a,
                    "maxOdds": { "homeWin": h_o, "draw": d_o, "awayWin": a_o, "over25": 0, "under25": 0 }
                })
        
        # Dosyaya kaydet
        with open('oranlar.json', 'w', encoding='utf-8') as f:
            json.dump({"son_guncelleme": datetime.now().isoformat(), "maclar": results}, f, ensure_ascii=False, indent=4)
        print(f"Bitti! {len(results)} maç yüklendi.")
    except Exception as e: print(f"Hata: {e}")

if __name__ == "__main__": main()
