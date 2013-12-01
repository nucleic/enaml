Align Example
===============================================================================

:download:`align <../../../examples/layout/basic/align.enaml>`

::

    An example which demonstrates the use of the `align` layout helper.
    
    In this example, we use the `align` layout helper to align various
    constraints of the children of a container. The layout consists of
    a Field pinned to the top of the Container. Below the Field are two
    PushButtons each of which have their `left` boundary aligned. The
    top PushButton is then aligned with the `h_center` of the Field.

::

 $ enaml-run align

.. image:: images/ex_align.png

.. literalinclude:: ../../../examples/layout/basic/align.enaml
    :language: enaml

