from flask import Blueprint, render_template, request
import folium
from clustering import Cluster
from shapely.geometry import Polygon
from sklearn.cluster import SpectralClustering, KMeans
import openrouteservice as ors
import pandas as pd

views = Blueprint(__name__, "views")

# Global Varibles
c = Cluster()
poly = Polygon([(53.515600,-2.281657), (53.528663,-2.233561), (53.504783,-2.179330),(53.472090,-2.163426), (53.447070,-2.180518), (53.435209,-2.240983), (53.462198,-2.320686)])
global global_coords
num_of_nodes = 10
# client = ors.Client(key='5b3ce3597851110001cf62488ae670d840d34a13bd196007d31fcfa7')
client = ors.Client(key='5b3ce3597851110001cf624839cd880da41445a894ef4137d7bf96bb')
num_of_vehicle = 3
pin_colors = [
    'blue',
    'gray',
    'darkred',
    'lightred',
    'orange',
    'beige',
    'green',
    'darkgreen',
    'lightgreen',
    'darkblue',
    'lightblue',
    'purple',
    'darkpurple',
    'pink',
    'cadetblue',
    'lightgray',
    'black'
]
zoom = 13
data = {'cost': [0], 'distance': [0], 'duration': [0]}
df = pd.DataFrame(data)
dfv = pd.DataFrame(data)

# Use for Testing Purpose
@views.route("/test.html")
def test():
    return render_template("test.html")

# Index Page
@views.route("/")
def home():
    global df, dfv
    m = folium.Map(location=(53.480399, -2.251116), tiles="openstreetmap", zoom_start=zoom)
    m.save("./static/map.html")
    # m.save("./static/randompoints.html")
    return render_template("index.html", dfMy=df, dfvrm=dfv, mapSrc = "./static/map.html", method = "(not optimized yet)")

# Generate random points on the map
@views.route("/generate", methods=['GET', 'POST'])
def generate():
    global global_coords
    global num_of_vehicle, dfv, df, num_of_nodes, data
    df = pd.DataFrame(data)
    dfv = pd.DataFrame(data)
    if request.method == "POST":
        num_of_nodes = int(request.form.get("numberOfNodes"))
        num_of_vehicle = int(request.form.get("numberOfDrivers"))
    points = c.polygon_random_points(poly, num_of_nodes)
    # Printing the results.
    coords = []
    for p in points:
        coords.append([p.x, p.y])

    coords = c.reverse_coords(coords)
    # visualize the points on a map
    m = folium.Map(location=(53.480399, -2.251116), tiles="openstreetmap", zoom_start=zoom)
    for coord in coords:
        folium.Marker(location=(coord[1],coord[0])).add_to(m)
    m.save("./static/randompoints.html")
    global_coords = coords
    print("Random map saved")
    return render_template("index.html", dfMy=df, dfvrm=dfv, mapSrc="./static/randompoints.html", method = "(not optimized yet)")

# Show the optimized Route with Spectral Clustering
@views.route('/routeOptimizationS', methods=['GET', 'POST'])
def routeOptimizationS():
    global global_coords, df, dfv, num_of_vehicle
    clusters_label = SpectralClustering(num_of_vehicle).fit_predict(global_coords)
    clustered_coords = get_clusters(clusters_label)
    # num_of_vehicles = 3
    m, df2 = optimization(clustered_coords, num_of_vehicle, num_of_nodes)
    print('OPTIMIZING')
    m.save("./static/optimizationS.html")
    print('Optimization Map Saved')
    df = df2
    print("My Optimization Cost", df2['cost'][0])
    return render_template("index.html", dfMy=df2, dfvrm=dfv, mapSrc="./static/optimizationS.html", method = "Spectral")

# Show the optimized Route with Knn Clustering
@views.route('/routeOptimizationK', methods=['GET', 'POST'])
def routeOptimizationK():
    global global_coords, df, dfv
    kmeans = KMeans(
    init="random",
    n_clusters=3,
    n_init=10,
    max_iter=300,
    random_state=42
    )
    features = pd.DataFrame(global_coords)
    # do clustering
    kmeans.fit(features)
    # save results
    labels = kmeans.labels_

    clustered_coords = get_clusters(labels)
    num_of_vehicles = 3
    m, df2 = optimization(clustered_coords, num_of_vehicles, num_of_nodes)
    print('OPTIMIZING')
    m.save("./static/optimizationK.html")
    print('Optimization Map Saved')
    df = df2
    print("My Optimization Cost", df2['cost'][0])
    return render_template("index.html", dfMy=df2, dfvrm=dfv, mapSrc="./static/optimizationK.html", method = "Knn")

# Show the optimized Route Using Vroom
@views.route('/routeOptimizationVroom', methods=['GET', 'POST'])
def routeOptimizationVroom():
    global global_coords, dfv, df
    mv, dfvs = optimization2(global_coords, num_of_vehicle, num_of_nodes)
    mv.save("./static/optimizationVroom.html")
    dfv=dfvs
    print("VROOM Optimization Cost", dfv['cost'][0])
    return render_template("index.html", dfMy=df, dfvrm=dfv, mapSrc="./static/optimizationVroom.html", method = "(not optimized yet)")
   
# Function translate labels to sets of coordinates
def get_clusters(clusters_label):
    c = [[] for _ in range(clusters_label.max()+1)]
    for i in range(len(clusters_label)):
        c[clusters_label[i]].append(global_coords[i])  
    return c

# Show the Spectral Clusters
@views.route('/showSpectral', methods=['GET', 'POST'])
def showSpectral():
    global global_coords, df, dfv, num_of_vehicle
    clusters_label = SpectralClustering(num_of_vehicle).fit_predict(global_coords)
    clustered_coords = get_clusters(clusters_label)
    vehicle_start = [-2.251116, 53.480399] # in lon, lat format
    m = folium.Map(location=(vehicle_start[1], vehicle_start[0]), tiles="openstreetmap", zoom_start=zoom)
    for index, coords in enumerate(clustered_coords):
        for coord in coords:
            folium.Marker(location=(coord[1],coord[0]), icon=folium.Icon(color=pin_colors[index])).add_to(m)
    m.save("./static/Spectral.html")
    print('spectral cluster saved')
    # return {'result': 'success'}
    return render_template("index.html", dfMy=df, dfvrm=dfv, mapSrc="./static/Spectral.html", method = "(not optimized yet)")

# Show the Sweep Clusters
@views.route('/showKnn')
def showKnn():
    global global_coords
    kmeans = KMeans(
    init="random",
    n_clusters=3,
    n_init=10,
    max_iter=300,
    random_state=42
    )
    features = pd.DataFrame(global_coords)
    # do clustering
    kmeans.fit(features)
    # save results
    labels = kmeans.labels_
    clustered_coords = get_clusters(labels)
    vehicle_start = [-2.251116, 53.480399] # in lon, lat format
    m = folium.Map(location=(vehicle_start[1], vehicle_start[0]), tiles="openstreetmap", zoom_start=zoom)
    for index, coords in enumerate(clustered_coords):
        for coord in coords:
            folium.Marker(location=(coord[1],coord[0]), icon=folium.Icon(color=pin_colors[index])).add_to(m)

    m.save("./static/Knn.html")
    print('Knn cluster saved')
    # return {'result': 'success'}
    return render_template("index.html", dfMy=df, dfvrm=dfv, mapSrc="./static/Knn.html", method = "(not optimized yet)")

# Function to optimze the route with clusters
def optimization(coords_list :list, vehicle_num: int, capacity: int):
    print('Enter optimization')
    # Create a DataFrame with three columns and set initial values to 0
    data = {'cost': [0], 'distance': [0], 'duration': [0]}
    df = pd.DataFrame(data)
    line_colors = ['green', 'black', 'blue', 'red']

    # client = ors.Client(key='5b3ce3597851110001cf62488ae670d840d34a13bd196007d31fcfa7')
    client = ors.Client(key='5b3ce3597851110001cf624839cd880da41445a894ef4137d7bf96bb')
    vehicle_start = [-2.251116, 53.480399] # in lon, lat format

    m = folium.Map(location=(vehicle_start[1], vehicle_start[0]), tiles="openstreetmap", zoom_start=zoom)
    for index, coords in enumerate(coords_list):
        for coord in coords:
            folium.Marker(location=(coord[1],coord[0]), icon=folium.Icon(color=pin_colors[index])).add_to(m)

    folium.Marker(location=list(reversed(vehicle_start)), icon=folium.Icon(color="red")).add_to(m)

    vehicles = []
    for v in range(vehicle_num):
        vehicles.append(ors.optimization.Vehicle(id=v, profile='driving-car', start=vehicle_start,  capacity=[capacity]))
    for ind, coords in enumerate(coords_list):

        jobs = [ors.optimization.Job(id=index, location=coords, amount=[1]) for index, coords in enumerate(coords)]
        optimized = client.optimization(jobs=jobs, vehicles=vehicles, geometry=True)
    
        for route in optimized['routes']:
            # print(route['cost'])
            df['cost']+=route['cost']
            df['distance']+=route['distance']
            df['duration']+=route['duration']
            folium.PolyLine(locations=[list(reversed(coords)) for coords in ors.convert.decode_polyline(route['geometry'])['coordinates']], color=line_colors[route['vehicle']]).add_to(m)
    # m.save("./static/optimization.html")
    return m, df

# Function to optimze the route
def optimization2(coords, vehicle_num: int, capacity: int):
    # Create a DataFrame with three columns and set initial values to 0
    data = {'cost': [0], 'distance': [0], 'duration': [0]}
    df = pd.DataFrame(data)
    client = ors.Client(key='5b3ce3597851110001cf624839cd880da41445a894ef4137d7bf96bb')
    # client = ors.Client(key='5b3ce3597851110001cf62488ae670d840d34a13bd196007d31fcfa7')
    vehicle_start = [-2.251116, 53.480399] # in lon, lat format

    m = folium.Map(location=(vehicle_start[1], vehicle_start[0]), tiles="openstreetmap", zoom_start=zoom)
    for coord in coords:
        folium.Marker(location=(coord[1],coord[0])).add_to(m)
        
    folium.Marker(location=list(reversed(vehicle_start)), icon=folium.Icon(color="red")).add_to(m)
    vehicles = []
    for v in range(vehicle_num):
        vehicles.append(ors.optimization.Vehicle(id=v, profile='driving-car', start=vehicle_start,  capacity=[capacity]))
    jobs = [ors.optimization.Job(id=index, location=coords, amount=[1]) for index, coords in enumerate(coords)]
    optimized = client.optimization(jobs=jobs, vehicles=vehicles, geometry=True)
    line_colors = ['green', 'orange', 'blue', 'yellow', 'black']
    for route in optimized['routes']:
        # print(route['cost'])
        df['cost']+=route['cost']
        df['distance']+=route['distance']
        df['duration']+=route['duration']
        folium.PolyLine(locations=[list(reversed(coords)) for coords in ors.convert.decode_polyline(route['geometry'])['coordinates']], color=line_colors[route['vehicle']]).add_to(m)
    return m, df