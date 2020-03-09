#------------------------------------------------------------------------------
# Copyright (c) 2013, Nucleic Development Team.
#
# Distributed under the terms of the Modified BSD License.
#
# The full license is in the file LICENSE, distributed with this software.
#------------------------------------------------------------------------------
import os
import shutil
import sys
import tempfile


def prep_dir():
    shutil.rmtree('./build', ignore_errors=True)


def build():
    os.system('python setup.py build')


def develop():
    os.system('python setup.py develop')


def install():
    os.system('python setup.py install')


def upload():
    os.system('python setup.py register sdist upload')


def test():
    os.system('python setup.py check -r')
    build()
    os.chdir('./build')
    os.system('nosetests --exe -v')
    os.chdir('..')


def gh_pages():
    temp_dir = tempfile.mkdtemp()
    os.system('git checkout master')
    os.system('git pull origin master')
    shutil.rmtree('./docs/build', ignore_errors=True)
    os.chdir('./docs')
    os.system('make html')
    os.chdir('..')
    shutil.copytree('./docs/build/html', temp_dir + '/docs')
    os.system('git checkout gh-pages')
    shutil.rmtree('./docs')
    shutil.copytree(temp_dir + '/docs', './docs')
    os.system('git add ./docs')
    os.system('git commit -m "rebuild docs"')
    os.system('git push origin gh-pages')
    shutil.rmtree(temp_dir)
    os.system('git checkout master')
    shutil.rmtree('./docs/_images', ignore_errors=True)
    shutil.rmtree('./docs/_static', ignore_errors=True)
    os.remove('./docs/.buildinfo')


handlers = {
    'build': build,
    'develop': develop,
    'install': install,
    'upload': upload,
    'test': test,
    'gh_pages': gh_pages,
}


args = sys.argv[1:]
if not args or not all(arg in handlers for arg in args):
    print('usage: python build.py [build, [develop, [install, [upload, [test, '
          '[gh_pages]]]]]')
    sys.exit()
prep_dir()
for arg in args:
    handlers[arg]()
