from setuptools import setup, find_packages


setup (
  name='enamllexer',
  version='0.1.0',
  packages=find_packages(),
  entry_points =
  """
 [pygments.lexers]
 enamllexer = enamllexer.lexer:EnamlLexer
 """,
)
