#!/usr/bin/env python
# -*- coding: utf-8 -*-

import numpy as np

def func (a, b, c):
  return np.sum([a, b, c])

print(func(1, 2, 3), end='', flush=True)
