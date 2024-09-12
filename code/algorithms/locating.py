import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
from matplotlib import transforms
from code.classes.case import Case, Node, H_station, M_station, L_station, Connection
from copy import deepcopy
from code.visualise import visualise, visualise_single, visualise_df, visualise_routes
import math
import copy
from code.location_restriction import run_locating_restriction
from collections import defaultdict
from code.algorithms.greedy import Greedy
import random

class Locating(Greedy):
    '''
    This class for the locating algorithm
    takes a case class of the specific case 
    returns a list of the stations and a dataframe with station locations
    '''
    def __init__(self, case):

        # create lists for each of the object types
        self.case = deepcopy(case)
        self.nodes = self.case.nodes
        self.h_stations = []
        self.m_stations = []
        self.l_stations = []
        self.connections = []
        self.l_groups = []
        self.m_groups = []
        self.h_groups = []

        # create dataframe to be returned as solution
        self.stations = pd.DataFrame(columns=['latitude', 'longitude', 'voltage', 'type'])
    

    def run(self):

        # for laagspanningsstations
        random.shuffle(self.nodes)
        connections, stations  = self.initual_solution(self.nodes, self.case.get_energy_cap()[0], type=0)
        iterations = 0
        while iterations < 10:
            connections.sort(key=lambda x : x.distance, reverse=True)
            connections = self.alocate_costumers(connections, stations, self.case.get_energy_cap()[0])
            self.l_groups, self.l_stations, connections = self.update_location(connections, stations)
            iterations += 1
        

        # for middelspanningsstations
        connections, stations  = self.initual_solution(self.l_stations, self.case.get_energy_cap()[1], type=1)
        iterations = 0
        while iterations < 10:
            connections.sort(key=lambda x : x.distance)
            connections = self.alocate_costumers(connections, stations, self.case.get_energy_cap()[1])
            self.m_groups, self.m_stations, connections = self.update_location(connections, stations)
            iterations += 1
        
        # for hoogspanningsstations
        connections, stations  = self.initual_solution(self.m_stations, self.case.get_energy_cap()[2], type=2)
        iterations = 0
        while iterations < 10:
            connections.sort(key=lambda x : x.distance)
            connections = self.alocate_costumers(connections, stations, self.case.get_energy_cap()[2])
            self.h_groups, self.h_stations, connections = self.update_location(connections, stations)
            iterations += 1

        # calculate the routes
        l_routes = self.calculate_route(self.l_groups, self.l_stations, ring=False)
        m_routes = self.calculate_route(self.m_groups, self.m_stations, ring=True)
        h_routes = self.calculate_route(self.h_groups, self.h_stations, ring=True)

        # create connections for the route
        self.add_connections(l_routes)
        self.add_connections(m_routes)
        self.add_connections(h_routes)

        # visualise the stations and routes
        visualise_routes(self.case.name,[self.nodes,self.l_stations, self.m_stations], l_routes + m_routes + h_routes)

        print(f'======================================')
        print(f'target function: {self.target_function()}')
        print(f'======================================')
        self.add_stations(self.l_stations + self.m_stations + self.h_stations)


    def initual_solution(self, facilities, max_energy, type):
        '''group the nodes based on energy usage'''
        # define the lists
        coordinates = [[l.x, l.y] for l in facilities]
        facilities = facilities.copy()
        group = []
        groups = []
        connections = []
        index = 0
        energy_usage = 0 

        # loop for as long as there are facilities
        while facilities:

            # add first element to the group
            facility = facilities.pop(index)
            coordinate = coordinates.pop(index)
            if group == []:
                group.append(facility)
                energy_usage += facility.energy

            # calculate the closest facility
            center_point = list(np.asarray([[l.x, l.y] for l in group]).mean(axis=0))
            if facilities:
                index = self.closest_node(center_point, coordinates)
                facility = facilities[index]

                # add closest facility to the group
                if max_energy >= energy_usage + facility.energy:
                    group.append(facility)
                    energy_usage += facility.energy
                else:
                    groups.append(group)
                    group = []
                    energy_usage = 0

        groups.append(group)
        # create the connections
        stations = []
        if len(groups[0]) > 1:
            for group in groups:
                station = self.calculate_location(group, type)
                stations.append(station)
                for facility in group:
                    coordinates_to_meters = 111132.954
                    connection = Connection(station, facility, type) 
                    connection.calc_distance()
                    connections.append(connection)

        return connections, stations


    def calculate_location(self, group, type):
        '''
        calculate the locations for a group of facilities
        so it minimizes the distance between all locations
        '''
        # define station types
        typings = [L_station, M_station,H_station]

        # for every group add 
        energy = sum([x.energy for x in group])
        coordinates1 = np.asarray([[l.x, l.y] for l in group])
        coordinates2 = np.asarray([[l.longitude, l.latitude] for l in group])
        location1 = list(coordinates1.mean(axis=0))
        location2 = list(coordinates2.mean(axis=0))

        station = typings[type](location2[0],location2[1], location1[0],location1[1], energy)
        

        return station

    def closest_node(self, node, nodes):
        '''
        find the closest node from a set of nodes
        nodes are in the form of x, y  coordinates
        '''
        nodes = np.asarray(nodes)
        dist_2 = np.sum((nodes - node)**2, axis=1)
        return np.argmin(dist_2)


    def sort_nodes(self, nodes):
        '''sort the nodes based on y coordinate'''
        # sort based on the lattitude
        self.nodes.sort(key=lambda l : l.y)
        return nodes


    def alocate_costumers(self, connections, stations, max_energy):
        # reset the energy
        for station in stations:
            station.energy = 0
        # for each connection look if there is a better connection possible
        for connection in connections:
            end_node = connection.end_node
            # calculate the distance between end_node and all the stations
            distances = []
            for station in stations:
                distances.append([math.dist((end_node.longitude,end_node.latitude), (station.longitude,station.latitude)) * 111132.954, station])
            # the station with shortest distance becomes the new start_node if energy is not maxed
            distances.sort()

            for distance in distances:
                if end_node.energy + distance[1].energy <= max_energy:
                    connection.start_node = distance[1]
                    connection.start_node.energy += end_node.energy
                    break
        return connections


    def update_location(self, connections, stations):
        # group the facility for all the connections

        groups = defaultdict(list)
        stations = defaultdict(list)
        for obj in connections:
            groups[obj.start_node].append(obj.end_node)
            stations[obj.start_node].append(obj.start_node)

        stations = [x[0] for x in list(stations.values())]
        groups = list(groups.values())

        # update the new location for each station
        for index, station in enumerate(stations):
            coordinates1 = np.asarray([[l.x, l.y] for l in groups[index]])
            coordinates2 = np.asarray([[l.longitude, l.latitude] for l in groups[index]])
            location1 = list(coordinates1.mean(axis=0))
            location2 = list(coordinates2.mean(axis=0))
            station.longitude = location2[0]
            station.latitude = location2[1]
            station.x = location1[0]
            station.y = location1[1]
        
        # update the distance of the connections
        for connection in connections:
            connection.calc_distance()

        return groups, stations, connections
