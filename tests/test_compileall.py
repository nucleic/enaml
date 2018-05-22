# -*- coding: utf-8 -*-
#------------------------------------------------------------------------------
# Copyright (c) 2013-2018, Nucleic Development Team.
#
# Distributed under the terms of the Modified BSD License.
#
# The full license is in the file COPYING.txt, distributed with this software.
#------------------------------------------------------------------------------
import os
import time
import shutil
import pytest
import hashlib
import subprocess
from enaml.compat import IS_PY3
from contextlib import contextmanager


@contextmanager
def cd(path):
    """ cd to the directory then return to the cwd 
    
    """
    cwd = os.getcwd()
    try:
        os.chdir(path)
        yield
    finally:
        os.chdir(cwd)


def clean_cache(path):
    """ Clean the cache files in the path 
    
    """
    with cd(path):
        if os.path.exists('__enamlcache__'):
            shutil.rmtree('__enamlcache__')
        if os.path.exists('__pycache__'):
            shutil.rmtree('__pycache__')
        for f in os.listdir('.'):
            if f.endswith('.pyc'):
                os.remove(f)


def sha256sum(path):
    with open(path, 'rb') as f:
        h = hashlib.sha256()
        h.update(f.read())
        return h.digest()


def hash_cache(path):
    """ Compute the sha256 sum of all .pyc and .enamlc files in the
    given path.
    
    """
    # Hash each cache file
    hashes = {}
    with cd(path):
        for f in os.listdir('__enamlcache__'):
            hashes[f] = sha256sum(os.path.join('__enamlcache__', f))

        if IS_PY3:
            for f in os.listdir('__pycache__'):
                hashes[f] = sha256sum(os.path.join('__pycache__', f))
        else:
            for f in os.listdir('.'):
                if f.endswith('.pyc'):
                    hashes[f] = sha256sum(f)
    return hashes



@pytest.mark.parametrize("tutorial", [
    'employee',
    'hello_world',
    'person'
])
def test_tutorials(tempdir, tutorial):
    # Run normally to generate cache files
    source = os.path.join('examples', 'tutorial', tutorial)
    example = os.path.join(tempdir.strpath, tutorial)

    # Copy to a tmp dir
    shutil.copytree(source, example)
    try:
        clean_cache(example)
        with cd(example):
            p = subprocess.Popen('python {}.py'.format(tutorial).split())
            time.sleep(1)
            p.kill()
            p.wait()

        # Since we terminate the process it doesn't generate the pyc file,
        # so also run compileall to generate the .pyc file
        subprocess.check_call(
            'python -m compileall {}'.format(example).split())

        # Compute the hashes fo each cache file
        expected_hashes = hash_cache(example)
        clean_cache(example)

        # Run compileall
        subprocess.check_call('enaml-compileall {}'.format(example).split())
        compileall_hashes = hash_cache(example)

        # Validate
        mismatches = []
        for f, expected_hash in expected_hashes.items():
            hash = compileall_hashes.get(f)
            if hash != expected_hash:
                mismatches.append(f)
                print("{} hashes don't match: {} != {}".format(
                    f, repr(hash), repr(expected_hash)))
            else:
                print("{} hashes match".format(f))
        assert not mismatches
    finally:
        shutil.rmtree(os.path.join('tests', 'tmp'))
