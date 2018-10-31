import os
import sys
import pickle
sys.path.insert(0, os.environ['SCRATCH']+"/MATH689/TextSum")
from Dev.DataTools import useful_functions

BASE_DIR = os.environ['SCRATCH']+"/MATH689/TextSum/Dev/"


PAPER_BOW_OF_WORDS_LOC = BASE_DIR+"DataTools/pickled_dicts/paper_bag_of_words.pkl"

def dump_bow_pkl(out_file):
    files = os.listdir(BASE_DIR+"Data/Papers/Full/Papers_With_Section_Titles/")
    bow = {}
    for file in files:
        paper = useful_functions.read_in_paper(file, sentences_as_lists=False)
        paper_string = " ".join(v for k,v in paper.iteritems())
        bow[file] = useful_functions.calculate_bag_of_words(paper_string)
    write_pkl(bow,out_file) 

def write_pkl(list_to_pickle, write_location):
    """
    Pickles a list - writes it out in Python's pickle format at the specified location.
    :param list_to_pickle: the list to persist.
    :param write_location: the location to write the list to.
    """
    with open(write_location, "wb") as f:
        pickle.dump(list_to_pickle, f)

dump_bow_pkl(PAPER_BOW_OF_WORDS_LOC)
