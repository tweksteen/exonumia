#!/usr/bin/env python

import math
import numpy
import base64

def monobit_test(bsq):
  bsqc = [ 2*x -1 for x in bsq ]
  n = len(bsq)
  s_obs = abs(sum(bsqc)) / math.sqrt(float(n))
  p_value = math.erfc(s_obs/math.sqrt(2))
  return p_value

def validate_integrity(tks):
  sizes = set([ len(t) for t in tks])
  if len(sizes) == 1:
    print "Tokens are {} bits long".format(sizes.pop() * 8)
    return True
  else:
    print "Tokens have various sizes: {}".format(sizes)
    return False

def expand_tokens_bits(tks):
  l = len(tks[0]) * 8
  r = []
  for i in range(l):
    idx = i/8
    shift = 7 - (i % 8)
    mask = (1 << shift)
    r.append([((ord(t[idx]) & mask) >> shift) for t in tks])
  return r

def main():
  tks = open("java_context_id.txt").read().splitlines()
  dtks =  [ base64.urlsafe_b64decode(t + "==") for t in tks ]
  if not validate_integrity(dtks):
    return
  bsqs = expand_tokens_bits(dtks)
  for i,bsq in enumerate(bsqs):
    p_value = monobit_test(bsq)
    if p_value < 0.01:
      print "Bit {0} has failed the monobit test (p-value={1})".format(i, p_value)

main()
