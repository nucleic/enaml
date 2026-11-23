w = range(10)
match w:
    case [x, y, *rest]:
        z = 0

w = range(100)
match w:
    case (x, y, *rest):
        z = 0

w = range(1000)
match w:
    case x, y, *rest:
        z = 0

w = range(1 << 10)
match w:
    case [x, y, *_]:
        z = 0

w = range(1 << 20)
match w:
    case (x, y, *_):
        z = 0

w = range(1 << 30)
match w:
    case x, y, *_:
        z = 0
