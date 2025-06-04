import os
import http.client
import json
from flask import Flask, render_template, request
from dotenv import load_dotenv

# 로컬 테스트 시 .env 파일에서 환경 변수 불러오기
load_dotenv()

app = Flask(__name__)

def fetch_movies():
    conn = http.client.HTTPSConnection("imdb232.p.rapidapi.com")
    headers = {
        'x-rapidapi-key': os.getenv("RAPIDAPI_KEY"),
        'x-rapidapi-host': os.getenv("RAPIDAPI_HOST")
    }

    conn.request("GET", "/api/title/get-chart-rankings?rankingsChartType=TOP_250&limit=20", headers=headers)
    res = conn.getresponse()
    data = res.read()
    decoded = json.loads(data.decode("utf-8"))

    # API 응답에서 'rankings' 리스트 추출
    rankings = decoded.get("rankings", [])
    movies = [{"title": item.get("title", {}).get("title", "Unknown")} for item in rankings]
    return movies

@app.route('/')
def index():
    query = request.args.get('query', '').lower()
    movies = fetch_movies()

    if query:
        movies = [m for m in movies if query in m['title'].lower()]

    return render_template("index.html", movies=movies)
