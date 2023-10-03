#!/usr/bin/env python
# -*- coding: utf-8 -*-

import ast
import types
import builtins

__author__  = ['Nico Curti']
__email__ = ['nico.curti2@unibo.it']

# list of built in functions for the pure-python
# codes
_BUILT_IN = [name for name, obj in vars(builtins).items()
              if isinstance(obj, types.BuiltinFunctionType)
            ]


class RenameVariable(ast.NodeTransformer):
  '''
  Rename all the variables of the code according
  to the provided look up table of values.
  '''

  def __init__ (self, lut):
    self.lut = lut

  def visit_arg(self, node : ast.arg) -> ast.arg:
    '''
    Rename variadic arguments
    '''
    return ast.arg(**{**node.__dict__, 
      'arg': self.lut.get(node.arg, node.arg)
    })

  def visit_Name(self, node : ast.Name) -> ast.Name:
    '''
    Rename node of type Name
    '''
    return ast.Name(**{**node.__dict__, 
      'id': self.lut.get(node.id, node.id)
    })

class RenameAttribute(ast.NodeTransformer):
  '''
  Rename all the functions of the code according
  to the provided look up table of values.
  '''

  def __init__ (self, lut):
    self.lut = lut

  def visit_keyword(self, node : ast.keyword) -> ast.keyword:
    '''
    Rename the argument names of each callable
    '''
    return ast.keyword(**{**node.__dict__,
      'arg': self.lut.get(node.arg, node.arg)
    })

  def visit_Attribute(self, node : ast.Attribute) -> ast.Attribute:
    '''
    Rename attribute names
    '''
    return ast.Attribute(**{**node.__dict__,
      'attr': self.lut.get(node.attr, node.attr)
    })

class RenameFunction(ast.NodeTransformer):
  '''
  Rename all the functions of the code according
  to the provided look up table of values.
  '''

  def __init__ (self, lut):
    self.lut = lut

  def visit_FunctionDef(self, node : ast.FunctionDef) -> ast.FunctionDef:
    '''
    Rename function names
    '''

    return ast.FunctionDef(**{**node.__dict__, 
      'name': self.lut.get(node.name, node.name)
    })

class RenameClass(ast.NodeTransformer):
  '''
  Rename all the classes of the code according
  to the provided look up table of values.
  '''

  def __init__ (self, lut):
    self.lut = lut

  def visit_ClassDef(self, node : ast.ClassDef) -> ast.ClassDef:
    '''
    Rename class names
    '''
    return ast.ClassDef(**{**node.__dict__,
      'name': self.lut.get(node.name, node.name)
    })

class EncryptString(ast.NodeTransformer):
  '''
  Encrypt all the code strings using hex fmt.
  '''

  def __init__(self):
    pass

  def visit_JoinedStr(self, node : ast.JoinedStr) -> ast.JoinedStr:
    '''
    Replace node of type f-string
    '''
    return node

  def visit_Constant(self, node : ast.Str) -> ast.Constant:
    '''
    Replace node of type string
    '''
    if isinstance(node.value, str):
      return ast.Constant(
        value=self.encode_string(node.value)
      )
    else:
      return node

  def encode_string (self, s : str) -> str:
    '''
    Encoding function for the string according to
    hex format.
    '''
    result = ''.join(f"\\x{ord(c):02x}" for c in s)
    return result

class RenamePkgAttribute(ast.NodeTransformer):
  '''
  Rename all the packages' functions according to
  the getattr function.
  In this way the functions will be replaced by strings
  that could (optionally) encrypted.
  '''

  def __init__(self, lut : dict):
    self.lut = lut

  def visit_Attribute(self, node : ast.Attribute) -> ast.Name:
    '''
    Replace package attribute functions
    '''
    attr = node.attr # get the function name
    if not hasattr(node.value, 'id'):
      return node

    pkg = node.value.id # get the belonging package name

    # if it is a private member function you cannot
    # rename it
    if pkg == 'self':
      return node

    # if the value of the lut is None but it is a builtin name
    # we need to use the correct pkg
    if self.lut.get(pkg, None) is None and attr in _BUILT_IN:
      return ast.Name(
        id=f'getattr(__import__("builtins"), "{attr}")',
        ctx=ast.Load()
      )
    # if the value of the lut is None it must be a
    # node to preserve
    elif self.lut.get(pkg, None) is None:
      return node

    return ast.Name(
      id=f'getattr(__import__("{self.lut.get(pkg, pkg)}"), "{attr}")',
      ctx=ast.Load()
    )

class ReplaceNumbers(ast.NodeTransformer):
  '''
  Replace number values according to a bit
  encoding and encrypted math operations.
  '''

  def __init__(self, lut : dict):
    self.lut = lut

  def visit_Constant(self, node : ast.Num) -> ast.Constant:
    '''
    Replace node of type number
    '''
    return ast.Constant(
      value=self.lut.get(str(node.value), str(node.value))
    )

def get_all_list_of_variable_names (root : ast.Module) -> list :
  '''
  Get the list of all variable names defined in the
  provided code.
  This list could be used to build a lut of values
  for the name replacement in the code.
  '''

  variable_names = set()
  # walk along the syntax tree
  for node in ast.walk(root):
    # if it is a standard variable assignment
    if isinstance(node, ast.Name) and not isinstance(node.ctx, ast.Load):
      variable_names.add(node.id)
    # if it is a member variable of a class defined by self
    elif isinstance(node, ast.Attribute) and isinstance(node.value, ast.Name) and node.value.id == 'self':
      variable_names.add(node.attr)
    # if it is a list of arguments defined in function definition
    elif isinstance(node, ast.FunctionDef):
      args = {x.arg for x in node.args.args if x.arg != 'self'}
      variable_names.update(args)

  return sorted(variable_names)

def get_all_list_of_class_names (root : ast.Module) -> list:
  '''
  Get the list of all class names defined in the
  provided code.
  This list could be used to build a lut of values
  for the name replacement in the code.
  '''

  class_names = sorted({node.name
    for node in ast.walk(root)
      if isinstance(node, ast.ClassDef)
    }
  )
  return class_names

def get_all_list_of_function_names (root : ast.Module) -> list:
  '''
  Get the list of all function names defined in the
  provided code.
  This list could be used to build a lut of values
  for the name replacement in the code.
  '''

  function_names = sorted({node.name
    for node in ast.walk(root)
      if isinstance(node, ast.FunctionDef) and not node.name.startswith('__')
    }
  )
  return function_names

def get_dict_of_module_names (root : ast.Module) -> dict:
  '''
  Get the lut of all package imported in the
  provided code, associated to the corresponding
  aliases.
  This lut is built as (alias : pkg) and it could
  be used for the correct management of the
  package member function.
  '''

  module_names = {}
  for node in ast.walk(root):
    if (isinstance(node, ast.Import) or isinstance(node, ast.ImportFrom)):
      name = node.names[0].name
      asname = node.names[0].asname
      if asname is None:
        module_names[name] = name
      else:
        module_names[asname] = name

  return module_names

def get_all_list_of_numbers (root : ast.Module) -> list:
  '''
  Get the list of all the numbers hard-coded in the
  provided code.
  This list could be used to build a lut of values
  for the number encryption in the code.
  '''

  numeric_var = sorted({node.value
    for node in ast.walk(root)
      if isinstance(node, ast.Num)
    }
  )
  return numeric_var

def insert_new_variable_in_header (root : ast.Module, name : str, value : str) -> ast.Module:
  '''
  Insert a new variable in the header of the scritp.
  This function could be used to create the header
  of encryption for numbers and other stuffs.

  Parameters
  ----------
    root : ast.Module
      Ast module to edit

    name : str
      Name of the new variable

    value : str
      Constant value to assign

  Returns
  -------
    root : ast.Module
      Edited module
  '''
  # insert the new variable in the first line
  root.body.insert(0,
    ast.Assign(targets=[
      ast.Name(id=name, ctx=ast.Store())
    ],
    value=ast.Constant(value=value))
  )
  # fix the code line numbers
  ast.fix_missing_locations(root)
  return root
