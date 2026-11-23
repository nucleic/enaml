x = 0
match x,:
    case y,:
        z = 0

w = 0
x = 0
match w, x:
    case y, z:
        v = 0

x = 0
match w := x,:
    case y as v,:
        z = 0

x = 0
y = None
match x:
    case 0 if x:
        y = 0

x = 0
y = None
match x:
    case 1e1000:
        y = 0
