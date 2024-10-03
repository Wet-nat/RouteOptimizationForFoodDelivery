# Importing Modules
import numpy as np
import random
# Use 'conda install shapely' to import the shapely library.
from shapely.geometry import Polygon, Point

class Cluster():
    def __init__(self):
        self.poly = Polygon([(53.515600,-2.281657), (53.528663,-2.233561), (53.504783,-2.179330),(53.472090,-2.163426), (53.447070,-2.180518), (53.435209,-2.240983), (53.462198,-2.320686) ])

    def polygon_random_points (self, poly, num_points):
        min_x, min_y, max_x, max_y = poly.bounds
        points = []
        while len(points) < num_points:
                random_point = Point([random.uniform(min_x, max_x), random.uniform(min_y, max_y)])
                if (random_point.within(poly)):
                    points.append(random_point)
        return points

    def reverse_coords(self, coords):
        nl = []
        for c in coords:
            nl.append(c[::-1])
        return nl

    
    
