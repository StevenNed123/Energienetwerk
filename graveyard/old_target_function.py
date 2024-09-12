import math

def target_function(self):
    '''calculates the current cost of the solution'''
    energy_loss = 0
    outage_penalty = 0

    # calculate costs for facility creation
    stations_count = [len(self.L_stations), len(self.M_stations), len(self.H_stations)]
    facility_costs = sum([a*b for a,b in zip(self.case.get_costs(),stations_count)])

    # calculate costs for connection creation
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

    # print costs
    print(f'distance_costs: {distance_costs}')
    print(f'facility_costs: {facility_costs}')
    return distance_costs + facility_costs + energy_loss + outage_penalty