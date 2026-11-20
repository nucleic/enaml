match ():
    case []:
        x = 0

match (0, 1, 2):
    case [*x]:
        y = 0

match (0, 1, 2):
    case [0, *x]:
        y = 0

match (0, 1, 2):
    case [0, 1, *x,]:
        y = 0

match (0, 1, 2):
    case [0, 1, 2, *x]:
        y = 0

match (0, 1, 2):
    case [*x, 2,]:
        y = 0

match (0, 1, 2):
    case [*x, 1, 2]:
        y = 0

match (0, 1, 2):
    case [*x, 0, 1, 2,]:
        y = 0

match (0, 1, 2):
    case [0, *x, 2]:
        y = 0

match (0, 1, 2):
    case [0, 1, *x, 2,]:
        y = 0

match (0, 1, 2):
    case [0, *x, 1, 2]:
        y = 0

match (0, 1, 2):
    case [*x,]:
        y = 0
