
import math
from collections import defaultdict

class StupidBackoffLanguageModel:

  def __init__(self, corpus):
    """Initialize your data structures in the constructor."""
    self.bigrams = defaultdict(int)
    self.unigrams = defaultdict(int)
    self.nwords = 0
    self.total_words = 0
    self.train(corpus)

  def train(self, corpus):
    """ Takes a corpus and trains your language model. 
        Compute any counts or other corpus statistics in this function.
    """  
    for sentence in corpus.corpus:
      l = '<s>'
      self.unigrams[ '<s>' ] += 1
      for datum in sentence.data:
        if not self.unigrams[ datum.word ]:
          self.nwords += 1
        self.bigrams[ (l, datum.word) ] += 1
        self.unigrams[ datum.word ] += 1
        self.total_words += 1
        l = datum.word
      self.bigrams[ (datum.word, '</s>') ] += 1

  def score_item( self, l, w, ls ):
    score = 0.0
    if self.bigrams[ (l, w) ]:
      score += math.log( self.bigrams[ (l, w) ] )
      score -= math.log( self.unigrams[ l ] )
    else:
      score += math.log( 0.4 ) + math.log( self.unigrams[ w ] + 1 )
      score -= math.log( self.total_words + ls )
    return score
    
  def score(self, sentence):
    """ Takes a list of strings as argument and returns the log-probability of the 
        sentence using your language model. Use whatever data you computed in train() here.
    """
    l = '<s>'
    score = 0.0
    for w in sentence:
      score += self.score_item( l, w, len(sentence) )
      l = w
    score += self.score_item( w, '</s>', len(sentence) )
    return score
