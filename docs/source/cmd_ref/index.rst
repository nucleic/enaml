.. _cmd_ref:

=================
Command Reference
=================

Enaml makes the following console scripts available

enaml-run
---------

A shortcut which will run an enaml file using the default QtApplication. This
can be used to display most of the examples as follows (assuming you are at the
root of the repo)::

    $ enaml-run examples/widgets/window.enaml

By default the script will look for a component (`enamldef` class) named `Main`
to display. One can use the `-c` (`--component`) option to use a different
name.


enaml-compileall
----------------

An extension to the builtin `compileall` module which generates cache files for
both .py and .enaml files. It's usage is the same as python's `compileall`_.

.. _compileall: https://docs.python.org/3.7/library/compileall.html
