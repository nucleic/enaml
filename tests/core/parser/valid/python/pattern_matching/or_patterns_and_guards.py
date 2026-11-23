x = False
match 0:
    case 0 | 1 | 2 | 3:
        x = True

x = False
match 1:
    case 0 | 1 | 2 | 3:
        x = True

x = False
match 2:
    case 0 | 1 | 2 | 3:
        x = True

x = False
match 3:
    case 0 | 1 | 2 | 3:
        x = True

x = False
match 4:
    case 0 | 1 | 2 | 3:
        x = True

x = 0
class A:
    y = 1
match x:
    case A.y:
        pass

x = 0
class A:
    y = 1
match x:
    case A.y as z:
        pass

class A:
    B = 0
match 0:
    case x if x:
        z = 0
    case _ as y if y == x and y:
        z = 1
    case A.B:
        z = 2
