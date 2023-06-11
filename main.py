from lib.sweep_surrogate import *
import wandb
import tqdm
import torch
from torch_geometric.nn.models import GCN
from torch_geometric.datasets import Planetoid
from torch_geometric.transforms import NormalizeFeatures
import os

sweep_config = {
  'method': 'grid',
  'name': 'sweep',
  'metric': {
      'goal': 'maximize',
      'name': 'val_acc'
  },
  'parameters': {
      "dataset": {"values": ["Cora", "Citeseer"]},
      "num_epochs": {'values': [100]},
      "GCN": {
          'parameters':{
            "hidden_channels": {'values': [32, 64]}, 
            "num_layers": {'values': [5]}
          }
      },
      "optimizer": {
          "parameters": {
            "lr": {'values':   [1e-2, 1e-3]},
            "weight_decay": {'values': [5e-3]}
          }
      }
  }
}


def main(config=None):
    
    with wandb.init(config=config):
        config = wandb.config
    
    dataset = Planetoid(root='data/Planetoid', name=config["dataset"], transform=NormalizeFeatures())
    data = dataset[0]  # Get the first graph object.
    
    model = GCN(
        in_channels=dataset.num_features,
        out_channels=dataset.num_classes,
        **config["GCN"]
    )
    optimizer = torch.optim.Adam(model.parameters(), **config["optimizer"])
    criterion = torch.nn.CrossEntropyLoss()

    def train():
        
        return loss
    
    progress = tqdm.trange(1, config["num_epochs"]+1) 
    for epoch in progress:
        model.train()
        optimizer.zero_grad()  # Clear gradients.
        out = model(data.x, data.edge_index)  # Perform a single forward pass.
        loss = criterion(out[data.train_mask], data.y[data.train_mask])  # Compute the loss solely based on the training nodes.
        loss.backward()  # Derive gradients.
        optimizer.step()  # Update parameters based on gradients.
        progress.set_description(f'Epoch: {epoch:03d}, loss.train: {loss:.4f}')
        
    wandb.finish()
    
if __name__=="__main__":
    os.environ["WANDB_MODE"]='offline'
    os.environ["WANDB_SILENT"] = "true"
    configs, _ = Sweep2Iterable(sweep_config)
    for nconfig, (key, config) in enumerate(configs.items()):
        print(f'Config {nconfig+1}/{len(configs)}')
        main(config)