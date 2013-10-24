.. _stylesheets:

============
Style Sheets
============

Enaml style sheets are a powerful feature which allow the developer to
customize the visual appearance of a view independent from the view's
structural definition. The concepts and nomenclature used in Enaml style
sheets are heavily based on CSS and WPF, but are adapted to the dynamic
and declarative world of Enaml.


Overview
--------

`Cascading Style Sheets`_ is a well known technology for specificing the look
and feel of documents written in XML markup, and is most commonly used to
style HTML web pages. The primary design goal of CSS is to separate document
content from document presentation, resulting in more scalable, flexible, and
maintainable code.

`WPF Styling`_ shares the same documents separation goals as CSS, but is
implemented using the same markup language as the document structure. WPF
styles also include development features which are not present in CSS
(such as data-driven style striggers), but which are immensely useful in
desktop application development.

Enaml style sheets combine the successful concepts from both CSS and WPF.
Style sheets:

- use selectors to match style rules to widgets
- cascade across the object hierarchy of the view
- are written with the same language as the rest of view
- are fully dynamic and data-driven

.. _Cascading Style Sheets: http://en.wikipedia.org/wiki/Cascading_Style_Sheets
.. _WPF Styling: http://msdn.microsoft.com/en-us/library/ms745683.aspx


Structure
---------

There are three classes which comprise the definition of a style sheet:
:class:`StyleSheet <enaml.styling.StyleSheet>`,
:class:`Style <enaml.styling.Style>`, and
:class:`Setter <enaml.styling.Setter>`. The developer arranges these classes
into a hiearchy declared on a :class:`Stylable <enaml.styling.Stylable>`
widget in order to apply the styling to that widget hierarchy. The following
simple example shows how to set the text color of all
:class:`PushButton <enaml.widgets.push_button.PushButton>` widgets in
a :class:`Window <enaml.widgets.window.Window>` to blue:

.. container:: code-and-img

    .. code-block:: enaml

        enamldef Main(Window):
            title = 'Style Sheet'
            StyleSheet:
                element = 'PushButton'
                Style:
                    Setter:
                        property = 'color'
                        value = 'blue'
            Container:
                PushButton:
                    text = 'First'
                PushButton:
                    text = 'Second'
                PushButton:
                    text = 'Third'

    .. image:: /images/simple_style.png
        :align: center

The :class:`StyleSheet <enaml.styling.StyleSheet>` class forms the root
of the hierarchy for a style sheet. Its sole purpose is to provide an
aggregation point for the :class:`Style <enaml.styling.Style>` objects
defined for the style sheet.

The :class:`Style <enaml.styling.Style>` class serves the role of the selector
in typical CSS parlance. It also serves as an aggregation point for the style
:class:`Setter <enaml.styling.Setter>` objects. The various attributes of the
style combine to form a rule against which all the widgets for the style sheet
are tested. If a widget is a match for the rule, then the style setters are
applied to that widget. The order in which multiple matching styles are applied
is governed by the rules of :ref:`selectors`, :ref:`specificity`, and
:ref:`cascading`.

The :class:`Setter <enaml.styling.Setter>` class provides the information
needed to style a single facet of an object in the form of ``property`` and
``value`` attributes. Both attributes accept strings values and represent the
property name and value to apply to a style property. A setter is declared as
a child of a :class:`Style <enaml.styling.Style>` object and is applied to any
widget which matches the style rule. Multiple setters may be defined on a
single style, and they are applied in the order in which they are declared.

See the :ref:`list_of_properties` reference section for the list of supported
style property names.


.. _selectors:

Selectors
^^^^^^^^^

A style sheet consists of a list of :class:`Style <enaml.styling.Style>`
objects, each having a list of :class:`Setter <enaml.styling.Setter>` objects
which will be applied to any :class:`Stylable <enaml.styling.Stylable>` widgets
which match the style's selector.

The style selector is made up of three attributes on the
:class:`Style <enaml.styling.Style>` object:

- **element** - This is a string which will match the name of the type of the
  stylable object or any of its subtypes. For example, ``"Field"`` will match
  all instances of :class:`Field <enaml.widgets.field.Field>` or any of its
  subtypes. An empty string will match all types. Multiple types can be
  specified by separating them with a comma, which will match using logical
  OR semantics.

- **style_class** - This is a string which will match the ``style_class``
  attribute on a stylable object. This is very similar to the concept of CSS
  classes. An empty string will match all style classes. Multiple style classes
  can be specified by separating them with a comma, which will match using
  logical OR semantics.

- **object_name** - This is a string which match the ``name`` attribute on a
  stylable object. This is very similar to the concept of CSS identifiers.
  An empty string will match all object names. Multiple object names can be
  specified by separating them with a comma, which will match using logical
  OR semantics.

All three selector must be a match for a given widget for the style to be
considered a match. See the section on :ref:`specificity` for details on
how the strength of the match is computed.

.. note::

    The ``style_class`` attribute on a
    :class:`Stylable <enaml.styling.Stylable>` object can be assigned a
    space-separated string, which indicates that the object belongs to
    more than one style class. Combined with the comma-separated style
    selectors, this provides a very powerful mechanism for targeted
    selection.

    Unlike CSS and WPF, Enaml style sheets do not provide selectors which
    match based on object attribute values. Developers should instead use
    Enaml's dynamic operators to update the style class of an object at
    runtime. The styling engine is optimized for this mode of operation.

The following simple example shows each of the selectors in use:

.. container:: code-and-img

    .. code-block:: enaml

        enamldef Main(Window):
            title = 'Style Sheet'
            StyleSheet:
                Style:
                    element = 'PushButton'
                    Setter:
                        property = 'color'
                        value = 'red'
                Style:
                    style_class = 'blue-class'
                    Setter:
                        property = 'color'
                        value = 'blue'
                Style:
                    object_name = 'special'
                    Setter:
                        property = 'color'
                        value = 'green'
                    Setter:
                        property = 'font-weight'
                        value = 'bold'
            Container:
                PushButton:
                    text = 'One'
                PushButton:
                    text = 'Two'
                Field:
                    style_class = 'blue-class'
                    text = 'Three'
                CheckBox:
                    style_class = 'blue-class'
                    text = 'Four'
                    checked = True
                PushButton:
                    text = 'Five'
                    name = 'special'

    .. image:: /images/selector_style.png
        :align: center


.. _specificity:

Specificity
^^^^^^^^^^^

The nature of style selectors is such that a single style can be matched to
multiple widgets, and a widget can be matched to multiple styles. This is the
main feature which makes style sheets so powerful and expressive! However, this
flexibility presents the possibility for conflicts in a widget's style
specification. What to do if a widget matches multiple styles, all of which
have a setter which defines a value for the ``color`` property? These sorts of
conflicts are resolved by examining the specificity of a selector match.

A selector's specificity is nothing more than an integer which indicates how
strongly a given widget is a match for the style. It is computed according to
the following formula:

1. Start with a specificty of 0.
2. Add 1 if the ``element`` selector matches the item.
3. Add 16 for every ``style_class`` which matches the item.
4. Add 256 if the ``object_name`` selector matches the item.
5. The final value is the specificity of the match.

When the styling engine is computing the style to apply to a widget for a
given style sheet, it computes the specificity for all matching styles and
then sorts them according to that specificity. Ties are broken by the order
in which the styles were declared. The styles are then applied in order from
least-specific to most-specific.

The following simple example demonstrates specificity:

.. container:: code-and-img

    .. code-block:: enaml

        enamldef Main(Window):
            title = 'Style Sheet'
            StyleSheet:
                Style:
                    element = 'PushButton'
                    Setter:
                        property = 'color'
                        value = 'blue'
                Style:
                    element = 'PushButton'
                    style_class = 'alpha'
                    Setter:
                        property = 'color'
                        value = 'red'
                Style:
                    element = 'PushButton'
                    style_class = 'beta'
                    Setter:
                        property = 'color'
                        value = 'green'
                Style:
                    style_class = 'alpha, beta'
                    Setter:
                        property = 'color'
                        value = 'steelblue'
                    Setter:
                        property = 'font'
                        value = 'bold 12pt Arial'
                Style:
                    object_name = 'special'
                    Setter:
                        property = 'color'
                        value = 'goldenrod'
            Container:
                PushButton:
                    text = 'One'
                PushButton:
                    text = 'Two'
                    style_class = 'alpha'
                PushButton:
                    text = 'Three'
                    style_class = 'beta'
                Field:
                    text = 'Four'
                    style_class = 'alpha beta'
                PushButton:
                    text = 'Five'
                    style_class = 'alpha beta'
                    name = 'special'

    .. image:: /images/specificity_style.png
        :align: center


.. _cascading:

Cascading
^^^^^^^^^

A style sheet can be applied to the global
:class:`Application <enaml.application.Application>` and to any
:class:`Stylable <enaml.styling.Stylable>` object. The base
:class:`Widget <enaml.widgets.widget.Widget>` class inherits the
:class:`Stylable <enaml.styling.Stylable>` class, so all standard Enaml
widgets support style sheets. A widgets effective style sheet is computed
by merging the widget's style sheet with all ancestor style sheets, and
finally with the application stylesheet.

When a conflict arises between style sheets, a widget's own style sheet takes
precedence over any ancestor style sheet or the application style sheet,
regardless of the specifity of the match in the conflicting sheet. This chain
of stylesheets is know as the cascade, and provides a very powerful and
flexible approach to styling. For example, it allows a developer to write an
application-wide style sheet which covers most cases, and selectively override
rules for particular widgets on a case-by-case basis.

The following simple example shows style sheet cascading in action:

.. container:: code-and-img

    .. code-block:: enaml

        enamldef AppSheet(StyleSheet):
            Style:
                element = 'PushButton'
                Setter:
                    property = 'color'
                    value = 'blue'


        enamldef View(Window):
            title = 'Style Sheet'
            Container:
                Container:
                    padding = 0
                    StyleSheet:
                        Style:
                            element = 'PushButton'
                            Setter:
                                property = 'color'
                                value = 'red'
                    PushButton:
                        text = 'One'
                    PushButton:
                        text = 'Two'
                PushButton:
                    text = 'Three'
                PushButton:
                    text = 'Four'
                PushButton:
                    text = 'Five'
                    StyleSheet:
                        Style:
                            Setter:
                                property = 'color'
                                value = 'green'


        def main():
            app = QtApplication()
            app.style_sheet = AppSheet()
            view = View()
            view.show()
            app.start()

    .. image:: /images/cascade_style.png
        :align: center


Pseudeo-Classes
^^^^^^^^^^^^^^^

A pseudo-class augments a style selector to require that an element have a
special state in order for the style to be a match. Usually, this state will
be the result of some external user interaction and may not be reflected in
the structure of the view. For example the ``'hover'`` pseudo-state will cause
the style to only match an element when the user hovers the mouse over it.

Pseudo-classes are specified by assigning a string to the ``pseudo_class``
attribute of a :class:`Style <enaml.styling.Style>` object. Multiple
pseudo-classes can be chained together with a colon, which will match using
logical AND semantics. A pseudo-class can also be negated with the exclamation
operator.

See the :ref:`list_of_pseudo_classes` reference section for the list of
supported pseudo-classes.

A following simple example demonstrates the use of pseudo-classes.

.. container:: code-and-img

    .. code-block:: enaml

        enamldef Main(Window):
            title = 'Style Sheet'
            StyleSheet:
                Style:
                    element = 'CheckBox'
                    pseudo_class = 'checked'
                    Setter:
                        property = 'color'
                        value = 'indianred'
                Style:
                    element = 'Field'
                    pseudo_class = 'focus'
                    Setter:
                        property = 'color'
                        value = 'green'
            Container:
                CheckBox:
                    text = 'One'
                CheckBox:
                    text = 'Two'
                Field:
                    text = 'Three'

    .. image:: /images/pseudo_class_style.png
        :align: center


Pseduo-Elements
^^^^^^^^^^^^^^^


Dynamism
^^^^^^^^

As the examples in this article have shown, all of the classes which are used
to define an Enaml style sheet are declarative; just like the standard Enaml
widget classes. This means that all of Enaml's language and framework features,
such as subscription operators, templates,
:class:`Include <enaml.core.include.Include>`,
:class:`Looper <enaml.core.looper.Looper>`, etc. work with style sheets in the
same way that they work with widgets. This gives the developer unlimited
flexibility in defining the styling for an application.


Inheritance
^^^^^^^^^^^

In typical CSS, properties like ``font`` and ``color``, unless specified,
will be inherited from a parent element. Other properties can be forcibly
inherited with the ``inherit`` keyword. With Enaml stylesheets, inhertance is
not supported in any form. Developers should rely on :ref:`cascading` and
:ref:`specificity` to style their applications appropriately.


Reference
---------

.. _list_of_properties:

List of Properties
^^^^^^^^^^^^^^^^^^


.. _list_of_pseudo_classes:

List of Pseudo-Classes
^^^^^^^^^^^^^^^^^^^^^^


.. _list_of_pseudo_elements:

List of Pseudo-Elements
^^^^^^^^^^^^^^^^^^^^^^^


Examples
--------
