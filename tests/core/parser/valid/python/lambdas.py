lambda: 1

lambda x: x

lambda x,: x

lambda x=1: x

lambda x, y: x + y

lambda x, /: x

lambda x, y=1, /: x + y

lambda x, /, y: x + y

lambda x, /, y=1, z=2: x + y + z

lambda x, y=1, /, z=5: x + y + z

lambda x=1, /, *y: x + y

lambda x, *, y: x + y

lambda x, *, y, z: x + y + z

lambda *, x: x

lambda *x: x

lambda **x: x

lambda x, **y: y
