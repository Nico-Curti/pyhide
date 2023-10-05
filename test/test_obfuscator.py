#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
from io import StringIO
from subprocess import PIPE, run
from contextlib import redirect_stdout as rstdout

from pyhide import Obfuscator

import pytest
import numpy as np
from datetime import datetime

__author__  = ['Nico Curti']
__email__ = ['nico.curti2@unibo.it']

test_dir = os.path.abspath(
  os.path.dirname(__file__)
)

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

  def test_fstring (self):

    code = """
#!/usr/bin/env python
# -*- coding: utf-8 -*-

x = 'Hello'
name = 'Nico'
print(f'{x} {name}', end='', flush=True)
"""
    assert exec(code) is None

    stdout = StringIO()
    with rstdout(stdout):
      exec(code)

    assert stdout.getvalue() == 'Hello Nico'

    obf = Obfuscator()
    obf_code = obf(code=code)

    assert exec(obf_code) is None

    stdout = StringIO()
    with rstdout(stdout):
      exec(obf_code)

    assert stdout.getvalue() == 'Hello Nico'

  def test_simple_func (self):

    code = """
def func (a, b, c):
  return sum([a, b, c])
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
import datetime
import numpy as np

def func (a, b, c):
  return np.sum([a, b, c])

print(func(a=1, b=2, c=3.14), end='', flush=True)
"""
    assert exec(code) is None

    stdout = StringIO()
    with rstdout(stdout):
      exec(code)

    assert np.round(float(stdout.getvalue()), 2) == 6.14

    obf = Obfuscator()
    obf_code = obf(code=code)

    assert exec(obf_code) is None

    stdout = StringIO()
    with rstdout(stdout):
      exec(obf_code)

    assert np.round(float(stdout.getvalue()), 2) == 6.14

  def test_class_func (self):

    code = """
class A:

  def __init__ (self, l):
    self.list = l

  def func (self, x):
    return self.list + x

a = A(l=[1, 2, 3])
print(a.func(x=[1, 2, 3]), end='', flush=True)
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

a = A(l=[1, 2, 3])
print(a.func(x=[1, 2, 3]), end='', flush=True)
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

a = A(l=[1, 2, 3])
print(a.func(x=[1, 2, 3]), end='', flush=True)
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

a = A(l=[1, 2, 3])
print(a.func(x=[1, 2, 3]), end='', flush=True)
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

a = A([1, -2, 3.14])
print(a.func([1, 2, 3]), end='', flush=True)
"""
    assert exec(code) is None

    stdout = StringIO()
    with rstdout(stdout):
      exec(code)

    assert stdout.getvalue() == '[1, -2, 3.14, 1, 2, 3]'

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

    assert stdout.getvalue() == '[1, -2, 3.14, 1, 2, 3]'

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

  def test_main_program (self):

    code = """#!/usr/bin/env python
# -*- coding: utf-8 -*-

class A:

  def __init__ (self, l):
    self.list = l

  def func (self, x):
    return self.list + x

a = A([1, -2, 3.14])
print(a.func([1, -2, 3.14]), end='', flush=True)
"""
    # dump the code to a dummy file
    dummy_file = os.path.join(test_dir, 'dummy.py')
    outfile = os.path.join(test_dir, 'dummy_obf.py')

    with open(dummy_file, 'w', encoding='utf-8') as fp:
      fp.write(code)

    # run the pyhide program
    proc = run(
      f'pyhide --input {dummy_file} --variable --function --class --pkg --num --str',
      stdout=PIPE, stderr=PIPE, universal_newlines=True, shell=True
    )
    # execute the program
    out = proc.stdout
    err = proc.stderr
    # check error
    assert os.path.exists(outfile)
    assert err == ''
    assert out == ''

    # execute the encoded program
    proc = run(
      f'python {outfile}',
      stdout=PIPE, stderr=PIPE, universal_newlines=True, shell=True
    )
    # execute the program
    out = proc.stdout
    err = proc.stderr
    # check error
    assert err == ''
    assert out == '[1, -2, 3.14, 1, -2, 3.14]'
    assert proc.returncode == 0

    # remove tmp files
    os.remove(dummy_file)
    os.remove(outfile)
