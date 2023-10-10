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

# global lut for numeric values
NUMBERS_LUT = {
  '0' : '((()==[])+(()==[]))',
  '1' : '((()==[])+(()==()))',
}

def get_all_list_of_variable_names (root : ast.Module) -> list :
  '''
  Get the list of all variable names defined in the
  provided code.
  This list could be used to build a lut of values
  for the name replacement in the code.

  Parameters
  ----------
    root: ast.Module
      Ast node on which start the search

  Returns
  -------
    variable_names: list
      Unique list of all the items which could be replaced
      in the original code
  '''

  # create a unique set of variables
  variable_names = set()

  # walk along the syntax tree
  for node in ast.walk(root):

    # if it is a standard variable assignment
    if isinstance(node, ast.Name) and \
       not isinstance(node.ctx, ast.Load):
      variable_names.add(node.id)

    # if it is a member variable of a class defined by self
    elif isinstance(node, ast.Attribute) and \
         isinstance(node.value, ast.Name):
      variable_names.add(node.attr)

    # if it is a list of arguments defined in function definition
    elif isinstance(node, ast.FunctionDef):
      args = {x.arg for x in node.args.args}
      variable_names.update(args)

  # convert the set onto a list
  variable_names = sorted(variable_names)

  return variable_names

def get_all_list_of_class_names (root : ast.Module) -> list:
  '''
  Get the list of all class names defined in the
  provided code.
  This list could be used to build a lut of values
  for the name replacement in the code.

  Parameters
  ----------
    root: ast.Module
      Ast node on which start the search

  Returns
  -------
    class_names: list
      Unique list of all the class names which could be replaced
      in the original code
  '''

  # walk along the code tree and get the class names
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

  Parameters
  ----------
    root: ast.Module
      Ast node on which start the search

  Returns
  -------
    function_names: list
      Unique list of all the function names which could be replaced
      in the original code
  '''

  # walk along the code tree and get the function names
  # given by the simple definition
  function_names = sorted({node.name
    for node in ast.walk(root)
      # avoid special functions
      if isinstance(node, ast.FunctionDef) and \
         not node.name.startswith('__')
    }
  )

  # add also the names of the function which are
  # called in the code, if they have a name
  function_names += sorted({node.func.id
    for node in ast.walk(root)
      # only functions with name has an id
      if isinstance(node, ast.Call) and \
         isinstance(node.func, ast.Name)
    }
  )

  # add also the function used as attributes
  # if they have an id
  function_names += sorted({node.attr
    for node in ast.walk(root)
      # check if they have an id, aka they are names
      if isinstance(node, ast.Attribute) and \
         hasattr(node.value, 'id')
    }
  )
  # return the obtained list
  return function_names

def get_dict_of_module_names (root : ast.Module) -> dict:
  '''
  Get the lut of all package imported in the
  provided code, associated to the corresponding
  aliases.
  This lut is built as (alias : pkg) and it could
  be used for the correct management of the
  package member function.

  Parameters
  ----------
    root: ast.Module
      Ast node on which start the search

  Returns
  -------
    module_names: dict
      lut of modules imported with corresponding aliases
  '''

  # create an empty lut
  module_names = {}

  # walk along the code tree
  for node in ast.walk(root):

    # if they are nodes related to imports
    if isinstance(node, ast.Import) or \
       isinstance(node, ast.ImportFrom):

      # get the module name
      name = node.names[0].name
      # get the optional alias
      asname = node.names[0].asname
      # if there is no alias
      if asname is None:
        # set the key equal to the value
        module_names[name] = name
      else:
        # otherwise use the alias for the indexing
        module_names[asname] = name

  # return the obtained lut
  return module_names

def get_all_list_of_numbers (root : ast.Module) -> list:
  '''
  Get the list of all the numbers hard-coded in the
  provided code.
  This list could be used to build a lut of values
  for the number encryption in the code.

  Parameters
  ----------
    root: ast.Module
      Ast node on which start the search

  Returns
  -------
    numeric_var: list
      List of all the numeric values found in the code
  '''

  # walk along the code tree and get the numbers
  numeric_var = sorted({node.value
    for node in ast.walk(root)
      # filter only the numeric values
      if isinstance(node, ast.Num)
    }
  )

  return numeric_var

def get_all_char_values (root : ast.Module) -> set:
  '''
  Get the unique set of all char found in the code
  for the minimal string encoding and the correct
  creation of the header of variables.

  Parameters
  ----------
    root: ast.Module
      Ast node on which start the search

  Returns
  -------
    chars: set
      Unique set of all the characters found in the
      code strings. These chars could be used for the
      encryption of the simple strings.
  '''
  # walk along the code and add all the strings
  # found
  chars = { node.value
    for node in ast.walk(root)
      # if they are constant strings
      if isinstance(node, ast.Constant) and \
         isinstance(node.value, str)
  }
  # combine all the chars a unique set
  chars = set(''.join(chars))
  # exclude the space characted since it cannot be
  # encrypt
  # NOTE: further characters could be inserted here!
  chars = sorted(chars - {' '})
  # convert the char into numeric value for a better
  # encoding
  chars = [ord(x) for x in chars]
  return chars

def get_all_strings (root : ast.Module) -> set:
  '''
  Get the set of constant strings for f-string
  formatting and encryption.

  Parameters
  ----------
    root: ast.Module
      Ast node on which start the search

  Returns
  -------
    strings: list
      List of unique strings found in the code tree
  '''
  # walk along the code and get all the strings
  # found as entire strings
  strings = { node.value
    for node in ast.walk(root)
      # if they are constant strings
      if isinstance(node, ast.Constant) and \
         isinstance(node.value, str)
  }
  # NOTE: the above set is the same of the
  # get_all_char_values without the final processing!

  # convert the set into a unique list
  strings = sorted(strings)
  # return the obtained list
  return strings

def encodeInteger (number : int) -> str:
  '''
  Encode integer numbers.
  This is the magic trick performed by the original
  python-code-obfuscator project by brandonasuncion

  Parameters
  ----------
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
  global NUMBERS_LUT

  sn = str(number)
  if sn in NUMBERS_LUT:
    return NUMBERS_LUT[sn]

  # get the binary format of the number
  bin_number = bin(number)[2:]
  shifts = 0
  obf_number = ''

  while bin_number != '':
    if bin_number[-1] == '1':

      if shifts == 0:
        obf_number += NUMBERS_LUT['1']

      elif str(1<<shifts) in NUMBERS_LUT:
        obf_number += NUMBERS_LUT[str(1<<shifts)]

      elif str(shifts) in NUMBERS_LUT:
        encode_bitshift = NUMBERS_LUT[str(shifts)]
        obf_number += f"({NUMBERS_LUT['1']}<<{encode_bitshift})"
      else:
        bit_m1 = encodeInteger(number=1 << (shifts-1))
        obf_number += f"({bit_m1}<<{NUMBERS_LUT['1']})"

      obf_number += '+'

    bin_number = bin_number[:-1]
    shifts += 1
  if bin_number.count('1') == 1:
    obf_number = obf_number[:-1]
  else:
    obf_number = f"({obf_number[:-1]})"

  return obf_number

def encodeFloat (number : float) -> str:
  '''
  Encode float numbers.
  This is just a workaround to create a more complex
  syntax for the evaluation of the floating point numbers,
  since the original number encoding works only for integers.

  The encoding is made converting the number as hex string
  and then re-analyzed using chr of integer

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
  # replace it as an hex string
  obf_number = ''.join(f"\\x{ord(c):02x}" for c in obf_number)
  # create a function encoding with concatenated chars
  obf_number = f'float(str("".join(chr(x) if isinstance(x, int) else x for x in "{obf_number}")))'
  # return the obfuscated number
  return obf_number

def insert_new_variable_in_header (root : ast.Module,
                                   name : str,
                                   value : str
                                  ) -> ast.Module:
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

def create_encryption_lut (root : ast.Module,
                           rename_variable : bool,
                           rename_function : bool,
                           rename_class : bool,
                           encode_pkg : bool,
                           encode_number : bool,
                           encode_string : bool,
                          ) -> dict:
  '''
  Create the lut of values for the correct
  encryption of all the possible values found
  in the code tree.

  Parameters
  ----------
    root: ast.Module
      Ast node on which start the search

    rename_variable : bool
      Enable/Disable the encoding of variable names

    rename_function : bool
      Enable/Disable the encoding of function names

    rename_class : bool
      Enable/Disable the encoding of class names

    encode_pkg : bool
      Enable/Disable the encoding of package names

    encode_number : bool
      Enable/Disable the encoding of number values

    encode_string : bool
      Enable/Disable the encoding of string values


  Returns
  -------
    lut: dict
      Lookup table of the aliases for the code
      encryption
  '''

  # get the unique set of all chars
  chars = get_all_char_values(root) if encode_string else []
  # get the set of all strings
  strings = get_all_strings(root) if encode_string else []
  # get the set of numbers
  numbers = get_all_list_of_numbers(root) if encode_number else []
  # get the set of all variable names
  var_names = get_all_list_of_variable_names(root) if rename_variable else []
  # get the set of all function names
  fun_names = get_all_list_of_function_names(root) if rename_function else []
  # get the set of all class names
  cls_names = get_all_list_of_class_names(root) if rename_class else []
  # get the lut of imported modules
  mod_lut = get_dict_of_module_names(root) if encode_pkg else {}

  # remove possible duplicates from
  # the whole list of values
  alias = set(chars)
  alias.update(set(strings))
  alias.update(set(numbers))
  alias.update(set(var_names))
  alias.update(set(fun_names))
  alias.update(set(cls_names))
  alias.update(set(mod_lut.keys()))
  # force the adding of bool vars
  alias.update({'True', 'False'})

  # create the lut of values
  lut = {k : '_' * (i + 1)
    for i, k in enumerate(alias)
  }

  return lut

def encrypt_constant_strings (node: ast.Constant,
                              lut: dict,
                              header: dict,
                              reduce_code_length: bool,
                             ) -> ast.Call:
  '''
  Encryption of simple strings found in the code.
  The processed strings must be also inserted in
  the header of the obfuscated script, so in this
  function we update also the header dictionary.

  The strings are encrypted using the evaluation
  of string made by a concatenation of variables
  obtained by the lookup table of the strings.

  Parameters
  ----------
    node: ast.Constant
      Ast string node to process

    lut: dict
      Lookup table for the code obfuscator

    header: dict
      Lookup table of the header variables
      to add on the obfuscated code

    reduce_code_length: bool
      Enable/Disable the string encoding using
      integer representation or simply the ord

  Returns
  -------
    obf_node: ast.Call
      The constant node is transformed into a Call
      one to use the 'eval' function on the string
      obtained by the join.

    header: dict
      Updated header
  '''

  # first of all update the header using the
  # ord value of each char, aka the number
  # which represents the character
  if reduce_code_length:
    header.update({
      # the key is given by the integer
      # to avoid possible overlapping with variable
      # names; the value is the string of the numeric
      # representation of the char
      lut[ord(x)] : str(ord(x))
        for x in node.value
          # filter only the char in the lut
          # since some characters are escaped during
          # the loading
          if ord(x) in lut
    })
  else:
    header.update({
      # the key is given by the integer
      # to avoid possible overlapping with variable
      # names; the value is the integer encoding of
      # the ord representation
      lut[ord(x)] : str(encodeInteger(number=ord(x)))
        for x in node.value
          # filter only the char in the lut
          # since some characters are escaped during
          # the loading
          if ord(x) in lut
    })

  # get the aliases obtained by the lut
  aliases = [ lut.get(ord(x), x)
    for x in node.value
  ]
  # create the encoded string
  enc = f"str(''.join(chr(x) if isinstance(x, int) else x for x in {aliases}))"

  # transform the node into a Call one
  obf_node = ast.Call(
    # assign the function 'eval' to the Call
    func = ast.Name(
      id='eval',
      ctx=ast.Load()
    ),
    # assign the arguments to the func, i.e. the enc string
    args = [
      ast.Constant(
        value=enc
      )
    ],
    # assign the optional keywords
    keywords = []
  )

  return obf_node, header

def encrypt_constant_bools (node: ast.Constant,
                            lut: dict,
                            header: dict
                            ) -> ast.Constant:
  '''
  Encryption of bool values (aka True, False).

  The encryption is made according to the same
  encoding of the numbers 0 -> False and 1 -> True.
  In this way we can reduce the amount of code

  Parameters
  ----------
    node: ast.Constant
      Ast bool node to process

    lut: dict
      Lookup table for the code obfuscator

    header: dict
      Lookup table of the header variables
      to add on the obfuscated code

  Returns
  -------
    obf_node: ast.Constant
      The constant node of the obfuscated bool.

    header: dict
      Updated header
  '''
  # get the value as int representation
  # for the search in the lut
  value = int(node.value)

  # get the variable name by the lut
  var_name = lut.get(str(node.value), str(node.value))

  obf_node = ast.Constant(
    **{**node.__dict__,
       # convert the integer to string
       # since the lut store string representation
       # of the numbers
       'value' : var_name
    }
  )
  header[var_name] = NUMBERS_LUT[str(value)]

  return obf_node, header

def encrypt_constant_integers (node: ast.Constant,
                               lut: dict,
                               header: dict
                              ) -> ast.Constant:
  '''
  Encryption of integer values.

  The encryption is made according to the 'encodeInteger'
  function.
  According to the new node value, the NUMBERS_LUT
  and the obfuscated code header will be updated.

  Parameters
  ----------
    node: ast.Constant
      Ast integer node to process

    lut: dict
      Lookup table for the code obfuscator

    header: dict
      Lookup table of the header variables
      to add on the obfuscated code

  Returns
  -------
    obf_node: ast.Constant
      The constant node of the obfuscated integer.

    header: dict
      Updated header
  '''
  global NUMBERS_LUT

  # get the integer value of the node
  value = node.value
  # encrypt the integer node
  obf_value = encodeInteger(number=value)
  # update the numbers lut
  NUMBERS_LUT[str(value)] = obf_value
  # get the alias of the variable from the lut
  var_name = lut.get(value, value)
  # update the header using as key
  # the variable name and as value
  # the encrypted value
  header[var_name] = obf_value
  # create the new node using the
  # name as value
  obf_node = ast.Constant(
    **{**node.__dict__,
       'value': var_name
    }
  )

  return obf_node, header

def encrypt_constant_floats (node: ast.Constant,
                             lut: dict,
                             header: dict
                            ) -> ast.Constant:
  '''
  Encryption of float values.

  The encryption is made according to the 'encodeFloat'
  function.
  According to the new node value, the obfuscated code
  header will be updated.

  Parameters
  ----------
    node: ast.Constant
      Ast float node to process

    lut: dict
      Lookup table for the code obfuscator

    header: dict
      Lookup table of the header variables
      to add on the obfuscated code

  Returns
  -------
    obf_node: ast.Constant
      The constant node of the obfuscated float.

    header: dict
      Updated header
  '''

  # get the float value of the node
  value = node.value
  # encrypt the float node
  obf_value = encodeFloat(number=value)
  # get the alias of the variable from the lut
  var_name = lut.get(value, value)
  # update the header using as key
  # the variable name and as value
  # the encrypted value
  header[var_name] = obf_value
  # create the new node using the
  # name as value
  obf_node = ast.Constant(
    **{**node.__dict__,
       'value': var_name
    }
  )

  return obf_node, header

def encrypt_function_def (node: ast.Constant,
                          lut: dict,
                          header: dict
                         ) -> ast.FunctionDef:
  '''
  Encryption of function definition names.

  The encryption is made by simply replacing the
  function name according to the global lookup
  table of aliases.

  Parameters
  ----------
    node: ast.FunctionDef
      Ast function definition node to process

    lut: dict
      Lookup table for the code obfuscator

    header: dict
      Lookup table of the header variables
      to add on the obfuscated code

  Returns
  -------
    obf_node: ast.FunctionDef
      The function definition node with the obfuscated
      function name.

    header: dict
      Updated header
  '''
  # the function name encryption
  # is simply made by the replacement
  # of the name according to the global lut
  obf_node = ast.FunctionDef(
    **{**node.__dict__,
       'name': lut.get(node.name, node.name)
    }
  )
  return obf_node, header

def encrypt_function_arg (node: ast.arg,
                          lut: dict,
                          header: dict
                         ) -> ast.arg:
  '''
  Encryption of function arg names (aka the names
  in the function signature).

  The encryption is made by simply replacing the
  arg name according to the global lookup
  table of aliases.

  Parameters
  ----------
    node: ast.arg
      Ast arg definition node to process

    lut: dict
      Lookup table for the code obfuscator

    header: dict
      Lookup table of the header variables
      to add on the obfuscated code

  Returns
  -------
    obf_node: ast.arg
      The arg node with the obfuscated
      arg name

    header: dict
      Updated header
  '''
  # the arg name encryption
  # is simply made by the replacement
  # of the name according to the global lut
  obf_node = ast.arg(
    **{**node.__dict__,
       'arg': lut.get(node.arg, node.arg)
    }
  )
  return obf_node, header

def encrypt_function_arguments (node: ast.arg,
                                lut: dict,
                                header: dict
                               ) -> ast.arguments:
  '''
  Encryption of function arguments names (aka the names
  in the function call).

  The encryption is made by simply replacing the
  arguments name according to the global lookup
  table of aliases.

  Parameters
  ----------
    node: ast.arguments
      Ast arguments definition node to process

    lut: dict
      Lookup table for the code obfuscator

    header: dict
      Lookup table of the header variables
      to add on the obfuscated code

  Returns
  -------
    obf_node: ast.arguments
      The arguments node with the obfuscated
      arguments name

    header: dict
      Updated header
  '''
  # the arguments name encryption
  # is simply made by the replacement
  # of the name according to the global lut
  obf_node = ast.arguments(
    **{**node.__dict__,
       'arguments': [
          lut.get(n.arg, n.arg)
            for n in node.args
      ]
    }
  )
  return obf_node, header

def encrypt_function_keyword (node: ast.keyword,
                              lut: dict,
                              header: dict
                             ) -> ast.keyword:
  '''
  Encryption of function keyword names (aka the names
  in the function call).

  The encryption is made by simply replacing the
  keyword name according to the global lookup
  table of aliases.

  Parameters
  ----------
    node: ast.keyword
      Ast keyword definition node to process

    lut: dict
      Lookup table for the code obfuscator

    header: dict
      Lookup table of the header variables
      to add on the obfuscated code

  Returns
  -------
    obf_node: ast.keyword
      The keyword node with the obfuscated
      keyword name

    header: dict
      Updated header
  '''
  # the keyword name encryption
  # is simply made by the replacement
  # of the name according to the global lut
  obf_node = ast.keyword(
    **{**node.__dict__,
       'arg': lut.get(node.arg, node.arg)
    }
  )
  return obf_node, header

def encrypt_class_def (node: ast.ClassDef,
                       lut: dict,
                       header: dict
                      ) -> ast.ClassDef:
  '''
  Encryption of class definition names.

  The encryption is made by simply replacing the
  class name according to the global lookup
  table of aliases.

  Parameters
  ----------
    node: ast.ClassDef
      Ast class definition node to process

    lut: dict
      Lookup table for the code obfuscator

    header: dict
      Lookup table of the header variables
      to add on the obfuscated code

  Returns
  -------
    obf_node: ast.ClassDef
      The class node with the obfuscated
      class name

    header: dict
      Updated header
  '''
  # the class name encryption
  # is simply made by the replacement
  # of the name according to the global lut
  obf_node = ast.ClassDef(
    **{**node.__dict__,
       'name': lut.get(node.name, node.name)
    }
  )
  return obf_node, header

def encrypt_import_aliases (node: ast.Import,
                            lut: dict,
                            header: dict
                            ) -> ast.Import:
  '''
  Encryption of import aliases.

  The encryption is made by simply replacing the
  alias name according to the global lookup
  table of aliases.

  Parameters
  ----------
    node: ast.Import
      Ast import node to process

    lut: dict
      Lookup table for the code obfuscator

    header: dict
      Lookup table of the header variables
      to add on the obfuscated code

  Returns
  -------
    obf_node: ast.arguments
      The arguments node with the obfuscated
      arguments name

    header: dict
      Updated header
  '''
  # copy the initial node
  obf_node = type(node)(
    **{**node.__dict__
    }
  )
  # the import alias encryption
  # is simply made by the replacement
  # of the alias according to the global lut
  # NOTE: the import could be a list
  # so we need to replace the entire list
  # of aliases
  for n in obf_node.names:
    # replace the alias according to the lut
    n.asname = lut.get(n.asname, n.asname)

  return obf_node, header

def encrypt_variable_name (node: ast.Name,
                           lut: dict,
                           header: dict
                          ) -> ast.Name:
  '''
  Encryption of variable names.

  The encryption is made by simply replacing the
  variable name according to the global lookup
  table of aliases.

  Parameters
  ----------
    node: ast.Name
      Ast name definition node to process

    lut: dict
      Lookup table for the code obfuscator

    header: dict
      Lookup table of the header variables
      to add on the obfuscated code

  Returns
  -------
    obf_node: ast.Name
      The name node with the obfuscated
      variable name

    header: dict
      Updated header
  '''
  # the variable name encryption
  # is simply made by the replacement
  # of the name according to the global lut
  obf_node = ast.Name(
    **{**node.__dict__,
       'id': lut.get(node.id, node.id)
    }
  )
  return obf_node, header

def encrypt_package_attribute (node: ast.Attribute,
                               lut: dict,
                               header: dict,
                               module_lut: dict
                              ) -> ast.Name:
  '''
  Encryption of attributes belonging to external packages.

  The encryption is made by transforming the node
  into a Name one given by the syntax:

  getattr(__import__("pkg"), "attr")

  where the "pkg" and "attr" strings are encoded using
  hex strings.

  Parameters
  ----------
    node: ast.Attribute
      Ast attribute definition node to process

    lut: dict
      Lookup table for the code obfuscator

    header: dict
      Lookup table of the header variables
      to add on the obfuscated code

    module_lut: dict
      Lookup table of module aliases

  Returns
  -------
    obf_node: ast.Name
      The name node with the obfuscated
      variable name

    header: dict
      Updated header
  '''
  # get the package full name
  pkg = module_lut[node.value.id]
  # encrypt the package name using hex string
  pkg = ''.join(f"\\x{ord(c):02x}" for c in pkg)
  # encrypt the package attribute using hex string
  attr = ''.join(f"\\x{ord(c):02x}" for c in node.attr)
  # transform the node into a Name one
  # with the function call given by the
  # 'geattr' function using as much strings as possible ;)
  obf_node = ast.Name(
    id = f'getattr(__import__("{pkg}"), "{attr}")',
    ctx = ast.Load()
  )

  return obf_node, header

def encrypt_self_attribute (node: ast.Attribute,
                            lut: dict,
                            header: dict
                           ) -> ast.Attribute:
  '''
  Encryption of attributes belonging to self.

  The encryption is made by simply replacing the
  attribute name according to the global lookup
  table of aliases.

  Parameters
  ----------
    node: ast.Attribute
      Ast attribute node to process

    lut: dict
      Lookup table for the code obfuscator

    header: dict
      Lookup table of the header variables
      to add on the obfuscated code

  Returns
  -------
    obf_node: ast.Attribute
      The attribute node with the obfuscated
      attribute name

    header: dict
      Updated header
  '''
  # the attribute name encryption
  # is simply made by the replacement
  # of the name according to the global lut
  obf_node = ast.Attribute(
    **{**node.__dict__,
       'attr': lut.get(node.attr, node.attr)
    }
  )
  return obf_node, header

def encrypt_generic_attribute (node: ast.Attribute,
                               lut: dict,
                               header: dict
                              ) -> ast.Attribute:
  '''
  Encryption of generic attributes.

  The encryption is made by simply replacing the
  attribute name and package according to the global lookup
  table of aliases.

  Parameters
  ----------
    node: ast.Attribute
      Ast attribute node to process

    lut: dict
      Lookup table for the code obfuscator

    header: dict
      Lookup table of the header variables
      to add on the obfuscated code

  Returns
  -------
    obf_node: ast.Attribute
      The attribute node with the obfuscated
      attribute name

    header: dict
      Updated header
  '''
  # the attribute name encryption
  # is simply made by the replacement
  # of the name according to the global lut
  obf_node = ast.Attribute(
    **{**node.__dict__,
       'value': ast.Name(
          id = lut.get(node.value.id, node.value.id),
          ctx = ast.Load()
        ),
       'attr': lut.get(node.attr, node.attr),
    }
  )
  return obf_node, header

def encrypt_builtin_function (node: ast.Call,
                              lut: dict,
                              header: dict
                             ) -> ast.Call:
  '''
  Encryption of builtin function names.

  The encryption is made by transforming the node
  into a Name one given by the syntax:

  getattr(__import__("pkg"), "attr")

  where the "pkg" and "attr" strings are encoded using
  hex strings.
  In this case the "pkg" string is equal to "builtins"

  Parameters
  ----------
    node: ast.Attribute
      Ast attribute definition node to process

    lut: dict
      Lookup table for the code obfuscator

    header: dict
      Lookup table of the header variables
      to add on the obfuscated code

  Returns
  -------
    obf_node: ast.Call
      The name node with the obfuscated
      variable name

    header: dict
      Updated header
  '''

  # encrypt the package name using hex string
  pkg = ''.join(f"\\x{ord(c):02x}" for c in 'builtins')
  # encrypt the package attribute using hex string
  attr = ''.join(f"\\x{ord(c):02x}" for c in node.func.id)
  # transform the node into a Name one
  # with the function call given by the
  # 'geattr' function using as much strings as possible ;)
  obf_node = ast.Call(
    **{**node.__dict__,
       'func': ast.Name(
          id = f'getattr(__import__("{pkg}"), "{attr}")',
          ctx = ast.Load()
        )
    }
  )

  return obf_node, header

def encrypt_generic_function (node: ast.Call,
                              lut: dict,
                              header: dict
                             ) -> ast.Call:
  '''
  Encryption of generic function.

  The encryption is made by simply replacing the
  function name according to the global lookup
  table of aliases.

  Parameters
  ----------
    node: ast.Call
      Ast callable node to process

    lut: dict
      Lookup table for the code obfuscator

    header: dict
      Lookup table of the header variables
      to add on the obfuscated code

  Returns
  -------
    obf_node: ast.Call
      The callable node with the obfuscated
      callable name

    header: dict
      Updated header
  '''
  # the callable name encryption
  # is simply made by the replacement
  # of the name according to the global lut
  obf_node = ast.Call(
    **{**node.__dict__,
     'func': ast.Name(
        id = lut.get(node.func.id, node.func.id),
        ctx = ast.Load()
      ),
    }
  )
  return obf_node, header

def encrypt_fstring_constant (node: ast.Constant,
                              lut: dict,
                              header: dict
                             ) -> ast.Constant:
  '''
  Encryption of constant string in f-string context.

  The encryption is made by creating a new variable
  in the code header using the hex encoding of the
  string, while in the current f-string the value
  is replaced by the lut value.

  Parameters
  ----------
    node: ast.Constant
      Ast constant string node to process

    lut: dict
      Lookup table for the code obfuscator

    header: dict
      Lookup table of the header variables
      to add on the obfuscated code

  Returns
  -------
    obf_node: ast.Constant
      The constant string node with the obfuscated
      string name

    header: dict
      Updated header
  '''

  # get the variable name from the lut
  var_name = lut.get(node.value, node.value)
  # get the encoded value of the string
  obf_value = ''.join(f"\\x{ord(c):02x}" for c in node.value)
  # update the header according to this new variable
  header[var_name] = f'"".join(chr(x) if isinstance(x, int) else x for x in "{obf_value}")'

  # create a new obfuscated node
  obf_node = ast.Constant(
    **{**node.__dict__,
       'value': '{' + var_name + '}'
    }
  )

  return obf_node, header

def encrypt_fstring_value (node: ast.FormattedValue,
                           lut: dict,
                           header: dict
                          ) -> ast.FormattedValue:
  '''
  Encryption of formatted string in f-string context.

  The encryption is made by encoding the value
  using the global lut (if it is a name).

  Parameters
  ----------
    node: ast.FormattedValue
      Ast string node to process

    lut: dict
      Lookup table for the code obfuscator

    header: dict
      Lookup table of the header variables
      to add on the obfuscated code

  Returns
  -------
    obf_node: ast.FormattedValue
      The string node with the obfuscated
      string name

    header: dict
      Updated header
  '''
  # if the node value is a Name, I know how
  # to encrypt it... otherwise I don't know...
  if isinstance(node.value, ast.Name):
    obf_node = ast.FormattedValue(
      **{**node.__dict__,
        'value':ast.Name(
          **{**node.value.__dict__,
            'id': lut.get(node.value.id, node.value.id)
          }
        )
      }
    )

    return obf_node, header

  else:
    return node, header

def encrypt_joined_string (node: ast.JoinedStr,
                           lut: dict,
                           header: dict
                          ) -> ast.JoinedStr:
  '''
  Encryption of f-string nodes.

  The encryption is made by encoding each element
  of the f-string according to its type.

  Parameters
  ----------
    node: ast.JoinedStr
      Ast string node to process

    lut: dict
      Lookup table for the code obfuscator

    header: dict
      Lookup table of the header variables
      to add on the obfuscated code

  Returns
  -------
    obf_node: ast.JoinedStr
      The string node with the obfuscated
      string name

    header: dict
      Updated header
  '''

  # get the joined string values
  values = node.values
  # create the encoded version of them
  encoded = []
  # loop over the values
  for v in values:
    # if the value is a constant instance
    if isinstance(v, ast.Constant):
      # encrypt the constant item of the f-string
      obf_value, header = encrypt_fstring_constant(
        node=v,
        lut=lut,
        header=header
      )
      # append the encoded value
      encoded.append(obf_value)
    # if the value is a formatted value instance
    elif isinstance(v, ast.FormattedValue):
      # encrypt the value item of the f-string
      obf_value, header = encrypt_fstring_value(
        node=v,
        lut=lut,
        header=header
      )
      # append the encoded value
      encoded.append(obf_value)
    # in any other case... I don't what is happening
    else:
      encoded.append(v)

  # transform the node into an obfuscated one
  obf_node = ast.JoinedStr(
    **{**node.__dict__,
      'values': encoded,
    }
  )

  return obf_node, header

def add_header_variables (root : ast.Module,
                          header : dict
                         ) -> ast.Module:
  '''
  Add extra variable in the header of the obfuscated
  code to take care of the encoding done.

  Parameters
  ----------
    root: ast.Module
      Ast module to edit

    header: dict
      Lookup table of the header variables
      to add on the obfuscated code

  Returns
  -------
    root: ast.Module
      Edited module
  '''

  # the node transformation involves the
  # creation of new variables that must be put
  # as header of the obfuscated script
  # Now it is time to add them...

  # loop along the keys and values of the header
  for k, v in header.items():
    # add a new variable item
    root = insert_new_variable_in_header(
      root=root,
      name=k, # variable name
      value=v, # variable value (encoded)
    )

  return root

def clean_header_issues (code : str,
                         header : dict
                        ) -> str:
  '''
  Post-processing of the obfuscated code
  according to the issues pointed-out by the
  node transformation.

  Parameters
  ----------
    code: str
      Obfuscated code to process

    header: dict
      Lookup table of the header variables
      to add on the obfuscated code

  Returns
  -------
    code: str
      Processed code according to the header
      information
  '''

  # the header variables requires some post-processing
  # since the node transformation could have issues.
  # NOTE: this step could be avoided using a better
  # node transformation in the previous steps...

  # loop along the keys and values of the header
  for k, v in header.items():
    # some values has an extra '' term
    code = code.replace(f"'{v}'", v)
    # some keys has an extra '' term
    code = code.replace(f"'{k}'", k)
    # some keys has an extra {
    code = code.replace('{' + k + '}', k)
    # the hex strings must be corrected
    code = code.replace(f"'{v}'".replace('\\', '\\\\'), v)

  return code
