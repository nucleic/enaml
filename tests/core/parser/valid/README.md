# Parser validation fixtures

This directory contains the validation corpus used to bring the Enaml parser
closer to the pegen-style parser test model.

The structure is intentionally split into two categories:

- `python/`: Python source snippets used to validate compatibility with the standard library AST behavior.
- `enaml/`: Enaml grammar fixtures exercised as parser acceptance checks for grammar coverage.

Fixtures are discovered recursively. Files are named for the syntax family they
exercise, and a directory can group the focused files formerly kept together in
one large fixture. Blank lines are ordinary source whitespace and are not used
as fixture delimiters.

This keeps the broad corpus separate from the targeted regression tests already
present in the surrounding `tests/core/parser` modules.
