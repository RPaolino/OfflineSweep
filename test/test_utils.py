import sys,os
import pytest

LIB_PATH = "/".join(os.path.abspath(__file__).split("/")[:-2])
sys.path.append(LIB_PATH)

from lib.utils import *

r'''
pytest test/test_utils.py
'''

expanded_dict = {
    'a': {
        'b': 1,
        'c': {
            'd': 2,
            'e':{
                'f': 3,
                'g': 4
            }
        }
    },
    'b': {
        'c': 5
    }
}

collapsed_dict = {
    'a.b': 1,
    'a.c.d': 2,
    'a.c.e.f': 3,
    'a.c.e.g': 4,
    'b.c': 5
}

# The following is both expanded and collapsed,
fixed_point = {
    'a': 1,
    'b': 2,
    'c': 3,
    'd': 4,
}
class TestIsCollapsed:
    r'''
        Test if the "is_collapsed" function has the expected behaviour.
        '''
    def test_1(self):
        assert not is_collapsed(expanded_dict)
    def test_2(self):
        assert is_collapsed(collapsed_dict)
    def test_3(self):
        assert not is_collapsed(fixed_point)

class TestEquals:  
    r'''
        Test if the "equals" function has the expected behaviour.
        '''    
    def test_1(self):
        assert equals(fixed_point, fixed_point)
    def test_2(self):
        assert not equals(expanded_dict, collapsed_dict)
    def test_3(self):
        assert equals(collapsed_dict, collapsed_dict)
    def test_4(self):
        assert equals(expanded_dict, expanded_dict)
    def test_5(self):
        assert not equals(expanded_dict, fixed_point)

class TestCollapse:          
    r'''
    Test if the "collapse" function has the expected behaviour.
    '''
    def test_1(self):
        assert equals(collapse(expanded_dict), collapsed_dict)
    def test_2(self):
        assert equals(collapse(collapsed_dict), collapsed_dict)
    def test_3(self):
        assert equals(collapse(fixed_point), fixed_point)

class TestKasKey: 
    r'''
        Test if the "has_key" function has the expected behaviour.
    '''      
    def test_1(self):
        assert has_key(fixed_point, "b")
    def test_2(self):
        assert has_key(collapsed_dict, "b.c")
    def test_3(self):
        assert not has_key(expanded_dict, "a")
    def test_4(self):
        assert has_key(expanded_dict, "b.c")
    def test_5(self):
        assert not has_key(collapsed_dict, "b.c.d")
    def test_6(self):
        assert not has_key(expanded_dict, "b.c.d")
    def test_7(self):
        assert not has_key(fixed_point, "b.c")
    
class TestCinsert:
    r'''
    Test if the "cinsert" function has the expected behaviour.
    '''
    def test_1(self):
        tmp = collapsed_dict.copy()
        tmp = cinsert(tmp, "i.j.k.l.m", 0)
        assert has_key(tmp, "i.j.k.l.m")
    def test_2(self):
        tmp = fixed_point.copy()
        tmp = cinsert(fixed_point, "i.j.k.l.m", 0)
        assert has_key(tmp, "i.j.k.l.m")
    def test_3(self):
        tmp = fixed_point.copy()
        tmp = cinsert(tmp, "i.j.k.l.m", 0)
        assert is_collapsed(tmp)

class TestEinsert:
    r'''
    Test if the "einsert" function has the expected behaviour.
    '''
    def test_1(self):
        tmp = expanded_dict.copy()
        tmp = einsert(tmp, "i.j.k.l.m", 0)
        assert has_key(tmp, "i.j.k.l.m")
        
class TestExpand:          
    r'''
    Test if the "collapse" function has the expected behaviour.
    '''
    def test_1(self):
        assert equals(expand(collapsed_dict), expanded_dict)
    def test_2(self):
        assert equals(expand(expanded_dict), expanded_dict)
    def test_3(self):
        assert equals(expand(fixed_point), fixed_point)