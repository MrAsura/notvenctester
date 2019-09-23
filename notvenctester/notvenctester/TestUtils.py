"""
Provides functionality to help generate test scripts
"""

import re
import itertools as it
from enum import Enum, auto
from copy import deepcopy
from typing import List, Dict, Tuple, Any, Callable
from skvzTestInstance import skvzTestInstance
from shmTestInstance import shmTestInstance


##### Function templates/factories for filters and transformers #####
"""
Return filter function
"""
def filterFactory() -> Callable[..., bool]:
    pass

"""
Return transformer function
@param param_set_transformer: Take in <parameter_set_name>:<parameter_set_transformer_func> pairs. The transformer func should take in as parameters the whole parameter group and return the transformed parameter set value
@return function that takes in <parameter_set_name>:<parameter_set_value> pairs (i.e. the parameter group) and returns a the transformed parameter_group
"""
def transformerFactory(**param_set_transformers: Dict[str,Callable[...,Any]]) -> Callable[..., dict]:
    return (lambda **param_group: {p_set_name: param_set_transformers.get(p_set_name, lambda **pg: pg[p_set_name])(**param_group) for p_set_name in param_group.keys()})

"""
Define types for parameter sets that defines the behaviour of adding parameter sets
"""
class _ParamSetType(Enum):
    CONST = auto()
    MULTI = auto()

"""
Class for managing test parameters
    
Takes in parameter sets and generates parameter groups so that each possible parameter combination amongst the parameter sets exist 
"""
class TestParameterGroup:

    __round2 = lambda x,base=2: int(base*round(x/base))
    __strscale = lambda size,scale: "x".join(map(lambda x: str(__round2(int(x)*scale)),re.search("_*(\d+)x(\d+)[_.]*",size).group(1,2)))
    __seq_scale = lambda scale, st: (st[0], _strscale(st[1],scale), st[2])
    __ctc_seq_map = lambda scale, seq, mod: r"{}_{}_{}_{}.yuv".format( *__seq_scale(scale,re.search("(.+\\\\.+)_(\d+x\d+)_(\d+)[_.]",seq).group(1,2,3)), mod )


        
    def __init__(self) -> None:

        self._parameter_sets = {}
        self._parameter_groups = []
        self._filters = []
        self._transformer = lambda **in_param: in_param


    """
    Return the cartesian product of all the parameter sets
    @return A list of tuples where each tuple contains one item from each parameter set 
    """
    def _cartesian_product(*param_sets: List[Tuple[str,List[Any]]]) -> list:
        #Transform each parameter set to [...,(<set name>, <set param #n>),(<set name>, <set param #n+1>),...] etc.
        flat_param = [[(param_set_name, param) for param in param_list] for param_set_name, param_list in param_sets]
        return it.product(*flat_param)

    
    """
    Add Parameters of the given type
    """
    def _add_param(self, type: _ParamSetType, name_param: Dict[str,Any]) -> 'TestParameterGroup':

        for name, param_set in name_param.items():
            if name not in self._parameter_sets:
                self._parameter_sets[name] = (type, param_set)
            else:
                raise ValueError(f"Parameter set '{name}' already exists.")

        return self

    """
    Add new parameter set. Each value in the given param_set is used when generating parameter groups, so that all parameter set value combinations exist in the parameter groups
    @param name_param: take in any number of {name : param_set} pairs
    @return self
    """
    def add_param_set(self, **name_param) -> 'TestParameterGroup':
        return self._add_param(_ParamSetType.MULTI, name_param)

    """
    Add parameter shared by all parameter groups that contains only one value
    @name_param take in any number of {name : param} pairs
    @return self
    """
    def add_const_param(self, **name_param) -> 'TestParameterGroup':
        return self._add_param(_ParamSetType.CONST, name_param)

    """
    Filter out all parameter groups that satisfy the given filter
    @filter function that takes in as parameters all parameter sets and returns a boolean value
    """
    def filter_parameter_group(self, filter: Callable[..., bool]) -> 'TestParameterGroup':
        self._filters.append(filter)
        return self


    """
    Set function that is 
    @return self
    """
    def set_param_group_transformer(self, func: Callable[..., dict]) -> 'TestParameterGroup':
        self._transformer = func
        return self

    """
    Apply filters in self._filters to the given parameter group
    @param param_group contain one group of parameters to test
    @return true if param_group 
    """
    def _apply_filters(self, param_group):
        return all(filt(**param_group) for filt in self._filters)

    """
    Return list of dicts containing the parameter groups that have been added
    """
    def dump(self) -> List[dict]:
        #Generate parameter groups
        const_params = {name : val for (name, (_, val)) in filter(lambda p_set: p_set[1][0] == _ParamSetType.CONST, self._parameter_sets.items())}
        multi_params = [(name, val) for (name, (_, val)) in filter(lambda p_set: p_set[1][0] == _ParamSetType.MULTI, self._parameter_sets.items())]

        for m_param_group in TestParameterGroup._cartesian_product(*multi_params):
            self._parameter_groups.append(self._transformer(**const_params, **dict(m_param_group)))

        #Filter the parameter groups before returning
        return [group for group in self._parameter_groups if self._apply_filters(group)]

    """
    Return a list of skvzTestInstances
    """
    def to_skvz_test_instance(self) -> List[skvzTestInstance]:
        return [skvzTestInstance(**param) for param in self.dump()]

    """
    Return a list of shmTestInstances
    """
    def to_shm_test_instance(self) -> List[shmTestInstance]:
        return [shmTestInstance(**param) for param in self.dump()]

    """
    Return a deep copy the parameter group
    """
    def copy(self) -> 'TestParameterGroup':
        new_pg = TestParameterGroup()
        new_pg._parameter_sets = deepcopy(self._parameter_sets)
        new_pg._parameter_groups = deepcopy(self._parameter_groups)
        new_pg._filters = deepcopy(self._filters)
        new_pg._transformer = deepcopy(self._transformer)
        return new_pg
