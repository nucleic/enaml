Factory Func Example
===============================================================================

:download:`factory_func <../../../examples/layout/advanced/factory_func.enaml>`

::

    An example of using a factory function to generate constraints.
    
    This example shows how a function can be used as a delegate for generating
    the list of layout constraints. This mode of constraint generation is useful
    when the children of a container change dynamically at runtime. The factory
    will be invoked automatically whenever the internal layout engine determines
    that a relayout is necessary.

::

 $ enaml-run factory_func

.. image:: images/ex_factory_func.png

.. literalinclude:: ../../../examples/layout/advanced/factory_func.enaml
    :language: enaml

