import os
import requests
from pymongo import MongoClient

MONGO_URI = os.environ.get("ATLAS_URI")
TMDB_KEY = os.environ.get("TMDB_KEY")

connect = MongoClient(host=MONGO_URI)
db = connect.test
collection_nowplaying = db.nowplayings
collection_popular = db.populars
collection_toprated = db.toprateds

def lambda_handler(event, context):
    def fetch_and_store_movies(url, collection):
        collection.delete_many({})
        response = requests.get(url)
        if response.status_code == 200:
            data = response.json()
            movies = data['results']
            return collection.insert_many(movies).inserted_ids
        else:
            return None

    now_playing_url = f"https://api.themoviedb.org/3/movie/now_playing?api_key={TMDB_KEY}&language=en-US&page=1"
    popular_url = f"https://api.themoviedb.org/3/movie/popular?api_key={TMDB_KEY}&language=en-US&page=1"
    top_rated_url = f"https://api.themoviedb.org/3/movie/top_rated?api_key={TMDB_KEY}&language=en-US&page=1"

    now_playing_ids = fetch_and_store_movies(now_playing_url, collection_nowplaying)
    popular_ids = fetch_and_store_movies(popular_url, collection_popular)
    top_rated_ids = fetch_and_store_movies(top_rated_url, collection_toprated)

    if now_playing_ids is None or popular_ids is None or top_rated_ids is None:
        return {
            'statusCode': 500,
            'body': 'Failed to retrieve or store data'
        }

    return {
        'statusCode': 200,
        'body': {
            'now_playing_ids': [str(id) for id in now_playing_ids],
            'popular_ids': [str(id) for id in popular_ids],
            'top_rated_ids': [str(id) for id in top_rated_ids]
        }
    }