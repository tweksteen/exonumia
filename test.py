#!/usr/bin/env python
import sys
import os.path
import argparse

import binary
import character 
import utils

alpha = 0.01

def input_token():
  x = sys.stdin.read()[:-1]
  bsqs = [ [ int(y) for y in x ],]
  binary.run_all_tests(bsqs)

def urandom(alpha):
  s = list(open("/dev/urandom").read(4096))
  bsqs = binary.expand_tokens_bits(s)
  binary.run_all_tests(bsqs, alpha)

def main():
  parser = argparse.ArgumentParser()
  parser.add_argument("-v", "--verbose", 
                      help="increase output verbosity", action="count")
  group = parser.add_mutually_exclusive_group(required=True)
  group.add_argument("-u", "--urandom", 
                     help="test 4096 bytes from /dev/urandom", 
                     action="store_true")
  group.add_argument("-c", "--character", metavar="FILE", 
                     help="perform character analysis on a file", type=file)
  group.add_argument("-b", "--binary", metavar="FILE", 
                     help="perform binary analysis on a file", type=file)
  args = parser.parse_args()
  
  if args.urandom:
    urandom(alpha)
  elif args.binary:
    binary.analyse(args.binary.read().splitlines(), alpha, args.verbose)
  elif args.character:
    character.analyse(args.character.read().splitlines(), alpha, args.verbose)
  else:
    parser.print_help()
      
if __name__ == '__main__':
  main()
