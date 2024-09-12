import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
from matplotlib import transforms
from code.visualise import visualise, visualise_df
import math


class Case:
    '''
    this class represents the case itself
    this class can be passed to a solver to find a solution
    class includes all information about the case itself
    '''
    def __init__(self, name):
        # read and scale the data
        self.name = name
        self.data = pd.read_csv(f'data/csv/{self.name}').copy() 
        self.data = self.scale_data(self.data)
        self.nodes = self.create_nodes(self.data)
        # define the energy capacity for each station
        self.l_energy = 400
        self.m_energy=  3_000
        self.h_energy = 110_000
        # define costs for each station
        self.l_costs = 35
        self.m_costs = 25_000
        self.h_costs = 100_000
        # define costs per meter
        self.l_meter_costs = 0.07
        self.m_meter_costs = 0.1
        self.h_meter_costs = 1
        # define the size of the cabels
        self.l_cabel_size = 0.00001
        self.m_cabel_size = 0.00005
        self.h_cabel_size = 0.00025
        # define the material of the cabels
        self.cable_material = 0.0000000265
        # define the stability matrix
        self.stability_matrix = [0.5,0.95,0.98,1,1,1,1,1,1,1]
        # define the amperage
        self.l_amperage = 25
        self.m_amperage = 100
        self.h_amperage = 500
        
    def get_amperage(self):
        return [self.l_amperage, self.m_amperage, self.h_amperage]
    
    def get_stability(self, con_amount):
        if con_amount >= 4:
            return 1
        else:
            return self.stability_matrix[con_amount]

    def get_costs(self):
        """ simple funciton to return the costs in a list of integers """
        return [self.l_costs, self.m_costs, self.h_costs]

    def get_energy_cap(self):
        """ simple funciton to return the costs in a list of integers """
        return [self.l_energy, self.m_energy, self.h_energy]

    def get_con_costs(self):
        """ simple funciton to return the costs in a list of floats"""
        return [self.l_meter_costs, self.m_meter_costs, self.h_meter_costs]

    def get_cabel_sizes(self):
        """ simple funciton to return the costs in a list of integers """
        return [self.l_cabel_size, self.m_cabel_size, self.h_cabel_size]

    def visualise(self, name):
        """ create a plot of the case for visual aid """
        visualise_df(self.data, name)

    def create_nodes(self, df):
        """ take the nodes out of the dataframe and put them in a neet little list """
        nodes = []
        # for each entry in the dataframe create a new node
        for index, row in df.iterrows(): 
            longitude = row['longitude']
            latitude = row['latitude'] 
            energy = (row['SJV_GEMIDDELD'] * row['AANSLUITINGEN_AANTAL']) / 10000
            x = row['x']
            y = row['y']
            nodes.append(Node(longitude, latitude,x,y,energy))
        
        return nodes
    
    def scale_data(self, df):
        """scales the longitude and the latitude from 1 to 100"""
        # save the maximum values to scale
        max_x = max(df.longitude)
        max_y = max(df.latitude)
        min_x = min(df.longitude)
        min_y = min(df.latitude)

        # scaling the data from 1 to 100
        scalerx = 100/(max_x - min_x)
        scalery = 100/(max_y - min_y)
        df.insert(4, 'x', (df.longitude - min_x) * scalerx, True)
        df.insert(4, 'y', (df.latitude - min_y) * scalery, True)
        return df


    def scale(self, point):
        """scales the data of a single point"""
        # save the maximum values to scale
        max_x = max(self.data.longitude)
        max_y = max(self.data.latitude)
        min_x = min(self.data.longitude)
        min_y = min(self.data.latitude)

        # scaling the data from 1 to 100
        scalerx = 100/(max_x - min_x)
        scalery = 100/(max_y - min_y)
        scaled_point = ((point[0] - min_x) * scalerx, (point[1] - min_y) * scalery)
        return scaled_point


class Node:
    '''
    this class represents each energy input Node
    in other words the postal codes that need to recieve the energy
    '''
    def __init__(self, longitude, latitude,x, y, energy):
        self.longitude = longitude
        self.latitude = latitude
        self.x = x
        self.y = y
        self.energy = energy
        self.connections = []
        self.type = 0
        self.distance_to_stations = 0
    def set_stabillity(self, stability):
        self.stability = stability


class H_station:
    '''
    this class represents each 'hoogspanningsstation'
    '''
    def __init__(self, longitude, latitude,x, y, energy):
        self.longitude = longitude
        self.latitude = latitude
        self.x = x
        self.y = y
        self.energy = energy        
        self.connections = []
        self.type = 3
        self.distance_to_stations = 0
    def set_stabillity(self, stability):
        self.stability = stability


class M_station:
    '''
    this class represents each 'middenspanningsstation'
    '''
    def __init__(self, longitude, latitude,x, y, energy):
        self.longitude = longitude
        self.latitude = latitude
        self.x = x
        self.y = y
        self.energy = energy
        self.connections = []
        self.type = 2
        self.distance_to_stations = 0
    def set_stabillity(self, stability):
        self.stability = stability


class L_station:
    '''
    this class represents each 'laagspanningsstation'
    '''
    def __init__(self, longitude, latitude,x, y, energy):
        self.longitude = longitude
        self.latitude = latitude
        self.x = x
        self.y = y
        self.energy = energy
        self.connections = []
        self.type = 1
        self.distance_to_stations = 0
    def set_stabillity(self, stability):
        stability_table = []
        self.stability = stability


class Connection:
    def __init__(self, starting_node, ending_node, type):
        self.start_node = starting_node 
        self.end_node = ending_node
        self.type = type
    def set_distance(self, distance):
        self.distance = distance
    def set_costs(self, costs):
        self.costs = costs
    def set_energy_loss(self, energy_loss):
        self.energy_loss = energy_loss
    def calc_distance(self):
        self.distance = math.dist((self.start_node.longitude,self.start_node.latitude), (self.end_node.longitude,self.end_node.latitude)) * 111132.954


