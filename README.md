# paracalc

A parachute gore template generator

## Prerequisites

Reportlab is required to generate pdf files

    pip install reportlab

## Usage

    python paracalc.py diameter spillhole gores [-h] [-t HEIGHT] [-a ALLOWANCE] [-l LINES] [-i ITERATIONS] [-o OUTPUT] [-m MARGINS [MARGINS ...]]

positional arguments:

    diameter    canopy diameter (measured in cm across the inflated canopy bottom)
    spillhole   spillhole diameter (measured in cm across the inflated canopy spillhole)
    gores       number of gores

optional arguments:

    -h, --help                  show help message and exit
    -t HEIGHT                   canopy height (measured in cm from canopy top to bottom, ignoring spillhole size)
    -a ALLOWANCE                stitching allowance in cm
    -l LINES                    number of line segments per side of gore
    -i ITERATIONS               total iterations used to approximate ellipse arc segments
    -o OUTPUT                   output file
    -m MARGINS [MARGINS ...]    page margins in cm (top, bottom, left, right)
