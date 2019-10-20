import math


def generate_arc(iterations, radius, height):
    # Generates points along the circumference of an ellipse with equal radial spacing
    arc = [] #(distance_along_arc, x_coordinate)
    inner_circle_radius = min(height, radius)
    outer_circle_radius = max(height, radius)
    angle_increment = math.pi / (2 * (iterations - 1))
    prev_x = outer_circle_radius
    prev_y = 0
    arc_length = 0
    
    # Use the concentric circle method to generate points with equal radial spacing
    # Equal radial spacing is close to equal spacing along the arc for ellipses with low eccentricity
    for i in range(iterations):
        y = inner_circle_radius * math.sin(i * angle_increment)
        x = outer_circle_radius * math.cos(i * angle_increment)
        arc_length += math.hypot(x-prev_x, y-prev_y)
        arc.append((arc_length, x))
        prev_x = x
        prev_y = y
    
    return arc
    