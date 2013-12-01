Advanced Example
===============================================================================

:download:`advanced <../../../examples/templates/advanced.enaml>`

::

    An advanced example of Enaml templates.
    
    This example shows how Enaml templates can be used to automatically
    generate the body of a form. Template specialization is used to select
    the proper control for a model attribute at runtime. Template recursion
    is then used to unroll a list of these controls into the body of a form.

::

 $ enaml-run advanced

.. image:: images/ex_advanced.png

.. literalinclude:: ../../../examples/templates/advanced.enaml
    :language: enaml

