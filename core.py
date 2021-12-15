import os
import json
from types import SimpleNamespace

##########
# GLOBAL #
##########

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