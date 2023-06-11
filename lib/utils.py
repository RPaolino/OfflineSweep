r'''
PRELIMINARIES
-------------
Since the sweep does not work in a machine with no internet access,
this library transform the sweep configuration in an iterable.

Suppose we have the (expanded) dict
ExpandedDict{
    'a': {
      'b': 3
      'c': 5
    }
  }
We call CollapsedDict the dictionary in which the keys are collapsed to a string, i.e.,
CollapsedDict = {
    'a.b': 3,
    'a.c': 5
  }
Hence 'a.b', 'a.c' will be referred as CollapsedKeys. 
The path will be referred as expanded_key.
'''

def collapse(Dict2Collapse={}, CollapsedKey="", CollapsedDict={}):
  r'''
  Given a nested dict of dicts, the function returns a collapsed dict
  dict whose nested keys are joined with a '.'.
  EXAMPLE
  -------
  Dict2Expand = {
    'a': {
      'b': 3
      'c': 5
    }
  }
  collapsedDict = {
    'a.b': 3,
    'a.c': 5
  }
  '''
  Dict2Collapse=Dict2Collapse.copy()
  CollapsedDict=CollapsedDict.copy()
  for key, value in Dict2Collapse.items():
    if type(value) is dict:
      r'''
      If the value is a dictionary, this must be collapsed as well. Hence, we get here a recursion.
      The key of the collapsed dict is then the concatenation of the collapsed key and the actual key.
      '''
      CollapsedDict = collapse(
        Dict2Collapse=value.copy(), 
        CollapsedKey=key if CollapsedKey=='' else CollapsedKey+f'.{key}', 
        CollapsedDict=CollapsedDict
      )
    else:
      r'''
      If the value is not a dictionary, we can set the value.
      '''
      if CollapsedKey=='':
        CollapsedDict[key]=value
      else:
        CollapsedDict[CollapsedKey+f'.{key}']=value
  return CollapsedDict

def is_collapsed(Dict2Check):
  r'''
  Check if a dict is in collapsed form. The function checks whether there is a nested dict AND whether one key has at least one '.'.
  CAVEAT: a simple dict {'a': 1, 'b': 1} is supposed to be in expanded form.
  '''
  nested=False
  key_w_dot=False
  for k, v in Dict2Check.items():
      if type(v) is dict:
        nested=True
      if  '.' in k:
        key_w_dot=True
  return ((not nested) and key_w_dot)

def equals(dict1, dict2, verbose=False):
  r'''
  Given two (possibly nested) dicts, check if they are equal. This means:
  1) both are collapsed (or expandend);
  2) both have same keys
  3) both have same values for the same key
  '''
  
  # Check if both are collapsed or expanded
  dict1_is_collapsed = is_collapsed(dict1)
  dict2_is_collapsed = is_collapsed(dict2)
  same_form = (dict1_is_collapsed == dict2_is_collapsed)
  
  # Equality is easier to check in collapsed form
  dict1_collapsed = collapse(dict1.copy())
  dict2_collapsed = collapse(dict2.copy())
  for key, value in dict1_collapsed.items():
    if key not in dict2_collapsed.keys():
      return False
    else:
      if value != dict2_collapsed[key]:
        return False
  return same_form

def has_key(InitialDict, CollapsedKey):
    r'''
    Check if CollapsedKey is in collapse(InitialDict).
    '''
    return (CollapsedKey in collapse(InitialDict.copy()))

def get_value(InitialDict, CollapsedKey):
    r'''
    Get the value of InitialDict corresponding to the key CollapsedKey.
    '''
    return collapse(InitialDict.copy())[CollapsedKey]


def cinsert(InitialDict, Key2Add, Value2Add=None):
    r'''
    Insert the collapsed Key2Add to a (collapsed) InitialDict. The corresponding value is Value2Add.
    '''
    CollapsedDict = collapse(InitialDict.copy())
    for key in CollapsedDict.keys():
        if key==Key2Add[:len(key)]:
          r'''
          If the dict has a key "a.b", we cannot insert "a.b.c", since this will overwrite "a.b" when expanded.
          For instance, suppose InitialDict = {"a.b": 1} and Key2Add="a.b.c", Value2Add="2".
          Then the final dict will have {"a.b": 1, "a.b.c": 2} which corresponds to the expanded {"b": 1} and {"b": {"c": 2}}.
          Hence, "b" would have to have 2 different values.
          '''
          raise AssertionError(f'Impossible to insert the key {Key2Add} because it would overwrite the key {key}.')
    CollapsedDict[Key2Add] = Value2Add
    return CollapsedDict.copy()
 

def einsert(InitialDict, Key2Add, Value2Add=None):
    r'''
    Useful to expand. Same behaviour as "cinsert". Useful to expand.
    '''
    keys = Key2Add.split(".")
    key_depth = len(keys)
    if key_depth==1:
      r'''
      If "keys" has length one, it means that the path has reached tha last node and
      we can set the value.
      '''
      if keys[0] not in InitialDict.keys():
          InitialDict[keys[0]]=Value2Add
          return InitialDict
    else:
      r'''
      If "keys" has length greater than one, it means that the path has not yet reached his final point.
      Therefore, we have to expand the rest of the path. This is the recursive step.
      '''
      if not has_key(InitialDict, ".".join(keys)):
        if keys[0] in InitialDict.keys():
          InitialDict[keys[0]]={**InitialDict[keys[0]], **einsert(InitialDict[keys[0]], ".".join(keys[1:]), Value2Add)}
        else:
          InitialDict[keys[0]]=einsert({}, ".".join(keys[1:]), Value2Add)
      return InitialDict

def expand(Dict2Expand, ExpandedDict={}):
    r'''
    Opposite of "collapse".
    EXAMPLE
    -------
    Dict2Expand = {
    'a.b': 3,
    'a.c': 5
    }
    ExpandedDict = {
    'a': {
        'b': 3
        'c': 5
    }
    }

    '''
    ExpandedDict=ExpandedDict.copy()
    for key, value in Dict2Expand.items():
        einsert(ExpandedDict, key, value)
    return ExpandedDict