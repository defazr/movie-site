import os
import http.client
import json
from flask import Flask, render_template, request
from dotenv import load_dotenv

load_dotenv()

app = Flask(__name__)

def fetch_movies():
    try:
        conn = http.client.HTTPSConnection("imdb232.p.rapidapi.com")

        headers = {
            'x-rapidapi-key': os.getenv("RAPIDAPI_KEY"),
            'x-rapidapi-host': "imdb232.p.rapidapi.com"
        }

        conn.request("GET", "/api/title/get-chart-rankings?rankingsChartType=TOP_250&limit=20", headers=headers)

        res = conn.getresponse()
        data = res.read()

        print(f"🔥 API 응답 원본: {data}")

        decoded = json.loads(data.decode("utf-8"))

        # ----------------------------------------------------
        # **** 이 부분이 수정되었습니다! ****
        # API 응답 구조에 맞게 'data', 'titleChartRankings', 'edges' 경로를 따라갑니다.
        edges = decoded.get("data", {}).get("titleChartRankings", {}).get("edges", [])

        movies = []
        for edge in edges:
            node_item = edge.get("node", {}).get("item", {})
            title = node_item.get("titleText", {}).get("text", "Unknown Title")
            image_url = node_item.get("primaryImage", {}).get("url", "") # 이미지 URL 추가
            movie_id = node_item.get("id", "") # 영화 ID 추가 (나중에 상세 페이지에 유용)
            
            movies.append({
                "id": movie_id,
                "title": title,
                "image_url": image_url # 딕셔너리에 이미지 URL 추가
            })
        # ----------------------------------------------------

        if not movies:
            print("⚠️ 경고: API 응답에서 영화 데이터를 찾을 수 없습니다. 파싱 로직 또는 API 응답을 확인하세요.")
        else:
            print(f"✅ 성공적으로 {len(movies)}개의 영화 데이터를 파싱했습니다.") # 성공 로그 추가

        return movies

    except Exception as e:
        print(f"❌ API 호출 또는 파싱 중 오류 발생: {e}")
        return []

@app.route('/')
def index():
    query = request.args.get('query', '').lower()
    movies = fetch_movies()

    if query:
        movies = [m for m in movies if query in m['title'].lower()]

    return render_template("index.html", movies=movies)