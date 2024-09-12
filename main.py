from code.helper import load, add_coordinates
from code.visualise import visualise, visualise_df
import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
from code.classes.case import Case
from code.algorithms.greedy import Greedy
from code.algorithms.prim import Prim
from code.algorithms.gwa import Gwa
from code.algorithms.locating import Locating
from code.algorithms.routing import Routing
from code.algorithms.tool_algorithms.greedy_ala import Greedy_ALA
from code.algorithms.tool_algorithms.greedy_kal import Greedy_KAL
from code.algorithms.tool_algorithms.greedy_greedy import Greedy_Greedy
from code.algorithms.tool_algorithms.prim_ala import Prim_ALA
from code.algorithms.tool_algorithms.prim_kal import Prim_KAL
from code.algorithms.tool_algorithms.prim_greedy import Prim_Greedy
import argparse


def main(city, algorithm1, algorithm2):

    #create the case
    name = city
    case = Case(name)
    #solve the case using the algorithm
    algorithms = {'greedy_ala': Greedy_ALA, 'prim_ala': Prim_ALA , 'greedy_kal': Greedy_KAL, \
                  'greedy_greedy': Greedy_Greedy, 'prim_kal': Prim_KAL, 'prim_greedy': Prim_Greedy}
    algorithm = algorithms[algorithm1+'_'+algorithm2]
    solution_data, solution = algorithm(case).run()
    #save the solution in solutions
    solution.to_csv(f'data/solutions/{name}', index=False)

    return solution_data

def parse_my_args(args):
    # load the board via the load function
    if args.load is True:
        # run this code to load the data
        load()

    if args.create_csv is True:
        # run this code to add the coordinates to a dataframe and than save the dataframe
        dataframe = add_coordinates(pd.read_csv(f'data/csv/{args.city}'))
        dataframe.to_csv(f'data/csv/{args.city}', index=False)
    
    elif args.visualise is True:
        # run this code to plot a visualisation of the dataframe
        name = args.city
        visualise_df(pd.read_csv(f'data/csv/{name}'), name)

    else:
        # run the main function to get a solution
        main(args.city, args.algorithm1, args.algorithm2)


if __name__ == "__main__":

    # setup the command line input
    parser = argparse.ArgumentParser(description="Create Energienetwork")

    parser.add_argument("-v", "--visualise", action="store_true", help="Visualise the selected city")
    parser.add_argument("-l", "--load", action="store_true", help="Perform the Initial Loading")
    parser.add_argument("-csv", "--create_csv", action="store_true", help="Create a CSV of the selected city")

    parser.add_argument(
        "-c", "--city", default="krommenie", metavar="city",
        choices=('amsterdam', 'eindhoven', 'krommenie', 'leiden'),
        help="Select a city to solve")
    parser.add_argument(
        "-a1", "--algorithm1", default="greedy", metavar="a1",
        choices=('greedy', 'prim'),
        help="Select a routing algorithm")
    parser.add_argument(
        "-a2", "--algorithm2", default="greedy", metavar="a2",
        choices=('greedy', 'kal', 'ala'),
        help="Select a locating algorithm")

    args = parser.parse_args()
    parse_my_args(args)