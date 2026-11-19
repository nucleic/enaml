x = False
match x:
    case bool(z):
        y = 0

x = True
match x:
    case bool(z):
        y = 0

x = bytearray()
match x:
    case bytearray(z):
        y = 0

x = b""
match x:
    case bytes(z):
        y = 0

x = {}
match x:
    case dict(z):
        y = 0

x = 0.0
match x:
    case float(z):
        y = 0

x = frozenset()
match x:
    case frozenset(z):
        y = 0

x = 0
match x:
    case int(z):
        y = 0

x = []
match x:
    case list(z):
        y = 0

x = set()
match x:
    case set(z):
        y = 0

x = ""
match x:
    case str(z):
        y = 0

x = ()
match x:
    case tuple(z):
        y = 0
