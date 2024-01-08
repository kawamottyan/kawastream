import pandas as pd
import numpy as np
import torch
import random

class Dataset(object):
    def __init__(self, df, session_key, item_key, time_key, item_idx, n_sample, itemmap, time_sort):
        self.df = df
        self.session_key = session_key
        self.item_key = item_key
        self.time_key = time_key
        self.item_idx = item_idx
        self.time_sort = time_sort
        if n_sample > 0:
            self.df = self.df[:n_sample]

        self.add_item_indices(itemmap=itemmap)
        self.df.sort_values([session_key, time_key], inplace=True)
        self.click_offsets = self.get_click_offset()
        self.session_idx_arr = self.order_session_idx()

    def add_item_indices(self, itemmap=None):
        if itemmap is None:
            item_ids = self.df[self.item_key].unique()
            item2idx = pd.Series(data=np.arange(len(item_ids)), index=item_ids)
            itemmap = pd.DataFrame({self.item_key: item_ids, self.item_idx: item2idx[item_ids].values})
        self.itemmap = itemmap
        self.df = pd.merge(self.df, self.itemmap, on=self.item_key, how='inner')

    def get_click_offset(self):
        offsets = np.zeros(self.df[self.session_key].nunique() + 1, dtype=np.int32)
        offsets[1:] = self.df.groupby(self.session_key).size().cumsum()
        return offsets

    def order_session_idx(self):
        if self.time_sort:
            sessions_start_time = self.df.groupby(self.session_key)[self.time_key].min().values
            session_idx_arr = np.argsort(sessions_start_time)
        else:
            session_idx_arr = np.arange(self.df[self.session_key].nunique())
        return session_idx_arr

    @property
    def items(self):
        return self.itemmap[self.item_key].unique()

class DataLoader():
    def __init__(self, dataset, item_idx, batch_size, is_train):
        self.dataset = dataset
        self.item_idx = item_idx
        self.batch_size = batch_size
        self.is_train = is_train
        self.total_items = len(set(self.dataset.df[self.item_idx]))
        item_counts = dataset.df[self.item_idx].value_counts()
        self.item_probabilities = item_counts / item_counts.sum()

    def __iter__(self):
        df = self.dataset.df
        click_offsets = self.dataset.click_offsets
        session_idx_arr = self.dataset.session_idx_arr

        iters = np.arange(self.batch_size)
        maxiter = iters.max()
        start = click_offsets[session_idx_arr[iters]]
        end = click_offsets[session_idx_arr[iters] + 1]
        mask = []
        finished = False
        batch_items = set()

        while not finished:
            minlen = (end - start).min()
            idx_target = df.item_idx.values[start]

            for i in range(minlen - 1):
                idx_input = idx_target
                idx_target = df.item_idx.values[start + i + 1]
                input = torch.LongTensor(idx_input)
                target = torch.LongTensor(idx_target)

                batch_items.update(idx_input.tolist())
                batch_items.update(idx_target.tolist())

                if self.is_train:
                    idx_negative_samples = self.generate_negative_samples(batch_items, num_samples=10)
                    negative_samples = torch.LongTensor(idx_negative_samples)
                    yield input, target, negative_samples, mask

                else:
                    yield input, target, mask

            start = start + (minlen - 1)
            mask = np.arange(len(iters))[(end - start) <= 1]
            for idx in mask:
                maxiter += 1
                if maxiter >= len(click_offsets) - 1:
                    finished = True
                    break
                iters[idx] = maxiter
                start[idx] = click_offsets[session_idx_arr[maxiter]]
                end[idx] = click_offsets[session_idx_arr[maxiter] + 1]

    def generate_negative_samples(self, batch_items, num_samples):
        try:
            all_items = set(range(self.total_items))
            available_items = list(all_items - batch_items)
            if not available_items:
                available_items = list(all_items)
            weights = self.item_probabilities[available_items].values
            idx_negative_samples = random.choices(available_items, weights=weights, k=num_samples)

            return idx_negative_samples

        except Exception as e:
            print("An error occurred:", e)
            raise e