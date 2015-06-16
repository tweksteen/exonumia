Token analyser presented at Ruxcon 2013. Use it to analyse session tokens, cookies, ticket numbers and any strings that may easily be collected.

# High level view

Two different approaches are possible:
  * Randomness tests: determine if the tokens are drawn from a random source.
  * Classification between two sets: determine if two different sets may be separated.

Things to keep in mind when analysing tokens:
  * Measure (Environment and Conditions).  (e.g., authenticated user, time of day)
  * Encoding and common formats. (e.g, Base16/Base32*/Base64{urlsafe}/hex/URL encoded/UUID)

# Randomness test

First, by considering the characters themselves:

    [tweek@sec0 exonumia]$ ./test.py -c ./examples/uuid1.txt
    Running the character analysis on 1000 tokens...
    Running global_freq_test
    It seems that 1 character(s) is/are extra: -
    (compared to 0123456789abcdef)
    global_freq_test has failed (p-value=0.0)
    Reason:
    Some characters appear not or too often. Below is the occurrence numbers:
    Min=179 Max=4319 E.Avg=2117.64705882
    [...]

Exonumia will try to match the observed character set with a known character set.
If no exact matching is found a warning is returned. In this case, the hexadecimal
set has been identified but an extra character has been found "-".

By default, only failed tests will be reported. For a full report, use the "-v" option.

Another warning included in the previous test:

    Running serial_test_nonoverlap at position 5
    It seems to be hexadecimal, consider decoding and use the binary tests

To run a binary analysis, use the "-b" flag in conjunction with the "-e" flag:

    [tweek@sec0 exonumia]$ ./test.py -b ./examples/django_csrf_token.txt -e hex
    Running the binary analysis on 10100 tokens...
    Decoding using hex
    Tokens have consistent length
    Running frequency_test
    Running serial_test
    [...]

By using the "-f" flag, it is possible to filter the position that have failed a test. i.e., only continue the analysis on the bits that are random enough.

    [tweek@sec0 exonumia]$ ./test.py -b ./examples/django_csrf_token.txt -e hex -f
    Running the binary analysis on 10100 tokens...
    Decoding using hex
    Tokens have consistent length
    Running frequency_test
    Keeping the following positions for further testing:  [0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20, 21, 22, 23, 24, 25, 26, 27, 28, 29, 30, 31, 32, 33, 34, 35, 36, 37, 38, 39, 40, 41, 42, 43, 44, 45, 46, 47, 48, 49, 50, 51, 52, 53, 54, 55, 56, 57, 58, 59, 60, 61, 62, 63, 64, 65, 66, 67, 68, 69, 70, 71, 72, 73, 74, 75, 76, 77, 78, 79, 80, 81, 82, 83, 84, 85, 86, 87, 88, 89, 90, 91, 92, 93, 94, 95, 96, 97, 98, 99, 100, 101, 102, 103, 104, 105, 106, 107, 108, 109, 110, 111, 112, 113, 114, 115, 116, 117, 118, 119, 120, 121, 122, 123, 124, 125, 126, 127]
    Running serial_test
    [...]


# Classification

In this case, you need two sets of measure. For instance, try to gather a list
of session identifier a t1 and another the day after at t2. We will try to
classify each set according to some features. If the score of the validation
is high enough, we could deduce that the time plays a role in the token representation.

This can also apply to any other factor you have control on (e.g., user, username, etc).

    [tweek@sec0 exonumia]$ ./classify.py ./examples/uuid4.txt ./examples/uuid42.txt
    Reading tokens
    Tokens have consistent length
    Tokens have consistent length
    Alphabet contains 17 characters: -0123456789abcdef
    Size of samples: 1000 and 1000
    Building features
    918 features have been generated
    Dropping empty features
    794 features have been kept
    Cross-validating the model
    Accuracy: 0.50 (+/- 0.06)
    -0.703887294798 #e1
    -0.694081569065 #73
    -0.687461383703 #6d
    -0.65124991849 2@25
    -0.642443165606 1@12
    ...
    0.633505011237 b@20
    0.635616401229 #b1
    0.667363643109 c@25
    0.695773311963 #30
    0.75696748193 #ab

The current features for the character case are:
  * Set of unigram (numbers of "A")
  * Set of bigram (numbers of "AB")
  * Unigram at position (if "A" is at the second position)

For the binary case:
  * Set of unigram (numbers of "1")
  * Set of bigram (numbers of "01")
  * ...
  * Set of n-grams (numbers of "01100011")
  * Unigram at position (if "1" is at the second position)

The naming scheme for these features:
  * `#e1`  => numbers of bi-gram "e1"
  * `b@20` => a character "b" in the 20th position
