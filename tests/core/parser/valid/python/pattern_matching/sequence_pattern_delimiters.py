match ():
    case ():
        x = 0

match (0, 1, 2):
    case (*x,):
        y = 0

match (0, 1, 2):
    case 0, *x:
        y = 0

match (0, 1, 2):
    case (0, 1, *x,):
        y = 0

match (0, 1, 2):
    case 0, 1, 2, *x:
        y = 0

match (0, 1, 2):
    case *x, 2,:
        y = 0

match (0, 1, 2):
    case (*x, 1, 2):
        y = 0

match (0, 1, 2):
    case *x, 0, 1, 2,:
        y = 0

match (0, 1, 2):
    case (0, *x, 2):
        y = 0

match (0, 1, 2):
    case 0, 1, *x, 2,:
        y = 0

match (0, 1, 2):
    case (0, *x, 1, 2):
        y = 0

match (0, 1, 2):
    case *x,:
        y = 0

x = collections.defaultdict(int, {0: 1})
match x:
    case {1: 0}:
        y = 0
    case {0: 0}:
        y = 1
    case {}:
        y = 2

x = collections.defaultdict(int, {0: 1})
match x:
    case {1: 0}:
        y = 0
    case {0: 0}:
        y = 1
    case {**z}:
        y = 2

x = collections.defaultdict(int, {0: 1})
match x:
    case {1: 0}:
        y = 0
    case {0: 0}:
        y = 1
    case {0: _, **z}:
        y = 2

x = {0: 1}
match x:
    case {1: 0}:
        y = 0
    case {0: 0}:
        y = 0
    case {}:
        y = 1

x = {0: 1}
match x:
    case {1: 0}:
        y = 0
    case {0: 0}:
        y = 0
    case {**z}:
        y = 1

x = {0: 1}
match x:
    case {1: 0}:
        y = 0
    case {0: 0}:
        y = 0
    case {0: _, **z}:
        y = 1
