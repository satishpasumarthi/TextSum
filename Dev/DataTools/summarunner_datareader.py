from __future__ import division,print_function

import os
import sys
import codecs
import collections
import numpy as np
import gensim
import pickle
from itertools import izip

#Don't disturb the below params, they are linked to many other scripts
#1.embediing dimensions
embedding_size = 100
#2.number of words per sentences
max_sen_length = 100 
#3.Max number of sentences per doc (as per training model)
max_sen_per_batch = 40

#Just to make sure we are not clipping for lower lengths
max_doc_length = 800

class Vocab:

    def __init__(self, token2index=None, index2token=None):
        self._token2index = token2index or {}
        self._index2token = index2token or []

    def feed(self, token):
        if token not in self._token2index:
            # allocate new index for this token
            index = len(self._token2index)
            #print(type(index))
            self._token2index[token] = long(index)
            self._index2token.append(token)

        return self._token2index[token]

    @property
    def size(self):
        return len(self._token2index)

    @property
    def token2index(self):
        return self._token2index

    def token(self, index):
        return self._index2token[index]

    def __getitem__(self, token):
        index = self.get(token)
        if index is None:
            raise KeyError(token)
        return index

    def get(self, token, default=None):
        return self._token2index.get(token, default)

    def save(self, filename):
        with open(filename, 'wb') as f:
            pickle.dump((self._token2index, self._index2token), f, pickle.HIGHEST_PROTOCOL)

    @classmethod
    def load(cls, filename):
        with open(filename, 'rb') as f:
            token2index, index2token = pickle.load(f)

        return cls(token2index, index2token)

def load_data(infile, max_doc_length=15, max_sent_length=50):

    word_vocab = Vocab()
    word_vocab.feed(' ')
    word_vocab.feed('{')
    word_vocab.feed('}')

    actual_max_doc_length = 0

    word_tokens = []
    word_doc = []
    word_tensors = {}
    with open(infile,'r') as INFILE:
        for line in INFILE:
            line = line.strip()
            line = line.replace('<unk>', ' | ')
            sent_list = line.split(" ")
            if len(sent_list) > max_sent_length - 2:  # space for 'start' and 'end' words
                sent_list = sent_list[:max_sent_length-2]

            word_array = [word_vocab.feed(c) for c in ['{'] + sent_list + ['}']]
            word_doc.append(word_array)

        if len(word_doc) > max_doc_length:
            word_doc = word_doc[:max_doc_length]
        actual_max_doc_length = max(actual_max_doc_length, len(word_doc))

        word_tokens.append(word_doc)
    assert actual_max_doc_length <= max_doc_length
    #print("Printing stats of the input paper :: ")
    #print("max_doc_len:", actual_max_doc_length)
    #print('actual longest document length is:', actual_max_doc_length)
    #print('size of word vocabulary:', word_vocab.size)
    #print('number of tokens in test:', len(word_tokens))

    # now we know the sizes, create tensors
    word_tensors = np.zeros([len(word_tokens), actual_max_doc_length, max_sent_length], dtype=np.int64)

    for i, word_doc in enumerate(word_tokens):
        for j, word_array in enumerate(word_doc):
            word_tensors[i][j][0:len(word_array)] = word_array

    return word_vocab, word_tensors, actual_max_doc_length

class DataReader:

    def __init__(self, word_tensor,batch_size):
        #print(word_tensor.shape)
        length = word_tensor.shape[0]
        doc_length = word_tensor.shape[1]
        sent_length = word_tensor.shape[2]
        #get the lower bound(multiple of 40)
        clipped_length = int(doc_length / batch_size) * batch_size
        #get the batch size
        batch_size = int(clipped_length/max_sen_per_batch)
        #word_tensor = word_tensor[:clipped_length]
        batch_size += 1
        #creating the dummy tensor to to make the doc_length multiples of 40
        dummy_tensor = np.zeros([length,batch_size*max_sen_per_batch -doc_length,sent_length])
        #append dummy tensor to word_tensor to make it reshapable
        word_tensor = np.append(word_tensor,dummy_tensor,axis=1)
        #print(word_tensor.shape,batch_size)
        x_batches = word_tensor.reshape([batch_size, -1,max_sen_per_batch, sent_length])

        self._x_batches = list(x_batches)
        self.length = len(self._x_batches)
        self.batch_size = batch_size
        self.max_sent_length = sent_length

    def iter(self):
        for batch in self._x_batches:
            yield batch

#################NOTE##################################
#input x --> takes in 40 sentences (which comprises of the top 20 and bottom 20 sentences acc. to ROUGE scores)
#ground truth y --> comprises of an array of 40 elements, consisting of binary values 0/1
#            0 --> not important to summary, 1 --> is an important statement
#predicted y_ --> comprises of an array of 40 elements that gives the probabilites for each statement.

def get_input_tensor(filename):

    vocab, word_tensors, max_length = load_data(filename,max_doc_length,max_sen_length)
    batch_size = 1
    test_reader = DataReader(word_tensors,batch_size).iter()
    return test_reader
