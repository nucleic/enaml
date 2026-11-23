x = "x"
match x:
    case ["x"]:
        y = 0
    case "x":
        y = 1

x = b"x"
match x:
    case [b"x"]:
        y = 0
    case ["x"]:
        y = 1
    case [120]:
        y = 2
    case b"x":
        y = 4

x = bytearray(b"x")
y = None
match x:
    case [120]:
        y = 0
    case 120:
        y = 1

x = ""
match x:
    case []:
        y = 0
    case [""]:
        y = 1
    case "":
        y = 2

x = "xxx"
match x:
    case ["x", "x", "x"]:
        y = 0
    case ["xxx"]:
        y = 1
    case "xxx":
        y = 2

x = b"xxx"
match x:
    case [120, 120, 120]:
        y = 0
    case [b"xxx"]:
        y = 1
    case b"xxx":
        y = 2
