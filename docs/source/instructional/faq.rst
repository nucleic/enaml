Help and Troubleshooting
===============================================================================

.. _FAQ:

FAQ's
-------------------------------------------------------------------------------

All of a sudden, |Enaml| quit compiling, what happened?
+++++++++++++++++++++++++++++++++++++++++++++++++++++++

Did you just use EPD or enpkg to install or update your Python distribution? If
so, it's possible one or more of the |Enaml| :ref:`dependencies` got bumped
out. Try running ``python setup.py install`` or ``python setup.py develop`` in
the packages |Enaml| needs if they are not included in your distrubtion. For
example, ``casuarius`` is necessary for |Enaml| but not included in the EPD
during beta development of |Enaml| (because ``casuarius`` is also under
development.)
