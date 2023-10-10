#!/usr/bin/env python
# -*- coding: utf-8 -*-

import ast

from ._encoder import _BUILT_IN
from ._encoder import create_encryption_lut
from ._encoder import get_dict_of_module_names
from ._encoder import encrypt_constant_strings
from ._encoder import encrypt_joined_string
from ._encoder import encrypt_constant_bools
from ._encoder import encrypt_constant_integers
from ._encoder import encrypt_constant_floats
from ._encoder import encrypt_variable_name
from ._encoder import encrypt_function_def
from ._encoder import encrypt_function_arg
from ._encoder import encrypt_function_arguments
from ._encoder import encrypt_function_keyword
from ._encoder import encrypt_package_attribute
from ._encoder import encrypt_self_attribute
from ._encoder import encrypt_generic_attribute
from ._encoder import encrypt_builtin_function
from ._encoder import encrypt_generic_function
from ._encoder import encrypt_class_def
from ._encoder import encrypt_import_aliases
from ._encoder import add_header_variables
from ._encoder import clean_header_issues

__author__  = ['Nico Curti']
__email__ = ['nico.curti2@unibo.it']

__all__ = ['Obfuscator']


class Obfuscator (object):

  def __init__ (self,
    rename_variable : bool = True,
    rename_function : bool = True,
    rename_class : bool = True,
    encode_pkg : bool = True,
    encode_number : bool = True,
    encode_string : bool = True,
    reduce_code_length : bool = False,
    ):

    self.rename_variable = rename_variable
    self.rename_function = rename_function
    self.rename_class = rename_class
    self.encode_pkg = encode_pkg
    self.encode_number = encode_number
    self.encode_string = encode_string
    self.reduce_code_length = reduce_code_length

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

    # get the lookup table of all the possible
    # values that can be replaced in the code
    lut = create_encryption_lut(
      root=root,
      rename_variable=self.rename_variable,
      rename_function=self.rename_function,
      rename_class=self.rename_class,
      encode_pkg=self.encode_pkg,
      encode_number=self.encode_number,
      encode_string=self.encode_string,
    )

    # import module lookup table
    module_lut = {}

    if self.encode_pkg:
      # get the import module lookup table
      # to discriminate between the attributes
      module_lut = get_dict_of_module_names(root=root)

    # create an empty header dict in which store
    # the variables created by the obfuscator
    header = {}

    # start the code encrypting

    # loop along the code tree
    for node in ast.walk(root):

      # if it is a Module instance
      if isinstance(node, ast.Module):
        continue

      # if it is a simple string constant
      elif isinstance(node, ast.Constant) and \
           isinstance(node.value, str):
        if self.encode_string:
          # obfuscate the value
          obf_node, header = encrypt_constant_strings(
            node=node,
            lut=lut,
            header=header,
            reduce_code_length=self.reduce_code_length,
          )
          node.__class__ = obf_node.__class__
          node.__dict__.update(obf_node.__dict__)

      # if it is an f-string constant
      elif isinstance(node, ast.JoinedStr):
        if self.encode_string:
          # obfuscate the f-string elements
          obf_node, header = encrypt_joined_string(
            node=node,
            lut=lut,
            header=header,
          )
          node.__class__ = obf_node.__class__
          node.__dict__.update(obf_node.__dict__)

      # if it is a bool variable (aka True or False)
      elif isinstance(node, ast.Constant) and \
           isinstance(node.value, bool):
        if self.encode_number:
          # obfuscate the value
          obf_node, header = encrypt_constant_bools(
            node=node,
            lut=lut,
            header=header,
          )
          node.__class__ = obf_node.__class__
          node.__dict__.update(obf_node.__dict__)

      # if it is an integer variable
      elif isinstance(node, ast.Constant) and \
           isinstance(node.value, int):
        if self.encode_number:
          # obfuscate the value
          obf_node, header = encrypt_constant_integers(
            node=node,
            lut=lut,
            header=header,
          )
          node.__class__ = obf_node.__class__
          node.__dict__.update(obf_node.__dict__)

      # if it is an float variable
      elif isinstance(node, ast.Constant) and \
           isinstance(node.value, float):
        if self.encode_number:
          # obfuscate the value
          obf_node, header = encrypt_constant_floats(
            node=node,
            lut=lut,
            header=header,
          )
          node.__class__ = obf_node.__class__
          node.__dict__.update(obf_node.__dict__)

      # if it is just a name in the code
      elif isinstance(node, ast.Name):
        # obfuscate the variable name
        obf_node, header = encrypt_variable_name(
          node=node,
          lut=lut,
          header=header,
        )
        node.__class__ = obf_node.__class__
        node.__dict__.update(obf_node.__dict__)

      # if it is a function definition
      elif isinstance(node, ast.FunctionDef):
        # obfuscate the function name
        obf_node, header = encrypt_function_def(
          node=node,
          lut=lut,
          header=header,
        )
        node.__class__ = obf_node.__class__
        node.__dict__.update(obf_node.__dict__)

      # if it is a function arg
      elif isinstance(node, ast.arg):
        # obfuscate the arg name
        obf_node, header = encrypt_function_arg(
          node=node,
          lut=lut,
          header=header,
        )
        node.__class__ = obf_node.__class__
        node.__dict__.update(obf_node.__dict__)

      # if it is a function arguments
      elif isinstance(node, ast.arguments):
        # obfuscate the arguments name
        obf_node, header = encrypt_function_arguments(
          node=node,
          lut=lut,
          header=header,
        )
        node.__class__ = obf_node.__class__
        node.__dict__.update(obf_node.__dict__)

      # if it is a function keyword
      elif isinstance(node, ast.keyword):
        # obfuscate the keyword name
        obf_node, header = encrypt_function_keyword(
          node=node,
          lut=lut,
          header=header,
        )
        node.__class__ = obf_node.__class__
        node.__dict__.update(obf_node.__dict__)

      # if it is a package attribute
      elif isinstance(node, ast.Attribute) and \
           isinstance(node.value, ast.Name) and \
           node.value.id in module_lut:
        # obfuscate the package attribute
        obf_node, header = encrypt_package_attribute(
          node=node,
          lut=lut,
          header=header,
          module_lut=module_lut
        )
        node.__class__ = obf_node.__class__
        node.__dict__.update(obf_node.__dict__)

      # if it is a self attribute
      elif isinstance(node, ast.Attribute) and \
           isinstance(node.value, ast.Name) and \
           node.value.id == 'self':
        # obfuscate the package attribute
        obf_node, header = encrypt_self_attribute(
          node=node,
          lut=lut,
          header=header,
        )
        node.__class__ = obf_node.__class__
        node.__dict__.update(obf_node.__dict__)

      # if it is a generic attribute
      elif isinstance(node, ast.Attribute) and \
           isinstance(node.value, ast.Name):
        # obfuscate the package attribute
        obf_node, header = encrypt_generic_attribute(
          node=node,
          lut=lut,
          header=header,
        )
        node.__class__ = obf_node.__class__
        node.__dict__.update(obf_node.__dict__)

      # if it is a builtin function
      elif isinstance(node, ast.Call) and \
           isinstance(node.func, ast.Name) and \
           node.func.id in _BUILT_IN:
        if self.rename_function:
          # obfuscate the function name
          obf_node, header = encrypt_builtin_function(
            node=node,
            lut=lut,
            header=header,
          )
          node.__class__ = obf_node.__class__
          node.__dict__.update(obf_node.__dict__)

      # if it is a generic callable object
      elif isinstance(node, ast.Call) and \
           isinstance(node.func, ast.Name):
        # obfuscate the function name
        obf_node, header = encrypt_generic_function(
          node=node,
          lut=lut,
          header=header,
        )
        node.__class__ = obf_node.__class__
        node.__dict__.update(obf_node.__dict__)

      # if it is a class definition
      elif isinstance(node, ast.ClassDef):
        # obfuscate the class name
        obf_node, header = encrypt_class_def(
          node=node,
          lut=lut,
          header=header,
        )
        node.__class__ = obf_node.__class__
        node.__dict__.update(obf_node.__dict__)

      # if it is an import package
      elif isinstance(node, ast.Import):
        # we can directly remove the package
        # since all the other functions will
        # replaced
        if self.encode_pkg:
          node.__class__ = ast.Del

      # if it is an import package
      elif isinstance(node, ast.ImportFrom):
        # obfuscate the imported aliases
        obf_node, header = encrypt_import_aliases(
          node=node,
          lut=lut,
          header=header,
        )
        node.__class__ = obf_node.__class__
        node.__dict__.update(obf_node.__dict__)

    # at the end of the encoding we need
    # to add the new extra-variables stored
    # in the header
    root = add_header_variables(
      root=root,
      header=header
    )

    # now we can re-convert the code
    obf_code = ast.unparse(root)

    # and clean the code as post-processing step
    obf_code = clean_header_issues(
      code=obf_code,
      header=header
    )

    return obf_code
