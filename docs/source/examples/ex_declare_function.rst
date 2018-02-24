Declare Function Example
===============================================================================

:download:`declare_function <../../../examples/functions/declare_function.enaml>`

::

    An example which demonstrates the use of the `func` keyword.
    
    Code in the body of the function has access to the same scope as a bound
    expression. This consists of an implicity `self` which resolves to the
    object on which the function was declared, as well as the identifiers
    declared in the enclosing `enamldef` block. It also has access to the
    dynamic scope which is rooted on `self`.

::

 $ enaml-run declare_function

.. image:: images/ex_declare_function.png

.. literalinclude:: ../../../examples/functions/declare_function.enaml
    :language: enaml

