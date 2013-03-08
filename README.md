==============================
Enaml is not a Markup Language
==============================
**E**\naml is **N**\ot **A** **M**\arkup **L**\anguage. Enaml is a library for
creating rich declarative user interfaces. Enaml combines a domain specific
declarative language with a constraints based layout system to allow users to
easily define rich UIs with complex and flexible layouts. Enaml applications
can be deployed on Windows, OSX, and Linux.

Other great Enaml features include

    1) Declarative UI specification langauge which is a strict superset of Python
    2) Architecture design which encourages Model-View separation
    3) Subscription based operators which allow state changes to freely flow between models and views
    4) Ability to easily subclass widgets to override functionality of builtin widgets
    5) Support for custom UI widgets
    6) Class based widget design encourages re-use of UI code
    7) Well documented code base that is easy to understand

Enaml is heavily inspired by Qt's QML system, but Enaml uses desktop widgets
for rendering instead of drawing on a 2D canvas.

Enaml is extensible and makes it extremely easy for the user to define
their own widgets, override existing widgets, create a new backend toolkit,
or even hook the runtime to apply their own expression dependency behavior.
About the only thing not hookable is the Enaml language syntax itself.

The enamldoc package provides a Sphinx extension for documenting Enaml objects.

Prerequisites
-------------
* Python >= 2.6 (not Python 3)
* Atom (https://github.com/nucleic/atom)
* PySide or PyQt4
* Casuarius (https://github.com/enthought/casuarius)
* PLY (Python Lex-Yacc)
* Sphinx (only if building the docs)
