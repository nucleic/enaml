Writing .enaml Files
====================

.. warning:: This documentation is currently under development and may
    be missing information.

Enaml files contain a domain-specific language for specifying a user-interface
and dynamically binding and computing values based on user interaction.

A simple example of an Enaml file might look something like this:

.. literalinclude:: ../../../examples/widgets/form.enaml
    :language: python

On the Python side, the Enaml code can be imported using a ``with`` statement
to add the Enaml import hooks.  The ``enamldef`` blocks are then available as
module-level functions that can be called normally from Python code.  Building
the UI is then a matter of calling an Enaml ``enamldef`` to build the view, and
creating that view from a ``Session`` instance. The parameters passed in to
the Enaml ``enamldef`` block from the Python side can be any Python or Enaml
objects that would make sense to use within the Enaml code. For example, if you
use an attribute of an object in the Enaml code, then passing an object without
that attribute will raise an ``AttributeError`` just as if you did the same
thing in a Python function.

Enaml Widgets and Layout
------------------------

Enaml widgets come in two basic types: Containers and Controls.  Controls
are conceptually single UI elements with no other Enaml widgets inside them,
such as labels, fields, and buttons.  Containers are widgets which contain other
widgets, usually including information about how to layout the widgets that they
contain.  Examples of containers include top-level windows, scroll areas and forms.

Enaml uses constraints-based layout implemented by the Cassowary layout system.
Constraints are specified as a system of linear inequalities together with an
error function which is minimized according to a modified version of the Simplex
method.  The error function is specified via assigning weights to the various
inequalities.  The default weights exposed in Enaml are ``'weak'``, ``'medium'``,
``'strong'``, ``'required'``, and ``'ignored'``, but other values are possible
within the system, if needed. While a developer writing Enaml code could specify
all constraints directly, in practice they will use a set of helper classes,
functions and attributes to help specify the set of constraints in a more
understandable way.

Every widget knows its preferred size, usually by querying the underlying toolkit,
and can express how closely it adheres to the preferred size via its ``hug_width``,
``hug_height``, ``resist_width`` and ``resist_height`` attribute which take one
of the previously mentioned weights. These are set to reasonable defaults for most
widgets, but they can be overriden. The ``hug`` attributes specify how strongly
the widget resists expansion by adding a constraint of the appropriate weight that
specifies that the dimension be equal to the preferred value, while the ``resist_clip``
attributes specify how strongly the widget resists compression by adding a constraint
that specifies that the dimension be greater than or equal to the preferred value.

.. todo::
    Example here

Containers can specify additional constraints that relate their child widgets.
By default a container simply lays out its children as a vertical list and tries
to expand them to use the full width and height that the container has available.
Layout containers, like Form, specify different default constraints that give
automatic layout of their children, and may provide additional hooks for other
widgets to use to align with their significant features.

Additional constraints are specified via the ``constraints`` attribute on the
container.  The simplest way to specify a constraint is with a simple equality
or inequality.  Inequalities can be specified in terms of symbols provided
by the components, which at least default to the symbols for a basic box model:
``top``, ``bottom``, ``left``, ``right``, ``v_center``, ``h_center``, ``width``
and ``height``.  Other components may expose other symbols: for example the
``Form`` widget exposes ``midline`` for aligning the fields of multiple forms
along the same line, and a ``Container`` exposes various ``contents`` symbols
to accound for padding around the boundaries of its children.

.. todo::
     Example here

However, this can get tedious, and so there are some helpers that are
available to simplify specifying layout.  These are:

    ``spacer``
        A singleton spacer that represents a flexible space in a layout
        with a minimum value of the default space.  Additional restrictions
        on the space can be specified using ``==``, ``<=`` and ``>=`` with
        an integer value.

    ``spacer.flex()``
        A flexible spacer that has a hard minimum but also a weaker preference
        to be no larger than that minimum.

    ``horizontal(*items)`` or ``hbox(*items)``

    ``vertical(*items)`` or ``vbox(*items)``
        These four functions take a list of symbols, widgets and spacers and
        create a series of constraints that specify a sequential horizontal
        or vertical layout where the sides of each object in sequence abut
        against each other.

    ``align(variable, *items)``
        Align the given string variable name on each of the specified items.

    ``grid(*rows, **config)``
        A function which takes a variable number of iterable rows and
        arranges the items in a grid according to the configuration
        parameters.

By using appropriate combinations of these objects you can specify complex layouts
quickly and clearly.

.. todo::
    Example here

Binding Operators
-----------------

`=`
    *Assignment*. RHS can be any expression. The assignment will be the
    default value, but the value can be changed later through Python code
    or other expression execution.

`:=`
    *Delegation*. RHS must be a simple lvalue, like ``foo.bar`` or
    ``spam[idx]``. Non-lvalue expressions here are a syntax error. The
    value of the view property and value of the attribute are synced,
    but the type checking of the view property is enforced.

`<<`
    *Subscription*. RHS can be any expression. The expression will be parsed
    for dependencies, and any dependency which is an atom attribute on an
    Atom subclass will have a listener attached. When the listener fires,
    the expression will be re-evaluated and the value of the view property
    will be updated.

`>>`
    *Update*. RHS must be a simple lvalue. The attribute will receive the
    view property's value any time it changes.

`::`
    *Notification*. RHS can be any statement. Additionally, an indented
    block of code can also be used. The statement/block will be evaluated
    any time the view property changes.

Scoping Rules
-------------

- Imports are global and accessible to everything in the file.
- Each top-level item defines its own local namespace. This namespace
  includes all elements that have a declared identifier.
- Each expression has its local namespace that is the union of the block
  locals and the attribute namespace of the object to which the expression
  is bound. In otherwords `self` is implicit. However, a `self` exists in
  this local namespace in order to break naming conflicts between block
  locals and attribute names. To any C++ or Java developers, this will seem
  natural.
- Each expression has a dynamic scope which exists between its local scope
  and the global scope. This scope is the chained union of all attribute
  namespaces of the ancestor tree of the object to which the expression
  is bound.

