""" data visualization functions """
import folium
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

from matplotlib import gridspec
from folium import plugins
from pipeline import get_ts, get_all_locations, get_top_k_locations, get_assignee_ts


"""
FUNCTIONS TO PRODUCE VISUALIZATIONS

FUNCTIONS FOR PART 1
"""

def get_html(full_year_data, viz, year, k = None, zoom_on = None) :
    """
    Produce HTML rendering of Folium map
    
    Inputs
    :full_year_data: required data for plotting the map
    :viz: string format, whether to include All, US, or Non-US assignees
    :year: string format
    :k: (optional) int, specifying the number of top assignees to include in the map
    :zoom_on: (latitude, longitude, zoom) specifying the initial position of the map (by default: World)
    
    Outputs
    :num_inventors: (only if k is not None) sum of number of inventors in year for the top k assignees
    """
    
    blur = 5
    radius = 5
    min_opacity = 0.2
    max_val = 1

    if (zoom_on):
        center = (zoom_on[0], zoom_on[1])
        zoom_start = zoom_on[2]
    else:
        center = (30,15)
        zoom_start = 1.75
    
    map_ = folium.Map(center, zoom_start = zoom_start, prefer_canvas = False, width= 1000, height = 600,
                      min_zoom = 2, max_zoom = 5, no_wrap = True, max_bounds = True, min_lat = -60, 
                      max_lat = 80, zoom_control = False)
    
    if viz == 'All':
    
        if (k):
            locations, df, num_inventors = get_top_k_locations(full_year_data[str(year)]['assignees'], k)
            # save dataframe to csv
            df.to_csv(viz + '_' + str(year) + '.csv')
        else:
            locations = get_all_locations(full_year_data[str(year)]['locations'])

        plugins.HeatMap(locations, radius = radius, blur = blur, show = True,
                        min_opacity = min_opacity, max_val = max_val).add_to(map_)
                    
    else:

        if viz == 'US Assignees':
            query = "type == '2' | type == '4' | type == '6'"
            
        if viz == 'Non-US Assignees': 
            query = "type == '3' | type == '5' | type == '7'"

        # also count number of inventors named in patents for the top k assignees            
        if (k):
            locations, df, num_inventors = get_top_k_locations(full_year_data[str(year)]['assignees'].query(query), k)
            # save dataframe to csv
            df.to_csv(viz + '_' + str(year) + '.csv')
        
            plugins.HeatMap(locations, radius = radius, blur = blur, show = True,
                            min_opacity = min_opacity + 0.2, max_val = max_val).add_to(map_)

    # save map to html file
    map_.save(viz + '_' + str(year) + '.html')
    
    if (k):     
        return num_inventors


def get_timeseries_fig(full_year_data, year_range, num_inventors_top_10_us, num_inventors_top_10_nonus):
    """
    Produces a figure with various time series plots and saves to working directory:
    - Number of utility patents vs design patents vs other patents
    - Total number of inventors
    - Number of inventors for the top K Non-US/US Assignees
    - Total number of Citations
    - Total number of individuals as assignees
    
    Inputs
    :full_year_data: all data
    :year_range: range type, from the first to the last year for which there is data in full_year_data
    :num_inventors_top_10_us: time series of data which is returned by get_html() when passing a value for the top K US assignees
    :num_inventors_top_10_nonus: same as previous, but for top K Non-US assignees
    """
    
    # get the time series data
    patents_ts, inventors_ts, citations_ts, utility_ts, design_ts, individuals_ts = get_ts(full_year_data)
    num_inventors_top_10_us = np.array(num_inventors_top_10_us) / 1000
    num_inventors_top_10_nonus = np.array(num_inventors_top_10_nonus) / 1000
    
    fig = plt.figure()

    # split figure area
    gs = gridspec.GridSpec(5, 2, wspace=0.5, hspace=0, height_ratios=[1, 1, 0.75, 0.75, 0.5]) # 5x2 grid
    ax0 = fig.add_subplot(gs[0, :]) # utility vs design vs other patents
    ax1 = fig.add_subplot(gs[1, :]) # all inventors
    ax2 = fig.add_subplot(gs[2, :]) # inventors for top k assignees (us vs nonus)
    ax3 = fig.add_subplot(gs[3, :]) # citations
    ax4 = fig.add_subplot(gs[4, :]) # number of individual assignees
    
    ax0.set_title("All Numbers in [000's]", size = 20)

    # BASE PATENTS
    ax0.stackplot(year_range, utility_ts, design_ts, patents_ts - utility_ts - design_ts,
                  colors = ['#377EB8','#55BA87','#7E1137'],
                  labels = ['Number of Utility Patents', ' Design Patents', 'Other Patents'])

    # INVENTORS
    ax1.plot(year_range, inventors_ts, linewidth = 2, color = '#7E1137', label = 'Number of Total Inventors')
    
    # INVENTORS CATEGORIES
    ax2.plot(year_range, num_inventors_top_10_us, linewidth = 2, color = '#377EB8', label = 'Inventors - top 10 US Assignees')
    ax2.plot(year_range, num_inventors_top_10_nonus, linewidth = 2, color = '#55BA87', label = 'top 10 Non-US Assignees')
    
    # CITATIONS
    ax3.plot(year_range, citations_ts, linewidth = 2, color = '#377EB8', label = 'Total Number of Citations by All Patents')
    
    # INDIVIDUAL ASSIGNEES
    ax4.plot(year_range, individuals_ts, linewidth = 2, color = '#55BA87', label = 'Number of Individuals as Assignees [in units]')
    
    # FORMAT PLOTS
    ax1.yaxis.tick_right()
    ax3.yaxis.tick_right()
    ax4.set_xticks(year_range)

    # despine
    for i, a in enumerate([ax0, ax1, ax2, ax3, ax4]):
        if i != 4:
            a.set_xticks([])
        a.grid(axis = 'y', which = 'major')
        a.tick_params(axis='y', which='both',length=0)
        leg = a.legend(prop = {'size' : 14}, frameon = False, loc = 2)
        leg.get_frame().set_linewidth(0.0)
        for spine in ["top", "right", "bottom"]:
            a.spines[spine].set_visible(False)
            
    plt.locator_params(axis='x', nbins=12)
                
    fig.set_size_inches(14,12)
    
    # save plot
    plt.savefig('tsplot.png', format='png', transparent=True, bbox_inches='tight')
    plt.close()


def get_assignees_plot(full_year_data, assignees_us, assignees_nonus):
    """
    Produces a figure comparing the time series plots of the number of inventors for two lists of assignees, and saves to working directory.
    
    Inputs
    :full_year_data: all data
    :assignees_us: list of assignee names, to plot on the first part
    :assignees_nonus: list of assignee names, to plot on the second part
    """
    # get time series of number of inventors
    ts_us = get_assignee_ts(full_year_data, assignees_us)
    ts_nonus = get_assignee_ts(full_year_data, assignees_nonus)
    
    # plot figure
    fig = plt.figure(figsize=(24,10))
    
    # split figure area
    gs = gridspec.GridSpec(1, 2, wspace=0, hspace=0, width_ratios=[0.5, 0.5]) # 1x2 grid
    ax0 = fig.add_subplot(gs[0])
    ax1 = fig.add_subplot(gs[1])

    ax0.plot(ts_us)
    plt.ylabel('Number of Inventors')
    ax1.plot(ts_nonus)
    ax1.set_ylim(ax0.get_ylim())
    ax1.set_yticks([])    
    ax0.legend(assignees_us)
    ax1.legend(assignees_nonus)
    
    # save figure
    plt.savefig('tsplot_assignees.png', dpi = fig.dpi, format='png', transparent=True, bbox_inches='tight')
    plt.close()


"""
FUNCTIONS TO PRODUCE VISUALIZATIONS

FUNCTIONS FOR PART 2
"""

def save_layers(layers_data, name, zoom_on = None, layered = True):
    """
    Produce HTML rendering of Folium map, with layer control (produces one file) or without layer control (produces number of files = number of layers).
    
    Inputs
    :layers_data: set returned when calling load_layers_data from pipeline module
    :name: string format, name of HTML file to which to save the map
    :zoom_on: (latitude, longitude, zoom) specifying the initial position of the map (by default: World)
    :layered: whether to add layer control to a single map, or produce many maps without layer control
    """
    blur = 5
    radius = 10
    min_opacity = 0.5
    max_val = 1
    
    if (zoom_on):
        center = (zoom_on[0], zoom_on[1])
        zoom_start = zoom_on[3]
    else:
        center = (30,15)
        zoom_start = 1.75
    
    if (layered):
        # produce a single map
        map_ = folium.Map(center, zoom_start = zoom_start, width= 960, height = 600,
                          min_zoom = 2, no_wrap = True, max_bounds = True, min_lat = -60, max_lat = 80,
                          zoom_control = False)
    
    for layer in layers_data:
        if layered == False:
            # produce one map for each layer
            map_ = folium.Map(center, zoom_start = zoom_start, width= 960, height = 600,
                              min_zoom = 2, no_wrap = True, max_bounds = True, min_lat = -60, max_lat = 80,
                              zoom_control = False)
            
        # for each layer, get the list of inventor locations
        locations = layers_data[layer]['inventors'].values
        # draw heat map
        plugins.HeatMap(locations, radius = radius, blur = blur, show = False,
                        min_opacity = min_opacity, max_val = max_val, name = layer).add_to(map_)
        
        if layered == False:
            # save the HTML file for the current layer
            map_.save(name + '_Layer' + layer + '.html')
        
    if (layered):
        folium.LayerControl(collapsed = False).add_to(map_)
        # save map to file
        map_.save(name + '.html')