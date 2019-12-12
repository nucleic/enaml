# person_model.py
from atom.api import Atom, Str

class Person(Atom):
    first_name = Str()
    last_name = Str()
