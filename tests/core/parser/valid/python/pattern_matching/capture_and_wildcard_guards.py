x = 0
match x:
    case z:
        y = 0

x = 0
y = None
match x:
    case _ if x:
        y = 0

x = 0
match x:
    case -1e1000:
        y = 0
    case 0:
        y = 1

x = 0
match x:
    case 0 if not x:
        y = 0
    case 1:
        y = 1

x = 0
z = None
match x:
    case 0:
        y = 0
    case z if x:
        y = 1

x = 0
match x:
    case 0:
        y = 0
    case _:
        y = 1

x = 0
match x:
    case 1 if x:
        y = 0
    case 0:
        y = 1

x = 0
y = None
match x:
    case 1:
        y = 0
    case 1 if not x:
        y = 1

x = 0
match x:
    case 1:
        y = 0
    case z:
        y = 1

x = 0
match x:
    case 1 if x:
        y = 0
    case _:
        y = 1

x = 0
match x:
    case z if not z:
        y = 0
    case 0 if x:
        y = 1

x = 0
match x:
    case z if not z:
        y = 0
    case 1:
        y = 1

x = 0
match x:
    case z if not x:
        y = 0
    case z:
        y = 1

x = 0
match x:
    case z if not z:
        y = 0
    case _ if x:
        y = 1

x = 0
match x:
    case _ if not x:
        y = 0
    case 0:
        y = 1

x = 0
y = None
match x:
    case _ if x:
        y = 0
    case 1:
        y = 1

x = 0
z = None
match x:
    case _ if not x:
        y = 0
    case z if not x:
        y = 1

x = 0
match x:
    case _ if not x:
        y = 0
    case _:
        y = 1
