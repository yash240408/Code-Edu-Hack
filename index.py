import random, os, requests
from flask import Flask, render_template, request
import pandas as pd
from sklearn.neighbors import NearestNeighbors

app = Flask(__name__)
app.config["TEMPLATES_AUTO_RELOAD"] = True
app.config['SESSION_REFRESH_EACH_REQUEST'] = True
TMDB_API_KEY = os.environ.get("API_KEY")

@app.after_request
def after_request(response):
    """Ensure responses aren't cached"""
    response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
    response.headers["Expires"] = 0
    response.headers["Pragma"] = "no-cache"
    return response


@app.route("/", methods=["GET", "POST"])
def home():
    return render_template("index.html")


@app.route("/search", methods=["GET", "POST"])
def search():
    if request.method == "POST":
        name = request.form.get("movie_name")
        if not name:
            return render_template("index.html", message="No Input Is Provided!")
        else:
            name = name.upper().strip()  # Convert input to uppercase
            similar_movies = get_similar_movies(movie_name=name)
            if similar_movies == "No Movie Find":
                return render_template("index.html", message="No Movie Was Found With Your Keyword")
            else:
                names_movies=[]
                links_movies=[]
                for i, movie in enumerate(similar_movies, start=1):
                    url = f'https://api.themoviedb.org/3/search/movie?query={movie}&api_key={TMDB_API_KEY}'
                    response = requests.get(url)
                    data = response.json()
                    if "results" in data and data["results"]:
                        img_path = data["results"][0]["poster_path"]
                        url2 = "http://image.tmdb.org/t/p/w500"
                        final_url = url2 + img_path
                        names_movies.append(movie)
                        links_movies.append(final_url)
                return render_template("results.html", movieName = names_movies, movieLink = links_movies)

    else:
        return render_template("index.html")


@app.route("/movies", methods=["GET", "POST"])
def random_movies():
    random_movie = random.randint(1, 500)
    url = f'https://api.themoviedb.org/3/discover/movie?api_key={TMDB_API_KEY}&language=en-US&sort_by=popularity.desc&include_adult=false&include_video=false&page={random_movie}'
    response = requests.get(url)
    data = response.json()
    movies = data["results"][:12]
    return render_template("gallery.html", data=movies)

def get_similar_movies(movie_name):
    try:
        df = pd.read_csv("static/ALL_MOVIE_DATA2.csv")
        # Convert movie names to uppercase for consistency
        df["Movie Names"] = df["Movie Names"].str.upper()
        ratings_matrix = df.pivot_table(values="Rating", index="ID", columns="Genere", fill_value=0)
        model = NearestNeighbors(n_neighbors=10, metric="cosine")
        model.fit(ratings_matrix)
        movie_id = df[df["Movie Names"] == movie_name].index[0]
        distances, indices = model.kneighbors(
            [ratings_matrix.iloc[movie_id, :]])
        similar_movies = []
        for i in indices[0]:
            similar_movies.append(df.iloc[i, 1])
        return similar_movies
    except Exception as e:
        return "No Movie Find"


if __name__ == "__main__":
    app.run(debug=True)
