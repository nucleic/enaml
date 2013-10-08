from setuptools import setup, find_packages


setup (
  name='enamllexer',
  packages=find_packages(),
  entry_points =
  """
 [pygments.lexers]
 enamllexer = enamllexer.lexer:EnamlLexer
 """,
)
