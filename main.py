import argparse
import wandb
import tqdm
import torch
from torch_geometric.nn.models import GCN
from torch_geometric.datasets import Planetoid
from torch_geometric.transforms import NormalizeFeatures
import os

from lib.sweep_surrogate import *


sweep_config_grid = {
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


sweep_config_random = {
  'method': 'random',
  'name': 'sweep',
  'metric': {
      'goal': 'maximize',
      'name': 'val_acc'
  },
  'parameters': {
      "dataset": {"values": ["Cora", "Citeseer"]},
      "seed":{
          "mu": 1000,
          "sigma": 100,
          "q": 3
      },
      "num_epochs": {
          'values': [100, 200],
          'probabilities': [1/3, 2/3]
        },
      "GCN": {
          'parameters':{
            "hidden_channels": {
                'distribution': 'int_uniform',
                'min': 32,
                'max': 64,
            }, 
            "num_layers": {'value': 5},
            "dropout": {
                'min': 0.,
                'max': 1.
            }
          }
      },
      "optimizer": {
          "parameters": {
            "lr": {
                'min': 1e-3,
                'max': 1e-1
            },
            "weight_decay": {
                'min': 0,
                'max': 5e-3,
            }
          }
      }
  }
}


def main(config=None):
    
    with wandb.init(config=config):
        config = wandb.config
    
    torch.manual_seed(config["seed"])
    
    dataset = Planetoid(root='data/Planetoid', name=config["dataset"], transform=NormalizeFeatures())
    data = dataset[0]  # Get the first graph object.
    
    model = GCN(
        in_channels=dataset.num_features,
        out_channels=dataset.num_classes,
        **config["GCN"]
    )
    optimizer = torch.optim.Adam(model.parameters(), **config["optimizer"])
    criterion = torch.nn.CrossEntropyLoss()
    
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
    
    parser = argparse.ArgumentParser(description='SweepOffline')
    parser.add_argument('-n', type=int, default=float("inf"), dest="MAX_NUM_RANDOM_CONFIGS", help='The maximal number of random configs to sweep upon. (default inf)')
    parser.add_argument('-d', type=str, default="grid", dest="DEBUG", help='Debug: "grid" or "random". (default "grid")')

    options = vars(parser.parse_args())
    
    if options["DEBUG"]=="grid":
        sweep_config = sweep_config_grid
    elif options["DEBUG"]=="random":
        sweep_config = sweep_config_random
    else:
        assert False, f'{options["DEBUG"]} not implemented!'
    
    if sweep_config["method"]=="grid":
        configs, _ = Sweep2Iterable(sweep_config)
        for nconfig, (key, config) in enumerate(configs.items()):
            print(f'Config {nconfig+1}/{len(configs)}')
            #print(config)
            main(config)
    elif sweep_config["method"]=="random":
        DistributionSweep = Sweep2Distribution(sweep_config)
        print('Distribution Sweep', DistributionSweep)
        nconfig = 1
        while nconfig < options["MAX_NUM_RANDOM_CONFIGS"]:
            config = SampleAndExpand(DistributionSweep)
            print(f'Config {nconfig}/{options["MAX_NUM_RANDOM_CONFIGS"]}')
            #print(config)
            main(config)
            nconfig += 1