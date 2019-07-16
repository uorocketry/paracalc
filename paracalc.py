import argparse
import math
import os
import reportlab
from reportlab.pdfgen import canvas


class LineGenerator(object):
    def __init__(self, arc, spillhole_radius, num_line_segments, num_gores, margins):
        self.arc = arc
        self.spillhole_radius = spillhole_radius
        self.num_line_segments = num_line_segments
        self.num_gores = num_gores
        self.margins = margins
        self.circumference_ratio = math.pi/num_gores
        self.page_centerline = self.circumference_ratio * arc[0][1] + margins[2]


    def get_line_point(self, arc_index):
        return (self.circumference_ratio * self.arc[arc_index][1], self.arc[arc_index][0] + self.margins[1])


    def add_line(self, lines_left, lines_right, arc_index):
        point = self.get_line_point(arc_index)
        # Points on each side are stored in opposite order so the left side can be reversed when forming a continuous
        lines_left.append((self.page_centerline - point[0], point[1], lines_left[-1][0], lines_left[-1][1]))
        lines_right.append((lines_right[-1][2], lines_right[-1][3], self.page_centerline + point[0], point[1]))


    def merge_line_sides(self, lines_left, lines_right):
        lines_left.reverse()
        return lines_left + [(lines_left[-1][2], lines_left[-1][3], lines_right[0][0], lines_right[0][1])] + lines_right


    def generate_lines(self):
        # Gets points with equal spacing along the arc and calculates their respective gore widths
        segment_length = self.arc[-1][0] / (self.num_line_segments + 1) # Length of one line segment
        arc_index = 0

        while self.arc[arc_index][0] < segment_length:
            arc_index += 1
        origin_point = self.get_line_point(0)
        first_point = self.get_line_point(arc_index)
        lines_left = [(self.page_centerline - first_point[0], first_point[1], self.page_centerline - origin_point[0], origin_point[1])] # (width_of_gore/2, distance_along_arc)
        lines_right = [(self.page_centerline + origin_point[0], origin_point[1], self.page_centerline + first_point[0], first_point[1])]
        self.width = origin_point[0] * 2

        for i in range(1, self.num_line_segments):
            while self.arc[arc_index][0] < segment_length * i:
                arc_index += 1
                if self.spillhole_radius >= self.arc[arc_index][1]:
                    # Stop at specified spillhole diameter
                    self.add_line(lines_left, lines_right, arc_index)
                    # Merge sides and add top cap for spillhole
                    self.height = self.arc[arc_index][0]
                    return self.merge_line_sides(lines_left, lines_right) + [(lines_left[0][0], lines_left[0][1], lines_right[-1][2], lines_right[-1][3])]
            self.add_line(lines_left, lines_right, arc_index)

        # No spillhole
        # Set tip x coordinate to zero to ensure that the gore lines form a closed loop
        self.add_line(lines_left, lines_right, len(self.arc) - 1)
        self.height = self.arc[-1][0]
        return self.merge_line_sides(lines_left, lines_right)
    

    def offset_lines(self, lines, offset):
        return 0


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


def generate_gore(iterations, diameter, spillhole_diameter, height, num_lines, num_gores, margins, file_path):
    # margins (top, bottom, left, right)
    print('generating gore: diameter = {0}cm, spillhole diameter = {1}cm, height = {2}cm, gores = {3}, lines = {4}, iterations = {5}'.format(round(diameter, 2), round(spillhole_diameter, 2), round(height, 2), num_gores, num_lines, iterations))
    
    # Convert from cm to points
    cm_to_point = 28.346456693
    diameter *= cm_to_point
    spillhole_diameter *= cm_to_point
    height *= cm_to_point
    margins = tuple(cm_to_point*margin for margin in margins)

    arc = generate_arc(iterations, diameter / 2, height) #(distance_along_arc, x_coordinate)
    line_generator = LineGenerator(arc, spillhole_diameter / 2, num_lines, num_gores, margins)
    line_segments = line_generator.generate_lines()

    # Size canvas and draw lines
    c = canvas.Canvas(file_path, pagesize=(
        margins[2] + line_generator.width + margins[3], 
        margins[0] + line_generator.height + margins[1]))
    c.lines(line_segments)

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
    parser.add_argument('-i', type=int, help='total iterations used to approximate ellipse arc segments', dest='iterations', default=10000)
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
    if args.lines <= 0:
        print('error: argument lines: number of lines must be greater than zero')
        return
    if args.iterations <= 1:
        print('error: argument iterations: iterations must be greater than one')
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
    if args.height <= 0:
        print('canopy height set to radius/sqrt(2)')
        height = args.diameter / (2 * math.sqrt(2))

    generate_gore(args.iterations, args.diameter, args.spillhole, height, args.lines, args.gores, tuple(args.margins), file_path)


parse_args()
