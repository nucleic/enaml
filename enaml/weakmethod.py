# --------------------------------------------------------------------------------------
# Copyright (c) 2013-2025, Nucleic Development Team.
#
# Distributed under the terms of the Modified BSD License.
#
# The full license is in the file LICENSE, distributed with this software.
# --------------------------------------------------------------------------------------
"""
WeakMethod - weak reference wrapper for bound methods.

This module provides identity caching for WeakMethod instances to ensure
that the same bound method always returns the same wrapper instance.
"""

import weakref
from enaml._rust import WeakMethod as _WeakMethod

# Cache for WeakMethod instances using weak values to allow garbage collection
_cache = weakref.WeakValueDictionary()


def WeakMethod(method, callback=None):
    """Create or retrieve a cached WeakMethod instance.
    
    This factory function ensures that the same bound method always returns
    the same WeakMethod instance (identity caching).
    
    Parameters
    ----------
    method : method
        The bound method to wrap with a weak reference.
    callback : callable, optional
        Optional callback to invoke when the weak reference dies.
    
    Returns
    -------
    WeakMethod
        A cached WeakMethod instance wrapping the bound method.
    """
    # Use the method's id as cache key
    method_id = id(method)
    
    # Check if we already have a cached instance
    if method_id in _cache:
        return _cache[method_id]
    
    # Create new instance and cache it
    instance = _WeakMethod(method, callback)
    _cache[method_id] = instance
    return instance


__all__ = ['WeakMethod']



