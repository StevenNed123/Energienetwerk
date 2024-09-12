import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
from matplotlib import transforms
from code.classes.case import Case, Node, H_station, M_station, L_station
from copy import deepcopy
from code.visualise import visualise, visualise_single, visualise_df
import math

class Greedy:
    '''
    This class is the greedy solver to create a first test solution
    '''
    def __init__(self, case):
        self.case = deepcopy(case)
        self.nodes = self.case.nodes
        self.H_stations = []
        self.M_stations = []
        self.L_stations = []

        self.stations = pd.DataFrame(columns=['latitude', 'longitude', 'voltage', 'type'])


    def target_function(self):
        '''calculates the current cost of the solution'''
        energy_loss = 0
        outage_penalty = 0

        # calculate costs
        stations_count = [len(self.L_stations), len(self.M_stations), len(self.H_stations)]
        facility_costs = sum([a*b for a,b in zip(self.case.get_costs(),stations_count)])

        coordinates_to_meters = 111132.954
        distance_costs = 0
        for l_station in self.L_stations:
            for connection in l_station.connections:
                distance = math.dist(self.rescale(connection.longitude, connection.latitude),self.rescale(l_station.longitude, l_station.latitude))
                distance_costs += distance * self.case.l_meter_costs * coordinates_to_meters
        for m_station in self.M_stations:
            for connection in m_station.connections:
                distance = math.dist(self.rescale(connection.longitude, connection.latitude),self.rescale(m_station.longitude, m_station.latitude))
                distance_costs += distance * self.case.m_meter_costs * coordinates_to_meters
        for h_station in self.H_stations:
            for connection in h_station.connections:
                distance = math.dist(self.rescale(connection.longitude, connection.latitude),self.rescale(h_station.longitude, h_station.latitude))
                distance_costs += distance * self.case.h_meter_costs * coordinates_to_meters

        print(f'distance_costs: {distance_costs}')
        print(f'facility_costs: {facility_costs}')
        return distance_costs + facility_costs + energy_loss + outage_penalty


    def rescale(self, value_x, value_y):
        scalerx,scalery,minx,miny = self.case.rescaler
        return [value_x/scalerx+minx, value_y/scalery+miny]


    def run(self):
        '''
        run the greedy algorithm, returns a dataframe with the stations
        '''
        # sort the nodes based on location
        nodes = self.sort_nodes(self.nodes)

        # group nodes together and calculate l locations
        groups = self.group_facility3(nodes, self.case.l_energy)
        l_stations = self.calculate_location(groups, type='l')
        self.L_stations = l_stations

        # group l_stations together and calculate m locations
        groups = self.group_facility3(l_stations, self.case.m_energy)
        m_stations = self.calculate_location(groups, type='m')
        self.M_station = m_stations
        #visualise('krommenie', m_stations)

        # group m_stations together and calculate h locations
        groups = self.group_facility3(m_stations, self.case.h_energy)
        h_stations = self.calculate_location(groups, type='h')
        self.H_stations = h_stations
        #visualise('amsterdam', h_stations)

        # add all stations to the stations dataframe
        print(f'Laagspanningsstations: {len(l_stations)}')
        print(f'Middenpanningsstations: {len(m_stations)}')
        print(f'Hoogpanningsstations: {len(h_stations)}')
        print(f'Cost estimate: {self.target_function()}')
        self.add_stations(l_stations + m_stations + h_stations)
        visualise('krommenie',[nodes,l_stations])

        return self.stations


    def calculate_route(self, groups):
        pass


    def add_stations(self, stations):
        '''add the stations to the dataframe'''
        for station in stations:
            self.stations.loc[len(self.stations)] = [station.latitude, station.longitude, station.energy, station.__class__.__name__]
        return self.stations


    def group_last_point(self, facilities, max_energy):
        '''group the nodes based on energy usage'''
        # define the lists
        coordinates = [[x.latitude, x.longitude] for x in facilities]
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


    def group_first_point(self, facilities, max_energy):
        '''group the nodes based on energy usage'''
        # define the lists
        coordinates = [[x.latitude, x.longitude] for x in facilities]
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
        coordinates = [[x.latitude, x.longitude] for x in facilities]
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
            center_point = list(np.asarray([[x.latitude, x.longitude] for x in group]).mean(axis=0))
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
        dist_2 = np.sum((nodes - node)**2, axis=1)
        return np.argmin(dist_2)


    def sort_nodes(self, nodes):
        '''sort the nodes based on x coordinate'''
        # sort based on the lattitude
        self.nodes.sort(key=lambda y : y.latitude)
        return nodes


    def calculate_location(self, groups, type):
        '''
        calculate the locations for a group of facilities
        so it minimizes the distance between all locations
        '''
        stations = []
        # define station types
        typings = {'l': L_station, 'm' : M_station, 'h' : H_station}

        # for every group add 
        for group in groups:
            energy = sum([x.energy for x in group])
            coordinates = np.asarray([[x.latitude, x.longitude] for x in group])
            centroid = list(coordinates.mean(axis=0))
            stations.append(typings[type](centroid[1],centroid[0],energy,connections=group))

        return stations

    


