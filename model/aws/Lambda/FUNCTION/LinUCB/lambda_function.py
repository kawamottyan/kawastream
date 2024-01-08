import os
import boto3
import json
from pymongo import MongoClient
from bson import ObjectId
from datetime import datetime

ENDPOINT_NAME = os.environ['ENDPOINT_NAME']
MONGO_URI = os.environ.get("ATLAS_URI")
runtime = boto3.client('runtime.sagemaker')

connect = MongoClient(host=MONGO_URI)
db = connect.test
collection_cli = db.clicks

def lambda_handler(event, context):

    with open('genre_dict.json', 'r') as file:
        genre_dict = json.load(file)

    user_id = event.get('detail', {}).get('fullDocument', {}).get('user')
    user_id_obj = ObjectId(user_id)
    user_clicks = collection_cli.find({"user": user_id_obj})

    genres = list(genre_dict.keys())
    user_features = []
    for genre in genres:
        found = any(click.get('containerName') == genre for click in user_clicks)
        user_features.append(1 if found else 0)

    cli_pipeline = [
        {"$match": {"user": user_id_obj}},
        {"$project": {"mediaId": 1}}
    ]

    cli_result = list(collection_cli.aggregate(cli_pipeline))
    cli_media_ids = [int(doc['mediaId']) for doc in cli_result if 'mediaId' in doc]

    test = {
        "u": user_features,
        "item": cli_media_ids
    }
    payload_json = json.dumps(test)

    try:
        response = runtime.invoke_endpoint(EndpointName=ENDPOINT_NAME, ContentType='application/json', Body=payload_json)
        result = json.loads(response['Body'].read().decode())

        genres = [genre for index in result for genre, idx in genre_dict.items() if idx == index]

        explains_collection = db.explains
        current_timestamp = datetime.utcnow().isoformat(timespec='milliseconds')

        filter_query = {
            "user": user_id_obj
        }

        update_data = {
            "$set": {
                "explains": genres,
                "updatedAt": current_timestamp,
            },
            "$setOnInsert": {
                "_id": ObjectId(),
                "createdAt": current_timestamp
            }
        }

        update_result = explains_collection.update_one(filter_query, update_data, upsert=True)

        if update_result.upserted_id:
            print(f"Inserted new genre for user: {user_id}")
        elif update_result.modified_count:
            print(f"Updated genre for user: {user_id}")

    except Exception as e:
        print(f"Error processing the request: {e}")
        return {
            'statusCode': 500,
            'body': json.dumps({
                'message': 'Error processing your request',
                'error': str(e)
            })
        }