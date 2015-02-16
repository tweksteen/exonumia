import base64
import itertools
from math import sqrt, erfc, log, pow
from binascii import unhexlify

import scipy.special
from numpy import fft, abs, sum

from utils import info, success, warning, error, phi

def validate_length(tks):
  sizes = set([ len(t) for t in tks])
  if len(sizes) == 1:
    print "Tokens have consistent length"
    return True
  else:
    print error("Tokens have various sizes: {}".format(sizes))
    return False

def expand_bytes(tks):
  l = len(tks[0]) * 8
  r = []
  for i in range(l):
    idx = i/8
    shift = 7 - (i % 8)
    mask = (1 << shift)
    r.append([((ord(t[idx]) & mask) >> shift) for t in tks])
  return r

def _b64_decode(tks, fct):
  pad = ""
  done = False
  while not done:
    try:
      dtks = [ fct(tk + pad) for tk in tks ]
    except TypeError, e:
      pad += "="
      if len(pad) > 2:
        raise e
      continue
    done = True
  return dtks

def decode_and_expand(tks, decode_method):
  print "Decoding using", decode_method
  if decode_method == "base64":
    dtks = _b64_decode(tks, base64.decodestring)
    if not validate_length(dtks): return
    bsqs = expand_bytes(dtks)
  elif decode_method == "base64_urlsafe":
    dtks = _b64_decode(tks, base64.urlsafe_b64decode)
    if not validate_length(dtks): return
    bsqs = expand_bytes(dtks)
  elif decode_method == "bin":
    dtks = tks
    if not validate_length(dtks): return
    bsqs = [ [ int(x) for x in l ] for l in zip(*dtks) ]
  elif decode_method == "hex":
    dtks = [ unhexlify(tk) for tk in tks ]
    if not validate_length(dtks): return
    bsqs = expand_bytes(dtks)
  else:
    print error("Decoding method unknown: {}".format(decode_method))
    print error("Available methods are: base64, base64_urlsafe, bin, hex")
    return None, None
  return dtks, bsqs

def frequency_test(bsq):
  bsqc = [ 2*x -1 for x in bsq ]
  n = len(bsq)
  s_obs = abs(sum(bsqc)) / sqrt(float(n))
  p_value = erfc(s_obs/sqrt(2))
  reason = "There is a disproportion between the number of 0 and 1:\n"
  reason += "#0: {} #1: {}".format(bsq.count(0), bsq.count(1))
  return p_value, reason

def run_test(bsq):
  vn = sum([ 0 if bsq[i] == bsq[i+1] else 1 for i in range(len(bsq)-1)]) + 1
  n = len(bsq)
  n1 = sum(bsq)
  n2 = n - n1
  mu = (2.*n1*n2 / n) + 1
  var = (mu-1) * (mu-2) / (n-1)
  if var == 0:
    return 0, "The frequency of the bits is obvious. See frequency_test"
  p_value = erfc(abs(vn - mu) / sqrt(2*var))
  reason = "There is a abnormal level of runs (sequence of identical bit)\n"
  if vn > mu:
    reason += "The oscillation between zeros and ones is too fast"
  else:
    reason += "The oscillation between zeros and ones is too slow"
  return p_value, reason

def _phi_m(bsq, m):
  v = list(itertools.product(["0","1"], repeat=m))
  dv = dict(zip([ "".join(x) for x in v], [0,] * len(v)))
  ebsq = bsq + bsq[:m-1]
  n = len(bsq)
  for i in range(len(bsq)):
    dv["".join(map(str,ebsq[i:i+m]))] += 1
  assert n == sum(dv.values())
  s = sum([ v**2 for v in dv.values()])
  return ((float(2**m) * s) / n) - n, dv

def serial_test(bsq):
  phi_3, dv3 = _phi_m(bsq, 3)
  reason = "Some patterns are more likely to appears:\n"
  reason += str(dv3) + "\n"
  phi_2, dv2 = _phi_m(bsq, 2)
  reason += str(dv2)
  phi_1, dv1 = _phi_m(bsq, 1)
  d1 = phi_3 - phi_2
  d2 = phi_3 - 2*phi_2 + phi_1
  p_value1 = 1 - scipy.special.gammainc(2, d1/2)
  p_value2 = 1 - scipy.special.gammainc(1, d2/2)
  p_value = min(p_value1, p_value2)
  return p_value, reason

def fourier_transform_test(bsq):
  bsqc = [ 2*x-1 for x in bsq ]
  n = len(bsqc)
  s = fft.fft(bsqc)
  m = abs(s[range(n/2)])
  t = sqrt(log(1./0.05)*n)
  n0 = .95*n/2
  n1 = len([x for x in m if x<t])
  d = (n1-n0)/sqrt(n*.95*.05*.25)
  p_value = erfc(abs(d)/sqrt(2))
  reason = "#peaks_obs: {}, #peaks_exp= {}, threshold={}".format(n1, n0, t)
  return p_value, reason

def backward_cumsum_test(bsq):
  return cumsum_test(bsq, True)

def cumsum_test(bsq, reverse=False):
  n = len(bsq)
  st = 0
  z = -1
  bsqc = [ 2*x-1 for x in bsq ]
  for i in range(n):
    if reverse:
      st += bsqc[n-i-1]
    else:
      st += bsqc[i]
    if abs(st) > z:
      z = abs(st)
  t1 = sum([ phi(((4*k+1)*z)/sqrt(n)) - phi(((4*k-1)*z)/sqrt(n)) for k in
           range((-n/z+1)/4, (n/z-1)/4+1)])
  t2 = sum([ phi(((4*k+3)*z)/sqrt(n)) - phi(((4*k+1)*z)/sqrt(n)) for k in
           range((-n/z-3)/4, (n/z-1)/4+1)])
  p_value = 1 - t1 + t2
  reason  = "A random walk significantly deviates from its origin."
  return p_value, reason

def phi_coefficient_test(bsq1, bsq2):
  n = len(bsq1)
  cmb = zip(bsq1, bsq2)
  a, b = cmb.count((0,0)), cmb.count((0,1))
  c, d = cmb.count((1,0)), cmb.count((1,1))
  if any(x == 0 for x in [a,b,c,d]):
    p_value = 0
  else:
    phi = float(a*d - b*c) / sqrt((a+b)*(c+d)*(a+c)*(b+d))
    chi_2 = n * pow(phi,2)
    p_value = erfc(sqrt(chi_2/2) )
  reason = "Two characters sequences are correlated. An abnormal level of "
  reason += "pairs has been detected:\n"
  reason += "#(0,0): {} #(0,1): {} #(1,0): {} #(1,1): {}".format(a,b,c,d)
  return p_value, reason

def run_all_tests(bsqs, alpha, filtered, verbose):
  n = len(bsqs)
  ibsqs = dict(zip(range(n), bsqs))
  for test in [frequency_test, serial_test, run_test, fourier_transform_test,
               cumsum_test, backward_cumsum_test]:
    print "Running {}".format(test.__name__)
    failed = set()
    for i, bsq in ibsqs.iteritems():
      p_value, reason = test(bsq)
      if p_value < alpha:
        print error("  {0} has failed (bit position={1}, p-value={2})".format(
                                                   test.__name__, i, p_value))
        print "  Reason:\n  {}".format(reason.replace("\n", "\n  "))
        failed.add(i)
      elif verbose:
        print success("  {0} has passed (bit position={1}, p-value={2})".format(
                                                     test.__name__, i, p_value))
    if filtered:
      ibsqs = dict([ (i, bsq) for i, bsq in ibsqs.iteritems() if i not in failed ])
      print "Keeping the following positions for further testing: ", ibsqs.keys()
  if filtered:
    print "Random bits (%d):" % len(ibsqs), ibsqs.keys()
  if len(ibsqs) > 1:
    print "Running correlation_test"
    for bsq1i, bsq2i in itertools.combinations(ibsqs.keys(), 2):
      p_value, reason = phi_coefficient_test(bsqs[bsq1i], bsqs[bsq2i])
      if p_value < alpha:
        print error("  correlation_test has failed (bit positions=({0},{1})," \
                    " p-value={2})".format(bsq1i, bsq2i, p_value))
        print "  Reason:\n  {}".format(reason.replace("\n", "\n  "))
      elif verbose:
        print success("  correlation_test  has passed (bit positions=" \
                      "({0},{1}), p-value={2})".format(bsq1i, bsq2i, p_value))
  else:
    print "Tokens are only one bit long. Not running the correlation tests."

def analyse(tks, alpha, decoding, filtered, verbose):
  print info("Running the binary analysis on {} tokens...".format(len(tks)))
  dtks, bsqs = decode_and_expand(tks, decoding)
  if dtks:
    run_all_tests(bsqs, alpha, filtered, verbose)

