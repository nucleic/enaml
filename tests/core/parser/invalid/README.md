# Invalid parser fixtures

Files below `python/` and `enaml/` are source fixtures for syntax that must be
rejected by the Enaml parser. They are not importable Python modules.

Each fixture starts with flat TOML keys encoded in comments. The header records
the expected diagnostic, parser target version, source locations, runtime
version variants, and skip bounds. Runtime variants use an `expectations` array
of inline TOML tables. The `# --- source ---` marker ends the metadata;
everything after it is passed to the parser unchanged.

Create one file per invalid program and place it in the directory named for the
syntax family it exercises. Do not import these files or use blank lines as
case delimiters. The fixture loader recursively discovers them and reports the
complete relative path when a case fails.

Diagnostics specifically concerned with a missing indented block are grouped
below `python/indentation/`, subdivided by the surrounding statement family.
