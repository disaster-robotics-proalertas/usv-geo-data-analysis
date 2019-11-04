# generate a rosbag with only the interesting topics for geo data analysis
#rosbag filter $1 $2  "topic == '/mavros/global_position/global/header/stamp/secs' or topic == '/mavros/global_position/global/latitude' or topic == '/mavros/global_position/global/longitude' or topic ==  '/mavros/global_position/global/altitude' or topic ==  '/atlas/raw/Conductivity/ec' or topic ==  '/atlas/raw/DissolvedOxygen/do' or topic ==  '/atlas/raw/RedoxPotential/orp' or topic ==  '/atlas/raw/Temperature/celsius' or topic == '/atlas/raw/pH/pH'"
#rosbag filter $1 $2  "'/mavros/global_position/global/header/stamp/secs' in topic or '/mavros/global_position/global/latitude' in topic or '/mavros/global_position/global/longitude' in topic or '/mavros/global_position/global/altitude' in topic or '/atlas/raw/Conductivity/ec' in topic or '/atlas/raw/DissolvedOxygen/do' in topic or '/atlas/raw/RedoxPotential/orp' in topic or '/atlas/raw/Temperature/celsius' in topic or '/atlas/raw/pH/pH' in topic"
rosbag filter $1 $2  "'atlas' in topic or '/mavros/global_position/global' in topic"