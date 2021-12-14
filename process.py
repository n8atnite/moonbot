import os
import core
import pandas as pd
from tqdm import tqdm

##########
# GLOBAL #
##########

GRADEBOOK = ["5","5+","6A","6A+","6B","6B+","6C","6C+","7A","7A+","7B","7B+","7C","7C+","8A","8A+","8B","8B+","8C","8C+"]

#############
# FUNCTIONS #
#############

def extract_board_data(board_type):
    """
    Extracts relevant data for a specific hold
    Return: dictionary
    """
    # define path to corresponding board holdsetup
    holdpath = os.path.join("data","-".join(board_type.split())+"-hold-setup.json")

    # import json from file path
    holddata = core.import_json(holdpath)

    # Convert data into a single dictionary of holds
    holddict = {}
    for holdset in holddata:
        for hold in holdset["Holds"]:
            key = hold["Location"]["Description"]
            data = {
                "X":hold["Location"]["X"],
                "Y":hold["Location"]["Y"],
                "Rotation":hold["Location"]["Rotation"],
                "Direction":hold["Location"]["Direction"]
            }
            holddict[key] = data
    return holddict
    
def extract_move_string_data(moves,board_type):
    """
    Extracts moves from a string and looks up their attributes
    Return: 
    """
    # get holdsetup for given board type
    holdsetup = extract_board_data(board_type)

    # initialize X, Y, Rotation, and Direction strings
    X,Y,R,D = "","","",""

    # for each move, get corresponding data
    for move in moves.split(","):
        X = X + "," + holdsetup[move]["X"]
        Y = Y + "," + holdsetup[move]["Y"]
        R = R + "," + holdsetup[move]["R"]
        D = D + "," + holdsetup[move]["D"]

    


def transform_problem_data(filedata):
    """
    Transforms data from a json file to a dataframe of values
    Return: DataFrame
    """
    # initialize master dataframe
    df = pd.DataFrame(columns=["ROUTE_MOVES","ROUTE_START","ROUTE_END","MOVE_ANGLES","ROUTE_GRADE","IS_BENCHMARK","REPEATS","RATING","BOARD_ANGLE","BOARD_TYPE"])

    # for each problem in file, extract info
    for i,problem in enumerate(filedata.values()):
        problem = core.convert_to_simple_namespace(problem)
        entry = []
        entry.append(",".join([a["Description"] for a in problem.Moves]))
        entry.append(",".join([a["Description"] for a in problem.Moves if a.get("IsStart")]))
        entry.append(",".join([a["Description"] for a in problem.Moves if a.get("IsEnd")]))
        entry.append(",".join(extract_move_string_data(entry[2],problem.Holdsetup["Description"].lower())))
        entry.append(GRADEBOOK.index(problem.Grade))
        entry.append(problem.IsBenchmark)
        entry.append(problem.Repeats)
        entry.append(problem.UserRating)
        entry.append()
        entry.append(int(problem.MoonBoardConfiguration["Description"][:2]))
        df.loc[i,:] = entry
    return df

def extract_data(directory_path):
    """
    Extracts data from multiple json files in specified directory into a DataFrame
    Return: DataFrame
    """
    # initialize master dataframe
    df = pd.DataFrame(columns=["ROUTE_ID","ROUTE_NAME","ROUTE_MOVES","ROUTE_START","ROUTE_END","ROUTE_GRADE","IS_BENCHMARK","REPEATS","RATING","BOARD_TYPE","BOARD_ANGLE"])

    # extract problem data from each file in the data directory
    with tqdm(os.scandir(directory_path)) as it:
        for entry in it:
            if entry.name == "problems.json":
                # specify the path to file
                path = os.path.join(directory_path,entry.name)

                # extract data from file
                filedata = core.import_json(path)

                # Convert json to DataFrame
                filedf = transform_problem_data(filedata)

                df = df.append(filedf)
    return df

##########
# DRIVER #
##########

if __name__ == "__main__":

    # specify the path to data directory
    data_directory_path = os.path.join("data")        
    
    # extract all data into a dataframe
    df = extract_data(data_directory_path)

    print("Length of dataframe",len(df))
    print(df.head())
    print(df.columns)
    print("Length of unique dataframe",len(df.drop_duplicates()))

    
