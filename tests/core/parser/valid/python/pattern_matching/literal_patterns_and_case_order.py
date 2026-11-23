x = 0
match x:
    case 0:
        y = 0

x = 0
y = None
match x:
    case False:
        y = 0

x = 0
y = None
match x:
    case 1:
        y = 0

x = 0
y = None
match x:
    case None:
        y = 0

x = 0
match x:
    case 0:
        y = 0
    case 0:
        y = 1

x = 0
y = None
match x:
    case 1:
        y = 0
    case 1:
        y = 1

x = "x"
match x:
    case "x":
        y = 0
    case "y":
        y = 1

x = "x"
match x:
    case "y":
        y = 0
    case "x":
        y = 1

x = "x"
match x:
    case "":
        y = 0
    case "x":
        y = 1

x = b"x"
match x:
    case b"y":
        y = 0
    case b"x":
        y = 1

x = 0
match x:
    case 0 if False:
        y = 0
    case 0:
        y = 1

x = 0
y = None
match x:
    case 0 if 0:
        y = 0
    case 0 if 0:
        y = 1

x = 0
match x:
    case 0 if True:
        y = 0
    case 0 if True:
        y = 1

x = 0
match x:
    case 0 if 1:
        y = 0
    case 0 if 1:
        y = 1

x = 0
match x:
    case 0 if True:
        y = 0
    case 0 if True:
        y = 1
y = 2

x = 0
match x:
    case 0 if 0:
        y = 0
    case 0 if 1:
        y = 1
y = 2

x = 0
y = None
match x:
    case 0 if not (x := 1):
        y = 0
    case 1:
        y = 1
