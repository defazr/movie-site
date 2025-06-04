from flask import Flask, render_template, request
import http.client
import json
import os

app = Flask(__name__)

def fetch_movies():
    conn = http.client.HTTPSConnection("imdb-top-100-movies.p.rapidapi.com")
    headers = {
        'x-rapidapi-key': os.getenv("RAPIDAPI_KEY"),
        'x-rapidapi-host': os.getenv("RAPIDAPI_HOST")
    }
    conn.request("GET", "/top", headers=headers)
    res = conn.getresponse()
    data = res.read().decode("utf-8")
    movies = json.loads(data)

    # 🎯 제목 문자열 변환 (title 메서드 적용)
    for movie in movies:
        if isinstance(movie.get('title'), str):
            movie['title'] = movie['title'].title()

    return movies

@app.route('/')
def index():
    query = request.args.get('q', '')
    movies = fetch_movies()
    if query:
        movies = [m for m in movies if query.lower() in m['title'].lower()]
    return render_template('index.html', movies=movies, query=query)

@app.route('/privacy-policy')
def privacy():
    return render_template('privacy.html')

@app.route('/terms')
def terms():
    return render_template('terms.html')

@app.route('/about')
def about():
    return render_template('about.html')

if __name__ == '__main__':
    app.run(debug=True)
