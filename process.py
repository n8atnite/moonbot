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

def transform_data(filedata):
    """
    Converts data from a SimpleNamespace into a dataframe of values
    Return: DataFrame
    """
    # initialize master dataframe
    df = pd.DataFrame(columns=["ROUTE_ID","ROUTE_NAME","ROUTE_MOVES","ROUTE_GRADE","IS_BENCHMARK","REPEATS","RATING","BOARD_TYPE","BOARD_ANGLE"])

    # for each problem in file, extract infso 
    for i,problem in enumerate(filedata):
        entry = []
        entry.append(problem.Id)
        entry.append(problem.NameForUrl)
        entry.append(",".join([a.Description for a in problem.Moves]))
        entry.append(core.GRADEBOOK.index(problem.Grade))
        entry.append(problem.IsBenchmark)
        entry.append(problem.Repeats)
        entry.append(problem.UserRating)
        entry.append(problem.Holdsetup.Description.lower())
        entry.append(int(problem.MoonBoardConfiguration.Description[:2]))
        df.loc[i,:] = entry
    return df

def extract_data(directory_path):
    """
    Extracts data from multiple json files in specified directory into a DataFrame
    Return: DataFrame
    """
    # initialize master dataframe
    df = pd.DataFrame(columns=["ROUTE_ID","ROUTE_NAME","ROUTE_MOVES","ROUTE_GRADE","IS_BENCHMARK","REPEATS","RATING","BOARD_TYPE","BOARD_ANGLE"])

    # extract problem data from each file in the data directory
    with tqdm(os.scandir(directory_path)) as it:
        for entry in it:

            if entry.name != "example_get_logbook.json":
                continue

            # specify the path to file
            path = os.path.join(directory_path,entry.name)

            # extract data from file into SimpleNamespace
            filedata = core.import_json(path).Data

            # Convert SimpleNamespace into DataFrame
            filedf = transform_data(filedata)

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

    print(df)

    
