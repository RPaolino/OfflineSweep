# Introduction
Working on a cluster with no internet access can be challenging, since one cannot leverage the ``sweep`` feature provided by ``wandb``. This library is designed to enable the execution of wandb sweeps offline. It offers a straightforward approach to leveraging wandb syntax in an iterable format that facilitates offline execution. By adopting this solution, users can continue to harness the power of wandb, regardless of internet availability.

Moreover, the results can be upload with the command
```
wandb sync --sync-all
```

# Disclaimer
So far only the ``grid`` search method has been implemented.