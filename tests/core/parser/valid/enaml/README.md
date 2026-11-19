# Enaml grammar fixtures

This directory stores Enaml programs that should parse successfully as part of the corpus-based validation layer.

Fixtures are organized into a directory per former corpus file, with a
descriptive file for each grammar construct or closely related family:

- `operators/one_way_binding.enaml`
- `functions/keyword_only.enaml`
- `templates/typed_parameter.enaml`
- `pragmas/body_pragma.enaml`

Files are discovered recursively and parsed and compiled as complete programs.
Blank lines are ordinary Enaml source whitespace rather than test delimiters.
