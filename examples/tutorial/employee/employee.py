#------------------------------------------------------------------------------
# Copyright (c) 2013, Nucleic Development Team.
#
# Distributed under the terms of the Modified BSD License.
#
# The full license is in the file LICENSE, distributed with this software.
#------------------------------------------------------------------------------
from __future__ import print_function

import datetime

from atom.api import Atom, Str, Range, Bool, Value, Int, Tuple, observe
import enaml
from enaml.qt.qt_application import QtApplication


class Person(Atom):
    """ A simple class representing a person object.

    """
    last_name = Str()

    first_name = Str()

    age = Range(low=0)

    dob = Value(datetime.date(1970, 1, 1))

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
            print(s)

    @observe('dob')
    def update_age(self, change):
        """ Update the person's age whenever their date of birth changes

        """
        # grab the current date time
        now = datetime.datetime.utcnow()
        # estimate the person's age within one year accuracy
        age = now.year - self.dob.year
        # check to see if the current date is before their birthday and
        # subtract a year from their age if it is
        if ((now.month == self.dob.month and now.day < self.dob.day)
            or now.month < self.dob.month):
                age -= 1
        # set the persons age
        self.age = age


class Employer(Person):
    """ An employer is a person who runs a company.

    """
    # The name of the company
    company_name = Str()


class Employee(Person):
    """ An employee is person with a boss and a phone number.

    """
    # The employee's boss
    boss = Value(Employer)

    # The employee's phone number as a tuple of 3 ints
    phone = Tuple(Int())

    # This method will be called automatically by atom when the
    # employee's phone number changes
    def _observe_phone(self, val):
        print('received new phone number for %s: %s' % (self.first_name, val))


def main():
    # Create an employee with a boss
    boss_john = Employer(
        first_name='John', last_name='Paw', company_name="Packrat's Cats",
    )
    employee_mary = Employee(
        first_name='Mary', last_name='Sue', boss=boss_john,
        phone=(555, 555, 5555),
    )

    # Import our Enaml EmployeeView
    with enaml.imports():
        from employee_view import EmployeeView

    app = QtApplication()
    # Create a view and show it.
    view = EmployeeView(employee=employee_mary)
    view.show()

    app.start()

if __name__ == '__main__':
    main()
