import requests
import json
import hashlib
from datetime import datetime, timedelta

# API Key: 01c6a8c323a4e78a9c7249cd8c61e00c

def main():
    try:
        api_key = "01c6a8c323a4e78a9c7249cd8c61e00c"
        base_url = "https://api.the-odds-api.com/v4/sports/"
        
        # ADIM 1: Tüm Futbol Liglerini Listele (ÜCRETSİZ)
        sports_resp = requests.get(f"{base_url}?apiKey={api_key}&all=true")
        sports_data = sports_resp.json()
        
        # Sadece Futbol (Soccer) liglerini süz
        soccer_keys = [s['key'] for s in sports_data if s['group'] == 'Soccer']
        print(f"Toplam {len(soccer_keys)} futbol ligi taranacak...")
        
        # ADIM 2: Zaman Aralığını Belirle (Bugünden +2 Gün Sonra)
        now = datetime.utcnow()
        time_from = now.strftime('%Y-%m-%dT%H:%M:%SZ')
        time_to = (now + timedelta(days=2)).strftime('%Y-%m-%dT%H:%M:%SZ')
        
        final_matches = []
        
        # ADIM 3: Her Lig İçin 2 Günlük Veriyi Çek (H2H ve TOTALS)
        # Kotayı korumak için en popüler 40 ligi turalayalım (Veya hepsini isterseniz listeyi kısıtlamayın)
        for sport in soccer_keys[:45]: # Ücretsiz kotayı korumak için ilk 45 aktif lig
            try:
                print(f"Çekiliyor: {sport}")
                url = f"{base_url}{sport}/odds/"
                params = {
                    "apiKey": api_key,
                    "regions": "eu", # Kotayı az yemek için sadece EU (Çoğu ligi kapsar)
                    "markets": "h2h,totals",
                    "commenceTimeFrom": time_from,
                    "commenceTimeTo": time_to
                }
                
                resp = requests.get(url, params=params)
                data = resp.json()
                
                if isinstance(data, list):
                    for m in data:
                        h = m.get('home_team'); a = m.get('away_team')
                        uid = hashlib.md5(f"{h}{a}{m.get('commence_time','')}".encode()).hexdigest()
                        
                        h_o = 0; d_o = 0; a_o = 0; over25 = 0; under25 = 0
                        bookies = m.get('bookmakers', [])
                        
                        if bookies:
                            # İlk bookmaker'dan pazarları süz
                            markets = bookies[0].get('markets', [])
                            for mkt in markets:
                                if mkt['key'] == 'h2h':
                                    for o in mkt['outcomes']:
                                        if o['name'] == h: h_o = o['price']
                                        elif o['name'] == a: a_o = o['price']
                                        elif o['name'] == 'Draw': d_o = o['price']
                                elif mkt['key'] == 'totals':
                                    for o in mkt['outcomes']:
                                        if o['name'] == 'Over' and o.get('point') == 2.5: over25 = o['price']
                                        if o['name'] == 'Under' and o.get('point') == 2.5: under25 = o['price']

                        final_matches.append({
                            "id": uid, "league": m.get('sport_title', sport),
                            "date": m.get('commence_time'), "home": h, "away": a,
                            "maxOdds": { "homeWin": h_o, "draw": d_o, "awayWin": a_o, "over25": over25, "under25": under25 }
                        })
            except: continue

        # KAYDET
        with open('oranlar.json', 'w', encoding='utf-8') as f:
            json.dump({"son_guncelleme": datetime.now().isoformat(), "maclar": final_matches}, f, ensure_ascii=False, indent=4)
        print(f"Bitti! {len(final_matches)} dev bülten yüklendi.")
        
    except Exception as e: print(f"Hata: {e}")

if __name__ == "__main__": main()
