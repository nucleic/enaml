x = ()
match x:
    case []:
        y = 0

x = ()
match x:
    case ():
        y = 0

x = (0,)
match x:
    case [0]:
        y = 0

x = ((),)
match x:
    case [[]]:
        y = 0

x = [0, 1]
match x:
    case [0, 1] | [1, 0]:
        y = 0

x = [1, 0]
match x:
    case [0, 1] | [1, 0]:
        y = 0

x = [0, 0]
y = None
match x:
    case [0, 1] | [1, 0]:
        y = 0

w = None
x = [1, 0]
match x:
    case [(0 as w)]:
        y = 0
    case [z] | [1, (0 | 1 as z)] | [z]:
        y = 1

x = [1, 0]
match x:
    case [0]:
        y = 0
    case [1, 0] if (x := x[:0]):
        y = 1
    case [1, 0]:
        y = 2

x = {0}
y = None
match x:
    case [0]:
        y = 0

x = set()
y = None
match x:
    case []:
        y = 0

x = iter([1, 2, 3])
y = None
match x:
    case []:
        y = 0

x = {}
y = None
match x:
    case []:
        y = 0

x = {0: False, 1: True}
y = None
match x:
    case [0, 1]:
        y = 0
