class Namespace:
    class Point:
        __match_args__ = ("x", "y")

match value:
    case Namespace.Point(x, y=y):
        result = x, y

match = case = 0
match match:
    case case:
        x = 0

match = case = 0
match case:
    case match:
        x = 0

x = []
match x:
    case [*_, _]:
        y = 0
    case []:
        y = 1

x = collections.defaultdict(int)
match x:
    case {0: 0}:
        y = 0
    case {}:
        y = 1

x = collections.defaultdict(int)
match x:
    case {0: 0}:
        y = 0
    case {**z}:
        y = 1
