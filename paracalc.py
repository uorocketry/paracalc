import argparse
import math
import os
import reportlab
from reportlab.pdfgen import canvas

from paracalc import arc_generator
from paracalc import outline_generator

def generate_gore(iterations, diameter, spillhole_diameter, height, outline_width, num_lines, num_gores, margins, file_path):
    # margins (top, bottom, left, right)
    print('generating gore: diameter = {0}cm, spillhole diameter = {1}cm, height = {2}cm, gores = {3}, lines = {4}, iterations = {5}'.format(round(diameter, 2), round(spillhole_diameter, 2), round(height, 2), num_gores, num_lines, iterations))
    
    # Convert from cm to points
    cm_to_point = 28.346456693
    diameter *= cm_to_point
    spillhole_diameter *= cm_to_point
    height *= cm_to_point
    outline_width *= cm_to_point
    margins = tuple(cm_to_point * margin + outline_width for margin in margins)

    arc = arc_generator.generate_arc(iterations, diameter / 2, height) #(distance_along_arc, x_coordinate)
    line_generator = outline_generator.LineGenerator(arc, spillhole_diameter / 2, num_lines, num_gores, margins)
    line_generator.create_template()

    # Size canvas and draw lines
    c = canvas.Canvas(file_path, pagesize=(
        margins[2] + line_generator.width + margins[3], 
        margins[0] + line_generator.height + margins[1]))
    c.lines(line_generator.template)
    c.setDash(2, 2)
    if outline_width > 0:
        c.lines(line_generator.create_outline(outline_width))

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
    parser.add_argument('-a', type=float, help='stitching allowance in cm', dest='allowance', default=2)
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
    if args.allowance < 0:
        print('error: argument allowance: stitching allowance can not be negative')
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

    generate_gore(args.iterations, args.diameter, args.spillhole, height, args.allowance, args.lines, args.gores, tuple(args.margins), file_path)


parse_args()
