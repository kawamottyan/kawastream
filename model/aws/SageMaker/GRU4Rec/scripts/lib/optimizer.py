import torch.optim as optim

class Optimizer:
    def __init__(self, params, optimizer_type, lr, weight_decay):
        if optimizer_type == 'Adagrad':
            self.optimizer = optim.Adagrad(params, lr=lr, weight_decay=weight_decay)
        else:
            raise NotImplementedError

    def zero_grad(self):
        self.optimizer.zero_grad()

    def step(self):
        self.optimizer.step()