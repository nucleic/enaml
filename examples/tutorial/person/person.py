#------------------------------------------------------------------------------
# Copyright (c) 2013, Nucleic Development Team.
#
# Distributed under the terms of the Modified BSD License.
#
# The full license is in the file COPYING.txt, distributed with this software.
#------------------------------------------------------------------------------
from atom.api import Atom, Unicode, Range, Bool, observe

import enaml
from enaml.qt.qt_application import QtApplication


class Person(Atom):
    """ A simple class representing a person object.

    """
    last_name = Unicode()

    first_name = Unicode()

    age = Range(low=0)

    debug = Bool(False)

    @observe('age')
    def debug_print(self, change):
        """ Prints out a debug message whenever the person's age changes.

        """
        if self.debug:
            templ = "{first} {last} is {age} years old."
            s = templ.format(
                first=self.first_name, last=self.last_name, age=self.age,
            )
            print s


if __name__ == '__main__':
    with enaml.imports():
        from person_view import PersonView

    john = Person(first_name='John', last_name='Doe', age=42)
    john.debug = True

    app = QtApplication()
    view = PersonView(person=john)
    view.show()

    app.start()
