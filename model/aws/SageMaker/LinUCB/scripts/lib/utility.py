import os
import pickle

def saveParams(model_dir, alpha, num_users, num_genres, num_items):
    if not os.path.exists(model_dir):
        os.mkdir(model_dir)
    file = open(os.path.join(model_dir, 'networkParams'), "w")
    file.write("alpha=" + str(alpha) + "\n")
    file.write("num_users=" + str(num_users) + "\n")
    file.write("num_genres=" + str(num_genres) + "\n")
    file.write("num_items=" + str(num_items) + "\n")
    file.close()

    return file

def loadParams(model_dir):
    params = {}
    with open(os.path.join(model_dir, 'networkParams'), 'r') as file:
        for line in file:
            key, value = line.strip().split('=')
            params[key] = value

    return params

def saveModel(model_dir, svd):
    if not os.path.exists(model_dir):
        os.mkdir(model_dir)
    with open(os.path.join(model_dir, 'svd_model.pkl'), 'wb') as f:
        pickle.dump(svd, f)

def loadModel(model_dir):
    with open(os.path.join(model_dir, 'svd_model.pkl'), 'rb') as f:
        svd = pickle.load(f)
    return svd

def saveDict(model_dir, item_id_mapping, genre_mapping):
    if not os.path.exists(model_dir):
        os.mkdir(model_dir)
    with open(os.path.join(model_dir, 'item_id_mapping.pkl'), 'wb') as f:
        pickle.dump(item_id_mapping, f)
    with open(os.path.join(model_dir, 'genre_mapping.pkl'), 'wb') as f:
        pickle.dump(genre_mapping, f)

def loadDict(model_dir):
    with open(os.path.join(model_dir, 'item_id_mapping.pkl'), 'rb') as f:
        item_id_mapping = pickle.load(f)
    with open(os.path.join(model_dir, 'genre_mapping.pkl'), 'rb') as f:
        genre_mapping = pickle.load(f)
    return item_id_mapping, genre_mapping