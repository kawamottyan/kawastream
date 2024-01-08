import torch
import torch.nn as nn

class GRU4REC(nn.Module):
    def __init__(self, input_size, output_size, hidden_size, num_layers, dropout_hidden, dropout_input, embedding_dim, final_act, batch_size, use_cuda):
        super(GRU4REC, self).__init__()
        self.input_size = input_size
        self.hidden_size = hidden_size
        self.output_size = output_size
        self.num_layers = num_layers
        self.dropout_hidden = dropout_hidden
        self.dropout_input = dropout_input
        self.embedding_dim = embedding_dim
        self.batch_size = batch_size
        self.use_cuda = use_cuda
        self.device = torch.device('cuda' if use_cuda else 'cpu')
        self.onehot_buffer = self.init_emb()
        self.h2o = nn.Linear(hidden_size, output_size)
        self.create_final_activation(final_act)
        if self.embedding_dim != -1:
            self.look_up = nn.Embedding(input_size, self.embedding_dim)
            self.gru = nn.GRU(self.embedding_dim, self.hidden_size, self.num_layers, dropout=self.dropout_hidden)
        else:
            self.gru = nn.GRU(self.input_size, self.hidden_size, self.num_layers, dropout=self.dropout_hidden)
        self = self.to(self.device)

    def create_final_activation(self, final_act):
        if final_act == 'tanh':
            self.final_activation = nn.Tanh()
        else:
            raise NotImplementedError

    def forward(self, input, hidden):
        if self.embedding_dim == -1:
            embedded = self.onehot_encode(input)
            if self.training and self.dropout_input > 0: embedded = self.embedding_dropout(embedded)
            embedded = embedded.unsqueeze(0)
        else:
            embedded = input.unsqueeze(0)
            embedded = self.look_up(embedded)

        output, hidden = self.gru(embedded, hidden)
        output = output.view(-1, output.size(-1))
        logit = self.final_activation(self.h2o(output))

        return logit, hidden

    def init_emb(self):
        onehot_buffer = torch.FloatTensor(self.batch_size, self.output_size)
        onehot_buffer = onehot_buffer.to(self.device)
        return onehot_buffer

    def onehot_encode(self, input):
        self.onehot_buffer.zero_()
        index = input.view(-1, 1)
        one_hot = self.onehot_buffer.scatter_(1, index, 1)
        return one_hot

    def embedding_dropout(self, input):
        p_drop = torch.Tensor(input.size(0), 1).fill_(1 - self.dropout_input)
        mask = torch.bernoulli(p_drop).expand_as(input) / (1 - self.dropout_input)
        mask = mask.to(self.device)
        input = input * mask
        return input

    def init_hidden(self, batch_size=None):
        if batch_size is None:
            batch_size = self.batch_size
        try:
            h0 = torch.zeros(self.num_layers, batch_size, self.hidden_size).to(self.device)
        except:
            self.device = 'cpu'
            h0 = torch.zeros(self.num_layers, batch_size, self.hidden_size).to(self.device)
        return h0