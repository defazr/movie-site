import os
import http.client
import json
from flask import Flask, render_template, request

app = Flask(__name__)

def fetch_movies():
    conn = http.client.HTTPSConnection("imdb-top-100-movies.p.rapidapi.com")
    headers = {
        "X-RapidAPI-Key": os.getenv("RAPIDAPI_KEY"),
        "X-RapidAPI-Host": os.getenv("RAPIDAPI_HOST")
    }

    conn.request("GET", "/top", headers=headers)
    res = conn.getresponse()
    data = res.read()

    # 📌 이 줄을 추가해서 받은 데이터를 확인해보세요
    print("🔥 API 응답 원본:", data)

    try:
        movies = json.loads(data.decode("utf-8"))
    except Exception as e:
        print("❌ JSON 디코딩 에러:", e)
        return [{"title": "Failed to load movies"}]

    # 혹시 에러 메시지일 경우 대비
    if isinstance(movies, dict) and 'message' in movies:
        print("❗에러 메시지:", movies['message'])
        return [{"title": movies['message']}]

    return movies




@app.route('/')
def index():
    query = request.args.get('query', '').lower()
    movies = fetch_movies()

    if query:
        movies = [movie for movie in movies if query in movie['title'].lower()]

    return render_template("index.html", movies=movies)
