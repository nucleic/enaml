# Enaml grammar fixtures

This directory stores Enaml programs that should parse successfully as part of the corpus-based validation layer.

Fixtures are organized by grammar area so they are easier to extend incrementally:

- attributes
- bindings
- functions
- templates
- widgets
- other structural Enaml syntax

The goal is to keep the broad grammar acceptance checks readable and maintainable rather than hiding them inside unrelated parser tests.
