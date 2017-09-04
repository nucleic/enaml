# -*- coding: utf-8 -*-
"""
Created on Sat Jul  1 19:14:52 2017

@author: Marül
"""
import dis
from enaml.c_compat import _fix_co_filename

print(_fix_co_filename.__doc__)

def f():
    a = [i for i in range(10)]

dis.dis(f)
print(f.__code__.co_filename)
_fix_co_filename(f.__code__, 'test')

dis.dis(f)
print(f.__code__.co_filename)

#_fix_co_filename(None, None)
#_fix_co_filename(f.__code__, None)
