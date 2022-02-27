import os
import core
import process
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

##########
# GLOBAL #
##########

#############
# FUNCTIONS #
#############

def extract_hold_string_frequencies(problems):
    """
    Extracts frequencies of moves from data
    Return: Series
    """
    # initialize dictionary
    holddict = {}
    
    # for each problem add count to dictionary
    for problem in problems:
        problem = core.convert_to_simple_namespace(problem)
        for move in problem.Moves:
            if holddict.get(move["Description"]):
                holddict[move["Description"]] += 1
            else:
                holddict[move["Description"]] = 1
    return pd.Series(holddict).sort_values(ascending=False)

def extract_hold_string_gradesums(problems):
    """
    Extracts gradesums of moves from data
    Return: Series
    """
    # initialize dictionary
    holddict = {}
    
    # for each problem add count to dictionary
    for problem in problems:
        problem = core.convert_to_simple_namespace(problem)
        for move in problem.Moves:
            if holddict.get(move["Description"]):
                holddict[move["Description"]] += process.GRADEBOOK.index(problem.Grade)
            else:
                holddict[move["Description"]] = process.GRADEBOOK.index(problem.Grade)
    return pd.Series(holddict).sort_values(ascending=False)

##########
# DRIVER #
##########

if __name__ == "__main__":
    # specify the path to data file
    path = os.path.join("data","problems.json") 

    # extract data from file
    filedata = core.import_json(path)

    # get all hold frequencies
    freqs = extract_hold_string_frequencies(filedata.values()).sort_index()

    # get all hold grade sums
    gsums = extract_hold_string_gradesums(filedata.values()).sort_index()
    
    # get 'average hold grade' metric for relative hold difficulty
    hards = gsums/freqs
    
    # extract all data into a dataframe
    df = process.extract_data(path)

    mpdf = pd.DataFrame()

    for i in range(len(df)):

        # identify current problem
        problem = df.loc[i]
        
        # initialize unnormalized problem dataframe
        pdf = pd.DataFrame()

        # extract data into dataframe
        pdf["holds"] = [h for h in problem["ROUTE_HOLDS"].split(",")]
        pdf["frequency"] = [freqs[h] for h in problem["ROUTE_HOLDS"].split(",")]
        pdf["difficulty"] = [hards[h] for h in problem["ROUTE_HOLDS"].split(",")]
        pdf["xcoords"] = [x for x in problem["HOLD_X_COORDS"].split(",")]
        pdf["ycoords"] = [y for y in problem["HOLD_Y_COORDS"].split(",")]
        pdf["angles"] = [a for a in problem["HOLD_ANGLES"].split(",")]
        pdf["directions"] = [d for d in problem["HOLD_DIRECTIONS"].split(",")]
        pdf["grade"] = len(pdf)*[problem["ROUTE_GRADE"]]
        pdf["repeats"] = len(pdf)*[problem["REPEATS"]]
        pdf["rating"] = len(pdf)*[problem["RATING"]]
        pdf["boardangle"] = len(pdf)*[problem["BOARD_ANGLE"]]
        pdf["benchmark"] = len(pdf)*[problem["IS_BENCHMARK"]]
        pdf["problem_id"] = len(pdf)*[problem["PROBLEM_ID"]]

        mpdf = mpdf.append(pdf)

    print(mpdf)

    #ax = mpdf.plot.scatter("frequency","difficulty")
    #plt.show()