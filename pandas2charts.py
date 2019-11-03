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

rosbag_filename = './data/furg-lake.bag'

df = pandas.read_pickle(rosbag_filename+"-df.pkl")

locations = df[['Latitude', 'Longitude']]
locationlist = locations.values.tolist()
len(locationlist)
locationlist[7]

print (df.shape)
print (df.info)
print (df.head)
print (df.Latitude.mean())
print (df.Longitude.mean())

temp_data = df[['Temperature']]
temp_data_lists = temp_data.values.tolist()

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

geomap = folium.Map([df.Latitude.mean(), df.Longitude.mean()], zoom_start=18)


for point in range(0, len(locationlist)):
	#print (locationlist[point])
	#print (temp_data_lists[point])
	#folium.Marker(locationlist[point], popup=temp_data_lists[point]).add_to(geomap)
	folium.CircleMarker(locationlist[point], 
		radius=1, #weight=0,#remove outline
		popup=temp_data_lists[point]).add_to(geomap)
	#folium.Marker(locationlist[point]).add_to(geomap)

geomap.save(os.path.join('results', 'folium-furg_0.html'))

geomap


