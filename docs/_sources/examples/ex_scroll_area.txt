Scroll Area Example
===============================================================================

:download:`scroll_area <../../../examples/widgets/scroll_area.enaml>`

::

    An example of the `ScrollArea` widget.
    
    A `ScrollArea` can have at most one child which must be an instance of
    `Container`. When to show the scroll bars is determined automatically
    based on the sizing constraints of the `Container`. However, that
    policy can be changed through the attributes 'horizontal_scrollbar' and
    'vertical_scrollbar'. These attributes can be set to 'as_needed',
    'always_on', and 'always_off'. The default is 'as_needed'.

::

 $ enaml-run scroll_area

.. image:: images/ex_scroll_area.png

.. literalinclude:: ../../../examples/widgets/scroll_area.enaml
    :language: enaml

