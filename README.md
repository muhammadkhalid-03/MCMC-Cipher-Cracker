# Cipher Cracker (python)

This is a python program that cracks substitution ciphers using the Metropolis-Hasting Algorithm

It uses a transition matrix derived from a reference text (War and Peace) to measure how well a proposed reverse cipher unscrambles the message into "proper English". The algorithm iteratively proposes new reverse ciphers by swapping two letters, calculates acceptance probabilities based on the transition probabilities of letter pairs in the unscrambled text, and keeps track of the best solution found. This process runs for 10,000 iterations to find the most likely reverse cipher that decodes the scrambled message.
