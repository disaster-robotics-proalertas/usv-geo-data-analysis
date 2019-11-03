
"""
 DESCRIPTION: takes Pandas Pickle files from rosbag2geopandas and create map charts with the USV data
 AUTHOR: Alexandre Amory (amamory@gmail.com)
 tested with python 2.7.X, installed by condas. required to install conda. does not have any depedency with ROS.
 DEPEDENCIES: 
     - conda install anaconda-clean
     - conda install -c conda-forge folium
     - conda install geopandas
     - conda install folium
     - conda install matplotlib
     - conda install flask   -- recomended, but not required
     - conda install jupyter -- recomended, but not required

 TODO: geopandas/shapely and rosbag_pandas are not reeealy necessary. it might be interesting to have a rosbag2pandas.py script
"""

# GeoPandas Heatmaps
# https://nbviewer.jupyter.org/gist/perrygeo/c426355e40037c452434
# download OSM maps
# https://www.openstreetmap.org/export#map=19/-32.07384/-52.16541
#import geopandas as gpd
import os
import sys
import pandas
import numpy as np
import folium
import branca.colormap as cm

#from flask import Flask

#from scipy import ndimage

#import matplotlib.pylab as pylab
#import matplotlib.pyplot as plt
#from mpl_toolkits.basemap import Basemap
#import gmplot 

# Create a dataframe with fake data
"""
df = pd.DataFrame({
    'longitude':   np.random.normal(11.84,     0.15,     1000),
    'latitude':    np.random.normal(55.55,     0.15,     1000),
    'temperature': np.random.normal(temp_mean, temp_std, 1000)})
"""

# exemplo bom c pandas
# https://github.com/python-visualization/folium/issues/958
# folium markers from list
# https://georgetsilva.github.io/posts/mapping-points-with-folium/
# folium c colormap
# https://github.com/collinreinking/longitude_latitude_dot_plots_in_python_with_folium/blob/master/MapsTutorials.ipynb
# group markers
# https://nbviewer.jupyter.org/github/python-visualization/folium/blob/master/examples/Plugins.ipynb
# folium and matplot examples
# http://cican17.com/data-visualization-with-python/
# folium lines
# https://deparkes.co.uk/2016/06/03/plot-lines-in-folium/


#load data file 
rosbag_filename = './data/furg-lake.bag'
df = pandas.read_pickle(rosbag_filename+"-df.pkl")

# check if the expected data is in the file
expected_columns = ['Latitude', 'Longitude', 'Condutivity', 'DissolvedOxygen', 'RedoxPotential', 'Temperature', 'pH']
for col in expected_columns:
	if col not in df.columns:
		print ("ERROR: column " + col + " not found in " + rosbag_filename +"-df.pkl")
		sys.exit(1)
# use only the expected columns
df = df[expected_columns]

expected_columns.remove('Latitude')
expected_columns.remove('Longitude')

#creating the map
geomap = folium.Map([df[['Latitude']].mean(), df[['Longitude']].mean()], zoom_start=18)

# a list of FeatureGroup/Layers and Colormaps
fg = []
cmap = []
cnt = 0

#for each layer
for data_var in expected_columns:
	#data_var = 'Temperature' #what variable will determine the color
	cmap.append( cm.LinearColormap(['blue', 'red'],
	                         vmin=df[[data_var]].quantile(0.05)[0], vmax=df[[data_var]].quantile(0.95)[0],
	                         caption = data_var)
				)

	# creating the data layers
	# https://github.com/python-visualization/folium/blob/master/examples/FeatureGroup.ipynb
	fg.append( folium.FeatureGroup(name=data_var) )

	fg[cnt].add_to(geomap)
	geomap.add_child(cmap[cnt])
	cnt = cnt+1
folium.LayerControl().add_to(geomap)

def plotDot(point):
    '''input: series that contains a numeric named latitude and a numeric named longitude
    this function creates a CircleMarker and adds it to your this_map'''
    cnt = 0
    # create the points to each data and associate with the FeatureGroup and Colormaps
    for data_var in expected_columns:
	    folium.CircleMarker(location=[point.Latitude, point.Longitude],
                    fill_color=cmap[cnt](point[data_var]),
                    radius=2,
                    popup= "%.2f" % point[data_var],
                    weight=0).add_to(fg[cnt])
	    cnt =  cnt +1
'''
    #add points to the Condutivity Layer
    folium.CircleMarker(location=[point.Latitude, point.Longitude],
                        fill_color=cmap[0](point['Condutivity']),
                        radius=2,
                        popup= "%.2f" % point['Condutivity'],
                        weight=0).add_to(fg[0])
    #add points to the DissolvedOxygen Layer
    folium.CircleMarker(location=[point.Latitude, point.Longitude],
                        fill_color=cmap[1](point['DissolvedOxygen']),
                        radius=2,
                        popup= "%.2f" % point['DissolvedOxygen'],
                        weight=0).add_to(fg[1])
    #add points to the RedoxPotential Layer
    folium.CircleMarker(location=[point.Latitude, point.Longitude],
                        fill_color=cmap[2](point['RedoxPotential']),
                        radius=2,
                        popup= "%.2f" % point['RedoxPotential'],
                        weight=0).add_to(fg[2])                            
    #add points to the Temperature Layer
    folium.CircleMarker(location=[point.Latitude, point.Longitude],
                        fill_color=cmap[3](point['Temperature']),
                        radius=2,
                        popup= "%.2f" % point['Temperature'],
                        weight=0).add_to(fg[3])
    # add points to the pH Layer
    folium.CircleMarker(location=[point.Latitude, point.Longitude],
                        fill_color=cmap[4](point['pH']),
                        radius=2,
                        popup= "%.2f" % point['pH'],
                        weight=0).add_to(fg[4])
'''

df.apply(plotDot, axis = 1)


#Set the zoom to the maximum possible
geomap.fit_bounds(geomap.get_bounds())

geomap.save(os.path.join('results', 'folium-furg_0.html'))

geomap


