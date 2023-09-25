#!/usr/bin/env python
# -*- coding: utf-8 -*-

from io import StringIO
from contextlib import redirect_stdout as rstdout

from pyhide import Obfuscator

import pytest
import numpy as np

__author__  = ['Nico Curti']
__email__ = ['nico.curti2@unibo.it']


class TestObfuscator:
  '''
  Tests:
    - if a simple Hello World works after the obfuscator
    - if a simple function is correctly obfuscated
    - if a package function is correctly obfuscated
    - if a class is correctly obfuscated
  '''

  def test_hello_world (self):

    code = """
#!/usr/bin/env python
# -*- coding: utf-8 -*-

print('Hello World', end='', flush=True)
"""
    assert exec(code) is None

    stdout = StringIO()
    with rstdout(stdout):
      exec(code)

    assert stdout.getvalue() == 'Hello World'

    obf = Obfuscator()
    obf_code = obf(code=code)

    assert exec(obf_code) is None

    stdout = StringIO()
    with rstdout(stdout):
      exec(obf_code)

    assert stdout.getvalue() == 'Hello World'

  def test_simple_func (self):

    code = """
def func (a, b, c):
  return a + b + c
print(func(1, 2, 3), end='', flush=True)
"""
    assert exec(code) is None

    stdout = StringIO()
    with rstdout(stdout):
      exec(code)

    assert stdout.getvalue() == '6'

    obf = Obfuscator()
    obf_code = obf(code=code)

    assert exec(obf_code) is None

    stdout = StringIO()
    with rstdout(stdout):
      exec(obf_code)

    assert stdout.getvalue() == '6'

  def test_pkg_func (self):

    code = """
import numpy as np

def func (a, b, c):
  return np.sum([a, b, c])

print(func(1, 2, 3), end='', flush=True)
"""
    assert exec(code) is None

    stdout = StringIO()
    with rstdout(stdout):
      exec(code)

    assert stdout.getvalue() == '6'

    obf = Obfuscator()
    obf_code = obf(code=code)

    assert exec(obf_code) is None

    stdout = StringIO()
    with rstdout(stdout):
      exec(obf_code)

    assert stdout.getvalue() == '6'

  def test_class_func (self):

    code = """
class A:

  def __init__ (self, l):
    self.list = l

  def func (self, x):
    return self.list + x

a = A([1, 2, 3])
print(a.func([1, 2, 3]), end='', flush=True)
"""
    assert exec(code) is None

    stdout = StringIO()
    with rstdout(stdout):
      exec(code)

    assert stdout.getvalue() == '[1, 2, 3, 1, 2, 3]'

    obf = Obfuscator()
    obf_code = obf(code=code)

    assert exec(obf_code) is None

    stdout = StringIO()
    with rstdout(stdout):
      exec(obf_code)

    assert stdout.getvalue() == '[1, 2, 3, 1, 2, 3]'
