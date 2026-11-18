a = (k for k in g)
b = (k for k in g if k == 1)
(k for k in g).send(None)


a = [k for k in g]
b = [k for k in g if k == 1]


a = {k for k in g}
b = {k for k in g if k == 1}
a = {k: 1 for k in g}
b = {k: 2 for k in g if k == 1}


[k for v in a for k in v]
[x for xs in ys for x in xs if x]
{x for x in xs for y in ys if x != y}
