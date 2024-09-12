import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
from matplotlib import transforms
from code.classes.case import Case, Source, H_station, M_station, L_station
from copy import deepcopy

class Greedy:
    '''
    This class is the greedy solver to create a first test solution
    '''
    def __init__(self, case):
        self.case = deepcopy(case)
        self.sources = self.case.sources
        self.H_station = []
        self.M_station = []
        self.L_station = []

        self.stations = pd.DataFrame()


    def target_function(self):
        costs = 0
        energy_loss = 0
        outage_penalty = 0
        return costs + energy_loss + outage_penalty
    

    def run(self):
        '''run the greedy algorithm, returns a dataframe with the stations'''
        # sort the sources based on location
        sources = self.sort_sources(self.sources)
        #input([x.latitude for x in sources])


        # group sources together and calculate l locations

        sources_groups = self.group_facility(sources, self.case.l_energy)
        #l_locations = self.calculate_location(sources_groups)

        # group l_stations together and calculate m locations
        #sources_groups = self.group_facility(sources, self.case.m_energy)
        #m_locations = self.calculate_location(sources_groups)

        # group m_stations together and calculate h locations
        #sources_groups = self.group_facility(sources, self.case.h_energy)
        #h_locations = self.calculate_location(sources_groups)

        # add all stations to de stations dataframe
        #self.stations.append(l_locations, m_locations, h_locations)

        return self.stations


    def group_facility(self, facilities, max_energy):
        '''group the sources based on energy usage'''
        # create coordinates
        coordinates = [[x.latitude, x.longitude] for x in facilities]

        groups = []
        group = []
        current_energy = 0
        node_index = 0
        previous_node_index = None
        for i in range(len(facilities)):
            if group == []:
                group.append(facilities[node_index])
                current_energy += facilities[node_index].energy

            
            new_node_index = self.closest_node(coordinates[node_index], coordinates[:node_index] + coordinates[node_index+1:])
            if new_node_index >= node_index:
                node_index = new_node_index + 1
            else:
                node_index = new_node_index
            facility = facilities[node_index]

            if max_energy <= current_energy + facility.energy:
                group.append(facility)
                current_energy += facility.energy
            else:
                groups.append(group)
                group = []    
                current_energy = 0

        return groups


    def closest_node(self, node, nodes):
        nodes = np.asarray(nodes)
        dist_2 = np.sum((nodes - node)**2, axis=1)
        return np.argmin(dist_2)


    def sort_sources(self, sources):
        '''sort the sources based on x and y coordinate'''
        # sort based on the lattitude
        self.sources.sort(key=lambda y : y.latitude)
        return sources


    def calculate_location(self, group):
        '''calculate the location for a facility for the group'''
        pass

    


