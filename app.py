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

# --- 여기부터 app.py 파일 마지막에 추가 ---

def fetch_movie_details(movie_id):
    try:
        conn = http.client.HTTPSConnection("imdb232.p.rapidapi.com")

        headers = {
            'x-rapidapi-key': os.getenv("RAPIDAPI_KEY"),
            'x-rapidapi-host': "imdb232.p.rapidapi.com"
        }

        # 특정 영화의 상세 정보를 가져오는 API 엔드포인트
        # 여기서 `imdb232` API의 'get-title-details' 또는 유사한 엔드포인트를 사용합니다.
        # 실제 API 문서에 따라 엔드포인트와 파라미터가 다를 수 있습니다.
        # 이 예시에서는 id 파라미터를 사용하여 영화 상세 정보를 요청합니다.
        conn.request("GET", f"/api/title/get-details?id={movie_id}", headers=headers)

        res = conn.getresponse()
        data = res.read()
        decoded_data = json.loads(data.decode("utf-8"))

        print(f"✨ 상세 페이지 API 응답 원본 (ID: {movie_id}): {data}")

        # 응답 구조에 맞게 상세 정보를 파싱합니다.
        # API 응답 구조에 따라 이 부분은 달라질 수 있습니다.
        # 여기서는 몇 가지 주요 정보만 예시로 가져옵니다.
        movie_details = {
            "id": decoded_data.get("id", movie_id),
            "title": decoded_data.get("titleText", {}).get("text", "Unknown Title"),
            "image_url": decoded_data.get("primaryImage", {}).get("url", ""),
            "plot": decoded_data.get("plot", {}).get("plotText", {}).get("plainText", "No plot available."),
            "release_year": decoded_data.get("releaseYear", {}).get("year", "N/A"),
            "genres": [g.get("text") for g in decoded_data.get("genres", {}).get("genres", []) if g.get("text")],
            "directors": [d.get("nameText", {}).get("text") for d in decoded_data.get("directors", {}).get("edges", []) if d.get("nameText", {}).get("text")],
            "cast": [c.get("name", {}).get("nameText", {}).get("text") for c in decoded_data.get("principalCredits", []) if c.get("__typename") == "Cast" and c.get("name", {}).get("nameText", {}).get("text")],
            "rating": decoded_data.get("ratingsSummary", {}).get("aggregateRating", "N/A"),
            "vote_count": decoded_data.get("ratingsSummary", {}).get("voteCount", "N/A"),
        }
        
        if not movie_details.get("title") or movie_details.get("title") == "Unknown Title":
            print(f"⚠️ 경고: 영화 ID {movie_id} 에 대한 상세 데이터를 찾을 수 없습니다. 파싱 로직 또는 API 응답을 확인하세요.")
        else:
            print(f"✅ 성공적으로 영화 ID {movie_id} 의 상세 데이터를 파싱했습니다.")

        return movie_details

    except Exception as e:
        print(f"❌ 영화 상세 정보 API 호출 또는 파싱 중 오류 발생 (ID: {movie_id}): {e}")
        return {}


@app.route('/movie/<movie_id>')
def movie_detail(movie_id):
    details = fetch_movie_details(movie_id)
    if not details: # 상세 정보가 없으면 홈페이지로 리다이렉트하거나 오류 페이지 표시
        return "영화 정보를 찾을 수 없습니다.", 404 # 간단한 오류 메시지 반환
        # 또는 from flask import redirect, url_for 를 임포트 후 return redirect(url_for('index'))
    return render_template("detail.html", movie=details)

# --- 여기까지 app.py 파일 마지막에 추가 ---