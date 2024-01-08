import numpy as np
import json

from scipy.sparse import csr_matrix
from sklearn.decomposition import TruncatedSVD

import os
import shutil
import joblib
import argparse

import lib

def parse_args():
    parser = argparse.ArgumentParser()

    parser.add_argument("--session_key", type=str, default='SessionId')

    parser.add_argument("--alpha", type=float, default=1.0)
    parser.add_argument("--num_users", type=int, default=100)
    parser.add_argument("--num_genres", type=int, default=19)
    parser.add_argument("--num_items", type=int, default=100)
    
    parser.add_argument("--n_components", type=int, default=100)

    parser.add_argument("--batch_size", type=int, default=50)
    parser.add_argument("--num_epochs", type=int, default=1)

    parser.add_argument("--train", type=str, default=os.environ.get("SM_CHANNEL_TRAIN"))
    parser.add_argument("--eval", type=str, default=os.environ.get("SM_CHANNEL_EVAL"))
    parser.add_argument("--model_dir", type=str, default=os.environ.get("SM_MODEL_DIR"))

    return parser.parse_known_args()

def model_fn(model_dir):
    print('### LOADING MODEL ###')
    params = lib.loadParams(model_dir)
    alpha = float(params['alpha'])
    num_users = int(params['num_users'])
    num_genres = int(params['num_genres'])
    num_items = int(params['num_items'])

    model_path = os.path.join(model_dir, 'model.joblib')
    model_data = joblib.load(model_path)

    model = lib.LinUCB(alpha, num_users, num_genres, num_items)
    model.A = model_data['A']
    model.b = model_data['b']
    return model

def input_fn(request_body, request_content_type):
    print('### LOADING DATA ###')
    if request_content_type == "application/json":
        input_data = json.loads(request_body)
        return input_data
    else:
        raise ValueError("Unsupported content type: {}".format(request_content_type))

def predict_fn(input_data, model):
    print('### PREDICT DATA ###')
    svd = lib.loadModel('/opt/ml/model')
    item_id_mapping, genre_mapping = lib.loadDict('/opt/ml/model')
    print('--svd--', svd)
    print('--item_id_mapping--', item_id_mapping)
    
    user_features = np.array(input_data['u'], dtype=np.int64)
    item_list = np.array(input_data['item'], dtype=np.int64)
    
    item_features = [1 if item_id_mapping.get(index) in item_list else 0 for index in range(len(item_id_mapping))]
    print('--item_features--', item_features)
    item_features_2d = np.array(item_features).reshape(1, -1)
    print('--item_features_2d--', item_features_2d)
    
    context_features = svd.transform(item_features_2d)
    print('--context_features--', context_features)
    
    predicted_items = model.predict(user_features, context_features)

    return predicted_items

def train():
    print('### LOADING PARAMETER ###')

    alpha = args.alpha
    num_users = args.num_users
    num_genres = args.num_genres
    num_items = args.num_items

    n_components = args.n_components

    batch_size = args.batch_size
    num_epochs = args.num_epochs

    train = args.train
    eval = args.eval
    model_dir = args.model_dir
    print('loaded parameter')

    print('### LOADING TRAIN DATA ###')
    rating_df, user_genre_matrix_df = lib.load_data(train, eval)
    user_genre_matrix, user_movie_matrix, svd, item_id_mapping, genre_mapping = lib.process_data(rating_df, user_genre_matrix_df, n_components)
    print('loaded user_genre_matrix\n', user_genre_matrix)
    print('loaded user_movie_matrix\n', user_movie_matrix)
    
    num_users = user_genre_matrix.shape[0]
    num_genres = user_genre_matrix.shape[1]
    num_items = user_movie_matrix.shape[1]
    print('number of users: ', num_users)
    print('number of genres: ', num_genres)
    print('number of items: ', num_items)

    lib.saveModel(model_dir, svd)
    lib.saveDict(model_dir, item_id_mapping, genre_mapping)

    print('### STARTING MODEL SETUP ###')
    model = lib.LinUCB(alpha, num_users, num_genres, num_items)
    print('created model: ', model)

    print('### TRAINING MODEL ###')
    model.fit(user_genre_matrix, user_movie_matrix, batch_size, num_epochs)
    print('finish training')

    print('### SAVING MODEL ###')
    model.save(model_dir)
    model.check_parameters_size()
    print('finish saving')

    print('### SAVING CODE ###')
    inference_code_name = "inference.py"
    inference_folder_name = "lib"
    inference_code_path = model_dir + "/code/"
    inference_folder_path = inference_code_path + inference_folder_name

    if not os.path.exists(inference_code_path):
        os.mkdir(inference_code_path)
    if os.path.exists(inference_folder_path):
        shutil.rmtree(inference_folder_path)

    shutil.copy(inference_code_name, inference_code_path)
    shutil.copytree(inference_folder_name, inference_folder_path)
    print('saved code in ', inference_code_path)
    
    print('### SAVING PARAMETER ###')
    file = lib.saveParams(model_dir, alpha, num_users, num_genres, num_items)
    print('saved parameter at ', file)

    print('### TRAINING END ###')

if __name__ == "__main__":
    args, _ = parse_args()
    train()