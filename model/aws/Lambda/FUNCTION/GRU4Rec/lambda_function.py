import os
import json
import boto3
import pandas as pd
from pymongo import MongoClient
from bson import ObjectId
from datetime import datetime

ENDPOINT_NAME = os.environ['ENDPOINT_NAME']
MONGO_URI = os.environ.get("ATLAS_URI")
runtime = boto3.client('runtime.sagemaker')

connect = MongoClient(host=MONGO_URI)
db = connect.test
collection = db.clicks

def lambda_handler(event, context):

    file_path = 'tmdb.json'
    df = pd.read_json(file_path, orient='records')

    current_timestamp = datetime.utcnow().isoformat(timespec='milliseconds')
    user_id = event.get('detail', {}).get('fullDocument', {}).get('user')
    user_id_obj = ObjectId(user_id)

    cli_pipeline = [
        {"$match": {"user": user_id_obj}},
        {"$project": {"mediaId": 1}}
    ]

    cli_result = list(collection.aggregate(cli_pipeline))
    cli_media_ids = [int(doc['mediaId']) for doc in cli_result if 'mediaId' in doc]

    payload = {
        "uid": 0,
        "iids": cli_media_ids
    }

    payload_json = json.dumps(payload)

    try:
        response = runtime.invoke_endpoint(EndpointName=ENDPOINT_NAME, ContentType='application/json', Body=payload_json)
        result = json.loads(response['Body'].read().decode())

        prediction_collection = db.predictions

        predictions = []
        for rank, prediction in enumerate(result):
            movie_id, predicted_rating = prediction
            movie_data = df[df['mediaId'] == movie_id]
            media_poster = movie_data['mediaPoster'].values[0] if movie_id in movie_data['mediaId'].values else None
            media_title = movie_data['mediaTitle'].values[0] if movie_id in movie_data['mediaId'].values else None
            backdrop_path = movie_data['backdrop_path'].values[0] if movie_id in movie_data['mediaId'].values else None
            vote_average = movie_data['vote_average'].values[0] if movie_id in movie_data['mediaId'].values else None
            release_date = movie_data['release_date'].values[0] if movie_id in movie_data['mediaId'].values else None
            genre_names = movie_data['genre_names'].values[0] if movie_id in movie_data['mediaId'].values else None

            prediction_data = {
                "rank": rank + 1,
                "mediaId": str(movie_id),
                "rating": predicted_rating,
                "mediaPoster": media_poster,
                "mediaTitle": media_title,
                "backdrop_path": backdrop_path,
                "vote_average": vote_average,
                "release_date": release_date,
                "genre_names": genre_names,
            }

            predictions.append(prediction_data)

        filter_query = {"user": user_id_obj}

        update_data = {
            "$set": {
                "predictions": predictions,
                "updatedAt": current_timestamp
            },
            "$setOnInsert": {
                "createdAt": current_timestamp
            }
        }

        update_result = prediction_collection.update_one(filter_query, update_data, upsert=True)

        if update_result.upserted_id:
            print(f"Inserted new predictions for user: {user_id}")
        elif update_result.modified_count:
            print(f"Updated predictions for user: {user_id}")

    except Exception as e:
        print(f"Error processing the request: {e}")
        return {
            'statusCode': 500,
            'body': json.dumps({
                'message': 'Error processing your request',
                'error': str(e)
            })
        }