import itertools
from lib.utils import *

r'''
Transforming the sweep into an iterable
'''

def Sweep2Iterable(sweep_config, verbose=False):
    r'''
    From a dictionary written in wandb sintax, return a dictionary with
    all possible configs to sweep.
    '''
    CollapsedDict = {}
    CollapsedDict = collapse(sweep_config.copy()).copy()
    
    #Removing "parameter" and "values"/"value"
    CleanedCollapsedDict = {}
    Keys2Sweep=[]
    for key, value in CollapsedDict.items():
        key = key.replace("parameters.", "")
        if "values" in key:
          key = key.replace(".values", "")
          if len(value)>1:
            Keys2Sweep.append(key)
          else:
            value=value[0]
        key = key.replace(".value", "")
        CleanedCollapsedDict[key]=value
    
    #Considering only the keys that requires sweeping
    Dict2Product={k:v for k, v in CleanedCollapsedDict.items() if k in Keys2Sweep}
    FixedDict = {k:v for k, v in CleanedCollapsedDict.items() if k not in Keys2Sweep}
    
    #Computing the grid (aka cartesian product)
    Configs2CartesianProduct = {}
    for num_config, (values) in enumerate(itertools.product(*list(Dict2Product.values()))):
        Configs2CartesianProduct[num_config] = {k:v for k,v in zip(Dict2Product.keys(), values)}
    
    #Adding back the keys that do not require sweeping
    for config_k, config_v in Configs2CartesianProduct.items():
      Configs2CartesianProduct[config_k]={**config_v, **FixedDict}
    
    #Expanding the config in wandb sintax
    Configs2Iterable={}
    for key, config in Configs2CartesianProduct.items():
        Configs2Iterable[key]=expand(config)

    return Configs2Iterable, Keys2Sweep
