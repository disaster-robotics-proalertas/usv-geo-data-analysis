"""
 DESCRIPTION: it takes a rosbag file with some pre-defined topic names and generate CSV and Pandas Pickle files used for data analysis
 AUTHOR: Alexandre Amory (amamory@gmail.com)
 ROS only supports python 2.X. So, before installing, make sure you are using the corrent Python version
 DEPEDENCIES: do not use pip to install them !
 	- sudo apt-get install python-pandas
 	- sudo apt-get install python-geopandas
 	- sudo apt-get install rospy_message_converter
 then compile/install these ROS packages
 	https://github.com/eurogroep/rosbag_pandas
 	https://github.com/disaster-robotics-proalertas/atlas-ros <== required to understand the water quality topic formats

 TODO: geopandas/shapely and rosbag_pandas are not reeealy necessary. it might be interesting to have a rosbag2pandas.py script
"""
import os, sys
import rosbag_pandas
import pandas
import geopandas as gpd
#import matplotlib.pyplot as plt
from shapely.geometry import Point
import time


# run the following command to reduce the rosbag file size to contain only the required topics
# $rosbag filter  original.bag filtered.bag "topic == '/mavros/global_position/global/header/stamp/secs' or topic == '/mavros/global_position/global/latitude' or topic == '/mavros/global_position/global/longitude' or topic ==  '/mavros/global_position/global/altitude' or topic ==  '/atlas/raw/Conductivity/ec' or topic ==  '/atlas/raw/DissolvedOxygen/do' or topic ==  '/atlas/raw/RedoxPotential/orp' or topic ==  '/atlas/raw/Temperature/celsius' or topic == '/atlas/raw/pH/pH'"
# rosbag filter  2019-10-25-20-54-34-no-state.bag 2019-10-25-20-54-34-no-state-selected2.bag "topic == '/mavros/global_position/global/header/stamp/secs' or topic == '/mavros/global_position/global/latitude' or topic == '/mavros/global_position/global/longitude' or topic ==  '/mavros/global_position/global/altitude' or topic ==  '/atlas/raw/Conductivity/ec' or topic ==  '/atlas/raw/DissolvedOxygen/do' or topic ==  '/atlas/raw/RedoxPotential/orp' or topic ==  '/atlas/raw/Temperature/celsius' or topic == '/atlas/raw/pH/pH'"

#verify correct input arguments: 1 or 2
if (len(sys.argv) > 2):
	print "invalid number of arguments:   " + str(len(sys.argv))
	print "should be 2: 'rosbag2geopandas.py' and 'bagName'"
	print "or just 1  : 'rosbag2geopandas.py'"
	sys.exit(1)
elif (len(sys.argv) == 2):
	listOfBagFiles = [sys.argv[1]]
	numberOfFiles = 1
	print "reading only 1 bagfile: " + str(listOfBagFiles[0])
elif (len(sys.argv) == 1):
	listOfBagFiles = [f for f in os.listdir(".") if f[-4:] == ".bag"]	#get list of only bag files in current dir.
	numberOfFiles = str(len(listOfBagFiles))
	print "reading all " + numberOfFiles + " bagfiles in current directory: \n"
	for f in listOfBagFiles:
		print f
	print "\n press ctrl+c in the next 10 seconds to cancel \n"
	time.sleep(10)
else:
	print "bad argument(s): " + str(sys.argv)	#shouldnt really come up
	sys.exit(1)

# for testing only
#listOfBagFiles = ['./data/furg-lake.bag']
#numberOfFiles = 1


count = 0
for currentFile in listOfBagFiles:
	# split filename in path, filename, extension
	filename, file_extension = os.path.splitext(currentFile)
	filepath, filename = os.path.split(filename)

	if (file_extension != '.bag'):
		print('ERROR: expecting a ROS bag file with extension .bag')
		sys.exit(1)

	rosbag_filesize = os.path.getsize(currentFile)/float(1024*1024)

	print "Reading rosbag file of " + "%.2f" % rosbag_filesize + " MBytes"

	if (rosbag_filesize > 30.0):
		print "It is not recommended to read such big file (> 30 MBytes). It will slowdown the computer."
		raw_input("Press CTRL+C to exit or other key to continue ...")

	# extract only these topics from the bag
	selected_topics = ['/mavros/global_position/global', '/atlas/raw/Conductivity', '/atlas/raw/DissolvedOxygen', '/atlas/raw/RedoxPotential', '/atlas/raw/Temperature', '/atlas/raw/pH']

	# header/stamp/secs has the timestamp in order
	selected_columns = ['/mavros/global_position/global/header/stamp/secs', '/mavros/global_position/global/latitude', '/mavros/global_position/global/longitude', '/mavros/global_position/global/altitude', '/atlas/raw/Conductivity/ec', '/atlas/raw/DissolvedOxygen/do', '/atlas/raw/RedoxPotential/orp', '/atlas/raw/Temperature/celsius', '/atlas/raw/pH/pH', '/atlas/raw/Conductivity/header/stamp/secs', '/atlas/raw/DissolvedOxygen/header/stamp/secs', '/atlas/raw/RedoxPotential/header/stamp/secs', '/atlas/raw/Temperature/header/stamp/secs', '/atlas/raw/pH/header/stamp/secs']

	df = rosbag_pandas.bag_to_dataframe(currentFile)
	#print (df.shape)
	#print (df.columns)
	#df.to_csv(os.path.join(filepath, filename+"-df3.csv"))

	print "###############################"
	print "Original table size (lines x cols): " + str(df.shape[0]) + " x " + str(df.shape[1])
	print "###############################"
	print ""

	# delete the unwanted columns
	col_names = df.columns
	for col in col_names:
		if col not in selected_columns:
			df = df.drop([col], axis=1)

	if len(df.columns) != len(selected_columns):
		print "ERROR: missing expected topics"
		sys.exit(1)
	#df.to_csv(os.path.join(filepath, filename+"-df2.csv")
	#print (df.shape)
	#print (df.columns)

	# dropping NaN data for every sensor data
	df_ec = df[['/atlas/raw/Conductivity/ec','/atlas/raw/Conductivity/header/stamp/secs']]
	df_ec = df_ec.dropna()
	water_samples = df_ec.shape[0]

	df_do = df[['/atlas/raw/DissolvedOxygen/do','/atlas/raw/DissolvedOxygen/header/stamp/secs']]
	df_do = df_do.dropna()
	#print "DO shape" + str(df_do.shape)

	df_orp = df[['/atlas/raw/RedoxPotential/orp','/atlas/raw/RedoxPotential/header/stamp/secs']]
	df_orp = df_orp.dropna()
	#print "ORP shape" + str(df_orp.shape)

	df_temp = df[['/atlas/raw/Temperature/celsius','/atlas/raw/Temperature/header/stamp/secs']]
	df_temp = df_temp.dropna()
	#print "temp shape" + str(df_temp.shape)

	df_ph = df[['/atlas/raw/pH/pH','/atlas/raw/pH/header/stamp/secs']]
	df_ph = df_ph.dropna()
	#print "PH shape" + str(df_ph.shape)

	df_gps = df[['/mavros/global_position/global/header/stamp/secs', '/mavros/global_position/global/latitude', '/mavros/global_position/global/longitude', '/mavros/global_position/global/altitude']]
	df_gps = df_gps.dropna()
	#print "GPS shape" + str(df_gps.shape)

	if df_ec.shape[0] != water_samples or df_do.shape[0] != water_samples or \
		df_orp.shape[0] != water_samples or df_temp.shape[0] != water_samples or \
		df_ph.shape[0] != water_samples:
		print "WARNING: diferent # of samples for each water parameter"
		print 'EC:', df_ec.shape[0], 'DO:', df_do.shape[0], 'ORP:', df_orp.shape[0], 'Temp:', df_temp.shape[0], 'pH:', df_ph.shape[0]
		num_samples = [df_ec.shape[0], df_do.shape[0], df_orp.shape[0], df_temp.shape[0], df_ph.shape[0]]
		water_samples = min(num_samples)

	csv_list =[]
	# build the output CSV file, row by row
	for i in range(water_samples):
		aux = [tuple(df_ec.iloc[i]),tuple(df_do.iloc[i]),tuple(df_orp.iloc[i]),tuple(df_temp.iloc[i]),tuple(df_ph.iloc[i]),]
		# extracts only the water sampling data, leaving the sample time
		water_data = [ seq[0] for seq in aux ]
		#print (water_data)
		# get the min and max time of this list of tuples. it correspond to get the time of the 1s and last samples
		min_time = min(aux, key = lambda t: t[1])[1]
		max_time = max(aux, key = lambda t: t[1])[1]
		#print (min_time, max_time)
		# get the gps readings related to the time interval of the water samples
		interval_gps = df_gps[df_gps['/mavros/global_position/global/header/stamp/secs'].between(min_time,max_time)]
		if interval_gps.shape[0] == 0:
			print ('ERROR: no GPS data was found between the atlas timestamps')
			sys.exit(1)
		# get the median of the values. median is selected to avoid outlier/glitches in gps data
		#print (interval_gps.shape)
		print (interval_gps.head)
		median_time  = interval_gps['/mavros/global_position/global/header/stamp/secs'].median()
		median_latitude  = interval_gps['/mavros/global_position/global/latitude'].median()
		median_longitude = interval_gps['/mavros/global_position/global/longitude'].median()
		median_altitude  = interval_gps['/mavros/global_position/global/altitude'].median()
		# now, a new row is ready to be saved
		#print ([median_time, median_latitude, median_longitude, median_altitude])
		csv_row = [median_time, median_latitude, median_longitude, median_altitude] + water_data
		#print (csv_row)
		csv_list.append(csv_row)

	column_label = ['Time', 'Latitude', 'Longitude', 'Altitude', 'Condutivity', 'DissolvedOxygen', 'RedoxPotential', 'Temperature', 'pH']
	final_df = pandas.DataFrame(csv_list, columns=column_label)
	# replaces the ordinary index by the time taken from the rosbag
	final_df.set_index('Time', inplace=True)
	
	print "###############################"
	print "Filtered table size (lines x cols): " + str(final_df.shape[0]) + " x " + str(final_df.shape[1])
	print "###############################"
	print "  saving CSV and Pickle data formats ... "
	#print (final_df.shape)
	#print (final_df.columns)
	#print (final_df.head)
	final_df.to_csv(os.path.join(filepath, filename+"-df.csv"))
	final_df.to_pickle(os.path.join(filepath, filename+"-df.pkl"))

	# converting to geopandas datafram
	geometry = [Point(xy) for xy in zip(final_df.Longitude, final_df.Latitude)]
	final_df = final_df.drop(['Longitude', 'Latitude'], axis=1)
	crs = {'init': 'epsg:4326'}
	final_gdf = gpd.GeoDataFrame(final_df, crs=crs, geometry=geometry)

	print "  saving Geopandas Pickle data format ... "
	final_gdf.to_pickle(os.path.join(filepath, filename+"-gdf.pkl"))

print "fim"
