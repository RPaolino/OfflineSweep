# Table of Contents
+ [Motivation](#motivation)
+ [How to Use](#how-to-use)
+ [Disclaimer](#disclaimer)
+ [Star the Project](#star-the-project)

# Motivation
Working on a cluster with no internet access can be challenging, since one cannot leverage the ``sweep`` feature provided by ``wandb``. This library is designed to enable the execution of wandb sweeps offline. It offers a straightforward approach to leveraging wandb syntax in an iterable format that facilitates offline execution. By adopting this solution, users can continue to harness the power of wandb, regardless of internet availability.

Moreover, the results can be uploaded with the command
```
wandb sync --sync-all
```

# How to Use
Clone the repository as
```
git clone git@github.com:RPaolino/OfflineSweep.git
```
Copy the files in ``lib`` to your current project. Import ``lib.sweep_surrogate`` in your main and use
```
configs, _ = Sweep2Iterable(sweep_config)
for key, config in enumerate(configs.items()):
    main(config)
```
for a grid search. The function ``Sweep2Iterable`` returns a dictionary with all possible configurations, while the ``for`` loop iterates over them.

For a random search, the setting is a bit different, since we want to be able to try as many configs as possible.
```
DistributionSweep = Sweep2Distribution(sweep_config)
nconfig = 1
while nconfig < options["MAX_NUM_RANDOM_CONFIGS"]:
    config = SampleAndExpand(DistributionSweep)
    main(config)
    nconfig += 1
```
We first generate a ``DistributionSweep`` dictionary. In such dictionary, every hyperparameter is a random variable that is sampled on the fly in the ``while`` statement. You can specify a maximal number of random configurations to try. Otherwise, you can let the code run freely setting ``MAX_NUM_RANDOM_CONFIGS = float("inf")``: in this way, you can stop it manually whenever you feel.

If you are unsure, the ``main.py`` should clarify your doubts.

# Disclaimer
So far only the ``grid`` and ``random`` search method have been implemented. If you experience any bug, please let me know!


# Star the Project
If you like this project, don't forget to give it a ✫