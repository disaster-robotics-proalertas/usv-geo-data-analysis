
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


rosbag_filename = './data/furg-lake.bag'

df = pandas.read_pickle(rosbag_filename+"-df.pkl")

df = df[['Latitude', 'Longitude','Temperature', 'pH']]
dflist = df.values.tolist()
#dflist = df["Latitude"].tolist()

dfLat = df[['Latitude']]
dflistLat = df["Latitude"].tolist()

dfLong = df[['Longitude']]
dflistLong = df['Longitude'].tolist()

dfTemp = df[['Temperature']]
dflistTemp = df['Temperature'].tolist()

dfpH = df[['pH']]
dflistpH = df['pH'].tolist()


#print (dfpH.values)

#len(locationlist)
#locationlist[7]

#print (df.shape)
#print (df.info)
#print (df.head)
#print (df.Latitude.mean())
#print (df.Longitude.mean())

#temp_data = df[['Temperature']]
#temp_data_lists = temp_data.values.tolist()

"""
app = Flask(__name__)


@app.route('/')
def index():
    start_coords = (df.Latitude.mean(), df.Longitude.mean())
    folium_map = folium.Map(location=start_coords, zoom_start=14)
    return folium_map._repr_html_()


if __name__ == '__main__':
    app.run(debug=True)
"""


print (dfTemp.quantile(0.05)[0])
print (dfTemp.quantile(0.95)[0])

color_var = 'Temperature' #what variable will determine the color
cmap = cm.LinearColormap(['blue', 'red'],
                         vmin=dfTemp.quantile(0.05)[0], vmax=dfTemp.quantile(0.95)[0],
                         #vmin=25, vmax=29,
                         caption = color_var)

#creating the map
geomap = folium.Map([dfLat.mean(), dfLong.mean()], zoom_start=18)


# creating the data layers
# https://github.com/python-visualization/folium/blob/master/examples/FeatureGroup.ipynb
#fg = folium.FeatureGroup
fgTemp = folium.FeatureGroup(name='Temperature')
fgpH = folium.FeatureGroup(name='pH')

folium.Marker(location=[dfLat.mean(), dfLong.mean()],
       popup='Mt. Hood Meadows').add_to(fgTemp)

folium.Marker(location=[dfLat.mean(), dfLong.mean()],
       popup='Timberline Lodge').add_to(fgpH)

fgTemp.add_to(geomap)
fgpH.add_to(geomap)
folium.LayerControl().add_to(geomap)
'''
g1 = folium.plugins.FeatureGroupSubGroup(fg, 'Temperature')
g2 = folium.plugins.FeatureGroupSubGroup(fg, 'pH')
geomap.add_child(fg)
geomap.add_child(g1)
geomap.add_child(g2)

    >>> fg = folium.FeatureGroup()                          # Main group
    >>> g1 = folium.plugins.FeatureGroupSubGroup(fg, 'g1')  # First subgroup of fg
    >>> g2 = folium.plugins.FeatureGroupSubGroup(fg, 'g2')  # Second subgroup of fg
    >>> m.add_child(fg)
    >>> m.add_child(g1)
    >>> m.add_child(g2)
    >>> g1.add_child(folium.Marker([0,0]))
    >>> g2.add_child(folium.Marker([0,1]))
    >>> folium.LayerControl().add_to(m)
'''


#Add the color map legend to your map
geomap.add_child(cmap)

def plotDot(point):
    '''input: series that contains a numeric named latitude and a numeric named longitude
    this function creates a CircleMarker and adds it to your this_map'''
    folium.CircleMarker(location=[point.Latitude, point.Longitude],
                        fill_color=cmap(point[color_var]),
                        radius=2,
                        popup= "%.2f" % point[color_var],
                        weight=0).add_to(geomap)
'''
for lat, lon, temp in zip(dflistLat,dflistLong,dflistTemp):
    print (lat, lon, temp[0])
    print (cmap(27))
    #print (cmap(temp_data[color_var]))
    #print (temp_data_lists[point])
    #folium.Marker(locationlist[point], popup=temp_data_lists[point]).add_to(geomap)
    #folium.CircleMarker(locationlist[point], 
    #   radius=1, #weight=0,#remove outline
    #   fill_color=cmap(temp_data[color_var]),
    #   popup=temp_data_lists[point]).add_to(geomap)
    folium.CircleMarker(location=[lat[0], lon[0]],
                        fill_color=cmap(temp[0]),
                        radius=2,
                        weight=0).add_to(geomap)
    #folium.Marker(locationlist[point]).add_to(geomap)
'''

df.apply(plotDot, axis = 1)


#Set the zoom to the maximum possible
geomap.fit_bounds(geomap.get_bounds())

geomap.save(os.path.join('results', 'folium-furg_0.html'))

geomap


