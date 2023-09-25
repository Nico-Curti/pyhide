#!/usr/bin/env python
# -*- coding: utf-8 -*-

import ast
import types
import builtins

from ._encoder import get_all_list_of_numbers
from ._encoder import get_all_list_of_variable_names
from ._encoder import get_all_list_of_function_names
from ._encoder import get_all_list_of_class_names
from ._encoder import get_dict_of_module_names
from ._encoder import insert_new_variable_in_header

from ._encoder import RenameVariable
from ._encoder import RenameAttribute
from ._encoder import RenameFunction
from ._encoder import RenameClass
from ._encoder import EncryptString
from ._encoder import RenamePkgAttribute
from ._encoder import ReplaceNumbers

__author__  = ['Nico Curti']
__email__ = ['nico.curti2@unibo.it']

__all__ = ['Obfuscator']

# list of built in functions for the pure-python
# codes
_BUILT_IN = [name for name, obj in vars(builtins).items()
              if isinstance(obj, types.BuiltinFunctionType)
            ]

class Obfuscator (object):

  def __init__ (self,
    rename_variable : bool = True,
    rename_function : bool = True,
    rename_class : bool = True,
    encode_pkg : bool = True,
    encode_number : bool = True,
    encode_string : bool = True
    ):

    self.rename_variable = rename_variable
    self.rename_function = rename_function
    self.rename_class = rename_class
    self.encode_pkg = encode_pkg
    self.encode_number = encode_number
    self.encode_string = encode_string

  def __call__ (self, code : str) -> str :
    '''
    Run the code obfuscation according
    to the parameters set in the constructor.

    Parameters
    ----------
      code : str
        Code to obfuscate and encrypt

    Returns
    -------
      obf_code : str
        Obfuscated code
    '''

    # create the syntax tree of the code
    root = ast.parse(code)
    # create the lut for number encoding
    numbers_lut = {}

    # if the number encoding is required
    if self.encode_number:
      # first of all get the list of numbers to encode
      numbers = get_all_list_of_numbers(root)
      # create the hard-coded value for 0 and 1 which
      # are the bases of the encryption
      numbers_lut.update({
        '0' : '((()==[])+(()==[]))',
        '1' : '({0}**{0})'.format('((()==[])+(()==[]))'),
      })
      # create the lut of numbers-encoding according
      # to the variable type
      for n in numbers:
        if isinstance(n, int):
          enc = self._encodeInteger(lut=numbers_lut, number=n)
        elif isinstance(n, float):
          enc = self._encodeFloat(number=n)
        else:
          raise ValueError('Something strange happens with numbers...')
        numbers_lut[str(n)] = enc

      # create the alias for the numbers
      numbers_alias = {}
      # for each variable add an header-variable on
      # the top of the code
      for i, (n, v) in enumerate(numbers_lut.items()):
        root = insert_new_variable_in_header(
          root=root,
          name='_' * (i + 1),
          value=v
        )
        numbers_alias[str(n)] = '_' * (i + 1)

      # add the extra hard-coded values to be sure
      # that all the todo-replacements will be stored
      # in this dictionary
      numbers_lut['True'] = '(()==())'
      numbers_lut['False'] = '(()==[])'
      # this list of numbers must be fixed at the end
      # of the processing, since the associated value
      # is set to a string, while it must be an expression

      # now we can replace the numbers with the obtained
      # encoding of the variables
      root = ReplaceNumbers(lut=numbers_alias).visit(root)
      # NOTE: since the variable replacement is obtained using
      # strings, we need to adjust them manually for the correct
      # execution of the code, inserting also the "support" for
      # the bool values
      obf_code = ast.unparse(root)
      obf_code = obf_code.replace('True', numbers_lut['True'])
      obf_code = obf_code.replace('False', numbers_lut['False'])
      for _, v in numbers_alias.items():
        obf_code = obf_code.replace(f"\'{v}\'", f'{v}')
      for _, v in numbers_lut.items():
        obf_code = obf_code.replace(f"\'{v}\'", f'{v}')
      root = ast.parse(obf_code)


    # declare the list of "variables" lut
    var_names, fun_names, cls_names = [], [], []

    # if the variable encoding is required
    if self.rename_variable:
      # now get the list of all variable names
      var_names = get_all_list_of_variable_names(root)
    # if the function encoding is required
    if self.rename_function:
      # now get the list of all function names
      fun_names = get_all_list_of_function_names(root)
    # if the class encoding is required
    if self.rename_class:
      # now get the list of all class names
      cls_names = get_all_list_of_class_names(root)

    # now we can rename all the variables of the code
    # according to the obtained lut of values
    var_lut = {}
    for i, v in enumerate(var_names + fun_names + cls_names):
      var_lut[v] = '_' * (i + 1 + len(numbers_lut))

    # if the function encoding is required
    if self.rename_variable:
      # the first layer of renaming is given by the code-variables
      root = RenameVariable(lut=var_lut).visit(root)
    # if the function encoding is required
    if self.rename_function:
      # the second layer of renaming is given by the functions
      root = RenameFunction(lut=var_lut).visit(root)
    # if the class encoding is required
    if self.rename_class:
      # the third layer of renaming is given by the class names
      root = RenameClass(lut=var_lut).visit(root)

    # if the class encoding is required
    if self.rename_variable and self.rename_function and self.rename_class:
      # rename also the attribute members as self var and other stuffs
      root = RenameAttribute(lut=var_lut).visit(root)

    # NOTE: the above three steps could not be implemented
    # into a single class, since the tree exploration is
    # stopped according to the first item found... so we need
    # to walk along the code according to a bottom-up exploration,
    # starting from the finest grain given by the variables,
    # moving to the intermediate function layer, and ending with
    # the top class names.

    # if the pkg encoding is required
    if self.encode_pkg:
      # create the lut for the package import
      mod_lut = get_dict_of_module_names(root)
      # add to the lut also the variable to preserve issue related
      # to local ModuleNotFoundError
      mod_lut.update({v : None for k, v in var_lut.items()})
      # now we can replace the packages with the __getitem__
      # encoding, creating an harder syntax
      root = RenamePkgAttribute(lut=mod_lut).visit(root)
      # NOTE: to preserve the builtin functions, we need to
      # adjust them manually
      obf_code = ast.unparse(root)
      for built_in in _BUILT_IN:
        if f'\"{built_in}\"' in obf_code: # it has been already processed by pkg
          continue
        obf_code = obf_code.replace(built_in,
          f'getattr(__import__("builtins"), "{built_in}")'
        )
      root = ast.parse(obf_code)

    # if the string encoding is required
    if self.encode_string:
      # now we can replace the strings with the hex encoding
      root = EncryptString().visit(root)

    # the last step is the correct replacement of the hex-strings
    # in the unparsed code
    obf_code = ast.unparse(root)
    obf_code = obf_code.replace('\\\\', '\\')

    return obf_code

  def _encodeInteger (self, lut : dict, number : int) -> str:
    '''
    Encode integer numbers.
    This is the magic trick performed by the original
    python-code-obfuscator project by brandonasuncion

    Parameters
    ----------
      lut : dict
        Look-up table of pre-determined values

      number : int
        Integer number to encrypt

    Returns
    -------
      obf_number : str
        Obfuscated integer number as string

    References
    ----------
    https://github.com/brandonasuncion/Python-Code-Obfuscator
    '''
    # if it is a negative number encode its abs
    # value, putting a invert symbol as prefix
    if number < 0:
      return "(~([]==())*{})".format(self._encodeInteger(lut, abs(number)))

    sn = str(number)
    if sn in lut:
      return lut[sn]

    # get the binary format of the number
    bin_number = bin(number)[2:]
    shifts = 0
    obf_number = ''

    while bin_number != '':
      if bin_number[-1] == '1':

        if shifts == 0:
          obf_number += lut['1']

        elif str(1<<shifts) in lut:
          obf_number += lut[str(1<<shifts)]

        elif str(shifts) in lut:
          encode_bitshift = lut[str(shifts)]
          obf_number += '({}<<{})'.format(lut['1'], encode_bitshift)

        else:
          bit_m1 = self._encodeInteger(lut, 1 << (shifts-1))
          obf_number += '({}<<{})'.format(bit_m1, lut['1'])

        obf_number += '+'

      bin_number = bin_number[:-1]
      shifts += 1
    if bin_number.count('1') == 1:
      obf_number = obf_number[:-1]
    else:
      obf_number = "({})".format(obf_number[:-1])

    return obf_number

  def _encodeFloat (self, number : float) -> str:
    '''
    Encode float numbers.
    This is just a workaround to create a more complex
    syntax for the evaluation of the floating point numbers,
    since the original number encoding works only for integers.

    Parameters
    ----------
      number : float
        Float number to encrypt

    Returns
    -------
      obf_number : str
        Obfuscated integer number as string

    References
    ----------
    https://github.com/brandonasuncion/Python-Code-Obfuscator
    '''
    # convert the number to string
    obf_number = str(number)
    # replace it as a call to the float function
    obf_number = f'float(\"{obf_number}\")'
    # return the obfuscated number
    return obf_number


def set_time_bomb (code : str, bomb : str, position : int) -> str:
  '''
  Insert a time bomb code in the syntax to ensure
  the stopping of the execution.

  Parameters
  ----------
    code : str
      Code to evaluate

    bomb : str
      Snippet of the time bomb

    position : int
      Position in which insert the time-bomb

  Returns
  -------
    code : str
      Code with the time bomb inserted
  '''
  # parse the code
  root = ast.parse(code)
  # insert the time bomb
  root.body.insert(position,
    ast.Expr(
      value=ast.Call(
        func=ast.Name(id='exec', ctx=ast.Load()),
        args=[ast.Constant(value=bomb)],
        keywords=[]
      )
    )
  )
  # fix the code line numbers
  ast.fix_missing_locations(root)
  # unparse it
  code = ast.unparse(root)
  return code
