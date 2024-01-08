import torch

class Predictiton(object):
    def __init__(self, model, item_map, session_key, item_key, time_key, item_idx):
        self.model = model
        self.device = model.device
        self.item_map = item_map
        self.session_key = session_key
        self.item_key = item_key
        self.time_key = time_key
        self.item_idx = item_idx

    def predict(self, input_data):
        predictions = []

        input_data_sorted = input_data.sort_values(by=self.time_key)
        item_map_indexed = self.item_map.set_index(self.item_key)

        batchSize = 1
        hidden = self.model.init_hidden(batchSize)

        with torch.no_grad():
            for item_id in input_data_sorted[self.item_key]:
                if item_id in item_map_indexed.index:
                    item_idx = item_map_indexed.loc[item_id, self.item_idx]
                    input_tensor = torch.LongTensor([item_idx]).to(self.device)

                    logit, hidden = self.model(input_tensor, hidden)
                    predictions.append(logit.cpu().numpy())

            return predictions[-1].flatten()