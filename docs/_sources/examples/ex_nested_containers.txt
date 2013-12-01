Nested Containers Example
===============================================================================

:download:`nested_containers <../../../examples/layout/advanced/nested_containers.enaml>`

::

    An example showing the unified layout across nested Containers.
    
    There are three Containers under the window, two sharing space on top and
    one taking up the entire horizontal space on the bottom. The two on top
    simply consist of a Label and a Field. The Container on the left is
    constrained to be slightly larger than the other by a constant multiplier.
    
    The Container on the bottom contains the more complicated example from
    `fluid.enaml` to demonstrate that a complicated layout works inside
    a nested Container, too.

::

 $ enaml-run nested_containers

.. image:: images/ex_nested_containers.png

.. literalinclude:: ../../../examples/layout/advanced/nested_containers.enaml
    :language: enaml

