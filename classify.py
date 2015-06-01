#!/usr/bin/env python
import operator
import argparse
from itertools import product

import numpy as np
import numpy.ma as ma
from sklearn import linear_model
from sklearn import cross_validation
from sklearn.feature_selection import chi2

from binary import validate_length, decode
from utils import alphabet, success, error

def build_character_features(tks, cs):
  """
  Build a set of features based on the tokens:
    * Set of unigram (numbers of "A")
    * Set of bigram (numbers of "AB")
    * Unigram at position (if "A" is at the second position)

  Return a matrix of size n_tokens x n_features
  """
  f1_size = len(cs)
  f2_size = len(cs) ** 2
  f3_size = len(tks[0]) * len(cs)
  n_features = f1_size + f2_size + f3_size
  features = np.ndarray(shape=(len(tks), n_features))
  for i, tk in enumerate(tks):
    # Unigram
    features[i][:f1_size] = [ float(tk.count(c))/len(tk) for c in cs ]
    fp = f1_size
    # Bigram
    features[i][fp:fp+f2_size] = [ float(tk.count(c1+c2))/(len(tk)/2)
                                   for c1 in cs for c2 in cs ]
    fp += f2_size
    # Unigram at position
    features[i][fp:fp+f3_size] = [ 1 if c == a else 0
                                   for c in cs for a in tk ]
  feature_type = [ "#" + str(c) for c in cs ]
  feature_type.extend([ "#" + str(c1) + str(c2) for c1 in cs for c2 in cs ])
  feature_type.extend([ str(c) + "@" + str(i) for c in cs for i in range(len(tk))])
  return features, feature_type

def build_binary_features(tks, cs, n=8):
  """
  Build a set of features based on the binary tokens:
    * Set of unigram (numbers of "1")
    * Set of bigram (numbers of "01")
    * ...
    * Set of n-grams (numbers of "01100011")
    * Unigram at position (if "1" is at the second position)

  Return a matrix of size n_tokens x n_features
  """
  fn_size = 2**(n+1) - 2
  f3_size = len(tks[0]) * 2
  n_features = fn_size + f3_size
  features = np.ndarray(shape=(len(tks), n_features))
  for i, tk in enumerate(tks):
    # n-grams
    fp = 0
    for l in range(1, n+1):
      l_size = 2**l
      features[i][fp:fp+l_size] = [ float(tk.count("".join(g)))/len(tk)/l
                                    for g in product("01", repeat=l) ]
      fp += l_size
    # Unigram at position
    features[i][fp:fp+f3_size] = [ 1 if c == a else 0
                                   for c in cs for a in tk ]
  feature_type = []
  for l in range(1,n+1):
    feature_type.extend([ "#" + "".join(g) for g in product("01", repeat=l) ])
  feature_type.extend([ str(c) + "@" + str(i) for c in cs for i in range(len(tk))])
  return features, feature_type

def mask_features(X):
  """
  Mask features that are null for all samples
  """
  masked = []
  for i, feature in enumerate(X.T):
    if not feature.any():
      masked.append(i)
  return masked

def read_characters(tks1, tks2, encoding):
  if not validate_length(tks1):
    error("The first samples have different sizes")
    return
  if not validate_length(tks2):
    error("The second samples have different sizes")
    return
  cs = list(alphabet(tks1 + tks2))
  print "Alphabet contains", len(cs), "characters:", "".join(sorted(cs))
  return tks1, tks2, cs

def read_binaries(tks1, tks2, encoding):
  dtks1 = decode(tks1, encoding)
  if not dtks1 or not validate_length(dtks1):
    error("The first samples have different sizes")
    return
  dtks2 = decode(tks2, encoding)
  if not dtks2 or not validate_length(dtks2):
    error("The second samples have different sizes")
    return
  btks1 = [ "".join([np.binary_repr(ord(c), width=8) for c in tk ]) for tk in dtks1 ]
  btks2 = [ "".join([np.binary_repr(ord(c), width=8) for c in tk ]) for tk in dtks2 ]
  return btks1, btks2, "01"

def classify(f1, f2, encoding, verbose):
  # Read tokens
  print "Reading tokens"
  tks1 = f1.read().splitlines()
  tks2 = f2.read().splitlines()
  reader = read_binaries if encoding else read_characters
  dtks1, dtks2, cs = reader(tks1, tks2, encoding)
  print "Size of samples:", len(dtks1), "and", len(dtks2)

  # Build features from both sets
  print "Building features"
  feature_builder = build_binary_features if encoding else build_character_features
  f1,f_type1 = feature_builder(dtks1, cs)
  f2,f_type2 = feature_builder(dtks2, cs)
  assert len(f_type1) == len(f_type2)
  X = np.concatenate((f1, f2))
  print X.shape[1], "features have been generated"
  print "Dropping empty features"
  masked_features = mask_features(X)
  X = np.delete(X, masked_features, 1)
  f_type = np.delete(np.array(f_type1), masked_features)
  print X.shape[1], "features have been kept"
  target = np.concatenate([np.zeros(len(f1)), np.ones(len(f2))])

  # Running Chi2
  #print u"Running features selection via \u03c7\u00b2"
  #c2, pval = chi2(X, target)
  #print list(sorted(pval))
  #for i, pv in enumerate(pval):
  #  if pv < 0.001:
  #    print pv, f_type[i]

  # Cross validate (learn & test)
  print "Cross-validating the model"
  logistic = linear_model.LogisticRegression()
  scores = cross_validation.cross_val_score(logistic, X, target, cv=5)
  acc = scores.mean()
  if acc > 0.9:
    print(success("Accuracy: %0.2f (+/- %0.2f)" % (acc, scores.std() * 2)))
  else:
    print(error("Accuracy: %0.2f (+/- %0.2f)" % (acc, scores.std() * 2)))

  logistic.fit(X, target)
  ordered_coef = sorted(enumerate(logistic.coef_[0]), key=operator.itemgetter(1))
  if verbose:
    for i, c in ordered_coef:
      print c, f_type[i]
  else:
    for i, c in ordered_coef[:5]:
      print c, f_type[i]
    print "..."
    for i, c in ordered_coef[-5:]:
      print c, f_type[i]

def main():
  parser = argparse.ArgumentParser()
  parser.add_argument("-v", "--verbose",
                      help="increase output verbosity", action="count")
  parser.add_argument("-e", "--encoding", action="store", default=None,
                     help="specify the format of the tokens")
  parser.add_argument("file1", type=file, help="file1")
  parser.add_argument("file2", type=file, help="file2")
  args = parser.parse_args()

  classify(args.file1, args.file2, args.encoding, args.verbose)

if __name__ == '__main__':
  main()
