import numpy as np
import torch
from tqdm import tqdm

from .dataset import DataLoader
from .evaluation import Evaluation

class Trainer(object):
    def __init__(self, model, train_data, item_idx, optim, use_cuda, loss_func, batch_size, k, n_epochs, is_train, is_eval, eval_data):
        self.model = model
        self.train_data = train_data
        self.item_idx =item_idx
        self.optim = optim
        self.loss_func = loss_func
        self.k = k
        self.batch_size = batch_size
        self.n_epochs = n_epochs
        self.is_train = is_train
        self.is_eval = is_eval
        self.eval_data = eval_data
        self.evaluation = Evaluation(self.model, self.loss_func, use_cuda, k)
        self.device = torch.device('cuda' if use_cuda else 'cpu')

    def train(self):
        epoch_loss = []
        epoch_ndcg = []
        for epoch in range(self.n_epochs):
            loss = self.train_epoch()
            epoch_loss.append(loss)
            print('finish epoch {}'.format(epoch + 1))
            print('loss', loss)
            if self.is_eval:
                ndcg = self.evaluation.eval(self.eval_data, self.item_idx, self.batch_size)
                epoch_ndcg.append(ndcg)
                print('ndcg', ndcg)
        if self.is_eval:
            return epoch_ndcg
        else:
            return epoch_loss

    def train_epoch(self):
        self.model.train()
        losses = []

        def reset_hidden(hidden, mask):
            if len(mask) != 0:
                hidden[:, mask, :] = 0
            return hidden

        hidden = self.model.init_hidden()
        dataloader = DataLoader(self.train_data, self.item_idx, self.batch_size, self.is_train)

        for ii, (input, target, negative_samples, mask) in tqdm(enumerate(dataloader), total=len(dataloader.dataset.df) // dataloader.batch_size, miniters = 1000):
            input = input.to(self.device)
            target = target.to(self.device)
            negative_samples = negative_samples.to(self.device)

            self.optim.zero_grad()
            hidden = reset_hidden(hidden, mask).detach()
            logit, hidden = self.model(input, hidden)

            pos_logits = logit[:, target.view(-1)]
            neg_logits = logit[:, negative_samples.view(-1)]

            loss = self.loss_func(pos_logits, neg_logits)
            losses.append(loss.item())

            loss.backward()
            self.optim.step()

        return np.mean(losses)