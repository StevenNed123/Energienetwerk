import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
from matplotlib import transforms
from code.classes.case import Case, Node, H_station, M_station, L_station, Connection
from code.classes.tree import Tree
from copy import deepcopy
from code.visualise import visualise, visualise_single, visualise_df
import math
from code.algorithms.greedy import Greedy
from code.visualise import visualise, visualise_single, visualise_df, visualise_routes
import random

class Prim_KAL(Greedy):
    '''
    this is the MST routing algorithm using prims algorithm
    '''
    def __init__(self, case):
        # create lists for each of the object types
        self.case = deepcopy(case)
        self.nodes = self.case.nodes
        self.h_stations = []
        self.m_stations = []
        self.l_stations = []
        self.h_groups = []
        self.m_groups = []
        self.l_groups = []
        self.connections = []

        # create dataframe to be returned as solution
        self.stations = pd.DataFrame(columns=['latitude', 'longitude', 'voltage', 'type'])


    def run(self):

        # sort the nodes based on location
        random.shuffle(self.nodes)
        nodes = self.nodes
        print(f'calculating l_stations location')

        # group nodes together and calculate l locations
        l_groups = self.group_best_point(nodes, self.case.l_energy)
        l_stations = self.calculate_location(l_groups,nodes, type='l')
        self.l_stations = l_stations
        self.l_groups = l_groups

        print(f'calculating m_stations location')

        # group l_stations together and calculate m locations
        m_groups = self.group_best_point(l_stations, self.case.m_energy)
        m_stations = self.calculate_location(m_groups,nodes, type='m')
        self.m_stations = m_stations
        self.m_groups = m_groups
        #visualise('krommenie', [m_stations])

        print(f'calculating h_stations location')

        # group m_stations together and calculate h locations
        h_groups = self.group_best_point(m_stations, self.case.h_energy)
        h_stations = self.calculate_location(h_groups,nodes, type='h')
        self.h_stations = h_stations
        self.h_groups = h_groups
        #visualise('amsterdam', h_stations)

        self.calculate_tree(l_groups, l_stations)
        self.calculate_tree(m_groups, m_stations)
        self.calculate_tree(h_groups, h_stations)

        #print(f'creating visualisation')

        # visualise the stations and routes
        visualise(self.case.name,[nodes,l_stations, m_stations], self.connections)
        print(f'======================================')
        target, solution_data = self.target_function()
        print(f'target function: {target}')
        print(f'======================================')

        # add all stations to the stations dataframe
        self.add_stations(l_stations + m_stations + h_stations)
        solution_data.append(target)
        return solution_data, self.stations


    def calculate_tree(self, groups, stations):
        if len(stations) > 0:
            for i, group in enumerate(groups):
                group.append(stations[i])
                tree = Tree(len(group))
                matrix = self.distance_matrix(group)
                tree.graph = matrix
                result = tree.primMST()
                self.create_connections(group, result)


    def distance_matrix(self, group):
        matrix = [[0.0 for x in range(len(group))] for y in range(len(group))] 
        c_to_m = 111132.954
        for i1 in range(len(group)):
            for i2 in range(len(group)):
                distance = math.dist((group[i1].longitude,group[i1].latitude), (group[i2].longitude,group[i2].latitude)) * c_to_m
                matrix[i1][i2] = distance      
        return matrix



    def create_connections(self, group, result):
        for data in result:
            # create the new connection
            start = group[data[0]]
            end = group[data[1]]
            new_connection = Connection(start,end, min(start.type, end.type))

            # set distance, costs, energy_loss for the new connection
            distance = data[2]
            new_connection.set_distance(distance)
            # set costs
            costs = distance*self.case.get_con_costs()[new_connection.type]
            new_connection.set_costs(costs)
            # set energy_loss
            energy_loss = self.calc_energy_loss(new_connection)
            new_connection.set_energy_loss(energy_loss)

            # add connection to the total connections
            self.connections.append(new_connection)
            # add connection to first facility and second facility if facility type match
            if new_connection.start_node.type > 0 and new_connection.end_node.type > 0:
                start.connections.append(new_connection)
                end.connections.append(new_connection)
                # update the stability of the facility 
                start.set_stabillity(self.case.get_stability(len(start.connections) - 1))
                end.set_stabillity(self.case.get_stability(len(end.connections) - 1))
