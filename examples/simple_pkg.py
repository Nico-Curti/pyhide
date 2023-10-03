#!/usr/bin/env python
# -*- coding: utf-8 -*-

import numpy as np

__author__  = ['Nico Curti']
__email__ = ['nico.curti2@unibo.it']

def func (a, b, c):
  return np.sum([a, b, c])

print(func(1, 2, 3), end='', flush=True)
