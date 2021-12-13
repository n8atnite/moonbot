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

def extract_move_string_data(moves):
    """
    Extracts moves from a string and looks up their attributes
    Return: 
    """
    # implement
    pass

def transform_data(filedata):
    """
    Transforms data from a json file to a dataframe of values
    Return: DataFrame
    """
    # initialize master dataframe
    df = pd.DataFrame(columns=["ROUTE_ID","ROUTE_NAME","ROUTE_MOVES","ROUTE_START","ROUTE_END","ROUTE_GRADE","IS_BENCHMARK","REPEATS","RATING","BOARD_TYPE","BOARD_ANGLE"])

    # for each problem in file, extract infso 
    for i,problem in enumerate(filedata.values()):
        problem = core.convert_to_simple_namespace(problem)
        entry = []
        entry.append(problem.Id)
        entry.append(problem.NameForUrl)
        entry.append(",".join([a["Description"] for a in problem.Moves]))
        entry.append(",".join([a["Description"] for a in problem.Moves if a.get("IsStart")]))
        entry.append(",".join([a["Description"] for a in problem.Moves if a.get("IsEnd")]))
        entry.append(",".join(extract_move_string_data(entry[2])))
        entry.append(GRADEBOOK.index(problem.Grade))
        entry.append(problem.IsBenchmark)
        entry.append(problem.Repeats)
        entry.append(problem.UserRating)
        entry.append(problem.Holdsetup["Description"].lower())
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

    print("Length of dataframe",len(df))
    print(df.head())
    print(df.columns)
    print("Length of unique dataframe",len(df.drop_duplicates()))

    
