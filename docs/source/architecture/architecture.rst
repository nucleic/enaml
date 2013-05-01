Design and Architecture
=======================

.. warning:: This documentation is not current and does not reflect the way
    Enaml currently works.

Enaml is designed with a flexible, open architecture.  It is designed to be
able to adapt to different UI toolkit backends beyond the currently supported
Qt and Wx backends, as well as allowing other key parts of the infrastructure
to be replaced.

Construction of a View
^^^^^^^^^^^^^^^^^^^^^^

When building a view, you typically will create it via a sequence of commands
like::

    import enaml
    
    with enaml.imports():
        from my_enaml_module import MyView
    
    view = MyView(model)
    view.show()

The import step parses and compiles the Enaml file, creating a Python module
containing view factories which can be used by importing the appropriate 
name.  When called, these views factories expect model objects to be passed 
via arguments and then use the UI toolkit to construct the actual UI components 
that will be used in the view.  Finally the show() method starts the application 
mainloop if needed and makes the UI components visible.

The enaml.imports() context manager provides an import hook that detects when an
``.enaml`` file is being imported, parses it into an Enaml AST and uses
:py:class:`~enaml.parsing.enaml_compiler.EnamlCompiler` to compile it to Enaml 
bytecode. From the importer's point of view it creates a standard Python module 
which has one or more :py:class:`EnamlDefinition` objects which create
re-usable UI templates.  The :py:class:`EnamlDefinition` objects can be used by
other Enaml modules which import them, or directly by Python code.  Each
:py:class:`EnamlDefinition` instance is a namespace which can have additional
variable values supplied as arguments when it is called.

Calling an :py:class:`EnamlDefinition` object uses the supplied arguments to
build its namespace and then executes the Enaml bytecode to construct the UI
shell components.  The UI shell components are toolkit independent atomic
classes which expose the functionality of a toolkit widget in a uniform manner.
The toolkit specific widget wrapper objects are managed internally by the 
shell components. Both of these objects are created through the use of special
Toolkit objects. Normally the Toolkit object to use is inferred from the user's
environment variables, but a particular toolkit can be selected using a context
manager::

    from enaml.toolkit import wx_toolkit
    
    with wx_tookit():
        view = MyView(model)
    
    view.show()

Finally the show() call on the view object recursively creates the underlying
gui toolkit widgets by following a formalized set process. This process calls
the following methods on each component in the tree in a top-down fashion:

* ``create()`` method to create the gui toolkit widget
* ``initialize()`` method to set the initial state of the gui toolkit widget
* ``bind()`` method to bind event handlers (or the toolkit equivalents)

In addition, widgets which participate in constraints-based layout will have 
methods called to register their constraints with the appropriate constraint 
solvers, and then solve the layout.

Adding New Widgets
^^^^^^^^^^^^^^^^^^

These layers of abstraction and delegation mean that it is fairly simple to add
new widget types in custom applications.  To create a new widget, one needs to:

    1)  Optionally, but ideally, define the abstract interface for your
        widget, which should be at least a subclass of the abstract base class
        :py:class:`~enaml.widgets.base_component.AbstractTkBaseComponent`
        but will likely be a subclass of 
        :py:class:`~enaml.widgets.control.AbstractTkControl` or
        :py:class:`~enaml.widgets.container.AbstractTkContainer`.
        Since this is an abstract base class, you shouldn't implement any of the
        functionality in this class.

        This class provides the generic API the individual toolkit backends will
        need to implement, and will provide the methods that the Enaml widget
        will call in order to communicate with the gui toolkit widget.  In 
        particular, there needs to be a specially named
        :py:meth:`shell_*_changed(self, value)` change handler for every
        dynamic Atom on the Enaml shell version of the Widget. These methods 
        will allow the toolkit widget to appropriately react to changes from 
        the user's code.

    2)  Create the Enaml shell version of the Widget.  This will at least be a 
        subclass of :py:class:`~enaml.widgets.base_component.BaseComponent`, 
        and most likely a subclass of :py:class:`~enaml.widgets.control.Control`
        or :py:class:`~enaml.widgets.container.AbstractTkContainer`.  This class
        defines the interface that the Enaml markup language sees and can use.
        There should be, at a minimum, atoms corresponding to values that can
        be read or changed on the widget, as well as methods for all standard
        actions for which access should be supplied.

        This class is not abstract, and should provide all the functionality
        required in a toolkit-independent manner.  This must define an atom 
        called :py:attr:`abstract_obj` which is an :py:class:`Instance()` of 
        the implementation interface defined in the previous step.

    3)  Create a version of the Widget for each backend that you need to support.
        Each of these will be a subclass of the appropriate backend-specific
        component, such as :py:class:`~enaml.widgets.wx.wx_base_component.WXBaseComponent`
        or  :py:class:`~enaml.widgets.qt.qt_base_component.QtBaseComponent` as well as
        subclassing the abstract interface defined in the first step.  Once again,
        these are most likely to be subclasses of the appropriate Control classes.

        Instances of this class will have a :py:attr:`shell_obj` attribute
        which provides a reference to the Enaml shell widget instance for that
        control so that values can be obtained and inspected. This attribute
        is provided by the base class and will normally not need to be overridden.

        This class must then, obviously, provide a concrete implemetation of the
        abstract interface.  In particular, it must provide the following methods
        (even if they are no-ops or implemented in a superclass):
        
            :py:meth:`create(self)`
                This is responsible for creating the underlying toolkit objects
                or widgets that the Enaml shell widget requires as part of its UI.
                e.g. create the QPushButton or wx.Button widget.

                You will almost always have to write this method.

            :py:meth:`initialize(self)`
                This is responsible for initializing the state of the toolkit
                object or objects based on the state of the Enaml shell widget.

                You will almost always have to write this method.

            :py:meth:`bind(self)`
                This is responsible for setting up the initial bindings of
                toolkit events to handlers on this object.

                You will almost always have to write this method.
        
        If you are writing a composite widget which contains a collection of
        toolkit widgets, as opposided to a single control-style widget, you
        may need to override the following:
        
            :py:meth:`size_hint(self)`
                This is responsible for returning a suggested size for the widget
                in its current state for use by the layout manager.
            
            :py:meth:`set_geometry(self, x, y, width, height)`
                This method is called when the layout system needs to re-position
                or resize the widget.  For a simple single widget control, this
                would usually just call the appropriate set geometry method on
                the underlying toolkit widget, but for an Enaml widget composed
                of multiple toolkit widgets you will need to lay them out
                relative to each other and the space that they have been provided.
            
            :py:meth:`move(self, x, y)`
                A position-only version of :py:meth:`set_geometry(...)`
            
            :py:meth:`resize(self, width, height)`
                A size-only version of :py:meth:`set_geometry(...)`

        In addition to these standard methods, you will need to provide
        implementations for each of the methods you declared in the first step:

            :py:meth:`shell_*_changed(self, value)`
                This has to react to a change to the appropriate atom on the
                Enaml widget and change the appropriate toolkit state.

        as well as any other methods that may be needed.
        
        If you are writing a control, you may need to handle error and exceptions
        generated by invalid values, either coming in to the widget from the
        underlying model, or from values entered by the user.  The
        :py:class:`enaml.widgets.control.Control` class provides a standard API
        for registering these::
        
            :py:attr:`error`
                This is a boolean atom which is True if an invalid value was
                entered.
            
            :py:attr:`exception`
                This is a atom which holds the Exception object that caused
                the error to be flagged.
        
        The :py:class:`enaml.widgets.control.Control` class provides two helper
        contexts which can be used to automatically capture any exceptions::
        
            :py:meth:`capture_exceptions`
                This will capture any exceptions generated by a block of code
                in a with statement, and will automatically set or clear the
                error state appropriately.  Because of the way that exceptions
                work in atom notification handlers, this may fail to capture
                errors generated by delegation or notification expresssions.
            
            :py:meth:`capture_notification_exceptions`
                This will capture any exceptions including exceptions generated
                in notification handlers fired by atom in response to changes
                within code in a with statement.
        
        Finally, to assist in debugging and logging, the toolkit object has a
        :py:attr:`control_exception_handler` callback that can be supplied which
        will be called with a single argument which is an exception captured by
        either of the above contexts.
        

        .. warning:: These methods are outdated and for the moment is only a placeholder

        To handle styling

            :py:meth:`create_style_handler(self)`
                This is responsible for creating a :py:class:`StyleHandler`
                instance.  You may need to implement a custom subclass of
                :py:class:`StyleHandler` if your widget has unusual styling
                needs.

                If your styling needs are simple, you may be able to
                define an appropriate :py:attr:`tags` class attribute which
                maps supported style tags to toolkit-dependent information,
                and use the default implementation of the method from the
                toolkit.

            :py:meth:`initialize_style(self)`
                This method is responsible for initializing the values on the
                :py:class:`StyleHandler` class created by the previous method.

                If your styling needs are simple, you may be able to use the
                default toolkit implementation of this class.

            :py:meth:`layout_child_widgets(self)`
                This method is used by :py:class:`Container` implementations to
                insert child widgets into the appropriate toolkit-specific
                layout object, and set the appropriate attributes and properties
                of this object.  Most simple Control subclasses do not need to
                implement this, since they do not have child widgets.

    4)  Create the toolkit constructor and add it to the appropriate toolkit
        object.  There are several ways to do this, depending on your goals:
        
            *   if you are adding a new control type to the main Enaml source,
                then you can directly create a constructor in the toolkit's
                ``constructors.py`` module.  This module contains a dictionary
                of constructors and a utility function for building them
                assuming that you have followed a naming pattern for your classes
                which is consistent with the rest of the toolkit widgets.
                
                Typically this will look something like::
                
                    QT_CONSTRUCTORS = dict((
                        ...
                        constructor('my_new_widget'),
                    ))
            
            *   if you are adding a new control type that is specific to your
                code and not part of the main Enaml system, then you will need
                to manually create an :py:class:`~enaml.toolkit.Constructor`
                instance and add it to an appropriate toolkit.  Building a
                constructor is simply a matter of creating a new
                :py:class:`~enaml.toolkit.Constructor` with your Enaml shell
                class from step (2) and your toolkit backend class from step (3).
                
                Typical code for this would look like::
                
                    from enaml.toolkit import Constructor
                    
                    def my_new_widget():
                        from my_widgets.my_new_widgets import MyNewWidget
                        return MyNewWidget
                    
                    def my_new_qt_widget():
                        from my_widgets.qt.qt_my_new_widgets import QtMyNewWidget
                
                    ctor = Constructor(my_new_widget, my_new_qt_widget)
                    
                The items passed to the Constructor are callables which return
                the appropriate classes, so that importing of the necessary
                modules can be delayed until the objects actually need to be
                used. This helps to drastically reduce runtime overhead for
                simple applications which only use a small portion of a ui
                toolkit.

                Once you have the constructor you need to add it to a toolkit.
                If you want this to be globally available in your process as part
                of the appropriate toolkit then you need to add it to the toolkit's
                constructor dictionary before you create any views::
                
                    from enaml.widgets.qt.constructors import QT_CONSTRUCTORS
                    
                    QT_CONSTRUCTORS['MyNewWidget'] = ctor
                    
                Any subsequent calls to :py:func:`~enaml.toolkit.qt_toolkit` will
                now contain your new widget.
                
                Alternatively, you may want to create your own toolkit that is
                separate from the usual backend toolkit::
                
                    from enaml.toolkit import qt_toolkit
                    
                    my_toolkit = qt_toolkit()
                    my_toolkit['MyNewWidget'] = ctor
                
                This will create a new toolkit which has all of the widgets in
                the standard Qt toolkit, but also includes yours.  Code can then
                choose whether to use the standard Qt toolkit or your new toolkit
                as appropriate.
            
            *   There is a convienence built into the constructors for the cases
                where a custom widget is only a simple subclass of an existing
                shell component. Suppose we wish to create a FloatField which
                is a simple subclass of Field that hard-codes the converter
                object to a float converter::
                    
                    from atom.api import Constant

                    from enaml.converters import FloatConverter
                    from enaml.widgets.field import Field

                    class FloatField(Field):
                        
                        converter = Constant(FloatConverter())

                It would be silly to require the definition of a new
                toolkit implementation class for each backend, since the 
                implementation class doesn't need to change. Instead, we
                can make sure that our new subclass uses the appropriate
                implementation but creating a clone of its constructor::
                    
                    from enaml.toolkits import qt_toolkit

                    def my_float_field():
                        return FloatField

                    my_toolkit = qt_toolkit()

                    field_constructor = my_toolkit['Field']

                    my_constructor = field_constructor.clone(my_float_field)

                    my_toolkit['FloatField'] = my_constructor

                This toolkit will now always be sure to use the proper
                toolkit widget for the FloatField.


Implementing A New Toolkit
^^^^^^^^^^^^^^^^^^^^^^^^^^

Currently, Enaml supports the Qt toolkit and the Wx toolkit (Wx officially on 
Windows only). The architecture is designed to be as toolkit-independent as 
possible.  To implement a new toolkit, you will need to perform the following 
steps:

    1)  Create a constructor dictionary for your toolkit.  You should be able
        to take the ``constructor.py`` module from either the Qt or Wx backends
        and modify the constructor factory function to import from the correct
        packages and mangle the class names appropriately.
    
    2)  Create a default stylesheet for your toolkit.  Initially it may be
        sufficient to copy the stylesheet for an existing backend, since the
        stylesheet definitions are toolkit-independent.

    3)  Create a new toolkit factory for your new backend.  This should look
        something like the current :py:class:`enaml.toolkit.wx_toolkit` or
        :py:class:`enaml.toolkit.qt_toolkit` factories.  This factory should
        create a Toolkit instance, which is a dictionary subclass whose keys
        are the available Enaml entity names.  Usually this will consist of the
        toolkit's constructor dictionary from (1) together with the standard
        ``OPERATORS`` from :py:mod:`enaml.toolkit` and a ``utils`` dictionary.
        In additon the following attributes need to be supplied with callables::

            :py:attr:`create_app`
                A function that is responsible for obtaining (or creating, if it
                doesn't yet exist) the main toolkit application object, or
                otherwise performing whatever initialization is needed to allow
                widgets to be created.  It should not start the main event loop,
                however.

                This should return the application object, if appropriate.

            :py:attr:`start_app`
                A function that takes an application object returned by
                :py:attr:`create_app` and starts the main event loop.

            :py:attr:`style_sheet`
                The default stylesheet for your toolkit.

    4)  Write toolkit-specific implementations of each Enaml widget.  See the
        previous section for discussion for the methods that you will need to
        implement on this class.

        This is where the bulk of the work will be performed.

    5)  Write the implementations of auxilliary objects, such as dialog windows.

If all of the above steps are performed correctly, you should be able to display
any Enaml UI in your new toolkit.


Using A Different Notification Model
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

Enaml uses Nucleic's Atom system by default for handling binding and
notification of expressions to model attributes.  You may have existing code
which uses a different system for reacting to changes within the model, and
Enaml can be extended to be able to use these systems as well.  This would
allow developers to write code which might do things like access a model on
a remote machine, or stored in a database.

To support this sort of behaviour, you will probably want to have a base class
that all model objects with this new reaction mechanism inherit from, or some
other simple way that these model instances can be distinguished from regular
Python or Atom instances.

You may then need to implement subclasses of
:py:class:`enaml.expressions.AbstractExpression` that correctly handle the
interactions that your notification system supports for its models.  These
subclasses will need to implement appropriate versions of the :py:meth:`bind`
and :py:meth:`eval_expression` methods.

For the four basic expression bindings, you will most likely need to create
subclasses of  :py:class:`enaml.expressions.SimpleExpression`,
:py:class:`enaml.expressions.UpdatingExpression`,
:py:class:`enaml.expressions.DelegatingExpression`, and
:py:class:`enaml.expressions.NotifyingExpression`.
When implementing overriden methods, all of these subclasses
must check to see whether the model object is of the new model type, and if
it is not then they need to fall back to using the standard superclass
implementation of the method.  If this is not done then expressions involving
widget atoms will fail to work correctly.

    :py:class:`~enaml.expressions.SimpleExpression`
        This class needs to be able to provide a default value for the
        expression, but does not need to react to changes in the model object
        or in the Enaml namespace.

        You may need to override the :py:meth:`eval_expression` handler
        to compute the default value from the model, but ideally you should
        be able to use this class unmodified.

    :py:class:`~enaml.expressions.UpdatingExpression`
        This class needs to provide a default value for the expression, but
        also needs to analyze the expression for dependencies and react to
        changes in the dependency values on the model objects.

        You may need to override the :py:meth:`eval_expression` handler
        to as in the :py:class:`~enaml.expressions.DefaultExpression` case,
        but again hopefully the default will be sufficient.

        You will also need to override the :py:meth:`bind` method to correctly
        hook up the expression to its dependencies in your model's notification
        model.  This is likely to require walking the provided expression AST
        to determine dependencies (the AttributeVisitor class may be useful
        for this) and you may have to register callbacks on an appropriate 
        object.  This callback will probably look something like the 
        :py:meth:`update_object()` method, but may need to perform additional 
        steps depending on your model.

    :py:class:`~enaml.expressions.NotifyingExpression`
        This class requires the ability to execute a code expression whenever
        an Enaml attribute changes.

        You may need to override the :py:meth:`notify()` method to compute the
        expression correctly, but ideally you should be able to use this
        class unmodified.

    :py:class:`~enaml.expressions.DelegatingExpression`
        This class requires both the ability to analyze and react to changes
        in expression dependencies, but also push changes from the Enaml
        atom which it is connected to onto the designated object.

        This will require an appropriate :py:meth:`bind()` method similar to
        the one that the :py:class:`~enaml.expressions.BindingExpression` uses,
        although the allowable expressions are much simpler for
        :py:class:`~enaml.expressions.DelegatingExpression`.

        You will also need to override the implementations of
        :py:meth:`update_object()` and :py:meth:`update_delegate()` to
        appropriately change the value on the underlying model.

Having written these classes, you will need to define operator factories for
each of them and override your toolkit's ``OPERATORS``, for example::

    from enaml.operators import operator_factory, OPERATORS
    
    OPERATORS['__operator_LessLess__'] = operator_factory(MyUpdatingExpression)

If it makes sense for your new expression to use a different operator than the
standard four, you can define a different name and then the corresponding
operator will be available, for example to enable ``<<<`` as an operator::
    
    OPERATORS['__operator_LessLessLess__'] = operator_factory(MyUpdatingExpression)

The above changes will be global in nature.  If you want to restrict the modified
operators to a subset of code, you can create an instance of at Toolkit object
and override the operators in just that instance::

    from enaml.operators import operator_factory
    from enaml.toolkit import qt_toolkit
    
    my_toolkit = qt_toolkit()
    my_toolkit['__operator_LessLess__'] = operator_factory(MyUpdatingExpression)


Or for even more fine grained control (and are accepting or horrible, horrible
hacks) then you can pass in an operator as a local variable to an EnamlDefinition::

    enamldef MainWindow(my_model, __operator_LessLessLess__):
        Window:
            PushButton:
                # The <<< operator is resolved to the 2nd argument 
                # to MainWindow
                text <<< my_model.foo

This could also be a keyword argument if desired, or even a module level 
python function. That is, operators resolved using the same scope rules as 
the rest of the Enaml file.

