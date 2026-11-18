a = b
a += b
a -= b
a *= b
a /= b
a //= b
a %= b
a |= b
a ^= b
a **= b
a &= b
a @= b
a <<= b
a >>= b
a += yield



(a) += 1
a[1] += 1
a.b += 1
a.b.c += 1
f(i for i in range(2)).a += 1
f().a += 1



(a) = 1
a.b = 1
a.b.c = 1
a.b.c.d = 1
a[b] = c
a[b][c] = 1
a.b[c] = 1
a[1:] = b
a[:1] = b
a[1:10:2] = b



a: int = b
a: int = yield
a.b: int
a.b: int = 1
a[b]: int = 1
a[b]: int = 1
a = 1
a = 1.0



a = ""
a = u""
a = r"\c"
a = b"a"
a = f"{a}"
a = f"{d}" "rr"
a = "rr" f"{d}" "rr"



a = ()
a = (1,)
a = (1, 2)



b = []
b = [
    1,
]
b = [1, 2]



c = {
    1,
}
c = {1, 2}
d = {}
d = {1: 2}
d = {
    1: 2,
}
d = {1: 2, 3: 4}



a = True
b = False
c = None



d = *a, (*b, c)
d = *a, (*b, *c)



f = (a := 1)



a, b = c
a, *b = c
a, *b, d = c
a, *b, d = yield d
