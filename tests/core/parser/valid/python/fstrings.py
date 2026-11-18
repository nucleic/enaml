a = 10
f'{a * x()}'



f'no formatted values'
f'eggs {a * x()} spam {b + y()}'



a = 10
f'{a * x()} {a * x()} {a * x()}'



a = 10
f'''
  {a
     *
       x()}
non-important content
'''



a = f'''
          {blech}
    '''



x = (
    f" {test(t)}"
)



x = (
    u'wat',
    u"wat",
    b'wat',
    b"wat",
    f'wat',
    f"wat",
)
y = (
    u'''wat''',
    u"""wat""",
    b'''wat''',
    b"""wat""",
    f'''wat''',
    f"""wat""",
)



x = (
        'PERL_MM_OPT', (
            f'wat'
            f'some_string={f(x)} '
            f'wat'
        ),
)



f'{expr:}'
f'{expr:d}'
foo = 3.14159
verbosePrint(f'Foo {foo:.3} bar.')


# Raw f-strings
rf'{a}\n'
fr'{a}\n'

# Format specifiers
x = 3
f'{x!r}'
f'{x!r:{width}}'
f'{x!s}'
f'{x!s:>10}'
f'{x!a}'



# Debug marker
x = 2
f'{x=}'
f'{ x = }'
f'{x+1=}'
f'{x=:>3}'
f'{x=:}'
f'''\n{x=}\n'''



# Parenthesized lambda expressions are valid inside f-string fields
x = f'{(lambda x: x)}'


# Nested format specifiers
x = y = z =2
f'{x:{y}}'
f'{x:{y}{z}}'
f'{x:{y}:z}'
f'{x:{y}{z}{q}}'