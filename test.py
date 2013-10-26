#!/usr/bin/env python
import sys
import argparse

import binary
import character 

def input_token():
  x = sys.stdin.read()[:-1]
  bsqs = [ [ int(y) for y in x ],]
  binary.run_all_tests(bsqs)

def urandom(alpha, verbose):
  s = list(open("/dev/urandom").read(4096))
  bsqs = binary.expand_bytes(s)
  binary.run_all_tests(bsqs, alpha, False, verbose)

def main():
  parser = argparse.ArgumentParser()
  parser.add_argument("-v", "--verbose", 
                      help="increase output verbosity", action="count")
  parser.add_argument("-f", "--filtered", action="store_true", 
                     help="do not execute further tests on already failed bits")
  parser.add_argument("-a", "--alpha", action="store", type=float,
                     help="alpha", default=0.001)
  parser.add_argument("-e", "--encoding", action="store", default="",
                     help="specify the format of the tokens")
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
    urandom(args.alpha, args.verbose)
  elif args.binary:
    binary.analyse(args.binary.read().splitlines(), args.alpha, args.encoding,
                   args.filtered, args.verbose)
  elif args.character:
    character.analyse(args.character.read().splitlines(), args.alpha, args.verbose)
  else:
    parser.print_help()
      
if __name__ == '__main__':
  main()
