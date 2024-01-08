import pandas as pd
import numpy as np
import json

import torch

import os
import itertools

import shutil
import argparse

import lib

def parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument("--session_key", type=str, default='SessionId')
    parser.add_argument("--item_key", type=str, default='ItemId')
    parser.add_argument("--time_key", type=str, default='Time')
    parser.add_argument("--item_idx", type=str, default='item_idx')

    parser.add_argument("--n_sample", type=float, default=-1)
    parser.add_argument("--itemmap", type=int, default=None)
    parser.add_argument("--time_sort", type=bool, default=False)

    parser.add_argument("--input_size", type=int, default=1)
    parser.add_argument("--output_size", type=int, default=1)

    parser.add_argument("--hidden_size", type=int, default=100)
    parser.add_argument("--num_layers", type=int, default=3)
    parser.add_argument("--dropout_input", type=float, default=0)
    parser.add_argument("--dropout_hidden", type=float, default=0.5)
    parser.add_argument("--embedding_dim", type=float, default=-1)
    parser.add_argument("--final_act", type=str, default='tanh')

    parser.add_argument("--optimizer_type", type=str, default='Adagrad')
    parser.add_argument("--lr", type=float, default=0.01)
    parser.add_argument("--weight_decay", type=float, default=0)

    parser.add_argument("--loss_type", type=str, default='BPR')
    parser.add_argument("--k", type=int, default=100)

    parser.add_argument("--batch_size", type=int, default=50)
    parser.add_argument("--n_epochs", type=int, default=3)

    parser.add_argument("--is_train", type=bool, default=True)
    parser.add_argument("--train", type=str, default=os.environ.get("SM_CHANNEL_TRAIN"))
    parser.add_argument("--is_eval", type=bool, default=False)
    parser.add_argument("--eval", type=str, default=os.environ.get("SM_CHANNEL_EVAL"))

    parser.add_argument("--model_dir", type=str, default=os.environ.get("SM_MODEL_DIR"))

    return parser.parse_known_args()

def get_data(train_dir, item_key, item_idx, itemmap):
    input_train_files = [ os.path.join(train_dir, file) for file in os.listdir(train_dir) ]
    for file in input_train_files:
        df = pd.read_csv(file)
    if itemmap is None:
        item_ids = df[item_key].unique()
        item2idx = pd.Series(data=np.arange(len(item_ids)), index=item_ids)
        itemmap = pd.DataFrame({item_key: item_ids, item_idx: item2idx[item_ids].values})
        lib.saveItemmap(itemmap, args.model_dir)
    else:
        df = df[df[item_key].isin(itemmap[item_key])]
        
    return df

def generate_time_ids():
    time_id = 1.0
    while True:
        yield time_id
        time_id += 1.0

def model_fn(model_dir):
    print('### LOADING MODEL ###')
    params = lib.loadParams(model_dir)
    input_size = int(params['input_size'])
    output_size = int(params['output_size'])
    hidden_size = int(params['hidden_size'])
    num_layers = int(params['num_layers'])
    dropout_input = float(params['dropout_input'])
    dropout_hidden = float(params['dropout_hidden'])
    embedding_dim = float(params['embedding_dim'])
    final_act = params['final_act']

    use_cuda = torch.cuda.is_available()
    batch_size = 1

    model = lib.GRU4REC(input_size, output_size, hidden_size, num_layers, dropout_hidden, dropout_input, embedding_dim, final_act, batch_size, use_cuda)
    model.load_state_dict(torch.load(model_dir + "/model.pth"))
    model.eval()

    return model

def input_fn(request_body, request_content_type):
    print('### LOADING DATA ###')
    params = lib.loadParams('/opt/ml/model')
    session_key = params['session_key']
    item_key = params['item_key']
    time_key = params['time_key']

    if request_content_type == "application/json":
        data = json.loads(request_body)
        time_id_generator = generate_time_ids()
        time_id_list = list(itertools.islice(time_id_generator, len(data['iids'])))

        df = pd.DataFrame({
            session_key: [data['uid']] * len(data['iids']),
            item_key: data['iids'],
            time_key: time_id_list
        })
        return df
    else:
        raise ValueError("Unsupported content type: ", request_content_type)

def predict_fn(input_data, model):
    print('### PREDICT DATA ###')
    params = lib.loadParams('/opt/ml/model')
    session_key = params['session_key']
    item_key = params['item_key']
    time_key = params['time_key']
    item_idx = params['item_idx']
    top_k = int(params['k'])

    item_map = lib.loadItemmap('/opt/ml/model')
    test_items = input_data[item_key].unique()

    Predictiton = lib.Predictiton(model, item_map, session_key, item_key, time_key, item_idx)
    predictions = Predictiton.predict(input_data)

    item_index_to_id = dict(zip(item_map[item_idx], item_map[item_key]))
    mapped_predictions = {item_index_to_id[i]: score for i, score in enumerate(predictions)}

    filtered_predictions = {item_id: score for item_id, score in mapped_predictions.items() if item_id not in test_items}
    top_items = sorted(filtered_predictions.items(), key=lambda x: x[1], reverse=True)[:top_k]

    return top_items

def train():
    print('### LOADING TRAIN DATA ###')
    train = args.train
    eval = args.eval
    is_train = args.is_train
    is_eval = args.is_eval
    session_key = args.session_key
    item_key = args.item_key
    time_key = args.time_key
    item_idx = args.item_idx
    n_sample = args.n_sample
    itemmap = args.itemmap
    time_sort = args.time_sort

    train_df = get_data(train, item_key, item_idx, itemmap)
    train_data = lib.Dataset(train_df, session_key, item_key, time_key, item_idx, n_sample, itemmap, time_sort)
    print('loaded train data\n', train_df.head(3))

    if is_eval:
        eval_df = get_data(eval, item_key, item_idx, itemmap)
        eval_data = lib.Dataset(eval_df, session_key, item_key, time_key, item_idx, n_sample, itemmap, time_sort)
        print('loaded eval data\n', eval_df.head(3))
    else:
        eval_data = None

    print('### LOADING PARAMETER ###')
    input_size = train_df[args.item_key].nunique()
    output_size = input_size
    hidden_size = args.hidden_size
    num_layers = args.num_layers
    dropout_input = args.dropout_input
    dropout_hidden = args.dropout_hidden
    embedding_dim = args.embedding_dim
    final_act = args.final_act
    optimizer_type = args.optimizer_type
    lr = args.lr
    weight_decay = args.weight_decay
    loss_type = args.loss_type
    k = args.k
    batch_size = args.batch_size
    n_epochs = args.n_epochs
    model_dir = args.model_dir
    use_cuda = torch.cuda.is_available()
    device = torch.device('cuda' if use_cuda else 'cpu')
    print('loaded parameter')

    print('### SAVING PARAMETER ###')
    file = lib.saveParams(model_dir, session_key, item_key, time_key, item_idx, input_size, output_size, hidden_size, num_layers, dropout_input, dropout_hidden, embedding_dim, final_act, k)
    print('saved parameter at ', file)

    print('### STARTING MODEL SETUP ###')
    model = lib.GRU4REC(input_size, output_size, hidden_size, num_layers, dropout_hidden, dropout_input, embedding_dim, final_act, batch_size, use_cuda)
    model = model.to(device)
    loss_func = lib.LossFunctionNeg(loss_type)
    optim = lib.Optimizer(model.parameters(), optimizer_type, lr, weight_decay)
    trainer = lib.Trainer( model, train_data, item_idx, optim, use_cuda, loss_func, batch_size, k, n_epochs, is_train, is_eval, eval_data)
    print('created model: ', model)
    print('created model parameters: ', model.parameters())

    print('### TRAINING MODEL ###')
    metrics = trainer.train()
    mean_metric = np.mean(metrics)
    print('epoch metrics: ', metrics)
    print('average metric: ', mean_metric)

    print('### SAVING MODEL ###')
    torch.save(model.state_dict(), model_dir + "/model.pth")
    print('saved model ', model)

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

    print('### TRAINING END ###')

if __name__ == "__main__":
    args, _ = parse_args()
    train()