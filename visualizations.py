""" data visualization functions """
import folium
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

from matplotlib import gridspec
from folium import plugins
from collections import Counter
from pipeline import get_ts


def get_top_k_locations(data, k):
    
    assignees = data[['organization', 'patents']].values[:k,:]
    loc_counters = data['inventors_loc'].values[:k]
    num_inventors = 0
    locations = Counter()
    
    for counter in loc_counters:
        num_inventors += sum(counter.values())
        locations += counter
    
    locations = np.hstack([np.array(list(locations.keys())), 
                           np.array(list(locations.values()))[:,None]])
    
    top = pd.DataFrame({'Top Assignees' : assignees[:,0],
                        'Patent Applications' : assignees[:,1]})
    
    return locations, top, num_inventors


def get_all_locations(data):
    
    locations = [(data.index.values[i][0],
                  data.index.values[i][1],
                  data.values[i][0]) 
                 for i in range(len(data))]

    return locations


def get_png(full_year_data, viz, year, k = None, zoom_on = None) :
    
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
                      min_zoom = 2, no_wrap = True, max_bounds = True, min_lat = -60, max_lat = 80,
                      zoom_control = False)
    
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


def save_layers(layers_data, name, zoom_on = None, layered = True):
    
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
        map_ = folium.Map(center, zoom_start = zoom_start, width= 960, height = 600,
                          min_zoom = 2, no_wrap = True, max_bounds = True, min_lat = -60, max_lat = 80,
                          zoom_control = False)
    
    for layer in layers_data:
        if layered == False:
            map_ = folium.Map(center, zoom_start = zoom_start, width= 960, height = 600,
                              min_zoom = 2, no_wrap = True, max_bounds = True, min_lat = -60, max_lat = 80,
                              zoom_control = False)
        
        locations = layers_data[layer]['inventors'].values
    
        plugins.HeatMap(locations, radius = radius, blur = blur, show = False,
                        min_opacity = min_opacity, max_val = max_val, name = layer).add_to(map_)
        
        if layered == False:
            map_.save(name + '_Layer' + layer + '.html')
        
    if (layered):
        folium.LayerControl(collapsed = False).add_to(map_)
        # save map to file
        map_.save(name + '.html')


def get_timeseries_fig(full_year_data, year_range, num_inventors_top_10_us, num_inventors_top_10_nonus):
    
    patents_ts, inventors_ts, citations_ts, utility_ts, design_ts, individuals_ts = get_ts(full_year_data)
    
    fig = plt.figure()
    
    # ADD NUM INVENTORS FOR TOP K ASSIGNEES TIME SERIES + NUM INDIVIDUALS 
    
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
    
    # INVENTORS categories
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