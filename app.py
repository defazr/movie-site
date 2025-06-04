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
    movies_raw = json.loads(data.decode("utf-8"))

    # title 필드가 문자열인 것만 추림
    movies = []
    for movie in movies_raw:
        title = movie.get("title")
        if isinstance(title, str):
            movies.append({"title": title})

    return movies

@app.route('/')
def index():
    query = request.args.get('query', '').lower()
    movies = fetch_movies()

    if query:
        movies = [movie for movie in movies if query in movie.get('title', '').lower()]

    return render_template("index.html", movies=movies)
