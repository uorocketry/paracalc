import argparse
import math
import os
import reportlab
from reportlab.pdfgen import canvas

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


def generate_lines(arc, spillhole_radius, num_line_segments, num_gores):
    # Gets points with equal spacing along the arc and calculates their respective gore widths
    line_segments = [] #(distance_along_arc, width_of_gore/2)
    segment_length = arc[len(arc) - 1][0] / (num_line_segments + 1) # Length of one line segment
    gore_circumference_ratio = math.pi/num_gores

    arc_index = 0
    for i in range(num_line_segments):
        while arc[arc_index][0] < segment_length * i:
            arc_index += 1
            if spillhole_radius >= arc[arc_index][1]:
                # Stop at specified spillhole diameter
                line_segments.append((arc[arc_index][0], gore_circumference_ratio * arc[arc_index][1]))
                return line_segments
        line_segments.append((arc[arc_index][0], gore_circumference_ratio * arc[arc_index][1]))

    # No spillhole
    # Set tip x coordinate to zero to ensure that the gore lines form a closed loop
    line_segments.append((arc[len(arc) - 1][0], 0))
    return line_segments


def generate_gore(iterations, diameter, spillhole_diameter, height, num_lines, num_gores, margins, file_path):
    # margins (top, bottom, left, right)
    print('Generating gore: diameter={0}cm, spillhole diameter={1}cm, height={2}cm, gores={3}, lines={4}, iterations={5}'.format(round(diameter, 2), round(spillhole_diameter, 2), round(height, 2), num_gores, num_lines, iterations))
    
    arc = generate_arc(iterations, diameter / 2, height) #(distance_along_arc, x_coordinate)
    line_segments = generate_lines(arc, spillhole_diameter / 2, num_lines, num_gores) #(distance_along_arc, width_of_gore/2)

    # Scale line segments from cm to points
    cm_to_point = 28.346456693
    for i in range(len(line_segments)):
        line_segments[i] = (cm_to_point * line_segments[i][0], cm_to_point * line_segments[i][1])
    margins = tuple(cm_to_point*margin for margin in margins)
    gore_radius = line_segments[0][1]

    # Size canvas
    c = canvas.Canvas(file_path, pagesize=(
        gore_radius * 2 + margins[2] + margins[3], 
        line_segments[len(line_segments) - 1][0] + margins[0] + margins[1]))
    
    # Draw lines
    for i in range(len(line_segments) - 1):
        c.line(
            gore_radius + line_segments[i][1] + margins[2], line_segments[i][0] + margins[1],
            gore_radius + line_segments[i+1][1] + margins[2], line_segments[i+1][0] + margins[1])
    for i in range(len(line_segments) - 1):
        c.line(
            gore_radius - line_segments[i][1] + margins[2], line_segments[i][0] + margins[1],
            gore_radius - line_segments[i+1][1] + margins[2], line_segments[i+1][0] + margins[1])
    c.line(
        gore_radius - line_segments[0][1] + margins[2], line_segments[0][0] + margins[1],
        gore_radius + line_segments[0][1] + margins[2], line_segments[0][0] + margins[1])
    if spillhole_diameter > 0:
        c.line(
            gore_radius - line_segments[len(line_segments) - 1][1] + margins[2], line_segments[len(line_segments) - 1][0] + margins[1],
            gore_radius + line_segments[len(line_segments) - 1][1] + margins[2], line_segments[len(line_segments) - 1][0] + margins[1])

    try:
        c.save()
        print('file saved to {0}'.format(file_path))
    except:
        print('error saving file to {0}'.format(file_path))


def parse_args():
    parser = argparse.ArgumentParser(description='Generate parachute gores')

    parser.add_argument('diameter', type=float, help='canopy diameter (measured in cm across the inflated canopy bottom)')
    parser.add_argument('spillhole', type=float, help='spillhole diameter (measured in cm across the inflated canopy spillhole)')
    parser.add_argument('gores', type=int, help='number of gores')
    parser.add_argument('-t', type=float, help='canopy height (measured in cm from canopy top to bottom, ignoring spillhole size)', dest='height', default=-1)
    parser.add_argument('-l', type=int, help='number of line segments per side of gore', dest='lines', default=100)
    parser.add_argument('-i', type=int, help='total iterations used to approximate ellipse arc segments', dest='iterations', default=100000)
    parser.add_argument('-o', type=str, help='output file', dest='output', default='template.pdf')
    parser.add_argument('-m', type=float, nargs='+', help='page margins in cm (top bottom left right)', dest='margins', default=[2,2,2,2])

    args = parser.parse_args()
    height = 0
    if args.diameter <= 0:
        print('error: argument diameter: diameter must be greater than zero')
        return
    if args.spillhole < 0:
        print('error: argument spillhole: diameter can not be negative')
        return
    if args.spillhole >= args.diameter:
        print('error: argument spillhole: spillhole diameter must be less than canopy diameter')
        return
    if args.gores <= 0:
        print('error: argument gores: number of gores must be greater than zero')
        return
    if args.height <= 0:
        print('canopy height set to radius/sqrt(2)')
        height = args.diameter / (2 * math.sqrt(2))
    if args.lines <= 0:
        print('error: argument lines: number of lines must be greater than zero')
        return
    if args.iterations <= 0:
        print('error: argument iterations: iterations must be greater than zero')
        return
    if not len(args.margins) == 4:
        print('error: argument margins: four margins must be specified')
        return
    for margin in args.margins:
        if margin < 0:
            print('error: argument margins: margins can not be negative')
            return

    file_path = ''
    if os.path.isabs(args.output):
        file_path = args.output
    else:
        file_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), args.output)
    if not os.path.exists(os.path.dirname(file_path)):
        print('error: argument output: invalid output file')
        return

    generate_gore(args.iterations, args.diameter, args.spillhole, height, args.lines, args.gores, tuple(args.margins), file_path)


parse_args()
