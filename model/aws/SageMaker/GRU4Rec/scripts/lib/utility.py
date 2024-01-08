import os
import pickle

def saveParams(model_dir, session_key, item_key, time_key, item_idx, input_size, output_size, hidden_size, num_layers, dropout_input, dropout_hidden, embedding_dim, final_act, k):
    if not os.path.exists(model_dir):
        os.mkdir(model_dir)
    file = open(os.path.join(model_dir, 'networkParams'), "w")
    file.write("session_key=" + str(session_key) + "\n")
    file.write("item_key=" + str(item_key) + "\n")
    file.write("time_key=" + str(time_key) + "\n")
    file.write("item_idx=" + str(item_idx) + "\n")
    file.write("input_size=" + str(input_size) + "\n")
    file.write("output_size=" + str(output_size) + "\n")
    file.write("hidden_size=" + str(hidden_size) + "\n")
    file.write("num_layers=" + str(num_layers) + "\n")
    file.write("dropout_input=" + str(dropout_input) + "\n")
    file.write("dropout_hidden=" + str(dropout_hidden) + "\n")
    file.write("embedding_dim=" + str(embedding_dim) + "\n")
    file.write("final_act=" + str(final_act) + "\n")
    file.write("k=" + str(k) + "\n")
    file.close()

    return file

def loadParams(model_dir):
    params = {}
    with open(os.path.join(model_dir, 'networkParams'), 'r') as file:
        for line in file:
            key, value = line.strip().split('=')
            params[key] = value

    return params

def saveItemmap(item_map, result_dir):
    if not os.path.exists(result_dir):
        os.makedirs(result_dir)

    file_path = os.path.join(result_dir, 'item_map.pkl')
    with open(file_path, 'wb') as file:
        pickle.dump(item_map, file)

def loadItemmap(result_dir):
    file_path = os.path.join(result_dir, 'item_map.pkl')
    with open(file_path, 'rb') as file:
        return pickle.load(file)