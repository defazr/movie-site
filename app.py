import os
import http.client
import json
from flask import Flask, render_template, request
from dotenv import load_dotenv

# 로컬 테스트 시 .env 파일에서 환경 변수 불러오기
load_dotenv()

app = Flask(__name__)

# --- API 호출 함수 수정 ---
def fetch_movies():
    try:
        # 이전에 테스트에 성공한 API 호스트로 변경
        conn = http.client.HTTPSConnection("imdb-top-100-movies.p.rapidapi.com")
        
        headers = {
            'x-rapidapi-key': os.getenv("RAPIDAPI_KEY"), # RAPIDAPI_KEY는 그대로 사용
            'x-rapidapi-host': "imdb-top-100-movies.p.rapidapi.com" # 호스트 변경
        }

        # 이전에 테스트에 성공한 엔드포인트 경로로 변경 (Root 경로 '/')
        conn.request("GET", "/", headers=headers)
        
        res = conn.getresponse()
        data = res.read()
        
        # API 응답 로깅 (디버깅용)
        print(f"🔥 API 응답 원본: {data}")
        
        decoded_data = json.loads(data.decode("utf-8"))
        
        # --- API 응답 파싱 로직 수정 (가정) ---
        # 'imdb-top-100-movies.p.rapidapi.com' API의 응답이
        # [ {"title": "Movie A"}, {"title": "Movie B"}, ... ] 형태라고 가정
        # 또는 단순히 영화 제목 문자열의 리스트일 수도 있습니다.
        # 정확한 응답 형태를 RapidAPI 문서에서 확인하고 아래 로직을 조정해야 합니다.
        
        movies = []
        if isinstance(decoded_data, list): # 응답이 리스트인 경우
            for item in decoded_data:
                if isinstance(item, dict) and "title" in item:
                    movies.append({"title": item["title"]})
                elif isinstance(item, str): # 응답이 문자열 리스트인 경우
                     movies.append({"title": item})
        elif isinstance(decoded_data, dict) and "items" in decoded_data:
            # 만약 응답이 {'items': [...]} 형태라면
            for item in decoded_data["items"]:
                if isinstance(item, dict) and "title" in item:
                    movies.append({"title": item["title"]})
                elif isinstance(item, str):
                    movies.append({"title": item})
        # 위 파싱 로직은 가장 흔한 몇 가지 응답 형태를 가정한 것입니다.
        # 실제 API 응답 구조에 따라 더 정교한 파싱이 필요할 수 있습니다.
        
        if not movies:
            print("⚠️ 경고: API 응답에서 영화 데이터를 찾을 수 없습니다. 파싱 로직을 확인하세요.")

        return movies

    except Exception as e:
        print(f"❌ API 호출 또는 파싱 중 오류 발생: {e}")
        # 오류 발생 시 빈 리스트 반환하여 웹사이트가 깨지지 않도록 함
        return []

@app.route('/')
def index():
    query = request.args.get('query', '').lower()
    movies = fetch_movies()

    if query:
        movies = [m for m in movies if query in m['title'].lower()]

    return render_template("index.html", movies=movies)

# 이 부분은 Render.com 배포 시 Gunicorn이 처리하므로 일반적으로 필요 없지만,
# 로컬 테스트를 위해 남겨두거나 추가할 수 있습니다.
# if __name__ == '__main__':
#     port = int(os.environ.get("PORT", 5000))
#     app.run(debug=True, host='0.0.0.0', port=port)
