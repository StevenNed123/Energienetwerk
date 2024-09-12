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
from code.algorithms.prim import Prim
from code.visualise import visualise, visualise_single, visualise_df, visualise_routes
import random
import copy

class Gwa():
    '''
    this is the Grey wolf algorithm
    '''
    def __init__(self, case):
        # create lists for each of the object types
        self.case = deepcopy(case)
        self.nodes = self.case.nodes
        self.h_stations = []
        self.m_stations = []
        self.l_stations = []
        self.connections = []

        # create dataframe to be returned as solution
        self.stations = pd.DataFrame(columns=['latitude', 'longitude', 'voltage', 'type'])


    def run(self):

        # create a starting population
        population = []
        population_size = 30
        for _ in range(population_size):
            prim = Prim(self.case)
            solution = prim.run()
            target = prim.target_function()
            population.append([prim, target])
        

        b = 0.1
        iterations = 10
        for i in range(50):
        # sort the population
            population.sort(key=lambda x: x[1])
            alpha = population[0]
            beta = population[1]
            delta = population[2]
            omegas = population[2:]
            a = 2*(1-(i/iterations))
            for omega in omegas:
                r1 = random.random()
                r2 = random.random()
                a_vector = 2*a*r1-a
                if abs(a_vector) < 1:
                    alpha_chance = 1/2*math.atan(i)
                    beta_chance = (2/math.pi)*math.asin(1/3)*math.atan(i)
                    delta_chance = 1 - alpha_chance - beta_chance
                    omega = self.local_search(alpha)
                elif r2 > b:
                    omega = self.local_search(omega)
                    b += 0.1
                else:
                    b = 0.1
                    omega = self.global_search(omega)

        return self.stations


    def local_search(self, solution):
        solution = self.add_connections(solution)
        solution = self.move_station(solution)
        solution = self.change_group(solution)
        return solution

    def change_group(self, solution):
        new_solution = copy.deepcopy(solution)
        #l_groups = new_solution.l_groups
        #l_stations = new_solution.stations
        return solution

    def move_station(self, solution):
        pass

    def add_connections(self, solution):
        solution = solution[0]
        for x in range(3):
            new_solution = copy.deepcopy(solution)
            samples = random.sample(new_solution.l_stations, 2)
            # check if the stations are already connected
            station1_connections = samples[0].connections
            connected_stations = [x.end_node and x.start_node for x in station1_connections]
            if samples[1] not in connected_stations:
                #input((connected_stations, samples[1]))
                # create the new connection
                new_connection = Connection(samples[0],samples[1], min(samples[0].type, samples[1].type))
                # set distance, costs, energy_loss for the new connection
                coordinates_to_meters = 111132.954
                distance = math.dist((samples[0].longitude,samples[0].latitude), (samples[1].longitude,samples[1].latitude)) * coordinates_to_meters
                new_connection.set_distance(distance)
                # set costs
                costs = distance*self.case.get_con_costs()[new_connection.type]
                new_connection.set_costs(costs)
                # set energy_loss
                energy_loss = self.calc_energy_loss(new_connection)
                new_connection.set_energy_loss(energy_loss)
                samples[0].connections.append(new_connection)
                samples[1].connections.append(new_connection)
                # update the stability of the facility 
                samples[0].set_stabillity(self.case.stability_matrix[len(samples[0].connections) - 1])
                samples[1].set_stabillity(self.case.stability_matrix[len(samples[1].connections) - 1])
                new_solution.connections.append(new_connection)
                if new_solution.target_function() < solution.target_function():
                    visualise(self.case.name,[solution.nodes,solution.l_stations, solution.m_stations], solution.connections)
                    input(('connection added', new_solution.target_function(), solution.target_function()))    
                    solution = new_solution
                    visualise(self.case.name,[solution.nodes,solution.l_stations, solution.m_stations], solution.connections)
                    input(('connection added', new_solution.target_function(), solution.target_function()))   

        # remove connections
        # for x in range(3):
        #     new_solution = copy.deepcopy(solution)
        #     l_station_connections = [x for x in new_solution.connections if x.start_node.type == 1 and x.end_node.type == 1]
        #     sample = random.sample(l_station_connections, 1)[0]

        #     if (len(sample.end_node.connections) > 1) and (len(sample.start_node.connections) > 1):
        #         new_solution.connections.remove(sample)
        #         sample.start_node.connections.remove(sample)
        #         sample.end_node.connections.remove(sample)
        #         # update the stability of the facility 
        #         sample.end_node.set_stabillity(self.case.stability_matrix[len(sample.end_node.connections) - 1])
        #         sample.start_node.set_stabillity(self.case.stability_matrix[len(sample.start_node.connections) - 1])

        #     if new_solution.target_function() < solution.target_function():
        #         solution = new_solution
        #         input('connection removed')    
        #         visualise(self.case.name,[solution.nodes,solution.l_stations, solution.m_stations], solution.connections)

        return solution, solution.target_function()



    def global_search(self, omega):
        prim = Prim(self.case)
        solution = prim.run()
        target = prim.target_function()
        return [solution, target]


    def calc_energy_loss(self, connection):
        soortelijke_weerstand = self.case.cable_material
        lengte = connection.distance
        dwarsdoorsnede = self.case.get_cabel_sizes()[connection.type]
        weerstand = soortelijke_weerstand * (lengte / dwarsdoorsnede)
        energy_flow = self.case.get_amperage()[connection.type]
        energy_loss = energy_flow * weerstand
        return energy_loss


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
