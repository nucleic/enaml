a = 10
t'{a * x()}'



t'no formatted values'
t'eggs {a * x()} spam {b + y()}'



a = 10
t'{a * x()} {a * x()} {a * x()}'



a = 10
t'''
  {a
     *
       x()}
non-important content
'''



a = t'''
          {blech}
    '''



x = (
    t" {test(t)}"
)



x = (
    u'wat',
    u"wat",
    b'wat',
    b"wat",
    t'wat',
    t"wat",
)
y = (
    u'''wat''',
    u"""wat""",
    b'''wat''',
    b"""wat""",
    t'''wat''',
    t"""wat""",
)



x = (
        'PERL_MM_OPT', (
            t'wat'
            t'some_string={f(x)} '
            t'wat'
        ),
)



t'{expr:}'
t'{expr:d}'
foo = 3.14159
verbosePrint(t'Foo {foo:.3} bar.')


# Raw t-strings
rt'{a}\n'
tr'{a}\n'

# Format specifiers
x = 3
t'{x!r}'
t'{x!r:{width}}'
t'{x!s}'
t'{x!a}'



# Debug marker
x = 2
t'{x=}'
t'{ x = }'
t'{x+1=}'
t'{x=:>3}'
t'{x=:}'
t'''
{x=}
'''



# Parenthesized lambda expressions are valid inside t-string fields
x = t'{(lambda x: x)}'



# Nested format specifiers
x = y = z =2
t'{x:{y}}'
t'{x:{y}{z}}'
t'{x:{y}:z}'
t'{x:{y}{z}{q}}'
