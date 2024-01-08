import torch
import torch.nn as nn
import torch.nn.functional as F

class LossFunctionNeg(nn.Module):
    def __init__(self, loss_type='BPR'):
        super(LossFunctionNeg, self).__init__()
        self.loss_type = loss_type
        if loss_type == 'BPR':
            self._loss_fn = BPRLossNeg()
        elif loss_type == 'TOP1':
            self._loss_fn = TOP1LossNeg()
        else:
            raise NotImplementedError

    def forward(self, pos_logits, neg_logits):
        return self._loss_fn(pos_logits, neg_logits)

class BPRLossNeg(nn.Module):
    def __init__(self):
        super(BPRLossNeg, self).__init__()

    def forward(self, pos_logits, neg_logits):

        pos_logits_expanded = pos_logits.unsqueeze(2)
        neg_logits_expanded = neg_logits.unsqueeze(1)

        diff = pos_logits_expanded - neg_logits_expanded
        loss = -torch.mean(F.logsigmoid(diff))

        return loss

class TOP1LossNeg(nn.Module):
    def __init__(self):
        super(TOP1LossNeg, self).__init__()
    def forward(self, logit):
        diff = -(logit.diag().view(-1, 1).expand_as(logit) - logit)
        loss = torch.sigmoid(diff).mean() + torch.sigmoid(logit ** 2).mean()
        return loss