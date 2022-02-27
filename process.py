import os
import core
import pandas as pd

##########
# GLOBAL #
##########

#######
# API #
#######

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
                "R":hold["Location"]["Rotation"],
                "D":hold["Location"]["Direction"]
            }
            holddict[key] = data
    return holddict
    
def extract_hold_string_data(moves,board_type):
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
        X += str(holdsetup[move]["X"]) if X == "" else "," + str(holdsetup[move]["X"])
        Y += str(holdsetup[move]["Y"]) if Y == "" else "," + str(holdsetup[move]["Y"])
        R += str(holdsetup[move]["R"]) if R == "" else "," + str(holdsetup[move]["R"])
        D += str(holdsetup[move]["D"]) if D == "" else "," + str(holdsetup[move]["D"])
    return X,Y,R,D

def transform_hold_string_data(moves):
    """
    Transforms a string representation of moves into a numerical value
    Return: int
    """
    return moves

def transform_problem_data(filedata):
    """
    Transforms data from a json file to a dataframe of values
    Return: DataFrame
    """
    # initialize master dataframe
    df = pd.DataFrame(columns=["PROBLEM_ID","ROUTE_HOLDS","ROUTE_START","ROUTE_END","HOLD_X_COORDS","HOLD_Y_COORDS","HOLD_ANGLES",
                               "HOLD_DIRECTIONS","BOARD_ANGLE","REPEATS","ROUTE_GRADE","IS_BENCHMARK","RATING"])

    # for each problem in file, extract info
    for i,problem in enumerate(filedata.values()):
        # convert problem to simple namespace for ease of access
        problem = core.convert_to_simple_namespace(problem)

        # initialize row entry container
        entry = []
        entry.append(i)

        # add string representation of route moves
        entry.append(",".join(sorted([core.HOLDS.index(m["Description"]) for m in problem.Moves])))

        # add string representations of starting holds and ending holds
        entry.append(",".join(sorted([core.HOLDS.index(m["Description"]) for m in problem.Moves if m.get("IsStart")])))
        entry.append(",".join(sorted([core.HOLDS.index(m["Description"]) for m in problem.Moves if m.get("IsEnd")])))

        # extract locational,rotational, and directional data for each hold
        X,Y,R = extract_hold_string_data(",".join([a["Description"] for a in problem.Moves]),
                                           problem.Holdsetup["Description"].lower())
        entry.append(X); entry.append(Y); entry.append(R)

        # add grade, benchmark, repeats, and user rating
        entry.append(int(problem.MoonBoardConfiguration["Description"][:2]))
        entry.append(int(problem.Repeats))
        entry.append(core.GRADEBOOK.index(problem.Grade))
        entry.append(1 if problem.IsBenchmark == "True" else 0)
        entry.append(int(problem.UserRating))
        df.loc[i,:] = entry
    return df

def extract_data(path):
    """
    Extracts data from multiple json files in specified directory into a DataFrame
    Return: DataFrame
    """
    # initialize master dataframe
    df = pd.DataFrame()

    # extract data from file
    filedata = core.import_json(path)

    # Convert json to DataFrame
    filedf = transform_problem_data(filedata)

    df = df.append(filedf)

    # if empty dataframe, return no problems data exception
    if len(df) == 0:
        raise Exception("ExtractionError:\tProblem data not found or extracted")
    return df #.astype("float64")

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
    # specify the path to data file
    path = os.path.join("data","problems.json")        
    
    # extract all data into a dataframe
    df = extract_data(path)

    # split samples from conditionals
    samples,conditionals = split_samples_from_conditionals(df,3)

    print(samples.info())
    print(samples.head())
    print(conditionals.info())
    print(conditionals.head())