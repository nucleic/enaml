# Python parser compatibility fixtures

This directory stores Python snippets that are intended to be parsed by the Enaml parser and compared against the stdlib `ast` module.

These fixtures are the foundation of the pegen-style valid-corpus migration. They should be grouped by language feature rather than by ad hoc file name alone.

Examples include assignment, function definitions, comprehensions, async syntax, and version-gated grammar features.

The corpus includes modern Python grammar cases such as template strings, walrus expressions, async syntax, and function definitions, and compares their AST output directly against the stdlib parser.
