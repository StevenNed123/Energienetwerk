import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
from matplotlib import transforms
import matplotlib as mpl


def visualise_df(df, name):
    """
    creates a visualisation of the data using matplotlib
    uses the longitude and latitude in the dataframe 
    simple function that uses only the data in the dataframe
    """
    plt.style.use('_mpl-gallery')

    # save the maximum values to print and to scale later
    max_x = max(df.longitude)
    max_y = max(df.latitude)
    min_x = min(df.longitude)
    min_y = min(df.latitude)

    # create the data that is going to be plotted
    x = df.longitude
    y = df.latitude

    # printing maximum and minumum values
    print(f'highest longitude:{max_x}, lowest longitude:{min_x }')
    print(f'highest latitude:{max_y}, lowest latitude:{min_y}')

    # scaling the data from 1 to 100
    scalerx = 100/(max_x - min_x)
    scalery = 100/(max_y - min_y)
    x = (x - min_x) * scalerx
    y = (y - min_y) * scalery

    # create the size of each dot by calculating the energy usage
    sizes = (df.SJV_GEMIDDELD * df.AANSLUITINGEN_AANTAL) / 100000

    # add the map to the plot as background image
    fig, ax = plt.subplots()
    img = plt.imread(f'data/maps/{name}_map.png')
    ax.imshow(img, extent=[0,100  , 0,100])

    # create a heatmap by scaling the data to rgb values
    scaler_c = 1/(max(sizes) - min(sizes))
    colors = (sizes - min(sizes)) * scaler_c
    colors = [(1 - x, 0.2, 0.2, 0.4 + 0.6*x) for x in colors]

    # create the scatterplot and save it as png
    ax.scatter(x, y, sizes, edgecolors='none', norm='logit', c=colors)
    ax.grid()
    ax.axis('on')
    fig.savefig(f'visualisations/{name}.png', dpi=3000)


def visualise(name, facilities, connections):
    """
    creates a visualisation of the data using matplotlib
    uses the longitude and latitude in the dataframe 
    visualise function that can plot each different station with different colors
    """
    plt.style.use('_mpl-gallery')

    x = []
    y = []
    sizes = []
    colors = []

    # add the map to the plot as background image
    fig, ax = plt.subplots()
    img = plt.imread(f'data/maps/{name}_map.png')
    ax.imshow(img, extent=[0,100  , 0,100])

    # add all facilities to the plot
    for i in range(len(facilities)):

        # create the data that is going to be plotted
        x = x + [l.x for l in facilities[i]]
        y = y + [l.y for l in facilities[i]]

        facilitiy_type = facilities[i][0].__class__.__name__
        # if node color red
        if facilitiy_type == 'Node':
            current_sizes = [x.energy / 100 for x in facilities[i]]
            sizes =  sizes + current_sizes
            scaler_c = 1/(max(current_sizes) - min(current_sizes)) if max(current_sizes) - min(current_sizes) != 0 else 1
            scaled = (np.asarray(current_sizes) - min(current_sizes)) * scaler_c
            colors = colors + [(1, 0.2, 0.2, 0.4 + 0.6*x) for x in scaled]

        # if l station color blue
        if facilitiy_type == 'L_station':
            current_sizes = [x.energy / 300 for x in facilities[i]]
            sizes =  sizes + current_sizes
            scaler_c = 1/(max(current_sizes) - min(current_sizes)) if max(current_sizes) - min(current_sizes) != 0 else 1
            scaled = (np.asarray(current_sizes) - min(current_sizes)) * scaler_c
            colors = colors + [(0.2, 0.2, 0.9, 0.6 + 0.4*x) for x in scaled]

        # if m station color green
        if facilitiy_type == 'M_station':
            current_sizes = [x.energy / 600 for x in facilities[i]]
            sizes =  sizes + current_sizes
            scaler_c = 1/(max(current_sizes) - min(current_sizes)) if max(current_sizes) - min(current_sizes) != 0 else 1
            scaled = (np.asarray(current_sizes) - min(current_sizes)) * scaler_c
            colors = colors + [(0.2, 0.9, 0.2, 0.4 + 0.6*x) for x in scaled]

        # if h station color purple
        if facilitiy_type == 'H_station':
            current_sizes = [x.energy / 4000 for x in facilities[i]]
            sizes =  sizes + current_sizes
            scaler_c = 1/(max(current_sizes) - min(current_sizes)) if max(current_sizes) - min(current_sizes) != 0 else 1
            scaled = (np.asarray(current_sizes) - min(current_sizes)) * scaler_c
            colors = colors + [(0.6, 0.1, 1, 1) for x in scaled]

    for connection in connections:
        ax.plot([connection.start_node.x, connection.end_node.x], [connection.start_node.y, connection.end_node.y], '', lw=0.1, color='black', zorder=1, alpha=0.8)

    # create the scatterplot and save it as png
    ax.scatter(x, y, sizes, edgecolors='none', norm='logit', c=colors, zorder=2)
    ax.grid(False)
    ax.axis('on')
    fig.savefig(f'tool_images/{name}.png', dpi=3000)


def visualise_routes(name, facilities, routes=[]):
    """
    creates a visualisation of the data using matplotlib
    uses the longitude and latitude in the dataframe 
    visualise function that also plots the routes of the stations
    """
    plt.style.use('_mpl-gallery')

    x = []
    y = []
    sizes = []
    colors = []

    # add the map to the plot as background image
    fig, ax = plt.subplots()
    img = plt.imread(f'data/maps/{name}_map.png')
    ax.imshow(img, extent=[0,100  , 0,100])

    # add all facilities to the plot
    for i in range(len(facilities)):

        # create the data that is going to be plotted
        x = x + [l.x for l in facilities[i]]
        y = y + [l.y for l in facilities[i]]

        facilitiy_type = facilities[i][0].__class__.__name__
        # if node color red
        if facilitiy_type == 'Node':
            current_sizes = [x.energy / 100 for x in facilities[i]]
            sizes =  sizes + current_sizes
            scaler_c = 1/(max(current_sizes) - min(current_sizes)) if max(current_sizes) - min(current_sizes) != 0 else 1
            scaled = (np.asarray(current_sizes) - min(current_sizes)) * scaler_c
            colors = colors + [(1, 0.2, 0.2, 0.4 + 0.6*x) for x in scaled]

        # if l station color blue
        if facilitiy_type == 'L_station':
            current_sizes = [x.energy / 300 for x in facilities[i]]
            sizes =  sizes + current_sizes
            scaler_c = 1/(max(current_sizes) - min(current_sizes)) if max(current_sizes) - min(current_sizes) != 0 else 1
            scaled = (np.asarray(current_sizes) - min(current_sizes)) * scaler_c
            colors = colors + [(0.2, 0.2, 0.9, 0.6 + 0.4*x) for x in scaled]

        # if m station color green
        if facilitiy_type == 'M_station':
            current_sizes = [x.energy / 500 for x in facilities[i]]
            sizes =  sizes + current_sizes
            scaler_c = 1/(max(current_sizes) - min(current_sizes)) if max(current_sizes) - min(current_sizes) != 0 else 1
            scaled = (np.asarray(current_sizes) - min(current_sizes)) * scaler_c
            colors = colors + [(0.2, 0.9, 0.2, 0.8) for x in scaled]

        # if h station color yellow
        if facilitiy_type == 'H_station':
            current_sizes = [x.energy / 600 for x in facilities[i]]
            sizes =  sizes + current_sizes
            scaler_c = 1/(max(current_sizes) - min(current_sizes)) if max(current_sizes) - min(current_sizes) != 0 else 1
            scaled = (np.asarray(current_sizes) - min(current_sizes)) * scaler_c
            colors = colors + [(0.6, 0.1, 1, 1) for x in scaled]

    counter = 0
    for route in routes:
        for i in range(len(route) - 1):
            counter += 1
            ax.plot([route[i].x, route[i+1].x], [route[i].y, route[i+1].y], '', lw=0.1, color='black', zorder=1, alpha=0.8)

    # create the scatterplot and save it as png
    ax.scatter(x, y, sizes, edgecolors='none', norm='logit', c=colors, zorder=2)
    ax.grid(False)
    ax.axis('on')
    fig.savefig(f'tool_images/{name}.png', dpi=3000)


def visualise_single(name, facilities):
    """
    creates a visualisation of the data using matplotlib
    simplefied version of the complete function
    this function is easier to edit but can only plot one type of facility
    """
    plt.style.use('_mpl-gallery')

    # create the data that is going to be plotted
    x = [x.longitude for x in facilities]
    y = [x.latitude for x in facilities]

    # create the size of each dot by calculating the energy usage
    sizes = [x.energy / 1 for x in facilities]

    # add the map to the plot as background image
    fig, ax = plt.subplots()
    img = plt.imread(f'data/maps/{name}_map.png')
    ax.imshow(img, extent=[0,100  , 0,100])

    # create a heatmap by scaling the data to rgb values
    try:
        scaler_c = 1/(max(sizes) - min(sizes))
    except ZeroDivisionError:
        scaler_c = 1

    colors = (np.asarray(sizes) - min(sizes)) * scaler_c
    # color red
    colors = [(1 - x, 0.2, 0.2, 0.4 + 0.6*x) for x in colors]


    # create the scatterplot and save it as png
    ax.scatter(x, y, sizes, edgecolors='none', norm='logit', c=colors)
    ax.grid(False)
    ax.axis('on')
    fig.savefig(f'tool_images/{name}.png', dpi=3000)