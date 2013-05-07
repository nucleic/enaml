.. _grammar-ref:

|Enaml| Grammar Reference
=========================

Five operators have special meaning in |Enaml| syntax:
:ref:`assignment<def-assignment-opr>`, :ref:`delegation<delegation-opr>`,
:ref:`subscription<subscription-opr>`, :ref:`update<update-opr>`
and :ref:`notification<notification-opr>`


.. _def-assignment-opr:

"\=" Default Assignment Operator
--------------------------------
Use when you want to initialize the left hand side only once. Supports full
Python expression syntax on the right hand side.

Example::

    enamldef MyView(Container):
        Label:
            text = "My Label's Text"


.. _delegation-opr:

":=" Delegation Operator
------------------------
Use when you want a bidirectional syncronization between a variable/ui-element
on the left hand side and an assignable expression on the right hand side.
Supports 'assignable' expressions on the right hand side. Assignable
expressions are expressions that can be used on the left hand side of the
Python "\=" operator. ``getattr`` is also supported as a special case and is
equivalent to an attribute access expression.

Example::

    enamldef MyView(Container):
        attr model

        CheckBox:
            text = "Enabled"
            checked := model.enabled


.. _subscription-opr:

"<<" Subscription Operator
--------------------------
Use when you want a variable/ui-element on the left hand side to subscribe to
the external world. Supports full Python expression syntax on right hand side.

Example::

    enamldef MyView(Container):
        attr model

        ProgressBar:
            value << int(model.progress_percentage) + 1


.. _update-opr:

">>" Update Operator
--------------------
Use when you want to notify the external world about any changes in a
variable/ui-element. Supports 'assignable' expressions on the right hand side.
Assignable expressions are expressions that can be used on left hand side of
Python "\=" operator. ``getattr`` is also supported as a special case and is
set to be equivalent to an attribute assignment expression.

Example::

    enamldef MyView(Container):
        attr model

        Slider:
            value >> model.value


.. _notification-opr:

"::" Notification Operator
--------------------------
Use when you just want to execute multiple statements whenever a
variable/ui-element changes. '::' supports full Python grammar except:
'def', 'class', 'lambda', 'return', and 'yield' on the right hand side.

Example::

    enamldef MyView(Container):
        PushButton:
            text = "Click Me!"
            clicked ::
                print "Somebody clicked me!"
                do_something_about_it()
        PushButton:
            text = "Click Me Too!"
            clicked :: print "Single line statement!"

