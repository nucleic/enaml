# --------------------------------------------------------------------------------------
# Copyright (c) 2013-2025, Nucleic Development Team.
#
# Distributed under the terms of the Modified BSD License.
#
# The full license is in the file LICENSE, distributed with this software.
# --------------------------------------------------------------------------------------
"""
CallableRef - weak reference wrapper for callable objects.

This module provides a Python wrapper around the Rust CallableRef implementation
to ensure proper handling of *args/**kwargs in the __call__ method and to provide
identity caching.
"""

import weakref
from enaml._rust import CallableRef as _CallableRefImpl


class CallableRef:
    """Weak reference wrapper for callable objects.
    
    When the object is garbage collected, calling the ref returns None.
    Multiple CallableRef instances for the same object will return the same
    wrapper instance (identity semantics for caching).
    """
    
    __slots__ = ('_impl', '__weakref__')
    _cache = weakref.WeakKeyDictionary()
    
    def __new__(cls, *args, **kwargs):
        """Create or retrieve a cached CallableRef instance."""
        if not args:
            raise TypeError("CallableRef() missing required positional argument: 'obj'")
        
        obj = args[0]
        remaining_args = args[1:]
        
        # Check if we have a cached entry for this object
        if obj not in cls._cache:
            cls._cache[obj] = {}
        
        obj_cache = cls._cache[obj]
        cache_key = 'default'
        
        if cache_key not in obj_cache:
            # Create new instance using the Rust implementation
            instance = object.__new__(cls)
            instance._impl = _CallableRefImpl(obj, *remaining_args, **kwargs)
            obj_cache[cache_key] = instance
        
        return obj_cache[cache_key]
    
    def __call__(self, *args, **kwargs):
        """Forward calls to the underlying weak reference.
        
        This uses the Rust-implemented _call_with_args method which properly
        handles PyTuple and PyDict arguments.
        """
        # Call the Rust helper method with tuple and dict of arguments
        return self._impl._call_with_args(args, kwargs if kwargs else None)
    
    def __repr__(self):
        """String representation."""
        return self._impl.__repr__()
    
    def __eq__(self, other):
        """Comparison based on identity or weakref equality."""
        if isinstance(other, CallableRef):
            # Identity comparison for cached instances
            return self is other
        
        # Compare with Python weakref.ref objects
        try:
            import weakref as weakref_module
            if isinstance(other, weakref_module.ref):
                # Compare by dereferencing both weak references
                our_obj = self._impl._get_ref()
                other_obj = other()
                # If either is None, they're equal only if both are None
                if our_obj is None or other_obj is None:
                    return our_obj is other_obj
                # Otherwise, compare the actual objects
                return our_obj is other_obj
        except (ImportError, AttributeError):
            pass
        
        return NotImplemented
    
    def __ne__(self, other):
        """Inequality comparison."""
        result = self.__eq__(other)
        if result is NotImplemented:
            return result
        return not result
    
    def __hash__(self):
        """Hash based on object identity."""
        return hash(id(self))
    
    def __reduce__(self):
        """Raise TypeError - CallableRef cannot be pickled."""
        raise TypeError("cannot pickle 'CallableRef' object")


__all__ = ['CallableRef']
