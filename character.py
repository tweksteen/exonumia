import string


def freq_test(csq, cs):
  f = {}
  for c in cs:
    f[c] = csq.count(c)
  print min(f.values()), max(f.values())
  print f.values()
  print float(len(csq))/len(cs)
