#!/usr/bin/env python
import operator
import argparse
from itertools import product

import numpy as np
from sklearn import linear_model
from sklearn import preprocessing
from sklearn import cross_validation

from utils import alphabet, success, error

def build_features(tks, cs):
  features = []
  for tk in tks:
    fc  = [ float(tk.count(c))/len(tk) for c in cs ]
    fc2 = [ float(tk.count(c1+c2))/(len(tk)/2) for c1 in cs for c2 in cs ]
    fc3 = [ 1 if c == a else 0 for c in cs for a in tk ] 
    f = fc + fc2 + fc3
    features.append(f)
  feature_type = [ "#" + str(c) for c in cs ]
  feature_type.extend([ "#" + str(c1) + str(c2) for c1 in cs for c2 in cs ])
  feature_type.extend([ str(c) + "@" + str(i) for c in cs for i in range(len(tk))])
  return features, feature_type

def classify(f1, f2, verbose):
  # Read tokens
  print "Reading tokens"
  tks1 = f1.read().splitlines()
  tks2 = f2.read().splitlines()
  cs = list(alphabet(tks1 + tks2))
  print "Alphabet contains", len(cs), "characters:", "".join(sorted(cs))

  # Build features from both sets
  print "Building features"
  f1,f_type1 = build_features(tks1, cs)
  f2,f_type2 = build_features(tks2, cs)
  assert len(f_type1) == len(f_type2)
  print len(f_type1), "features have been generated"
  target = [0,] * len(f1) + [1,] * len(f2)

  #print f_type1
  #print f1[:2]
  #print f2[:2]
  #print target[:2]

  # Cross validate (learn & test)
  print "Cross-validating the model" 
  X = f1 + f2
  logistic = linear_model.LogisticRegression()
  scores = cross_validation.cross_val_score(logistic, X, np.array(target), cv=5)  
  acc = scores.mean()
  if acc > 0.9:
    print(success("Accuracy: %0.2f (+/- %0.2f)" % (acc, scores.std() * 2)))
  else:
    print(error("Accuracy: %0.2f (+/- %0.2f)" % (acc, scores.std() * 2)))

  logistic.fit(X, target)
  ordered_coef = sorted(enumerate(logistic.coef_[0]), key=operator.itemgetter(1))
  if verbose:
    for i, c in ordered_coef:
      print c, f_type1[i]
  else:
    for i, c in ordered_coef[:5]:
      print c, f_type1[i]
    print "..."
    for i, c in ordered_coef[-5:]:
      print c, f_type1[i]

def main():
  parser = argparse.ArgumentParser()
  parser.add_argument("-v", "--verbose", 
                      help="increase output verbosity", action="count")
  parser.add_argument("file1", type=file, help="file1")
  parser.add_argument("file2", type=file, help="file2")
  args = parser.parse_args()
  
  classify(args.file1, args.file2, args.verbose)
  
if __name__ == '__main__':
  main()
