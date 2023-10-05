#!/usr/bin/env python
# -*- coding: utf-8 -*-

class A:

  def __init__ (self, l):
    self.list = l

  def func (self, x):
    return self.list + x

a = A([1, 2, 3])
print(a.func([1, 2, 3]), end='', flush=True)
