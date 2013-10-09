#!/usr/bin/env python

from sklearn import linear_model
from sklearn import preprocessing
from sklearn import cross_validation

from utils import alphabet

def build_features(tks, cs):
  features = []
  for tk in tks:
    f = [ float(tk.count(c))/len(tk) for c in cs ]
    features.append(f)
  return features

# Open sets
tks1 = open("examples/uuid12.txt").read().splitlines()
tks2 = open("examples/uuid1.txt").read().splitlines()
cs = list(alphabet(tks1 + tks2))
#print cs

# Build features from both sets
f1 = build_features(tks1, cs)
f2 = build_features(tks2, cs)
target = [0,] * len(f1) + [1,] * len(f2)

#print f1[:2]
#print f2[:2]
#print target[:2]

# Cross validate (learn & test)
X = f1 + f2
X_train, X_test, y_train, y_test = cross_validation.train_test_split(
     X, target, test_size=0.3)

logistic = linear_model.LogisticRegression()
logistic.fit(X_train, y_train)

for i, c in enumerate(cs):
  print logistic.coef_[0][i], c

#for x,y in zip(X_test, y_test):
#  print x, logistic.predict(x), y

print('LogisticRegression score: %f' % logistic.score(X_test, y_test))
