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
import random

class Greedy_KAL:
    '''
    This class is the greedy solver to create a first test solution
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
        '''
        run the greedy algorithm, returns a dataframe with the stations
        '''
        # sort the nodes based on location
        random.shuffle(self.nodes)
        nodes = self.nodes

        print(f'calculating l_stations location')

        # group nodes together and calculate l locations
        l_groups = self.group_best_point(nodes, self.case.l_energy)
        l_stations = self.calculate_location(l_groups,nodes, type='l')
        self.l_stations = l_stations

        print(f'calculating m_stations location')

        # group l_stations together and calculate m locations
        m_groups = self.group_best_point(l_stations, self.case.m_energy)
        m_stations = self.calculate_location(m_groups,nodes, type='m')
        self.m_stations = m_stations
        #visualise('krommenie', [m_stations])

        print(f'calculating h_stations location')

        # group m_stations together and calculate h locations
        h_groups = self.group_best_point(m_stations, self.case.h_energy)
        h_stations = self.calculate_location(h_groups,nodes, type='h')
        self.h_stations = h_stations
        #visualise('amsterdam', h_stations)

        print(f'calculating routes')

        # calculate the routes
        l_routes = self.calculate_route(l_groups, l_stations, ring=False)
        m_routes = self.calculate_route(m_groups, m_stations, ring=True)
        h_routes = self.calculate_route(h_groups, h_stations, ring=True)

        # create connections for the route
        self.add_connections(l_routes)
        self.add_connections(m_routes)
        self.add_connections(h_routes)

        print(f'creating visualisation')

        # visualise the stations and routes
        visualise_routes(self.case.name,[nodes,l_stations, m_stations], l_routes + m_routes + h_routes)

        # add all stations to the stations dataframe
        print(f'======================================')
        target, solution_data = self.target_function()
        print(f'target function: {target}')
        print(f'======================================')
        self.add_stations(l_stations + m_stations + h_stations)
        solution_data.append(target)
        return solution_data, self.stations


    def target_function(self):
        '''calculates the current cost of the solution'''
        # calculate costs for facility creation
        stations_count = [len(self.l_stations), len(self.m_stations), len(self.h_stations)]
        facility_costs = sum([a*b for a,b in zip(self.case.get_costs(),stations_count)])

        # calculate costs for connection creation
        distance_costs = sum(connection.costs for connection in self.connections)
        # calculate the energy loss
        energy_loss = sum(connection.energy_loss for connection in self.connections)

        # calculate the stability
        stability1 = sum(x.stability for x in self.l_stations)/(len(self.l_stations))
        #stability2 = sum(1 - x.stability for x in self.m_stations)/(len(self.m_stations))
        stability = stability1

        # define the factors
        if self.case.name == 'krommenie':
            a = 3.10
            b = 10125
        if self.case.name == 'leiden':
            a = 6.11
            b = 129482
        if self.case.name == 'Amsterdam':
            a = 13.50
            b = 1830000        
        else:
            a = 3.10
            b = 1446.46

        # print costs
        print(f'distance_costs: {distance_costs}')
        print(f'facility_costs: {facility_costs}')
        print(f'energy_loss: {energy_loss}')
        print(f'network_stability: {stability}')
        print(f'Laagspanningsstations: {len(self.l_stations)}')
        print(f'Middenpanningsstations: {len(self.m_stations)}')
        print(f'Hoogpanningsstations: {len(self.h_stations)}')
        solution_data = [distance_costs, facility_costs, energy_loss, stability, len(self.l_stations), len(self.m_stations), len(self.h_stations)]
        return distance_costs + facility_costs + a*energy_loss + b*(1-stability), solution_data
    

    def add_connections(self,routes):
        for route in routes:
            for i in range(len(route)-1):
                # create the new connection
                new_connection = Connection(route[i],route[i+1], min(route[i].type, route[i+1].type))

                # set distance, costs, energy_loss for the new connection
                coordinates_to_meters = 111132.954
                distance = math.dist((route[i].longitude,route[i].latitude), (route[i+1].longitude,route[i+1].latitude)) * coordinates_to_meters
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
                if new_connection.start_node.type == new_connection.end_node.type:
                    route[i].connections.append(new_connection)
                    route[i+1].connections.append(new_connection)
                    # update the stability of the facility 
                    route[i].set_stabillity(self.case.stability_matrix[len(route[i].connections) - 1])
                    route[i+1].set_stabillity(self.case.stability_matrix[len(route[i+1].connections) - 1])


    def calc_energy_loss(self, connection):
        soortelijke_weerstand = self.case.cable_material
        lengte = connection.distance
        dwarsdoorsnede = self.case.get_cabel_sizes()[connection.type]
        weerstand = soortelijke_weerstand * (lengte / dwarsdoorsnede)
        energy_flow = self.case.get_amperage()[connection.type]
        energy_loss = energy_flow * weerstand
        return energy_loss
                

    def calculate_route(self, groups, stations, ring=False):
        """
        return a list that contains a list for each route
        each route starts at a station
        """
        routes = []
        groups = groups.copy()
        
        # for each station create the routes
        for i in range(len(stations)):
            # create variables necessary to create the routes
            group = groups[i]
            station = stations[i]
            nodes = [[l.x, l.y] for l in group]
            hub_node = [station.x,station.y]
            previous_node = hub_node
            route = [station]
            while nodes:

                # find closest node to the previous node
                index = self.closest_node(previous_node, nodes)
                node = nodes.pop(index)
                facility = group.pop(index)

                # if distance < distance to hub node: add the node to the route
                # otherwise start a new route 
                if math.dist(previous_node, node) <= math.dist(hub_node, node) or ring==True:
                    # add node to the route
                    route.append(facility)
                    previous_node = node
                else:
                    # add finished route to the routes
                    routes.append(route)
                    # add station to the route first
                    route = [station]
                    route.append(facility)
                    previous_node = node

            # creat the ring form if ring form is set to true
            if ring==True:
                route.append(route[1])
            routes.append(route)

        return routes


    def add_stations(self, stations):
        '''add the stations to the dataframe'''
        for station in stations:
            self.stations.loc[len(self.stations)] = [station.latitude, station.longitude, station.energy, station.__class__.__name__]
        return self.stations


    def group_last_point(self, facilities, max_energy):
        '''group the nodes based on energy usage'''
        # define the lists
        coordinates = [[l.x, l.y] for l in facilities]
        facilities = facilities.copy()
        group = []
        groups = []
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
            if facilities:
                index = self.closest_node(coordinate, coordinates)
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
        return groups


    def group_best_point(self, facilities, max_energy):
        '''group the nodes based on energy usage'''
        # define the lists
        coordinates = [[l.x, l.y] for l in facilities]
        group_coordinates = []
        facilities = facilities.copy()
        group = []
        groups = []
        index = 0
        energy_usage = 0 

        # loop for as long as there are facilities
        while facilities:

            # add first element to the group
            facility = facilities.pop(index)
            coordinate = coordinates.pop(index)
            if group == []:
                group.append(facility)
                group_coordinates.append([facility.x, facility.y])
                energy_usage += facility.energy

            # calculate the closest facility
            if facilities:
                index = self.closest_node_2(group_coordinates, coordinates)
                facility = facilities[index]

                # add closest facility to the group
                if max_energy >= energy_usage + facility.energy:
                    group.append(facility)
                    group_coordinates.append([facility.x, facility.y])
                    energy_usage += facility.energy
                else:
                    groups.append(group)
                    group = []
                    group_coordinates = []
                    energy_usage = 0

        groups.append(group)
        return groups


    def closest_node_2(self,nodes1,nodes2):
        shortest_distance = float('inf')
        closest_pair = None

        for point1 in nodes1:
            x1, y1 = point1
            for i, point2 in enumerate(nodes2):
                x2, y2 = point2
                distance = math.sqrt((x2 - x1) ** 2 + (y2 - y1) ** 2)  # Euclidean distance
                if distance < shortest_distance:
                    shortest_distance = distance
                    closest_pair = (point1, point2)
                    index = i

        return index


    def group_first_point(self, facilities, max_energy):
        '''group the nodes based on energy usage'''
        # define the lists
        coordinates = [[l.x, l.y] for l in facilities]
        facilities = facilities.copy()
        group = []
        groups = []
        index = 0
        energy_usage = 0 

        # loop for as long as there are facilities
        while facilities:

            # add first element to the group
            facility = facilities.pop(index)
            coordinate = coordinates.pop(index)
            if group == []:
                group.append(facility)
                first_node = coordinate
                energy_usage += facility.energy

            # calculate the closest facility
            if facilities:
                index = self.closest_node(first_node, coordinates)
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
        return groups


    def group_centre_point(self, facilities, max_energy):
        '''group the nodes based on energy usage'''
        # define the lists
        coordinates = [[l.x, l.y] for l in facilities]
        facilities = facilities.copy()
        group = []
        groups = []
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
        return groups


    def closest_node(self, node, nodes):
        '''
        find the closest node from a set of nodes
        nodes are in the form of x, y  coordinates
        '''
        nodes = np.asarray(nodes)
        node = np.asarray(node)
        dist_2 = np.sum((nodes - node)**2, axis=1)
        return np.argmin(dist_2)


    def sort_nodes(self, nodes):
        '''sort the nodes based on y coordinate'''
        # sort based on the lattitude
        self.nodes.sort(key=lambda l : l.y)
        return nodes


    def calculate_location(self, groups, postal_codes, type):
        '''
        calculate the locations for a group of facilities
        so it minimizes the distance between all locations
        '''
        stations = []
        # define station types
        typings = {'l': L_station, 'm' : M_station, 'h' : H_station}

        # for every group add a stations
        # first check if there is only one station
        if not (len(groups) <= 1 and len(groups[0]) <= 1):
            for group in groups:
                energy = sum([x.energy for x in group])
                coordinates1 = np.asarray([[l.x, l.y] for l in group])
                coordinates2 = np.asarray([[l.longitude, l.latitude] for l in group])
                location1 = list(coordinates1.mean(axis=0))
                location2 = list(coordinates2.mean(axis=0))

                #check for the location restriction
                # if (type=='m' or type=='h'):
                #    location2 = self.locating_restriction(postal_codes, location2)
                #     #scale the longitude and latitude to x and y
                #    location1 = self.case.scale(location2)
                stations.append(typings[type](location2[0],location2[1], location1[0],location1[1], energy))

        return stations


    def locating_restriction(self, postal_codes, location):
        radius = 100/111132.954
        new_location = run_locating_restriction(postal_codes, radius, location)
        return new_location

                



