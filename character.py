import string
import operator
import collections

import scipy.special

from utils import info, success, warning, error

def character_set(tks):
  return set("".join(tks))

def validate_charset(cs, verbose):
  # Try to match the character set with something known
  sets = [(string.printable, None), 
          (string.letters + string.digits + "/+", "base64"),
          (string.letters + string.digits + "_-", "base64_urlsafe"),
          (string.letters + string.digits, None),
          (string.letters, None),
          (string.uppercase + string.digits, None),
          (string.uppercase, None),
          (string.lowercase + string.digits, None),
          # TODO: base32
          (string.lowercase, None),
          (string.hexdigits, "hexadecimal"),
          ("0123456789ABCDEF", "hexadecimal"), 
          ("0123456789abcdef", "hexadecimal"), 
          (string.digits, None),
          (string.octdigits, "octal"),
          ("01", "binary"),
         ]
  diff_sym = [ (set(s), len(set(s) ^ cs), sugg) for s,sugg in sets ]
  min_diff_set, diff, sugg = sorted(diff_sym, key=operator.itemgetter(1))[0]
  if diff == 0:
    if verbose:
      print "  The character set seems complete."
    if sugg:
      print warning("  It seems to be {}, consider decoding and use the binary tests".format(sugg))
  else:
    if len(cs) <= 4:
      print warning("  Character set is tiny")
    elif cs <= min_diff_set:
      print warning("  It seems that {0} character(s) is/are missing: {1}".format( 
                      diff,"".join(sorted(min_diff_set - cs))))
      print warning("  (compared to {})".format("".join(sorted(min_diff_set))))
    else:
      print warning("  It seems that {0} character(s) is/are extra: {1}".format(
                      diff, "".join(sorted(cs - min_diff_set))))
      print warning("  (compared to {})".format("".join(sorted(min_diff_set))))

def expand_tokens_chars(tks):
  l = len(tks[0])
  r = []
  for i in range(l):
    r.append([t[i] for t in tks])
  return r

def global_freq_test(csqs, verbose):
  gcs = character_set([ "".join(character_set(csq)) for csq in csqs ])
  if verbose:
    print "  Global Character Set:", "".join(sorted(gcs))
  validate_charset(gcs, verbose)
  return _freq_test("".join(["".join(csq) for csq in csqs]), gcs, verbose)

def local_freq_test(csq, verbose):
  lcs = character_set(csq)
  if verbose:
    print "  Local Character Set:", "".join(sorted(lcs))
  validate_charset(lcs, verbose)
  return _freq_test(csq, lcs, verbose)

def _freq_test(csq, cs, verbose):
  f = {}
  n = len(csq)
  for c in cs:
    f[c] = csq.count(c)
  expected = float(n) / len(cs)
  v_obs = sum([ float((v - expected)**2)/expected for k,v in f.iteritems()])
  if verbose:
    print "  X^2 = %f" % v_obs
  p_value = 1 - scipy.special.gammainc((len(cs) - 1) / 2., v_obs / 2)
  reason = "Some characters appear not or too often. Below is the occurrence numbers:\n"
  reason += "Min={0} Max={1} E.Avg={2}\n".format(min(f.values()), max(f.values()), 
                                                 float(len(csq))/len(cs))
  reason += "{"
  reason += "\n ".join([ "'" + k + "'" + ": " + str(v) for k, v in sorted(f.iteritems(), key=operator.itemgetter(1), reverse=True)])
  reason += "}"
  return p_value, reason

def correlation_test(csq1, csq2, cs):
  pairs = zip(csq1, csq2)
  dpairs = [ ("".join([c1,c2]), pairs.count((c1,c2))) for c1 in cs for c2 in cs ]
  sdpairs = sorted(dpairs, key=operator.itemgetter(1))
  print sdpairs[0], sdpairs[-1]

def diff_test(csq, cs):
  diff = []
  for i in range(len(csq)-1):
    i1 = cs.index(csq[i+1])
    i2 = cs.index(csq[i])
    l = len(cs)
    v = min( abs(i2-i1), abs(i2+l-i1), abs(i2-i1-l))
    diff.append(v)
  ddiff = collections.defaultdict(int)
  for d in diff:
    ddiff[d] += 1
  print sorted(ddiff.items(), key=operator.itemgetter(1))

def analyse(tks, alpha, verbose):
  print info("Running the character analysis on {} tokens...".format(len(tks)))
  csqs = expand_tokens_chars(tks)
  run_all_tests(csqs, alpha, verbose)

def run_all_tests(csqs, alpha, verbose):
  for test in [global_freq_test, ]:
    print "Running {}".format(test.__name__)
    p_value, reason = test(csqs, verbose)
    if p_value < alpha:
      print error("  {0} has failed (p-value={1})".format(test.__name__, p_value))
      print "  Reason:\n  {}".format(reason.replace("\n","\n  "))
    elif verbose:
      print success("  {0} has passed (p-value={1})".format(test.__name__, p_value))
  for test in [local_freq_test, ]:
    for i,csq in enumerate(csqs):
      print "Running {} at position {}".format(test.__name__, i)
      p_value, reason = test(csq, verbose)
      if p_value < alpha:
        print error("  {0} has failed (character position={1}, p-value={2})".format(
                                                            test.__name__, i, p_value))
        print "  Reason:\n  {}".format(reason.replace("\n", "\n  "))
      elif verbose:
        print success("  {0} has passed (character position={1}, p-value={2})".format(
                                                            test.__name__, i, p_value))
  #  diff_test(csq,cgs)
  #for csq1, csq2 in combinations(csqs, 2):
  #  correlation_test(csq1, csq2, gcs)

