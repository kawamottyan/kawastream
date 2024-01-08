import numpy as np
import os
import joblib

class LinUCB:
    def __init__(self, alpha, num_users, num_genres, num_items):
        self.alpha = alpha
        self.num_users = num_users
        self.num_genres = num_genres
        self.num_items = num_items
        self.d = num_genres + num_items
        self.A = np.repeat(np.identity(self.d, dtype=np.float32)[np.newaxis, :, :], num_genres, axis=0)
        self.b = np.zeros((num_genres, self.d), dtype=np.float32)

    def fit(self, user_genre_matrix, user_movie_matrix, batch_size, num_epochs):
        avg_rewards = []
        for epoch in range(num_epochs):
            print('start epoch', str(epoch))
            rewards = []

            A_a_inv = np.array([np.linalg.inv(self.A[a]) for a in range(self.num_genres)])

            for batch_start in range(0, self.num_users, batch_size):
                batch_end = min(batch_start + batch_size, self.num_users)
                batch_user_features = np.concatenate((user_genre_matrix[batch_start:batch_end], user_movie_matrix[batch_start:batch_end]), axis=1)

                for a in range(self.num_genres):
                    theta_a = A_a_inv[a].dot(self.b[a])
                    p_t_batch = batch_user_features.dot(theta_a) + \
                                self.alpha * np.sqrt(np.sum(batch_user_features.dot(A_a_inv[a]) * batch_user_features, axis=1))

                    for i, user_id in enumerate(range(batch_start, batch_end)):
                        a_t = a if p_t_batch[i] == max(p_t_batch) else None
                        if a_t is not None:
                            r_t = 1 if user_genre_matrix[user_id, a_t] == 1 else 0
                            rewards.append(r_t)

                            x_t_at = batch_user_features[i].reshape(-1, 1)
                            self.A[a_t] = self.A[a_t] + x_t_at.dot(x_t_at.T)
                            self.b[a_t] = self.b[a_t] + r_t * x_t_at.flatten()

                            A_a_inv[a_t] = np.linalg.inv(self.A[a_t])

            avg_rewards.append(np.mean(rewards))

        return avg_rewards

    def predict(self, user_features, context_features):
        p_t = np.zeros(self.num_genres)

        for genre_id in range(self.num_genres):
            user_features_vector = user_features.reshape(-1)
            context_features_vector = context_features.reshape(-1)

            combined_features = np.concatenate((user_features_vector, context_features_vector))

            x_ta = combined_features.reshape(-1, 1)
            A_a_inv = np.linalg.inv(self.A[genre_id])
            theta_a = A_a_inv.dot(self.b[genre_id])

            p_t[genre_id] = theta_a.T.dot(x_ta) + self.alpha * np.sqrt(x_ta.T.dot(A_a_inv).dot(x_ta))

        recommended_genres = np.argsort(-p_t)
        return recommended_genres

    def update(self, user_id, item_id, reward, user_features, context_features):
        user_features_vector = user_features.reshape(-1)
        context_features_vector = context_features.reshape(-1)
        combined_features = np.concatenate((user_features_vector, context_features_vector))

        x_t_at = combined_features.reshape(-1, 1)

        self.A[item_id] = self.A[item_id] + x_t_at.dot(x_t_at.T)
        self.b[item_id] = self.b[item_id] + reward * x_t_at.flatten()

    def save(self, model_dir):
        model_path = os.path.join(model_dir, 'model.joblib')
        joblib.dump({'A': self.A, 'b': self.b}, model_path)

    def check_parameters_size(self):
        a_shape = self.A.shape
        a_dtype = self.A.dtype
        b_shape = self.b.shape
        b_dtype = self.b.dtype

        print(f"Shape of A: {a_shape}, Data type: {a_dtype}")
        print(f"Shape of b: {b_shape}, Data type: {b_dtype}")

        a_memory = np.prod(a_shape) * np.dtype(a_dtype).itemsize
        b_memory = np.prod(b_shape) * np.dtype(b_dtype).itemsize

        total_memory_bytes = a_memory + b_memory
        total_memory_megabytes = total_memory_bytes / (1024 * 1024)

        print(f"Estimated memory usage of A: {a_memory} bytes ({total_memory_megabytes} MB)")
        print(f"Estimated memory usage of b: {b_memory} bytes ({total_memory_megabytes} MB)")

        total_memory = total_memory_bytes / (1024 * 1024)
        print(f"Total estimated memory usage: {total_memory} MB")