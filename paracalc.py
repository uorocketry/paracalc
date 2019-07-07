import argparse
import math


def generate_arc(iterations, radius, height):
    # Generates points along the circumference of an ellipse with equal radial spacing
    arc = [] #(distance_along_arc, x_coordinate)
    inner_circle = min(height, radius)
    outer_circle = max(height, radius)
    
    angle_increment = math.pi / (2 * iterations)
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


def generate_gore(iterations, diameter, height, num_lines, num_gores):
    print('Generating gore: diameter={0}, height={1}, gores={2}, lines={3}, iterations={4}'.format(diameter, height, num_gores, num_lines, iterations))
    
    arc = generate_arc(iterations, diameter / 2, height) #(distance_along_arc, x_coordinate)
    line_segments = generate_lines(arc, num_lines, num_gores) #(distance_along_arc, width_of_gore/2)

    print(line_segments)
    print(len(line_segments))


def parse_args():
    parser = argparse.ArgumentParser(description='Generate parachute gores')

    parser.add_argument('diameter', type=float, help='Canopy diameter (measured across the inflated canopy bottom).')
    parser.add_argument('gores', type=int, help='Number of gores.')
    parser.add_argument('-t', type=float, help='Canopy height (measured from canopy top to bottom, ignoring spillhole size).', dest='height', default=-1)
    parser.add_argument('-l', type=int, help='Number of line segments per side of gore.', dest='lines', default=100)
    parser.add_argument('-i', type=int, help='Total iterations used to approximate ellipse arc segments', dest='iterations', default=100000)

    args = parser.parse_args()
    height = 0
    if args.diameter <= 0:
        print('error: argument diameter: diameter must be greater than zero')
        return
    if args.gores <= 0:
        print('error: argument gores: number of gores must be greater than zero')
        return
    if args.height <= 0:
        print('canopy height set to radius/sqrt(2)')
        height = args.diameter / 2*math.sqrt(2)
    if args.lines <= 0:
        print('error: argument lines: number of lines must be greater than zero')
        return
    if args.iterations <= 0:
        print('error: argument iterations: iterations must be greater than zero')
        return

    generate_gore(args.iterations, args.diameter, height, args.lines, args.gores)


parse_args()
