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
    movies = json.loads(data.decode("utf-8"))

    # 문자열이면 딕셔너리로 변환
    normalized = []
    for movie in movies:
        if isinstance(movie, dict) and "title" in movie:
            normalized.append({"title": str(movie["title"])})
        elif isinstance(movie, str):
            normalized.append({"title": movie})
    return normalized


@app.route('/')
def index():
    query = request.args.get('query', '').lower()
    movies = fetch_movies()

    if query:
        movies = [movie for movie in movies if query in movie['title'].lower()]

    return render_template("index.html", movies=movies)
