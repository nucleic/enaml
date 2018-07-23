Dates Example
===============================================================================

:download:`dates <../../../examples/widgets/dates.enaml>`

::

    An example demonstrating a number of date-related widgets:
    `datetime_selector`, `date_selector`, `time_selector` and `calendar`.

    There are several different widgets that can be used to enter a date and/or
    time. This example shows each of them in use, motivated by a glib
    "personality assessment" based on the data the user entered.

    The `datetime_selector`, `date_selector`, `time_selector` widgets each
    return an instance of the corresponding `datetime` class. Each them them
    collects the information in a visually compact manner.

    In contrast, the `calendar` widget gives a larger, month-by-month display
    of the dates, for the user to select.

::

 $ enaml-run dates

.. image:: images/ex_dates.png

.. literalinclude:: ../../../examples/widgets/dates.enaml
    :language: enaml

