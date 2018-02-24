Override Layout Constraints Example
===============================================================================

:download:`override_layout_constraints <../../../examples/layout/advanced/override_layout_constraints.enaml>`

::

    An example which demonstrates overriding `layout_constraints`.
    
    This example shows how one can override `layout_constraints` method from
    enaml syntax to generate custom constraints using procedural code. This
    can be useful for complex layout scenarios where generating constraints
    from a single expression would be difficult or impossible.

::

 $ enaml-run override_layout_constraints

.. image:: images/ex_override_layout_constraints.png

.. literalinclude:: ../../../examples/layout/advanced/override_layout_constraints.enaml
    :language: enaml

