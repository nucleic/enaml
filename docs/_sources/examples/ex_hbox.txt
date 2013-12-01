Hbox Example
===============================================================================

:download:`hbox <../../../examples/layout/basic/hbox.enaml>`

::

    An example which demonstrates the use of the `hbox` layout helper.
    
    In this example, we use the `hbox` layout helper to layout the children
    of the Container in a horizontal group. The `hbox` function is a fairly
    sophisticated layout helper which automatically takes into account the
    content boundaries of its parent. It also provides the necessary layout
    spacers in the vertical direction to allow for children of various
    heights.
    
    In this example, all widgets have same native height so there is no need
    for extra alignment constraints in the vertical direction. PushButtons
    expand freely in width by default, so when the Window is expanded, one
    of the PushButtons will be expanded to fill. The particular PushButton
    which is chosen to expand is nondeterministic. To force are particular
    choice would require extra constraints to be defined on the buttons.
    That extra specification is deliberately omitted in this example.

::

 $ enaml-run hbox

.. image:: images/ex_hbox.png

.. literalinclude:: ../../../examples/layout/basic/hbox.enaml
    :language: enaml

