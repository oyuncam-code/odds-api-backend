name: Oran Guncelleme
on:
  schedule:
    - cron: '0 */3 * * *'
  workflow_dispatch:
jobs:
  veri-cek:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-python@v5
        with:
          python-version: '3.10'
      - run: |
          pip install --upgrade pip
          pip install soccerapi
      - name: Kazıyıcı Kodunu Çalıştır
        run: python scraper.py
      - run: |
          git config --local user.email "action@github.com"
          git config --local user.name "GitHub Action Bot"
          git pull origin main --rebase
          git add oranlar.json
          git commit -m "🤖 Oranlar güncellendi" || exit 0
          git push origin main
