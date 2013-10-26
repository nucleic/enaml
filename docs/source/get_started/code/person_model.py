# person_model.py
from atom.api import Atom, Unicode

class Person(Atom):
    first_name = Unicode()
    last_name = Unicode()
