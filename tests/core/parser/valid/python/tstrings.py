a = 10
t"{a * x()}"

t"no formatted values"
t"eggs {a * x()} spam {b + y()}"

# Raw t-strings
rt"{a}\n"
rt"{a}\n"

x = 2
t"{x=}"
t"{x:{y}}"
