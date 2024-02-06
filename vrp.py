import folium
import openrouteservice as ors
import math

import pandas as pd

# Create a DataFrame with three columns and set initial values to 0
data = {'cost': [0], 'distance': [0], 'duration': [0]}
df = pd.DataFrame(data)

# Simple single route optimization SHOULD BE IN LON LAT format!!
coords = [
    [-2.248555, 53.476935],
    [-2.253360, 53.474304],
    [-2.242935, 53.472388],
    [-2.239761, 53.479642],
    [-2.241995, 53.486725],
    [-2.260269, 53.481413],
    [-2.230429, 53.473963],
    [-2.248788, 53.466197],
]
# visualize the points on a map
m = folium.Map(location=(53.486725, -2.241995), tiles="cartodbpositron", zoom_start=14)
for coord in coords:
    folium.Marker(location=(coord[1],coord[0])).add_to(m)



m.save("./static/map.html")

client = ors.Client(key='5b3ce3597851110001cf62488ae670d840d34a13bd196007d31fcfa7')
vehicle_start = [-2.251116, 53.480399] # in lon, lat format

m = folium.Map(location=(vehicle_start[1], vehicle_start[0]), tiles="cartodbpositron", zoom_start=14)
for coord in coords:
    folium.Marker(location=(coord[1],coord[0])).add_to(m)
    
folium.Marker(location=list(reversed(vehicle_start)), icon=folium.Icon(color="red")).add_to(m)


vehicles = [
    ors.optimization.Vehicle(id=0, profile='driving-car', start=vehicle_start, end=vehicle_start, capacity=[5]),
    ors.optimization.Vehicle(id=1, profile='driving-car', start=vehicle_start, end=vehicle_start, capacity=[5])
]
jobs = [ors.optimization.Job(id=index, location=coords, amount=[1]) for index, coords in enumerate(coords)]
optimized = client.optimization(jobs=jobs, vehicles=vehicles, geometry=True)
line_colors = ['green', 'orange', 'blue', 'yellow']
for route in optimized['routes']:
    print(route['cost'])
    df['cost']+=route['cost']
    df['distance']+=route['distance']
    df['duration']+=route['duration']
    folium.PolyLine(locations=[list(reversed(coords)) for coords in ors.convert.decode_polyline(route['geometry'])['coordinates']], color=line_colors[route['vehicle']]).add_to(m)
m.save("./static/optimization.html")

# {'vehicle': 1, 'cost': 827, 'delivery': [3], 'amount': [3], 'pickup': [0], 'setup': 0, 'service': 0, 'duration': 827, 'waiting_time': 0, 'priority': 0, 'distance': 5235, 'steps': [{'type': 'start', 'location': [-2.251116, 53.480399], 'setup': 0, 'service': 0, 'waiting_time': 0, 'load': [3], 'arrival': 0, 'duration': 0, 'violations': [], 'distance': 0}, {'type': 'job', 'location': [-2.239761, 53.479642], 'id': 3, 'setup': 0, 'service': 0, 'waiting_time': 0, 'job': 3, 'load': [2], 'arrival': 188, 'duration': 188, 'violations': [], 'distance': 1181}, {'type': 'job', 'location': [-2.241995, 53.486725], 'id': 4, 'setup': 0, 'service': 0, 'waiting_time': 0, 'job': 4, 'load': [1], 'arrival': 386, 'duration': 386, 'violations': [], 'distance': 2332}, {'type': 'job', 'location': [-2.260269, 53.481413], 'id': 5, 'setup': 0, 'service': 0, 'waiting_time': 0, 'job': 5, 'load': [0], 'arrival': 664, 'duration': 664, 'violations': [], 'distance': 4293}, {'type': 'end', 'location': [-2.251116, 53.480399], 'setup': 0, 'service': 0, 'waiting_time': 0, 'load': [0], 'arrival': 827, 'duration': 827, 'violations': [], 'distance': 5235}], 'violations': []}