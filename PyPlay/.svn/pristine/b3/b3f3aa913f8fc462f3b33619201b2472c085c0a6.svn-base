
from collections import defaultdict

from nltk import corpus
from nltk import ConditionalFreqDist

word_to_context = ConditionalFreqDist()
context_to_word = ConditionalFreqDist()

tokens = corpus.brown.words()
def context( tokens, i ):
    if i == 0:
        return ('*START*', tokens[i+1].lower())
    if i == len(tokens) - 1:
        return (tokens[i-1].lower(), '*END*')
    return (tokens[i-1].lower(), tokens[i+1].lower())
    
for i, word in enumerate( tokens ):
    word_to_context[ word.lower() ].inc( context(tokens, i) )
    context_to_word[ context(tokens, i) ].inc( word.lower() )

threshold = 10
groups = defaultdict(list)
for w in word_to_context.conditions():
    if w not in groups:
        groups[w] = [w]
        for c in word_to_context[w]:
            for word in context_to_word[c]:
                if context_to_word[c][word] * context_to_word[c][w] > threshold:
                    groups[w].append( word )
                    groups[word] = groups[w]

for v in set(tuple(v) for v in groups.values()):
    print v
    print
    
def similar( word ):
    word = word.lower()
    scores = defaultdict(int)
    for c in word_to_context[ word ]:
        for w in context_to_word[ c ]:
            if w != word:
                scores[w] += context_to_word[c][word] * context_to_word[c][w]

    return sorted(scores, key=scores.get, reverse=True)[:10]

print similar( 'woman' )
print similar( 'bought' )
            
    

    
    
