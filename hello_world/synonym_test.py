from gensim.models import KeyedVectors
from nltk.corpus import wordnet as wn
import copy
# load the Stanford GloVe model
filename = 'glove/glove.6B.200d.txt'
print("loading glove embeddings")
model = KeyedVectors.load_word2vec_format(filename, binary=False, no_header=True)

system_vocabulary = ["i","want","a","steak","soup","salad",]

def wn_similarity(w1, w2):
    topscore = -1
    for i in wn.synsets(w1):
        for j in wn.synsets(w2):
            ws = i.wup_similarity(j)
            if ws > topscore:
                topscore = ws
    return topscore

#x is word
def most_similar_word(x, vocab, sim_func):
    best = None
    topscore = -2
    for i in vocab:
        s = sim_func(i,x)
        if s > topscore:
            topscore = s
            best = i
    return (best, topscore)


#x is list of words
def synonym_replace(x, vocab, cutoff, sim_func):
    replaced = copy.deepcopy(x)
    for i in range(len(x)):
        if not x[i] in vocab:
            best = most_similar_word(x[i], vocab, sim_func)
            if best[1] > cutoff:
                replaced[i] = best[0]
    return replaced


print(model.similarity("soup","leaf"))
print(model.similarity("soup","vegetable"))
print(model.similarity("soup","ramen"))
print(model.similarity("soup","gazpacho"))
print(model.similarity("soup","metal"))
print(model.similarity("soup","chicken"))


print(synonym_replace("I want a ribeye".lower().split(), system_vocabulary, 0.4, model.similarity))
print(synonym_replace("I want ramen".lower().split(), system_vocabulary, 0.4, model.similarity))
print(synonym_replace("I want gazpacho".lower().split(), system_vocabulary, 0.4, model.similarity))
print(synonym_replace("I want a leaf".lower().split(), system_vocabulary, 0.4, model.similarity))
print(synonym_replace("I want a flower".lower().split(), system_vocabulary, 0.4, model.similarity))
print(synonym_replace("I want a vegetable".lower().split(), system_vocabulary, 0.4, model.similarity))

print(synonym_replace("I want a ribeye".lower().split(), system_vocabulary, 0.4, wn_similarity))
print(synonym_replace("I want ramen".lower().split(), system_vocabulary, 0.4, wn_similarity))
print(synonym_replace("I want gazpacho".lower().split(), system_vocabulary, 0.4, wn_similarity))
print(synonym_replace("I want a leaf".lower().split(), system_vocabulary, 0.4, wn_similarity))
print(synonym_replace("I want a flower".lower().split(), system_vocabulary, 0.4, wn_similarity))
print(synonym_replace("I want a vegetable".lower().split(), system_vocabulary, 0.4, wn_similarity))
