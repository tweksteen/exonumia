#!/usr/bin/env python

import base64
import os.path
from binascii import unhexlify
from itertools import combinations

from binary import *
from character import *

alpha = 0.01

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

def expand_tokens_chars(tks):
  l = len(tks[0])
  r = []
  for i in range(l):
    r.append([t[i] for t in tks])
  return r

def all_test(bsqs):
  bsqs = enumerate(bsqs)
  for t in [monobit_test, run_test_fips, run_test_std, fourier_transform_test, ]:
    passed = []
    for i, bsq in bsqs:
      p_value = t(bsq)
      if p_value < alpha:
        print "Bit {0} has failed {1} (p-value={2})".format(i, t.__name__, p_value)
      else:
        passed.append((i,bsq))
    bsqs = passed
  print "Random bits (%d):" % len(passed), [ i for i,e in passed ]
  for bsq1i, bsq2i in combinations(range(len(bsqs)), 2):
    p_value = phi_coefficient_test(bsqs[bsq1i][1], bsqs[bsq2i][1])
    if p_value < alpha:
      print "Bit {0} and {1} are correlated (p-value={2})".format(bsq1i, bsq2i, p_value)
    

def urandom():
  s = list(open("/dev/urandom").read(4096))
  bsqs = expand_tokens_bits(s)
  all_test(bsqs)

def btoken_file():
  tks = open(os.path.expanduser("~/.current/pwreset_tokens")).read().splitlines()
  dtks = [ unhexlify(t) for t in tks ] 
  #dtks =  [ base64.urlsafe_b64decode(t + "==") for t in tks ]
  if not validate_integrity(dtks):
    return
  bsqs = expand_tokens_bits(dtks)
  all_test(bsqs)

def ctoken_file():
  tks = open(os.path.expanduser("~/.current/tokens2")).read().splitlines()
  csqs = expand_tokens_chars(tks)
  for csq in csqs:
    freq_test(csq, "0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZ")

def base32hex(s):
  ctable = ('0', '1', '2', '3', '4', '5', '6', '7', '8', '9', 'a', 'b', 'c', 'd', 'e', 'f', 'g', 'h', 'i', 'j', 'k', 'l', 'm', 'n', 'o', 'p', 'q', 'r', 's', 't', 'u', 'v')
  return "".join([ ctable.index(c) for c in s])
    

def input_token():
  import sys
  x = sys.stdin.read()[:-1]
  bsqs = [ [ int(y) for y in x ],]
  all_test(bsqs)

#urandom()
btoken_file()
