import pickle
import requests
from nltk.stem.porter import PorterStemmer
from sklearn.feature_extraction.text import CountVectorizer
from sklearn.metrics.pairwise import cosine_similarity
import pandas as pd

movies_tag_data = pickle.load(open('text_search_data.pkl', 'rb'))
movies_tag = pickle.load(open('text_search_tag.pkl','rb'))

def fetch_poster(movie_id):
    response = requests.get(
        'https://api.themoviedb.org/3/movie/{}?api_key=<API KEY>&language=en-US'.format(
            movie_id))
    data = response.json()
    return "https://image.tmdb.org/t/p/w500/" + data['poster_path']

def text_movie(text):
    text = text.lower()

    ps = PorterStemmer()

    def stem(txt):
        L = []
        for i in txt.split():
            L.append(ps.stem(i))
        return " ".join(L)

    text = stem(text)

    text = pd.DataFrame({'tags': [text]})
    movie_data = movies_tag.append(text, ignore_index=True).copy()

    cv = CountVectorizer(max_features=20000, stop_words='english')

    vectors = cv.fit_transform(movie_data['tags']).toarray()

    last_vect = vectors[len(movie_data) - 1].reshape(1, -1)

    similarity = cosine_similarity(last_vect, vectors)

    def recommend():
        distances = similarity[0]
        movies_list = sorted(list(enumerate(distances)), reverse=True, key=lambda x: x[1])[1:13]

        list2 = []
        for i in movies_list:
            list1 = []
            list1.append(movies_tag_data.iloc[i[0]].title)
            list1.append(fetch_poster(movies_tag_data.iloc[i[0]].id))
            list1.append(movies_tag_data.iloc[i[0]].genres)
            list1.append(movies_tag_data.iloc[i[0]].release_date)
            list1.append(movies_tag_data.iloc[i[0]].imdb_id)

            list2.append(list1)
        return list2

    movie_data.drop(movie_data.tail(1).index, inplace=True)

    return recommend()
