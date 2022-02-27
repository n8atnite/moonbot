import os
import json
import itertools
from types import SimpleNamespace

##########
# GLOBAL #
##########

GRADEBOOK = ["5","5+","6A","6A+","6B","6B+","6C","6C+","7A","7A+","7B","7B+","7C","7C+","8A","8A+","8B","8B+","8C","8C+"]
LETTERS = ["A","B","C","D","E","F","G","H","I","J","K"]
NUMBERS = ["1","2","3","4","5","6","7","8","9","10","11","12","13","14","15","16","17","18"]
HOLDS = ["".join(t) for t in itertools.product(LETTERS,NUMBERS)]

#############
# FUNCTIONS #
#############

def get_page_count(total, size):
    return total//size + 1

def import_json(path):
    """
    Loads in data in json file specified from given path
    Return: tuple of data values
    """
    with open(path) as f:
        return json.load(f) #object_hook=lambda x: SimpleNamespace(**x)) 

def convert_to_simple_namespace(obj):
    """
    Takes data object and returns it as a SimpleNameSpace
    Return: SimpleNameSpace
    """
    return SimpleNamespace(**obj)

def write_to_file(name, obj):
    """
    Handler for writing an object into a file with given name
    Return: None
    """
    # identify extension of object
    ext = os.path.splitext(name)[1].lower()

    # handle case of txt
    if ext == ".txt":
        with open(name, "w") as file:
            try:
                thing = str(obj)
            except TypeError:
                print("Cannot convert object to string. Skipping file write...")
                return
            file.write(thing)
    # handle case of json
    elif ext == ".json":
        with open(name, "w") as file:
            try:
                json.dump(obj, file, indent=4)
            except:
                print("Cannot jsonify object. Skipping file write...")
                return

##########
# DRIVER #
##########

if __name__ == "__main__":
    # ADD TESTING HERE
    pass