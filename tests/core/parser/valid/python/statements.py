pass
pass;
x = 1, 2, 3



assert a
assert a; assert b
assert a, "eee"



raise RuntimeError
raise RuntimeError from e



def f():
    return
def f():
    return 1
def f():
    return 1,



del a
del (a)
del a, b
del a, b,
del a[:]
del a.b
del (a,)
del (a, b)
del [a, b]
del a;



global a
global a, b
nonlocal a
nonlocal a, b



yield a
yield from a



for i in a:
    pass

for i, in a:
    pass

for (i,) in a:
    pass

for (i,), in a:
    pass

for i, *j in a:
    pass

for i, (a, *b) in a:
    pass


async def f():
    async for i in a:
        pass

    async for i, in a:
        pass

    async for (i,) in a:
        pass

    async for (i,), in a:
        pass

    async for i, *j in a:
        pass

    async for i, (a, *b) in a:
        pass



for i in b:
    pass
else:
    pass



if a:
    b=1

if a:
    pass
else:
    pass

if a:
    pass
elif b:
    pass
else:
    pass

if a:
    pass
elif b:
    pass
elif c:
    pass



while s:
    pass

while False:
    pass
else:
    pass



for i in a:
    continue

for i in a:
    break



with a:
    pass

with a, b:
    pass

with a as b:
    pass

with a as b, c:
    pass


async def g():
    async with a:
        pass

    async with a, b:
        pass

    async with a as b:
        pass

    async with a as b, c:
        pass



try:
    pass
finally:
    pass

try:
    pass
except:
    raise
finally:
    pass

try:
    pass
except ValueError:
    pass
except (IndexError, RuntimeError,):
    pass
except Exception as e:
    pass
else:
    pass
finally:
    pass
