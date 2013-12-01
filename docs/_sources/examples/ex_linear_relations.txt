Linear Relations Example
===============================================================================

:download:`linear_relations <../../../examples/layout/basic/linear_relations.enaml>`

::

    An example which demonstrates linear relational constraints.
    
    This example shows how one may define a constraint as a linear relation
    of some other constraint. In this example, the horizontal position and
    width of a `PushButton` depends up the width of the `Container`, and the
    vertical position of another `PushButton` depends upon the width of the
    other `PushButton`.
    
    This is a contrieved example, but serves to demonstrate the feature.

::

 $ enaml-run linear_relations

.. image:: images/ex_linear_relations.png

.. literalinclude:: ../../../examples/layout/basic/linear_relations.enaml
    :language: enaml

