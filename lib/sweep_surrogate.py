import itertools
import numpy as np
from lib.utils import *
import lib.custom_rvs as crv

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


def Sweep2Distribution(sweep_config):
    r'''
    From a dictionary written in wandb sintax, return one dictionary with
    values as rvs. that will be sampled on the flight.
    '''
    CollapsedDict = {}
    CollapsedDict = collapse(sweep_config.copy()).copy()
    
    #Creating a new dict where each element is a distribution
    CleanedCollapsedDict = {}    
    
    #Make all default values explicit
    CollapsedDictWDefault = CollapsedDict.copy()
    for key, value in CollapsedDict.items():
      if "parameters" in key[:10]:
        ParentKey =".".join(key.split(".")[:-1])
        KeysWSameParentIdx = [ParentKey in k for k in CollapsedDict.keys()]
        KeysWSameParent = np.array(list(CollapsedDict.keys()))[KeysWSameParentIdx]
        DistributionKeyIsPresent = ["distribution" in k for k in KeysWSameParent]
        if np.sum(DistributionKeyIsPresent)==0:
          if np.sum([(("value" in k) and not ("values" in k)) for k in KeysWSameParent]):
            CollapsedDictWDefault[f'{ParentKey}.distribution'] = "constant"
          elif np.sum(["values" in k for k in KeysWSameParent]):
            CollapsedDictWDefault[f'{ParentKey}.distribution'] = "categorical"
          elif np.sum([(("min" in k) or ("max" in k)) for k in KeysWSameParent]):
            if np.sum(["q" in k for k in KeysWSameParent]):
              CollapsedDictWDefault[f'{ParentKey}.distribution'] = "q_uniform"
            else:
              CollapsedDictWDefault[f'{ParentKey}.distribution'] = "uniform"
          elif np.sum([(("mu" in k) or ("sigma" in k)) for k in KeysWSameParent]):
            if np.sum(["q" in k for k in KeysWSameParent]):
              CollapsedDictWDefault[f'{ParentKey}.distribution'] = "normal"
            else:
              CollapsedDictWDefault[f'{ParentKey}.distribution'] = "normal"
      else:
        CleanedCollapsedDict[key] = value    
    
    #Since we added the "distribution" before, we can consider only the keys that have "distribution" as a substring
    for key, value in CollapsedDictWDefault.items():
        if "distribution" in key[-12:]:
          ParentKey =".".join(key.split(".")[:-1])
          if value in ["normal", "log_normal", "q_normal", "q_log_normal"]:
            if ParentKey+f'.mu' in CollapsedDictWDefault.keys():
              mu = CollapsedDictWDefault[ParentKey+f'.mu']
            else:
              mu=0.
            if ParentKey+f'.sigma' in CollapsedDictWDefault.keys():
              sigma = CollapsedDictWDefault[ParentKey+f'.sigma']
            else:
              sigma=1.
            if ParentKey+f'.q' in CollapsedDictWDefault.keys():
              q = CollapsedDictWDefault[ParentKey+f'.q']
            else:
              q=1.
            if value in ["normal", "log_normal"]:
              distribution = getattr(crv, value)(mean=mu, sigma=sigma)
            else:
              distribution = getattr(crv, value)(mean=mu, sigma=sigma, q=q)
          elif value in ["uniform", "int_uniform", "log_uniform", "q_uniform", "q_log_uniform"]:
            if ParentKey+f'.min' in CollapsedDictWDefault.keys():
              min = CollapsedDictWDefault[ParentKey+f'.min']
            else:
              min=0
            if ParentKey+f'.max' in CollapsedDictWDefault.keys():
              max = CollapsedDictWDefault[ParentKey+f'.max']
            else:
              max=1
            if ParentKey+f'.q' in CollapsedDictWDefault.keys():
              q = CollapsedDictWDefault[ParentKey+f'.q']
            else:
              q=1
            if value in ["uniform"]:
              distribution = getattr(crv, "uniform")(low=min, high=max)
            elif value in ["int_uniform"]:
              distribution = getattr(crv, "int_uniform")(low=min, high=max+1)
            elif value in ["log_uniform"]:
              distribution = getattr(crv, value)(low=min, high=max+1)
            elif value in ["q_uniform", "q_log_uniform"]:
              distribution = getattr(crv, value)(low=min, high=max+1, q=q)
          elif value in ["constant"]:
            k = CollapsedDictWDefault[ParentKey+f'.value']
            distribution = getattr(crv, "constant")(k=k)
          elif value in ["categorical"]:
            support = CollapsedDictWDefault[ParentKey+f'.values']
            if ParentKey+f'.probabilities' in CollapsedDictWDefault.keys():
              probs = CollapsedDictWDefault[ParentKey+f'.probabilities']
            else:
              probs = np.ones(len(support))/len(support)
            distribution = getattr(crv, "categorical")(support=support, probs=probs)
          
          ParentKey = ParentKey.replace("parameters.", "")
          ParentKey = ParentKey.replace(".values", "")
          ParentKey = ParentKey.replace(".value", "")
          CleanedCollapsedDict[ParentKey]=distribution

    return CleanedCollapsedDict
  
def SampleAndExpand(DistributionDict):
  config = DistributionDict.copy()
  for key, value in DistributionDict.items():
    if hasattr(value, "rvs"):
      config[key] = value.rvs()[0]
  config=expand(config)
  return config