#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import sys
import argparse
from datetime import datetime

from pyhide import __version__
from pyhide import Obfuscator
from pyhide import set_time_bomb

__author__ = ['Nico Curti']
__email__ = ['nico.curti2@unibo.it']


def parse_args ():

  description = ('pyhide - '
    'Python code obfuscator'
  )

  parser = argparse.ArgumentParser(
    prog='pyhide',
    argument_default=None,
    add_help=True,
    prefix_chars='-',
    allow_abbrev=True,
    exit_on_error=True,
    description=description,
    epilog=f'pyHide Python package v{__version__}'
  )

  # pyhide --version
  parser.add_argument(
    '--version', '-v',
    dest='version',
    required=False,
    action='store_true',
    default=False,
    help='Get the current version installed',
  )

  # input file -i
  parser.add_argument(
    '--input', '-i',
    dest='inptfile',
    required=True,
    action='store',
    help='Input python file to obfuscate'
  )

  # output file -o
  parser.add_argument(
    '--output', '-o',
    dest='outfile',
    required=False,
    action='store',
    default=None,
    help='Output obfuscated python code'
  )

  # encode variable -x
  parser.add_argument(
    '--variable', '-x',
    dest='rename_variable',
    required=False,
    action='store_true',
    default=False,
    help='Enable/Disable the variable encoding',
  )

  # encode function -f
  parser.add_argument(
    '--function', '-f',
    dest='rename_function',
    required=False,
    action='store_true',
    default=False,
    help='Enable/Disable the function encoding',
  )

  # encode class -c
  parser.add_argument(
    '--class', '-c',
    dest='rename_class',
    required=False,
    action='store_true',
    default=False,
    help='Enable/Disable the class encoding',
  )

  # encode pkg -p
  parser.add_argument(
    '--pkg', '-p',
    dest='encode_pkg',
    required=False,
    action='store_true',
    default=False,
    help='Enable/Disable the package encoding',
  )

  # encode number -n
  parser.add_argument(
    '--num', '-n',
    dest='encode_number',
    required=False,
    action='store_true',
    default=False,
    help='Enable/Disable the number encoding',
  )

  # encode string -s
  parser.add_argument(
    '--str', '-s',
    dest='encode_string',
    required=False,
    action='store_true',
    default=False,
    help='Enable/Disable the string encoding',
  )

  # time bomb of the script -b
  parser.add_argument(
    '--bomb', '-b',
    dest='time_bomb',
    required=False,
    action='store',
    type=str,
    default=None,
    help='Set the maximum datetime (dd/mm/yyyy fmt) after which the code stops to run'
  )

  args = parser.parse_args()

  return args


def main ():

  # get the cmd parameters
  args = parse_args()

  # results if version is required
  if args.version:
    # print it to stdout
    print(f'Graphomics package v{__version__}',
      end='\n', file=sys.stdout, flush=True
    )
    # exit success
    exit(0)

  # check the correctness of the input file extension
  name, ext = os.path.splitext(args.inptfile)
  if ext != '.py':
    raise ValueError(('Invalid extension file in provided input code. '
      'The code obfuscator works only for .py files. '
      f'Given: {args.inptfile}'
    ))

  # if the output file is not set create it using the
  # input name
  if args.outfile is None:
    args.outfile = f'{name}_obf{ext}'

  # create the obfuscator object
  obf = Obfuscator(
    rename_variable=args.rename_variable,
    rename_function=args.rename_function,
    rename_class=args.rename_class,
    encode_pkg=args.encode_pkg,
    encode_number=args.encode_number,
    encode_string=args.encode_string,
  )

  # parse the input file
  with open(args.inptfile, 'r', encoding='utf-8') as fp:
    code = fp.read()

  # check if the timebomb is required
  if args.time_bomb is not None:
    now = datetime.now()
    now = now.strftime('%d/%m/%Y')
    bomb = f"""
bomb = '''
from datetime import datetime

now = datetime.strptime('{now}', '%d/%m/%Y')
death = datetime.strptime('{args.time_bomb}', '%d/%m/%Y')
if death > now:
  print('The code is no longer available... sorry', end='', flush=True)
  exit(1)
'''
exec(bomb)
"""
  code = set_time_bomb(code=code, bomb=bomb, position=0)

  # call the obfuscator and get the encrypted version of the
  # code according to the provided parameters
  obf_code = obf(code)

  # dump the resulting code to the output file
  with open(args.outfile, 'w', encoding='utf-8') as fp:
    fp.write(obf_code)

  # exit success
  exit(0)

if __name__ == '__main__':

  main ()
