from flask import Flask, jsonify
from flask_cors import CORS
import requests
from bs4 import BeautifulSoup
import re

app = Flask(__name__)
CORS(app)

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (HTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
}

LEAGUE_GROUP = {
    "Brasileirão": "br", "Série B": "br", "Série C": "br", "Série D": "br",
    "Copa do Brasil": "br", "Br. Feminino": "br", "LNF": "br",
    "Brasileirão Feminino": "br", "Copa LNF": "br"
}

def scrape_page(url):
    try:
        r = requests.get(url, headers=HEADERS, timeout=15)
        soup = BeautifulSoup(r.text, "html.parser")
        games = []
        content = soup.find("div", class_="entry-content")
        if not content:
            return []
        for h3 in content.find_all("h3"):
            text = h3.get_text(strip=True)
            m = re.match(r"(\d{1,2}h\d{2})\s*[–-]\s*(.+?)\s*[–-]\s*(.+)", text)
            if not m:
                continue
            time_str = m.group(1).strip()
            match_str = m.group(2).strip()
            league = m.group(3).strip()
            channels = ""
            nxt = h3.find_next_sibling()
            if nxt and nxt.name == "p":
                ch_text = nxt.get_text(strip=True)
                ch_text = re.sub(r"^Canais?:\s*", "", ch_text)
                channels = ch_text
            league_short = league
            if "Brasileirão Feminino" in league or "Brasileiro Feminino" in league:
                league_short = "Br. Feminino"
            group = "br" if any(k in league_short for k in LEAGUE_GROUP) else "int"
            games.append({
                "time": time_str,
                "match": match_str,
                "league": league_short,
                "group": group,
                "channels": channels
            })
        return games
    except Exception as e:
        return []

@app.route("/hoje")
def hoje():
    data = scrape_page("https://mantosdofutebol.com.br/guia-de-jogos-tv-hoje-ao-vivo/")
    return jsonify(data)

@app.route("/amanha")
def amanha():
    data = scrape_page("https://mantosdofutebol.com.br/jogos-de-amanha-tv/")
    return jsonify(data)

@app.route("/")
def index():
    return jsonify({"status": "ok", "message": "Futebol TV API"})

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=10000)
