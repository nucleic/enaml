x = 0
match x:
    case 0 if not (x := 1):
        y = 0
    case (0 as z):
        y = 1

x = 0
match x:
    case (1 as z) if not (x := 1):
        y = 0
    case 0:
        y = 1

x = 0
match x:
    case (0 as z):
        y = 0

x = 0
y = None
match x:
    case (1 as z):
        y = 0

x = 0
y = None
match x:
    case (0 as z) if (w := 0):
        y = 0

x = 0
match x:
    case ((0 as w) as z):
        y = 0

x = 0
match x:
    case (0 | 1) | 2:
        y = 0

x = 1
match x:
    case (0 | 1) | 2:
        y = 0

x = 2
match x:
    case (0 | 1) | 2:
        y = 0

x = 3
y = None
match x:
    case (0 | 1) | 2:
        y = 0

x = 0
match x:
    case 0 | (1 | 2):
        y = 0

x = 1
match x:
    case 0 | (1 | 2):
        y = 0

x = 2
match x:
    case 0 | (1 | 2):
        y = 0

x = 3
y = None
match x:
    case 0 | (1 | 2):
        y = 0
