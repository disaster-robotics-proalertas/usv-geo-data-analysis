# generate a rosbag with only the interesting topics for geo data analysis
rosbag filter $1 $2  "topic == '/mavros/global_position/global/header/stamp/secs' or topic == '/mavros/global_position/global/latitude' or topic == '/mavros/global_position/global/longitude' or topic ==  '/mavros/global_position/global/altitude' or topic ==  '/atlas/raw/Conductivity/ec' or topic ==  '/atlas/raw/DissolvedOxygen/do' or topic ==  '/atlas/raw/RedoxPotential/orp' or topic ==  '/atlas/raw/Temperature/celsius' or topic == '/atlas/raw/pH/pH'"
