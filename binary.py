import math
from binascii import unhexlify
from itertools import combinations

from numpy import fft, abs, sum

def expand_tokens_bits(tks):
  l = len(tks[0]) * 8
  r = []
  for i in range(l):
    idx = i/8
    shift = 7 - (i % 8)
    mask = (1 << shift)
    r.append([((ord(t[idx]) & mask) >> shift) for t in tks])
  return r

def bin_validate(tks):
  sizes = set([ len(t) for t in tks])
  if len(sizes) == 1:
    print "Tokens are {} bits long".format(sizes.pop() * 8)
    return True
  else:
    print "Tokens have various sizes: {}".format(sizes)
    return False

def frequency_test(bsq):
  bsqc = [ 2*x -1 for x in bsq ]
  n = len(bsq)
  s_obs = abs(sum(bsqc)) / math.sqrt(float(n))
  p_value = math.erfc(s_obs/math.sqrt(2))
  if p_value < alpha:
    print "#0: {} #1: {}".format(bsq.count(0), bsq.count(1))
  return p_value

def run_test_fips(bsq):
  vn = sum([ 0 if bsq[i] == bsq[i+1] else 1 for i in range(len(bsq)-1)]) + 1
  n = len(bsq)
  p = float(sum(bsq)) / n
  p_value = math.erfc(abs(vn - 2*n*p*(1-p)) / (math.sqrt(2*n) * 2*p*(1-p)))
  return p_value

def run_test_std(bsq):
  vn = sum([ 0 if bsq[i] == bsq[i+1] else 1 for i in range(len(bsq)-1)]) + 1
  n = len(bsq)
  n1 = sum(bsq)
  n2 = n - n1
  mu = (2.*n1*n2 / n) + 1
  var = (mu-1) * (mu-2) / (n-1)
  p_value = math.erfc(abs(vn - mu) / math.sqrt(2*var))
  return p_value

def fourier_transform_test(bsq):
  bsqc = [ 2*x-1 for x in bsq ]
  n = len(bsqc)
  s = fft.fft(bsqc)
  m = abs(s[range(n/2)])
  t = math.sqrt(math.log(1./0.05)*n)
  n0 = .95*n/2
  n1 = len([x for x in m if x<t])
  d = (n1-n0)/math.sqrt(n*.95*.05*.25)
  p_value = math.erfc(abs(d)/math.sqrt(2))
  if p_value < alpha:
    print "#peaks_obs: {}, #peaks_exp= {}, threshold={}".format(n1, n0, t)
  return p_value

def phi_coefficient_test(bsq1, bsq2):
  n = len(bsq1)
  cmb = zip(bsq1, bsq2)
  a, b = cmb.count((0,0)), cmb.count((0,1))
  c, d = cmb.count((1,0)), cmb.count((1,1))
  phi = float(a*d - b*c) / math.sqrt((a+b)*(c+d)*(a+c)*(b+d))
  chi_2 = n * math.pow(phi,2)
  p_value = math.erfc(math.sqrt(chi_2/2) )
  if p_value < alpha:
    print a,b,c,d
  return p_value

def run_all_tests(bsqs, alpha):
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

def analyse(tks, alpha):
  #dtks = [ unhexlify(t) for t in tks ] 
  #dtks =  [ base64.urlsafe_b64decode(t + "==") for t in tks ]
  if not validate_integrity(dtks):
    return
  bsqs = expand_tokens_bits(dtks)
  run_all_tests(bsqs, alpha)
