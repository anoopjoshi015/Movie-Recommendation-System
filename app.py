from castsearch import *
from flask import Flask, render_template, request
import pickle
import requests

from requests import post

movies = pickle.load(open('movies.pkl', 'rb'))
similarity = pickle.load(open('similarity.pkl', 'rb'))
top_movies = pickle.load(open('topmovies.pkl', 'rb'))


def fetch_poster(movie_id):
    response = requests.get(
        'https://api.themoviedb.org/3/movie/{}?api_key=<API KEY>&language=en-US'.format(
            movie_id))
    data = response.json()
    return "https://image.tmdb.org/t/p/w500/" + data['poster_path']


def fetch_actor_details(actor_id):
    response = requests.get(
        'https://api.themoviedb.org/3/person/{}?api_key=<API KEY>&language=en-US'.format(
            actor_id))
    data = response.json()
    list1 = []
    list1.append("https://www.themoviedb.org/t/p/w300_and_h450_bestv2" + data['profile_path'])
    # list1.append(data['biography'])
    # list1.append(data['known_for_department'])
    list1.append(data['name'])
    # list1.append(data['birthday'])
    # list1.append(data['gender'])
    # list1.append(data['place_of_birth'])
    list1.append(data['imdb_id'])
    # list1.append(data['popularity'])

    return list1


app = Flask(__name__)


@app.route('/')
def index():
    all_movie = list(movies['title'].values)
    return render_template('home.html', all_movies=all_movie)


@app.route('/top')
def topmovie():
    return render_template('top.html',
                           movie_name=list(top_movies['title'].values),
                           movie_poster=list(top_movies['poster'].values),
                           movie_imdb_id=list(top_movies['imdb_id'].values),
                           movie_genres=list(top_movies['genres'].values),
                           movie_release_date=list(top_movies['release_date'].values),
                           movie_vote_count=list(top_movies['vote_count'].values))


@app.route('/search_res')
def searchres():
    return render_template('search_result.html')


@app.route('/recommend_search', methods=['post'])
def searchRecom():
    user_input = request.form.get('search')
    movie_index = movies[movies['title'] == user_input].index[0]
    distances = similarity[movie_index]
    movies_list = sorted(list(enumerate(distances)), reverse=True, key=lambda x: x[1])[1:7]
    cast_ids = movies[['cast_id']].iloc[movie_index, 0]

    data1 = []
    list2 = []
    data1.append(fetch_poster(movies.iloc[movie_index].id))
    data1.append(movies.iloc[movie_index].title)
    data1.append(movies.iloc[movie_index].genres)
    data1.append(movies.iloc[movie_index].runtime)
    data1.append(movies.iloc[movie_index].vote_count)
    data1.append(movies.iloc[movie_index].overview)
    data1.append(movies.iloc[movie_index].imdb_id)
    list2.append(data1)

    actor_profile = []
    for i in cast_ids:
        actor_profile.append(fetch_actor_details(i))

    data2 = []
    for i in movies_list:
        List1 = []
        List1.append(movies.iloc[i[0]].title)
        List1.append(fetch_poster(movies.iloc[i[0]].id))
        List1.append(movies.iloc[i[0]].genres)
        List1.append(movies.iloc[i[0]].imdb_id)

        data2.append(List1)
    return render_template('Search_result.html', data2=data2, list2=list2, actor_profile=actor_profile)

@app.route('/text_search')
def homeTextSearch():
    return render_template('textsearch.html')


@app.route('/text_search', methods=['post'])
def textSearch():
    text_input = request.form.get('text_input')
    recommended_movies = text_movie(text_input)
    return render_template('textsearch.html',recommended_movies = recommended_movies)



if __name__ == "__main__":
    app.run(debug=True)
