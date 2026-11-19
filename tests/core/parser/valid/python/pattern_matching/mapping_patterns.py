x = {}
match x:
    case {}:
        y = 0

x = {0: 0}
match x:
    case {}:
        y = 0

x = {}
y = None
match x:
    case {0: 0}:
        y = 0

x = {0: 0}
match x:
    case {0: (0 | 1 | 2 as z)}:
        y = 0

x = {0: 1}
match x:
    case {0: (0 | 1 | 2 as z)}:
        y = 0

x = {0: 2}
match x:
    case {0: (0 | 1 | 2 as z)}:
        y = 0

x = {0: 3}
y = None
match x:
    case {0: (0 | 1 | 2 as z)}:
        y = 0

x = {}
y = None
match x:
    case {0: [1, 2, {}]}:
        y = 0
    case {0: [1, 2, {}], 1: [[]]}:
        y = 1
    case []:
        y = 2

x = {False: (True, 2.0, {})}
match x:
    case {0: [1, 2, {}]}:
        y = 0
    case {0: [1, 2, {}], 1: [[]]}:
        y = 1
    case []:
        y = 2

x = {False: (True, 2.0, {}), 1: [[]], 2: 0}
match x:
    case {0: [1, 2, {}]}:
        y = 0
    case {0: [1, 2, {}], 1: [[]]}:
        y = 1
    case []:
        y = 2

x = {False: (True, 2.0, {}), 1: [[]], 2: 0}
match x:
    case {0: [1, 2]}:
        y = 0
    case {0: [1, 2, {}], 1: [[]]}:
        y = 1
    case []:
        y = 2

x = []
match x:
    case {0: [1, 2, {}]}:
        y = 0
    case {0: [1, 2, {}], 1: [[]]}:
        y = 1
    case []:
        y = 2

x = {0: 0}
match x:
    case {0: [1, 2, {}]}:
        y = 0
    case {0: ([1, 2, {}] | False)} | {1: [[]]} | {0: [1, 2, {}]} | [] | "X" | {}:
        y = 1
    case []:
        y = 2

x = {0: 0}
match x:
    case {0: [1, 2, {}]}:
        y = 0
    case {0: [1, 2, {}] | True} | {1: [[]]} | {0: [1, 2, {}]} | [] | "X" | {}:
        y = 1
    case []:
        y = 2

x = {0: 0}
match x:
    case {None: 1}:
        y = 0
    case {True: 1}:
        y = 0
    case {False: 1}:
        y = 0
    case {1 + 1j: 1}:
        y = 0
    case {a.b: 1}:
        y = 0
