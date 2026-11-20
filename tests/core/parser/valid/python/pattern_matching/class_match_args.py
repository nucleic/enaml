class Class:
    __match_args__ = ("a", "b")
c = Class()
c.a = 0
c.b = 1
match c:
    case Class(x, y):
        z = 0

class Class:
    __match_args__ = ("a", "b")
c = Class()
c.a = 0
c.b = 1
match c:
    case Class(x, b=y):
        z = 0

class Parent:
    __match_args__ = "a", "b"
class Child(Parent):
    __match_args__ = ("c", "d")
c = Child()
c.a = 0
c.b = 1
match c:
    case Parent(x, y):
        z = 0

class Parent:
    __match_args__ = ("a", "b")
class Child(Parent):
    __match_args__ = "c", "d"
c = Child()
c.a = 0
c.b = 1
match c:
    case Parent(x, b=y):
        z = 0
