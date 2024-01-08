import pandas as pd
import os

from scipy.sparse import csr_matrix
from sklearn.decomposition import TruncatedSVD

def load_data(train_dir, eval_dir):
    input_train_files = [ os.path.join(train_dir, file) for file in os.listdir(train_dir) ]
    for file in input_train_files:
        rating_df = pd.read_csv(file)
    input_eval_files = [ os.path.join(eval_dir, file) for file in os.listdir(eval_dir) ]
    for file in input_eval_files:
        user_genre_matrix_df =  pd.read_csv(file)

    return rating_df, user_genre_matrix_df

def process_data(rating_df, user_genre_matrix_df, n_components):
            
    genre_mapping = {col: idx for idx, col in enumerate(user_genre_matrix_df.columns)}
    
    rating_df['interaction'] = 1
    sparse_matrix = csr_matrix((rating_df['interaction'], 
                                (rating_df['SessionId'].astype('category').cat.codes, 
                                 rating_df['ItemId'].astype('category').cat.codes)))
    
    print('--sparse_matrix--', sparse_matrix)
    print('--sparse_matrix shape--', sparse_matrix.shape)

    session_id_mapping = dict(enumerate(rating_df['SessionId'].astype('category').cat.categories))
    item_id_mapping = dict(enumerate(rating_df['ItemId'].astype('category').cat.categories))
    
    svd = TruncatedSVD(n_components=n_components)

    user_movie_matrix = svd.fit_transform(sparse_matrix)
    user_genre_matrix = user_genre_matrix_df.to_numpy().astype('float64')

    return user_genre_matrix, user_movie_matrix, svd, item_id_mapping, genre_mapping