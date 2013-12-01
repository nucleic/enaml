Vbox Example
===============================================================================

:download:`vbox <../../../examples/layout/basic/vbox.enaml>`

::

    An example which demonstrates the use of the `vbox` layout helper.
    
    In this example, we use the `vbox` layout helper to layout the children
    of the Container in a vertical group. The `vbox` function is a fairly
    sophisticated layout helper which automatically takes into account the
    content boundaries of its parent. It also provides the necessary layout
    spacers in the horizontal direction to allow for children of various
    widths.

::

 $ enaml-run vbox

.. image:: images/ex_vbox.png

.. literalinclude:: ../../../examples/layout/basic/vbox.enaml
    :language: enaml

