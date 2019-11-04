
"""
 DESCRIPTION: takes Pandas Pickle files from rosbag2geopandas and it creates map charts with the USV data
 AUTHOR: Alexandre Amory (amamory@gmail.com)
 tested with python 2.7.X, installed by condas. required to install conda. It does not have any depedency with ROS.
 DEPEDENCIES: 
     - conda install anaconda-clean
     - conda install -c conda-forge folium
     - conda install geopandas
     - conda install folium
     - conda install matplotlib
     - conda install flask   -- recomended, but not required
     - conda install jupyter -- recomended, but not required
 
 The water quality probes are from Atlas Scientific. Refer to the manuals for more info of each parameter 
 https://www.atlas-scientific.com/product_pages/kits/env-sds-kit.html
   pH:
     Range: .001 − 14.000
     Resolution: .001
     Accuracy: +/– 0.002
   ORP:
     Range: -1019.9mV − 1019.9mV
     Resolution: ???
     Accuracy: +/– 1mV
   Dissolved Oxigen:
     Range: 0.01 − 100+ mg/L
     Resolution: ???
     Accuracy: +/– 0.05 mg/L
   Conductivity:
     Range: 0.07 − 500,000+ μS/cm
     Resolution: ???
     Accuracy: +/– 2% 
   Temperature
     Range:  -126.000 °C − 1254 °C
     Resolution: 0.001
     Accuracy:	+/– (0.10 C + 0.0017 x C)           
"""

import os
import sys
import pandas
import numpy as np
import folium
import branca.colormap as cm

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


#verify correct input arguments: 1 or 2
if (len(sys.argv) > 2):
	print ("ERROR: invalid number of arguments:   " + str(len(sys.argv)))
	print ("should be 2: 'pandas2charts.py' and 'bagName'")
	print ("or just 1  : 'pandas2charts.py'")
	sys.exit(1)
elif (len(sys.argv) == 2):
	listOfFiles = [sys.argv[1]]
	numberOfFiles = 1
	print ("reading only 1 bagfile: " + str(listOfFiles[0]))
elif (len(sys.argv) == 1):
	listOfFiles = [f for f in os.listdir(".") if f[-4:] == ".bag"]	#get list of only bag files in current dir.
	numberOfFiles = str(len(listOfFiles))
	print ("reading all " + numberOfFiles + " bagfiles in current directory: \n")
	for f in listOfFiles:
		print (f)
	print ("\n press ctrl+c in the next 10 seconds to cancel \n")
	time.sleep(10)
else:
	print ("ERROR: bad argument(s): " + str(sys.argv))	#shouldnt really come up
	sys.exit(1)

# for testing only
#listOfFiles = ['./data/furg-lake.bag']
#numberOfFiles = 1

count = 0
for currentFile in listOfFiles:
	# split filename in path, filename, extension
	filename, file_extension = os.path.splitext(currentFile)
	filepath, filename = os.path.split(filename)

	if (file_extension != '.pkl'):
		print('ERROR: expecting a pandas Pickle file with extension .pkl')
		sys.exit(1)
	#print ([filepath,filename, file_extension])
	
	df = pandas.read_pickle(currentFile)
	print ('Pickle file shape:', df.shape)
	#print (df.head)

	# check if the expected data is in the file
	expected_columns = ['Latitude', 'Longitude', 'Condutivity', 'DissolvedOxygen', 'RedoxPotential', 'Temperature', 'pH']
	for col in expected_columns:
		if col not in df.columns:
			print ("ERROR: column " + col + " not found in " + currentFile)
			sys.exit(1)
	# use only the expected columns
	df = df[expected_columns]

	expected_columns.remove('Latitude')
	expected_columns.remove('Longitude')

	#creating the map
	#print ([df[['Latitude']].mean(), df[['Longitude']].mean()])
	geomap = folium.Map([df[['Latitude']].mean(), df[['Longitude']].mean()], zoom_start=18)

	# a list of FeatureGroup/Layers and Colormaps
	fg = []
	cmap = []
	cnt = 0
	colormap_caption = ['Condutivity (μS/cm)', 'DissolvedOxygen (mg/L)', 'RedoxPotential (mV)', 'Temperature (C)', 'pH']

	#for each layer
	for data_var in expected_columns:
		#data_var = 'Temperature' #what variable will determine the color
		cmap.append( cm.LinearColormap(['blue', 'red'],
								 # this option is good to remove outliers. It removes 5% lowest and the 5% highest values
		                         vmin=df[[data_var]].quantile(0.05)[0], vmax=df[[data_var]].quantile(0.95)[0],
		                         # this option keep all data, including possible outliers
		                         #vmin=df[[data_var]].min()[0], vmax=df[[data_var]].max()[0],
		                         caption = colormap_caption[cnt])
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


	df.apply(plotDot, axis = 1)


	#Set the zoom to the maximum possible
	geomap.fit_bounds(geomap.get_bounds())

	# save the map
	geomap.save(os.path.join(filepath, filename+'.html'))

	# present basic statistics for all expected data
	df_temp = pandas.DataFrame(columns=expected_columns)

	for data_var in expected_columns:
		# get basic statistics
		temp_ser = df[data_var].describe()
		# set the entire column at once
		df_temp[data_var] = temp_ser

	print (df_temp)

	geomap

print ('fim')
