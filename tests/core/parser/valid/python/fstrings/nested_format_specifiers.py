# Nested format specifiers
x = y = z =2
f'{x:{y}}'
f'{x:{y}{z}}'
f'{x:{y}:z}'
f'{x:{y}{z}{q}}'
