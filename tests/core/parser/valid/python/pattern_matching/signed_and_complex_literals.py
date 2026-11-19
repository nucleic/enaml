x = 0
match x:
    case -0:
        y = 0

x = 0
match x:
    case -0.0:
        y = 0

x = 0
match x:
    case -0j:
        y = 0

x = 0
match x:
    case -0.0j:
        y = 0

x = -1
match x:
    case -1:
        y = 0

x = -1.5
match x:
    case -1.5:
        y = 0

x = -1j
match x:
    case -1j:
        y = 0

x = -1.5j
match x:
    case -1.5j:
        y = 0

x = 0
match x:
    case 0 + 0j:
        y = 0

x = 0
match x:
    case 0 - 0j:
        y = 0

x = 0
match x:
    case -0 + 0j:
        y = 0

x = 0
match x:
    case -0 - 0j:
        y = 0

x = 0.25 + 1.75j
match x:
    case 0.25 + 1.75j:
        y = 0

x = 0.25 - 1.75j
match x:
    case 0.25 - 1.75j:
        y = 0

x = -0.25 + 1.75j
match x:
    case -0.25 + 1.75j:
        y = 0

x = -0.25 - 1.75j
match x:
    case -0.25 - 1.75j:
        y = 0
