# Python parser compatibility fixtures

This directory stores Python snippets that are intended to be parsed by the
Enaml parser and compared against the stdlib `ast` module.

Each file is parsed once as a complete Python module. Fixtures are grouped by
language feature in directories and have descriptive filenames such as
`statements/for_statement.py`. Do not use a run of blank lines to delimit
independent test cases; create another file instead.

Some directories cover syntax gated to newer Python versions. Their relative
paths are used when applying the corresponding pytest skip marks on older
interpreters.

The EOF regression fixtures at this directory's root intentionally preserve
their missing-final-newline property and should remain single, focused files.
