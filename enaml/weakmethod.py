# --------------------------------------------------------------------------------------
# Copyright (c) 2013-2025, Nucleic Development Team.
#
# Distributed under the terms of the Modified BSD License.
#
# The full license is in the file LICENSE, distributed with this software.
# --------------------------------------------------------------------------------------
"""
WeakMethod - weak reference wrapper for bound methods with identity caching.

This module provides the WeakMethod class which wraps bound methods as weak references,
allowing them to be collected when the object is garbage collected. Multiple calls to
WeakMethod with the same bound method will return the same WeakMethod instance
(identity semantics for caching).
"""

import gc
import inspect
import weakref
from enaml._rust import WeakMethod as _WeakMethodImpl


class WeakMethod:
    """Weak reference wrapper for bound methods with identity caching.
    
    Multiple calls to WeakMethod with the same bound method will return
    the same WeakMethod instance (identity semantics for caching).
    """
    
    __slots__ = ('_impl', '__weakref__')
    _cache = weakref.WeakKeyDictionary()
    
    def __new__(cls, *args, **kwargs):
        """Create or retrieve a cached WeakMethod instance."""
        # Handle various argument combinations with proper error messages
        if not args:
            if kwargs:
                kwarg_names = ', '.join(kwargs.keys())
                raise TypeError(
                    f"WeakMethod() got unexpected keyword argument(s): {kwarg_names}"
                )
            raise TypeError("WeakMethod() takes 1 argument but 0 were given")
        
        if len(args) > 1:
            raise TypeError(f"WeakMethod() takes 1 argument but {len(args)} were given")
        
        if kwargs:
            kwarg_names = ', '.join(kwargs.keys())
            raise TypeError(
                f"WeakMethod() got unexpected keyword argument(s): {kwarg_names}"
            )
        
        method = args[0]
        
        # Validate that we have a bound method
        if not inspect.ismethod(method):
            # Get the actual type for error message
            actual_type = type(method).__name__
            raise TypeError(
                f"WeakMethod() argument must be a MethodType, not {actual_type}"
            )
        
        # Get the object that the method is bound to
        obj = method.__self__
        method_name = method.__name__
        
        # Check if we have a cached entry for this object
        if obj not in cls._cache:
            cls._cache[obj] = {}
        
        method_cache = cls._cache[obj]
        
        # Check if we've already created a WeakMethod for this method
        cache_key = method_name
        if cache_key not in method_cache:
            # Create new instance using the Rust implementation
            instance = object.__new__(cls)
            instance._impl = _WeakMethodImpl(method)
            method_cache[cache_key] = instance
        
        return method_cache[cache_key]
    
    def __call__(self, *args, **kwargs):
        """Forward calls to the underlying weak reference.
        
        This uses the Rust-implemented _call_with_args method which properly
        handles PyTuple and PyDict arguments.
        """
        # Call the Rust helper method with tuple and dict of arguments
        return self._impl._call_with_args(args, kwargs if kwargs else None)
    
    def __get__(self, obj, objtype=None):
        """Descriptor protocol support."""
        return self._impl.__get__(obj, objtype)
    
    def __repr__(self):
        """String representation."""
        return self._impl.__repr__()
    
    def __reduce__(self):
        """Raise TypeError - WeakMethod cannot be pickled."""
        raise TypeError("cannot pickle 'WeakMethod' object")


__all__ = ['WeakMethod']
