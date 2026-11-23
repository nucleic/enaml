x = 0
match x:
    case 0 | 1 | 2:
        y = 0

x = 1
match x:
    case 0 | 1 | 2:
        y = 0

x = 2
match x:
    case 0 | 1 | 2:
        y = 0

x = 3
y = None
match x:
    case 0 | 1 | 2:
        y = 0

x = 0
match x:
    case (0 as z) | (1 as z) | (2 as z) if z == x % 2:
        y = 0

x = 1
match x:
    case (0 as z) | (1 as z) | (2 as z) if z == x % 2:
        y = 0

x = 2
y = None
match x:
    case (0 as z) | (1 as z) | (2 as z) if z == x % 2:
        y = 0

x = 3
y = None
match x:
    case (0 as z) | (1 as z) | (2 as z) if z == x % 2:
        y = 0
