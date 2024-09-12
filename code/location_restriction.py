import numpy as np
import matplotlib.pyplot as plt
from shapely.geometry import Point, Polygon, MultiPolygon, LineString
from shapely.ops import unary_union

# Function to generate random circles
def generate_random_circles(postal_codes, radius):
    circles = []
    for adress in postal_codes:
        circles.append(Point(adress.longitude, adress.latitude).buffer(radius))
    return circles

# Function to merge overlapping circles into a single polygon
def merge_overlapping_circles(circles):
    return unary_union(circles)

# Function to find the nearest available edge of a polygon
def nearest_available_edge(point, polygon, circles):
    if isinstance(polygon, MultiPolygon):
        min_dist = float('inf')
        nearest_edge_point = None
        for poly in polygon.geoms:
            edges = list(poly.exterior.coords)
            for i in range(len(edges) - 1):
                edge = LineString([edges[i], edges[i+1]])
                dist = point.distance(edge)
                if dist < min_dist and not any(circle.contains(edge) for circle in circles):
                    min_dist = dist
                    nearest_edge_point = edge.interpolate(edge.project(point))
        return nearest_edge_point.coords[0]
    else:
        edges = list(polygon.exterior.coords)
        min_dist = float('inf')
        nearest_edge_point = None
        for i in range(len(edges) - 1):
            edge = LineString([edges[i], edges[i+1]])
            dist = point.distance(edge)
            if dist < min_dist and not any(circle.contains(edge) for circle in circles):
                min_dist = dist
                nearest_edge_point = edge.interpolate(edge.project(point))
        return nearest_edge_point.coords[0]

# Function to visualize circles/polygon and points
def visualize(circles, merged_polygon, green_dot, red_dot):
    fig, ax = plt.subplots()
    
    for circle in circles:
        ax.plot(*circle.exterior.xy, color='blue',fillstyle='full')
    
    if isinstance(merged_polygon, MultiPolygon):
        for poly in merged_polygon.geoms:
            ax.plot(*poly.exterior.xy, color='orange', alpha=0.5)
    else:
        ax.plot(*merged_polygon.exterior.xy, color='orange', alpha=0.5)
        
    ax.plot(*green_dot.xy, marker='o', markersize=10, color='green')
    ax.plot(*red_dot.xy, marker='o', markersize=8, color='red')
    
    ax.set_aspect('equal', 'box')
    ax.set_xlabel('X')
    ax.set_ylabel('Y')
    ax.set_title('Polygon, Start point, End point')
    ax.grid(True)
    
    fig.savefig(f'visualisations/circles{green_dot}.png')


def run_locating_restriction(postal_codes, radius, starting_point):
    # Parameters
    radius = radius
    postal_codes = postal_codes
    starting_point = Point(starting_point)

    # Generate random circles
    circles = generate_random_circles(postal_codes, radius)

    # Merge overlapping circles into a single polygon
    merged_polygon = merge_overlapping_circles(circles)

    # Find the nearest available edge of the merged polygon
    nearest_edge_point = nearest_available_edge(starting_point, merged_polygon, circles)

    # Visualize
    #visualize(circles, merged_polygon, starting_point, Point(nearest_edge_point))

    return nearest_edge_point