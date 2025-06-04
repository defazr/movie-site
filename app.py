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
    raw_movies = json.loads(data.decode("utf-8"))

    # 만약 리스트 안에 문자열만 있는 경우 (title만 따로 있는 형식)
    if all(isinstance(movie, str) for movie in raw_movies):
        movies = [{"title": title} for title in raw_movies]
    # 또는 dict로 되어 있지만 title 필드가 문자열이 아닌 경우를 위한 방어코드
    elif all(isinstance(movie, dict) and "title" in movie for movie in raw_movies):
        movies = raw_movies
    else:
        # 예외적인 형식이 올 경우에도 대응
        movies = [{"title": str(movie)} for movie in raw_movies]

    return movies



@app.route('/')
def index():
    query = request.args.get('query', '').lower()
    movies = fetch_movies()

    if query:
        movies = [movie for movie in movies if query in movie['title'].lower()]

    return render_template("index.html", movies=movies)
