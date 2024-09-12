import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
from matplotlib import transforms
from code.visualise import visualise, visualise_df


class Case:
    '''
    this class represents the case itself
    this class can be passed to a solver to find a solution
    class includes all information about the case and no information about solution
    '''
    def __init__(self, name):
        # read and scale the data
        self.name = name
        self.data = pd.read_csv(f'data/csv/{self.name}').copy() 
        self.data_scaled, self.rescaler = self.scale_data(self.data)
        self.nodes = self.create_nodes(self.data_scaled)
        # define the energy for each station
        self.l_energy = 400
        self.m_energy=  3_000
        self.h_energy = 110_000
        # define costs for each station
        self.l_costs = 35
        self.m_costs = 1_500
        self.h_costs = 25_000
        # define costs per meter
        self.l_meter_costs = 0.07
        self.m_meter_costs = 0.1
        self.h_meter_costs = 1

    

    def get_costs(self):
        return [self.l_costs, self.m_costs, self.h_costs]


    def visualise(self, name):
        """ create a plot of the case for visual aid """
        visualise_df(self.data, name)


    def create_nodes(self, df):
        """ take the nodes out of the dataframe and put them in a neet little list """
        nodes = []
        for index, row in df.iterrows(): 
            longitude = row['longitude']
            latitude = row['latitude'] 
            energy = (row['SJV_GEMIDDELD'] * row['AANSLUITINGEN_AANTAL']) / 10000
            nodes.append(Node(longitude, latitude, energy))
        
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
        df.longitude = (df.longitude - min_x) * scalerx
        df.latitude = (df.latitude - min_y) * scalery
        
        #calculate rescaler
        rescaler = [scalerx,scalery,min_x,min_y]


        return df, rescaler


class Node:
    '''
    this class represents each energy input Node
    the postal codes that need to recieve energy
    '''
    def __init__(self, longitude, latitude, energy):
        self.longitude = longitude
        self.latitude = latitude
        self.energy = energy
    

class H_station:
    '''
    this class represents each 'hoogspanningsstation'
    '''
    def __init__(self, longitude, latitude, energy, connections):
        self.longitude = longitude
        self.latitude = latitude
        self.energy = energy        
        self.connections = connections

class M_station:
    '''
    this class represents each 'middenspanningsstation'
    '''
    def __init__(self, longitude, latitude, energy, connections):
        self.longitude = longitude
        self.latitude = latitude
        self.energy = energy
        self.connections = connections

class L_station:
    '''
    this class represents each 'laagspanningsstation'
    '''
    def __init__(self, longitude, latitude, energy, connections):
        self.longitude = longitude
        self.latitude = latitude
        self.energy = energy
        self.connections = connections