import numpy as np
import torch
from tqdm import tqdm

from .dataset import DataLoader

class Evaluation(object):
    def __init__(self, model, loss_func, use_cuda, k):
        self.model = model
        self.loss_func = loss_func
        self.topk = k
        self.device = torch.device('cuda' if use_cuda else 'cpu')

    def eval(self, eval_data, item_idx, batch_size):
        self.model.eval()
        ndcgs = []
        dataloader = DataLoader(eval_data, item_idx, batch_size, is_train=False)
        with torch.no_grad():
            hidden = self.model.init_hidden()
            for ii, (input, target, mask) in tqdm(enumerate(dataloader), total=len(dataloader.dataset.df) // dataloader.batch_size, miniters = 1000):

                input = input.to(self.device)
                target = target.to(self.device)
                logit, hidden = self.model(input, hidden)

                ndcg = evaluate_ndcg(logit, target, k=self.topk)
                ndcgs.append(ndcg)

        mean_ndcg = np.mean(ndcgs)

        return mean_ndcg

def dcg(scores, k):
    scores = np.asfarray(scores)[:,:k]
    n_scores = scores.shape[1]
    if n_scores == 0:
        return 0.
    return np.sum((2 ** scores - 1) / np.log2(np.arange(2, n_scores + 2)), axis=1)

def evaluate_ndcg(logits, targets, k):
    probs = torch.softmax(logits, dim=1).cpu().detach().numpy()
    targets_one_hot = np.zeros_like(probs)
    targets_numpy = targets.cpu().numpy()

    for i, target in enumerate(targets_numpy):
        adjusted_target = target - 1
        targets_one_hot[i, adjusted_target] = 1

    dcg_val = dcg(probs, k)
    order = np.argsort(-probs, axis=1)
    sorted_targets = np.take_along_axis(targets_one_hot, order, axis=1)
    idcg_val = dcg(sorted_targets, k)

    ndcg = np.mean(dcg_val / np.maximum(idcg_val, 1e-10))

    return ndcg
