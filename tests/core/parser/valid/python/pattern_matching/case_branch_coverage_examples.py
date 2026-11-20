match 42:
    case 42:
        return locals()

match 1:
    case 1 | 2 | 3:
        return locals()

match ...:
    case _:
        return locals()

match ...:
    case abc:
        return locals()

match ..., ...:
    case a, b:
        return locals()

match {"k": ..., "l": ...}:
    case {"k": a, "l": b}:
        return locals()

match MyClass(..., ...):
    case MyClass(x, y=y):
        return locals()

match ...:
    case b as a:
        return locals()

match x:
    case _:
        return 0

match x:
    case 0:
        return 0

match x:
    case 0:
        return 0
    case _:
        return 1

match x:
    case 0:
        return 0
    case 1:
        return 1

match x:
    case 0:
        return 0
    case 1:
        return 1
    case _:
        return 2

match x:
    case 0:
        return 0
    case 1:
        return 1
    case 2:
        return 2
