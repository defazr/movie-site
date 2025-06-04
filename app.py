from flask import Flask, render_template, request
import http.client
import json
import os

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
    movies = json.loads(data)
    return movies

@app.route('/')
def index():
    query = request.args.get('query', '')
    movies = fetch_movies()
    if query:
        movies = [movie for movie in movies if query.lower() in movie['title'].lower()]
    return render_template('index.html', movies=movies)

@app.route('/privacy-policy')
def privacy():
    return "<h1>Privacy Policy</h1><p>This is a sample privacy policy page.</p>"

if __name__ == '__main__':
    app.run(debug=True)
