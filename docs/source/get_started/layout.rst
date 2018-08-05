.. _layout:

==================
Constraints Layout
==================

Enaml widgets come in two basic types: Containers and Controls.  Controls
are conceptually single UI elements with no other Enaml widgets inside them,
such as labels, fields, and buttons.  Containers are widgets which contain
other widgets, usually including information about how to layout the widgets
that they contain.  Examples of containers include top-level windows, scroll
areas and forms.

Enaml uses constraints-based layout implemented by the Cassowary layout system.
Constraints are specified as a system of linear inequalities together with an
error function which is minimized according to a modified version of the
Simplex method. The error function is specified via assigning weights to the
various inequalities.  The default weights exposed in Enaml are ``'weak'``,
``'medium'``, ``'strong'``, ``'required'``, and ``'ignored'``, but other values
are possible within the system, if needed. While a developer writing Enaml
code could specify all constraints directly, in practice they will use a set of
helper classes, functions and attributes to help specify the set of constraints
in a more understandable way.

Every widget knows its preferred size, usually by querying the underlying
toolkit, and can express how closely it adheres to the preferred size via its
``hug_width``, ``hug_height``, ``resist_width`` and ``resist_height``,
``limit_width`` and ``limit_height`` attribute which take one of the previously
mentioned weights. These are set to reasonable defaults for most widgets, but
they can be overriden. The ``hug`` attributes specify how strongly the widget
resists deformation by adding a constraint of the appropriate weight that
specifies that the dimension be equal to the preferred value, while the
``resist`` attributes specify how strongly the widget resists compression by
adding a constraint that specifies that the dimension be greater than or equal
to the preferred value. The  ``limit`` attributes specify how strongly the
widget resists expansion by adding a constraint that specifies that the
dimension be smaller than or equal to the preferred value

Containers can specify additional constraints that relate their child widgets.
By default a container simply lays out its children as a vertical list and
tries to expand them to use the full width and height that the container has
available. Layout containers, like Form, specify different default constraints
that give automatic layout of their children, and may provide additional hooks
for other widgets to use to align with their significant features.

Additional constraints are specified via the ``constraints`` attribute on the
container.  The simplest way to specify a constraint is with a simple equality
or inequality.  Inequalities can be specified in terms of symbols provided
by the components, which at least default to the symbols for a basic box model:
``top``, ``bottom``, ``left``, ``right``, ``v_center``, ``h_center``, ``width``
and ``height``.  Other components may expose other symbols: for example the
``Form`` widget exposes ``midline`` for aligning the fields of multiple forms
along the same line, and a ``Container`` exposes various ``contents`` symbols
to account for padding around the boundaries of its children.

.. code-block:: enaml

    enamldef Main(Window):
        Container:
            constraints = [
                # Pin the first push button to the top contents anchor.
                pb1.top == contents_top,

                # Relate the left side of the push button to the width
                # of the container.
                pb1.left == 0.3 * width,

                # Relate the width of the push button to the width of
                # the container
                pb1.width == 0.5 * width,

                # Pin the second push button to the left contents anchor.
                pb2.left == contents_left,

                # Relate the top of the push button to width of the first
                # push button.
                pb2.top == 0.3 * pb1.width + 10
            ]
            PushButton: pb1:
                text = 'Horizontal'
            PushButton: pb2:
                text = 'Long Name Foo'


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

    ``factory(func, *args, **kwargs)``
        A function which takes a function which should return the set of
        constraints to use. The factory function is called each time the layout
        can change (widget addition, deletion, etc).The arguments are passed
        are passed to function.

By using appropriate combinations of these objects you can specify complex
layouts quickly and clearly.

.. code-block:: enaml

    enamldef Main(Window):
        Container:
            constraints = [
                # Arrange the Html Frame above the horizontal row of butttons
                vbox(
                    html_frame,
                    hbox(
                        add_button, remove_button, spacer,
                        change_mode_button, spacer, share_button,
                    ),
                ),

                # Weakly align the centers of the Html frame and the center
                # button. Declaring this constraint as 'weak' is what allows
                # the button to ignore the constraint as he window is resized
                # too small to allow it to be centered.
                align('h_center', html_frame, change_mode_button) | 'weak',

                # Set a sensible minimum height for the frame
                html_frame.height >= 150,
            ]
            Html: html_frame:
                source = '<center><h1>Hello Enaml!</h1></center>'
            PushButton: add_button:
                text = 'Add'
            PushButton: remove_button:
                text = 'Remove'
                clicked :: print('removed')
            PushButton: change_mode_button:
                text = 'Change Mode'
            PushButton: share_button:
                text = 'Share...'

Alternatively one can override the ``layout_constraints`` function in the
enaml definition.

.. code-block:: enaml

    enamldef Main(Window):
        title = 'Custom Constraints'
        Container:
            layout_constraints => ():
                rows = []
                widgets = self.visible_widgets()
                row_iters = (iter(widgets),) * 2
                rows = list(zip_longest(*row_iters))
                return [grid(*rows)] + [align('v_center', *row) for row in rows]
            Label:
                text = 'Name'
            Field:
                pass
            Label:
                text = 'Surname'
            Field:
                pass
            PushButton:
                text = 'Click me'
