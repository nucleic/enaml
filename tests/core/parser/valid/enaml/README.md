# Enaml grammar fixtures

This directory stores Enaml programs that should parse successfully as part of the corpus-based validation layer.

Fixtures are kept as a single file per grammar construct at the root of this directory so the accepted syntax is easy to scan and extend without artificial "basic_" prefixes:

- attributes.enaml
- bindings.enaml
- events.enaml
- functions.enaml
- templates.enaml
- async.enaml
- other Enaml syntax files that represent a single construct or family

The goal is to keep the broad grammar acceptance checks readable and maintainable rather than hiding them inside unrelated parser tests.
