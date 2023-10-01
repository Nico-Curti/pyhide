#!/usr/bin/env python
# -*- coding: utf-8 -*-

from io import StringIO
from contextlib import redirect_stdout as rstdout

from pyhide import Obfuscator
from pyhide import set_time_bomb

import pytest
import numpy as np
from datetime import datetime

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
print(func(a=1, b=2, c=3), end='', flush=True)
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

print(func(a=1, b=2, c=3), end='', flush=True)
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

  def test_nothing_enabled (self):

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

    obf = Obfuscator(
      rename_variable=False,
      rename_function=False,
      rename_class=False,
      encode_pkg=False,
      encode_number=False,
      encode_string=False,
    )
    obf_code = obf(code=code)

    assert exec(obf_code) is None

    stdout = StringIO()
    with rstdout(stdout):
      exec(obf_code)

    assert stdout.getvalue() == '[1, 2, 3, 1, 2, 3]'

  def test_only_var (self):

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

    obf = Obfuscator(
      rename_variable=True,
      rename_function=False,
      rename_class=False,
      encode_pkg=False,
      encode_number=False,
      encode_string=False,
    )
    obf_code = obf(code=code)

    assert exec(obf_code) is None

    stdout = StringIO()
    with rstdout(stdout):
      exec(obf_code)

    assert stdout.getvalue() == '[1, 2, 3, 1, 2, 3]'

  def test_only_func (self):

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

    obf = Obfuscator(
      rename_variable=False,
      rename_function=True,
      rename_class=False,
      encode_pkg=False,
      encode_number=False,
      encode_string=False,
    )
    obf_code = obf(code=code)

    assert exec(obf_code) is None

    stdout = StringIO()
    with rstdout(stdout):
      exec(obf_code)

    assert stdout.getvalue() == '[1, 2, 3, 1, 2, 3]'

  def test_only_class (self):

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

    obf = Obfuscator(
      rename_variable=False,
      rename_function=False,
      rename_class=True,
      encode_pkg=False,
      encode_number=False,
      encode_string=False,
    )
    obf_code = obf(code=code)

    assert exec(obf_code) is None

    stdout = StringIO()
    with rstdout(stdout):
      exec(obf_code)

    assert stdout.getvalue() == '[1, 2, 3, 1, 2, 3]'

  def test_only_pkg (self):

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

    obf = Obfuscator(
      rename_variable=False,
      rename_function=False,
      rename_class=False,
      encode_pkg=True,
      encode_number=False,
      encode_string=False,
    )
    obf_code = obf(code=code)

    assert exec(obf_code) is None

    stdout = StringIO()
    with rstdout(stdout):
      exec(obf_code)

    assert stdout.getvalue() == '[1, 2, 3, 1, 2, 3]'

  def test_only_number (self):

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

    obf = Obfuscator(
      rename_variable=False,
      rename_function=False,
      rename_class=False,
      encode_pkg=False,
      encode_number=True,
      encode_string=False,
    )
    obf_code = obf(code=code)

    assert exec(obf_code) is None

    stdout = StringIO()
    with rstdout(stdout):
      exec(obf_code)

    assert stdout.getvalue() == '[1, 2, 3, 1, 2, 3]'

  def test_only_str (self):

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

    obf = Obfuscator(
      rename_variable=False,
      rename_function=False,
      rename_class=False,
      encode_pkg=False,
      encode_number=False,
      encode_string=True,
    )
    obf_code = obf(code=code)

    assert exec(obf_code) is None

    stdout = StringIO()
    with rstdout(stdout):
      exec(obf_code)

    assert stdout.getvalue() == '[1, 2, 3, 1, 2, 3]'

  def test_timer (self):

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

    death = datetime.now()
    death = death.strftime('%d/%m/%Y')
    now = '1/1/1980'
    bomb = f"""
bomb = '''
from datetime import datetime

now = datetime.strptime('{now}', '%d/%m/%Y')
death = datetime.strptime('{death}', '%d/%m/%Y')
if death > now:
  raise ValueError()
'''
exec(bomb)
"""
    obf_code = set_time_bomb(code=obf_code, bomb=bomb, position=0)

    with pytest.raises(ValueError):
      exec(obf_code)
