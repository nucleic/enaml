.. _developer_notes:

Developer notes
================

These notes are meant to help developers and contributors with regards to some
details of the implementation and coding style of the project.

Python codebase
---------------

The Python codebase currently targets Python 3.6+, strives to follow PEP 8 and
uses Numpy style docstring.


Python C++ bindings
-------------------

The bindings are hand-written and relies on cppy (https://github.com/nucleic/cppy).
Enaml tries to use a reasonably modern C API and to support sub-interpreter,
this has a couple of consequences:

- static variables use is limited to cases that cannot lead to state leakage
  between multiple sub-interpreters. Note that this is currently not heavily
  tested and may require some improvements.
- all the non exported symbol are enclosed in anonymous namespaces
- enaml does not use static types and only dynamical types (note that the
  type slots and related structures are stored in a static variable)
- modules use the multi-phases initialization mechanism as defined in
  PEP 489 -- Multi-phase extension module initialization
