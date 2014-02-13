Hbox Equal Widths Example
===============================================================================

:download:`hbox_equal_widths <../../../examples/layout/basic/hbox_equal_widths.enaml>`

::

    An example of the `hbox` layout helper with auxiliary constraints.
    
    This example is nearly identical to the `hbox.enaml` example. However,
    this time we add some auxiliary constraints to make the buttons equal
    widths. When resizing the window, each button is therefore guaranteed
    to expand by the same amount.

::

 $ enaml-run hbox_equal_widths

.. image:: images/ex_hbox_equal_widths.png

.. literalinclude:: ../../../examples/layout/basic/hbox_equal_widths.enaml
    :language: enaml

