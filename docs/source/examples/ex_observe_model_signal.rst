Observe Model Signal Example
===============================================================================

:download:`observe_model_signal <../../../examples/functions/observe_model_signal.enaml>`

::

    An example which demonstrates how to observe a model signal.
    
    This examples uses a model with a signal to notify listeners about in
    place changes to a list. This pattern is interesting for the times when
    a ContainerList would emit too many synchronous notifications. A common
    example is reordering the elements in a list.

::

 $ enaml-run observe_model_signal

.. image:: images/ex_observe_model_signal.png

.. literalinclude:: ../../../examples/functions/observe_model_signal.enaml
    :language: enaml

