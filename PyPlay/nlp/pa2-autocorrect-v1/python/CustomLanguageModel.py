
import math
from collections import defaultdict

class CustomLanguageModel:
  def __init__(self, corpus):
    """Initialize your data structures in the constructor."""
    self.bigrams = defaultdict(int)
    self.unigrams = defaultdict(int)
    self.nunigrams = defaultdict(int)

    self.nwords = 0
    self.total_words = 0
    self.total_bigrams = 0
    self.train(corpus)

  def best_fit( self, xs, ys ):
    N = float(len(xs))
    x, y = sum( xs ) / N, sum( ys ) / N
    xy = sum( x*y for x, y in zip(xs, ys) ) / N
    xx = sum( x*x for x in xs ) / N
    
    b = (xy - x*y) / (xx - x*x)
    a = y - b*x
    return a, b
    
  def train(self, corpus):
    """ Takes a corpus and trains your language model. 
        Compute any counts or other corpus statistics in this function.
    """  
    for sentence in corpus.corpus:
      l = '<s>'
      self.unigrams[ '<s>' ] += 1
      self.total_words += 1
      for datum in sentence.data:
        if not self.unigrams[ datum.word ]:
          self.nwords += 1

        self.bigrams[ (l, datum.word) ] += 1
        self.total_bigrams += 1

        self.unigrams[ datum.word ] += 1
        self.total_words += 1
        
        l = datum.word

      self.bigrams[ (datum.word, '</s>') ] += 1
      self.total_bigrams += 1

    for k, v in self.unigrams.items():
      self.nunigrams[ v ] += 1

    xs, ys = [], []
    for i in range(3, 15):
      v = self.nunigrams[i]
      if not v: break
      xs.append( math.log(i) )
      ys.append( math.log(v) )

    a, b = self.best_fit( xs, ys )
    for i in range(3, max(self.nunigrams.keys())+2):
      self.nunigrams[i] = math.exp(a + b*math.log(i))

  def score_item( self, l, w, ls ):
    score = 0.0
    if self.bigrams[ (l, w) ]:
      score += math.log( self.bigrams[ (l, w) ] )
      score -= math.log( self.unigrams[ l ] )
    else:
      c = self.unigrams[ w ]
      if not c:
        score += math.log( self.nunigrams[1] )
        score -= 2*math.log( self.total_words )
      else:
        score += math.log( c + 1 )
        score += math.log( self.nunigrams[c + 1] )
        score -= math.log( self.nunigrams[c] )
        score -= math.log( self.total_words )
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

