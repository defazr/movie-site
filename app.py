import os
import http.client
import json
from flask import Flask, render_template, request
from dotenv import load_dotenv

load_dotenv()

app = Flask(__name__)

def fetch_movies():
    try:
        # 원래 사용하던 API 호스트로 복구
        conn = http.client.HTTPSConnection("imdb232.p.rapidapi.com")

        headers = {
            'x-rapidapi-key': os.getenv("RAPIDAPI_KEY"),
            'x-rapidapi-host': "imdb232.p.rapidapi.com" # 호스트 복구
        }

        # 원래 사용하던 엔드포인트 경로로 복구
        conn.request("GET", "/api/title/get-chart-rankings?rankingsChartType=TOP_250&limit=20", headers=headers)

        res = conn.getresponse()
        data = res.read()

        print(f"🔥 API 응답 원본: {data}") # 디버깅용 로그

        decoded = json.loads(data.decode("utf-8"))

        # API 응답에서 'rankings' 리스트 추출 로직 (원래 코드)
        rankings = decoded.get("rankings", [])
        movies = [{"title": item.get("title", {}).get("title", "Unknown")} for item in rankings]

        if not movies:
            print("⚠️ 경고: API 응답에서 영화 데이터를 찾을 수 없습니다. 파싱 로직 또는 API 응답을 확인하세요.")

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

# 이 부분은 Render.com 배포 시 Gunicorn이 처리하므로 일반적으로 필요 없습니다.
# if __name__ == '__main__':
#     port = int(os.environ.get("PORT", 5000))
#     app.run(debug=True, host='0.0.0.0', port=port)
