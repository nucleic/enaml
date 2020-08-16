.. _syntax:

============================
Enaml syntax and Data Models
============================


Enaml defines a superset of the Python language, which means that any valid
Python code is valid in an enaml file, including function and class definitions.
The following sections present the extension provided by Enaml to declare views
and bind it to a model.

.. note::

    Just like in any Python file, you need to import the definitions of the
    objects you use. One minor difference between standard Python files and
    Enaml files is that inside an enaml file you do not need to use the
    `enaml.imports()` context manager when importing objects defined in an
    Enaml file.

Enamldef syntax
---------------

To define a view element, one uses the `enamldef` keyword in a way similar to
the `class` keyword in a normal Python file. Your widget must inherit from
a widget, either a builtin one or one defined using an `enamldef` and cannot
inherit from several widgets.

In the body of the declaration, you add widget by simply declaring it. The
parent/child is directly encoded in the indentation. Furthermore, you can
add to each widget an id which must unique inside the declaration. This id
can be used to reference it in the layout (see :ref:`layout`), or to access
one of its attribute.

.. code-block:: enaml

    enamldef MyWindow(Window):

        Container: cont:

            Field: field:
                pass


Defining attributes and aliases
-------------------------------

When defining a widget using the `enamldef` keyword, one can add custom
attributes to the widget using the `attr` keyword. Furthermore, you can enforce
type validation using the following syntax.

.. code-block:: enaml

    attr my_attr : set = {1, 2, 3}

.. note::

    One can specify a default value using `=` even if no type validation is
    specified.

One can also define the equivalent of atom.Event, that is to say an attribute
that does not store the value it is assigned but simply fires a notification
each time it is assigned a value. To do so, simply replace the `attr` keyword
with the `event` keyword. Type validation works in the same way as for regular
`attr` defined attributes.

Additionally, one can define an attribute that simply allows access to a child widget
or a child widget attribute in a transparent way using the `alias`
keyword. The syntax is presented below.

.. code-block:: enaml

    enamldef MyWindow(Window):

        alias child_widget : cont

        alias child_widget_attr : field.text

        Container: cont:
            Field: field:
                pass

.. note::

    To avoid clashes between the ids attributed to child widgets in different
    widgets, one cannot access a widget by its id outside of the declaration.
    This means that the following does not work and raises an `AttributeError`.
    This is why you need an alias if you need to access to the inner widget.

    .. code-block:: enaml

        enamldef MyWindow(Window):

            Container: cont:
                pass

        MyWindow().cont


Binding Operators
-----------------

To describe how a widget should be connected to the model driving it, Enaml
uses a set of four operators:


`=`
    *Assignment*. Right hand side can be any expression. The assignment will be
    the default value, but the value can be changed later through Python code
    or other expression execution.

`:=`
    *Delegation*. Right hand side must be a simple lvalue, like ``foo.bar`` or
    ``spam[idx]``. Non-lvalue expressions here are a syntax error. The
    value of the view property and value of the attribute are synced,
    but the type checking of the view property is enforced.

`<<`
    *Subscription*. Right hand side can be any expression or statement.
    In the case of an expression, the expression will be parsed for
    dependencies, and any dependency which is a member attribute on a Atom
    class will have a listener attached. When the listener fires, the
    expression will be re-evaluated and the value of the view property
    will be updated.
    The behavior for statements is quite similar. Whichever value the statement
    return will be set to the left-hand side.

`>>`
    *Update*. Right hand side must be a simple lvalue. The attribute will
    receive the view property's value any time it changes.

`::`
    *Notification*. Right hand side can be any statement. Additionally, an
    indented block of code can also be used. The statement/block will be
    evaluated any time the view property changes. Inside this block, one can
    access the notification that triggered the execution under the name
    ``change``. In  particular when using Atom object for the model, the new
    value can be accessed as ``change['value']``


Declarative function definition and overriding
----------------------------------------------

In addition to defining attributes inside an ``enamldef`` declaration, one can
define the equivalent of methods, or override them. In the context of
``enamldef`` objects, we will refer to them as declarative functions.

Such functions are defined using the ``func`` keyword, and obey the scoping
rules described in the next section. In particular, ``self`` can be used to
access the instance of the widget on which they are defined but does not need
to be listed explicitly in the arguments (and should not be).

Such functions can be overridden using a slightly different syntax, as
illustrated below:

.. code-block:: enaml

    enamldef MyWindow(Window):

        attr a = 2

        func my_func():
            return 3*self.a

    enamldef MyCustomWindow(MyWindow):

        attr a = 2

        my_func => ():
            return 3*a


Scoping Rules
-------------

- Imports are global and accessible to everything in the file.
- Each top-level item defines its own local namespace. This namespace
  includes all elements that have a declared identifier.
- Each expression has its local namespace that is the union of the block
  locals and the attribute namespace of the object to which the expression
  is bound. In other words, ``self`` is implicit. However, a ``self`` exists in
  this local namespace in order to break naming conflicts between block
  locals and attribute names. To any C++ or Java developers, this will seem
  natural.
- Each expression has a dynamic scope which exists between its local scope
  and the global scope. This scope is the chained union of all attribute
  namespaces of the ancestor tree of the object (i.e. the parents of the widget
  on which teh expression is defined) to which the expression is bound.

We illustrate these rules and of their consequences below:

.. code-block:: enaml

    enamldef MyWindow(Window):

        attr a = 2

        attr b: str = ""

        a::
            b = 1
            self.b = "test"

        b::
            print(change)
            print(f"{a}")

In the example above, in the notification handler for ``a``, we first create a
new local variable ``b``, which is scoped to the handler (i.e. it does not
exist outside). In order to set the attribute ``b`` of the widget we need to
use the implicit ``self`` referencing the widget. As a consequence, under
Python 3.8, the walrus operator ``:=`` will always create a local variable and
will never modify the state of the widget.

In the notification handler of ``b``, we first access the implicit ``change``
dictionary which is provided by the model. Second, we access the variable ``a``
which does not exist in the local namespace and is hence found in the widget
namespace. This is equivalent to ``self.a``.

.. code-block:: enaml

    enamldef MyLabel(Label):

        text << f"{a}"

    enamldef MyWindow(Window):

        attr a = 2

        MyLabel:
            pass

    enamldef MyWindow2(Window):

        attr b = 2

        MyLabel:
            pass

In the above example, ``MyWindow`` can be instantiated and the label text will
be ``"2"``. It is because the parent of ``MyLabel`` i.e. ``MyWindow`` has the
name ``a`` in its namespace. On the other end, ``MyWindow2`` will generate a
:class:`NameError` since ``a`` is not defined in ``MyLabel`` scope nor in any
of its parents scope.

Using this feature requires to properly document the expectation of the widget
since otherwise the reason for the :class:`NameError` may be hard to track. It
is however a powerful feature to avoid manually propagating a name through the
whole hierarchy. One typical example is when using the Enaml workbench with the
UI plugin to build a plugin application. In such application, accessing the
workbench object which is set on the main window is very common since the
workbench orchestrate the interaction between plugins. Since it is set on the
main window, any widget which can trace its ancestry to it, which is in the
general the case for all widgets, can use the name ``workbench`` safely.
