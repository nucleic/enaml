from setuptools import setup, find_packages


setup (
  name='pygments-enaml',
  version='0.1.0',
  packages=find_packages(),
  install_requires=['pygments'],
  entry_points=
  """
 [pygments.lexers]
 enaml = pygments_enaml.lexer:EnamlLexer
 """,
)
