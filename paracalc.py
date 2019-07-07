import math

def generate_arc(iterations, radius, height):
    # Generates points along the circumference of an ellipse with equal radial spacing
    arc = [] #(distance_along_arc, x_coordinate)
    inner_circle = min(height, radius)
    outer_circle = max(height, radius)
    
    prev_x = outer_circle
    prev_y = 0
    arc_length = 0
    
    # Use the concentric circle method to generate points with equal radial spacing
    # Equal radial spacing is close to equal spacing along the arc for ellipses with low eccentricity
    for i in range(iterations):
        y = inner_circle * math.sin(i * angle_increment)
        x = outer_circle * math.cos(i * angle_increment)
        arc_length += math.hypot(x-prev_x, y-prev_y)
        arc.append((arc_length, x))
        prev_x = x
        prev_y = y
    
    return arc

def generate_lines(arc, num_line_segments, num_gores):
    # Gets points with equal spacing along the arc and calculates their respective gore widths
    line_segments = [] #(distance_along_arc, width_of_gore/2)
    segment_length = arc[len(arc) - 1][0] / num_line_segments # Length of one line segment
    gore_circumference_ratio = math.pi/num_gores

    arc_index = 0
    for i in range(num_line_segments):
        while arc[arc_index][0] < segment_length * i:
            arc_index += 1
        line_segments.append((arc[arc_index][0], gore_circumference_ratio * arc[arc_index][1]**2))
    line_segments.append((arc[len(arc) - 1][0], 0))

    return line_segments

radius = 1
height = radius / math.sqrt(2)
num_gores = 12
num_line_segments = 100

iterations = 100000
angle_increment = math.pi / (2 * iterations)

arc = generate_arc(iterations, radius, height) #(distance_along_arc, x_coordinate)
line_segments = generate_lines(arc, num_line_segments, num_gores) #(distance_along_arc, width_of_gore/2)

print(line_segments)
print(len(line_segments))
