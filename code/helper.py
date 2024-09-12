import pandas as pd
import pgeocode
from functools import partial

def load():
    """
    this function does the initial loading of the datasets
    takes a little long so only need to run it once to create the dataframes
    """
    # read liander dataset
    liander = pd.read_excel('data/Liander & Enexis Data.xlsx', sheet_name=0)
    liander = liander.applymap(lambda x : str(x).strip())
    liander = liander[['NETGEBIED','STRAATNAAM','POSTCODE_VAN','POSTCODE_TOT','WOONPLAATS','PRODUCTSOORT','AANSLUITINGEN_AANTAL','LEVERINGSRICHTING_PERC','SOORT_AANSLUITING','SJV_GEMIDDELD']]
    liander = liander.loc[liander['PRODUCTSOORT'] == 'ELK']
    liander.to_csv('data/csv/liander')

    # create amsterdam only dataset
    amsterdam = liander.loc[liander['WOONPLAATS'] == 'AMSTERDAM']
    amsterdam.to_csv('data/csv/amsterdam')

    # create leiden only dataset
    leiden = liander.loc[liander['WOONPLAATS'] == 'LEIDEN']
    leiden.to_csv('data/csv/leiden')

    # create krommenie only dataset
    krommenie = liander.loc[liander['WOONPLAATS'] == 'KROMMENIE']
    krommenie.to_csv('data/csv/krommenie')

    # read enexis dataset
    enexis = pd.read_excel('data/Liander & Enexis Data.xlsx', sheet_name=1)
    enexis = enexis[['NETGEBIED','STRAATNAAM','POSTCODE_VAN','POSTCODE_TOT','WOONPLAATS','PRODUCTSOORT','AANSLUITINGEN_AANTAL','LEVERINGSRICHTING_PERC','SOORT_AANSLUITING','SJA_GEMIDDELD']]
    enexis = enexis.loc[enexis['PRODUCTSOORT'] == 'ELK']
    enexis.to_csv('data/csv/enexis')

    # create eindhoven only dataset
    eindhoven = enexis.loc[enexis['WOONPLAATS'] == 'EINDHOVEN']
    eindhoven.to_csv('data/csv/eindhoven')


def add_coordinates(dataframe):
    """
    this function is used to add the coordinates to the database
    returns a dataframe, save dataframe to save the added columns
    credit to www.geonames.org for the database of postal_codes and coordinates
    """    
    # create dataframe from the NL_full data to query later
    with open('data/NL_full') as file:
        postcode = []
        latitude = []
        longitude = []
        while True:
            content=file.readline()
            if not content:
                break
            # this data file has no column names, instead look for commas manually
            commaindex = [i for i, ltr in enumerate(content) if ltr == ',']
            postcode.append(content[commaindex[0]+1:commaindex[1]] + content[commaindex[1]+1:commaindex[2]])
            latitude.append(content[commaindex[-2]+1:commaindex[-1]])
            longitude.append(content[commaindex[-3]+1:commaindex[-2]])

    # create the dataframe with created lists
    coordinates_df = pd.DataFrame(list(map(list, zip(postcode,latitude,longitude))))
    coordinates_df.columns = ['postcode', 'latitude', 'longitude']

    # make copy of dataframe for self containment
    df = dataframe.copy()
    i = 1
    j = len(dataframe.index)
    latitude = []
    longitude = []
    # go through each row and add the latitude and longitude to the dataframe
    for index, row in df.iterrows():
        postcode = row['POSTCODE_TOT']
        new_row = coordinates_df.loc[coordinates_df['postcode'] == postcode]
        try:
            latitude.append(new_row['latitude'].values[0])
            longitude.append(new_row['longitude'].values[0]) 
        # some postal codes are missing, in that case just take the last value
        except IndexError:
            try:
                print('ERROR')
                latitude.append(latitude[len(latitude) - 1])
                longitude.append(longitude[len(longitude) - 1]) 
            # if the last value is also missing delete the row
            except IndexError:
                print('SUPER ERROR, DELETING COLUMN IMMINENT!!!')
                df = df.drop(index)    

        # printing percentage complete, because this function takes a long ass time
        print(f'Percentage complete: {((i/j)*100): .2f}%')
        i += 1

    # add the new latitude collumns to the dataframe
    df['latitude'] = longitude
    df['longitude'] = latitude

    return df