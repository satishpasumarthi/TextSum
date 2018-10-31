import os
import sys
import pickle
sys.path.insert(0, os.environ['SCRATCH']+"/MATH689/TextSum")
from Dev.DataTools import useful_functions

BASE_DIR = os.environ['SCRATCH']+"/MATH689/TextSum/Dev/"

KEYPHRASES_LOC = BASE_DIR+"DataTools/pickled_dicts/keyphrases.pkl"

def dump_keyphrases_pkl(out_file):
    files = os.listdir(BASE_DIR+"Data/Papers/Full/Papers_With_Section_Titles/")
    keyphrases = {}
    for file in files:
        paper = useful_functions.read_in_paper(file, sentences_as_lists=False)
        keyphrases[file] = paper["KEYPHRASES"] 
    write_pkl(keyphrases,out_file)

def write_pkl(list_to_pickle, write_location):
    """
    Pickles a list - writes it out in Python's pickle format at the specified location.
    :param list_to_pickle: the list to persist.
    :param write_location: the location to write the list to.
    """
    with open(write_location, "wb") as f:
        pickle.dump(list_to_pickle, f)

dump_keyphrases_pkl(KEYPHRASES_LOC)
