# main.py
import enaml
from enaml.qt.qt_application import QtApplication

from person_model import Person


if __name__ == '__main__':
    with enaml.imports():
        from person_view import PersonView

    john = Person(first_name='John', last_name='Doe')

    app = QtApplication()

    view = PersonView(person=john)
    view.show()

    app.start()
