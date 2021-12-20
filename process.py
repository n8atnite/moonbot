import os
import core
import pandas as pd

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
    Return: tuple of strings
    """
    # get holdsetup for given board type
    holdsetup = extract_board_data(board_type)

    # initialize X, Y, Rotation, and Direction strings
    X,Y,R,D = "","","",""

    # for each move, get corresponding data
    for move in moves.split(","):
        X += str(holdsetup[move]["X"]) if X == "" else ","+str(holdsetup[move]["X"])
        Y += str(holdsetup[move]["Y"]) if Y == "" else ","+str(holdsetup[move]["Y"])
        R += str(holdsetup[move]["Rotation"]) if R == "" else ","+str(holdsetup[move]["Rotation"])
        D += str(holdsetup[move]["Direction"]) if D == "" else ","+str(holdsetup[move]["Direction"])
    return X,Y,R,D

def transform_problem_data(filedata):
    """
    Transforms data from a json file to a dataframe of values
    Return: DataFrame
    """
    # initialize master dataframe
    df = pd.DataFrame(columns=["ROUTE_MOVES","ROUTE_START","ROUTE_END","MOVE_X_COORDS","MOVE_Y_COORDS","MOVE_ANGLES","MOVE_DIRECTIONS","BOARD_ANGLE","REPEATS","ROUTE_GRADE","IS_BENCHMARK","RATING"])

    # for each problem in file, extract info
    for i,problem in enumerate(filedata.values()):
        # convert problem to simple namespace for ease of access
        problem = core.convert_to_simple_namespace(problem)

        # initialize row entry container
        entry = []

        # add string representation of route moves
        entry.append(",".join([a["Description"] for a in problem.Moves]))

        # add string representations of starting moves and ending moves
        entry.append(",".join([a["Description"] for a in problem.Moves if a.get("IsStart")]))
        entry.append(",".join([a["Description"] for a in problem.Moves if a.get("IsEnd")]))
        
        # extract locational,rotational, and directional data for each move
        X,Y,R,D = extract_move_string_data(entry[0],problem.Holdsetup["Description"].lower())
        entry.append(X)
        entry.append(Y)
        entry.append(R)
        entry.append(D)

        # add grade, benchmark, repeats, and user rating
        entry.append(int(problem.MoonBoardConfiguration["Description"][:2]))
        entry.append(int(problem.Repeats))
        entry.append(GRADEBOOK.index(problem.Grade))
        entry.append(1 if problem.IsBenchmark == "True" else 0)
        entry.append(int(problem.UserRating))
        df.loc[i,:] = entry
    return df

def extract_data(directory_path):
    """
    Extracts data from multiple json files in specified directory into a DataFrame
    Return: DataFrame
    """
    # initialize master dataframe
    df = pd.DataFrame(columns=["ROUTE_MOVES","ROUTE_START","ROUTE_END","MOVE_X_COORDS","MOVE_Y_COORDS","MOVE_ANGLES","MOVE_DIRECTIONS","BOARD_ANGLE","REPEATS","ROUTE_GRADE","IS_BENCHMARK","RATING"])

    # extract problem data from each file in the data directory
    with os.scandir(directory_path) as it:
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

def split_samples_from_conditionals(df,conditional_column_len):
    """
    Separates data from one frame into two on specified columns
    Return: tuple of dataframes
    """
    samples = df.drop(columns=df.columns[-conditional_column_len:])
    conditionals = df.drop(columns=df.columns[:len(df.columns)-conditional_column_len])
    return samples,conditionals

##########
# DRIVER #
##########

if __name__ == "__main__":
    # specify the path to data directory
    data_directory_path = os.path.join("data")        
    
    # extract all data into a dataframe
    df = extract_data(data_directory_path)

    # split samples from conditionals
    samples,conditionals = split_samples_from_conditionals(df,3)

    print(samples.head())
    print(samples.columns)
    print(conditionals.head())
    print(conditionals.columns)
    