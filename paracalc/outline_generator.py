import math

class LineGenerator:
    def __init__(self, arc, spillhole_radius, num_line_segments, num_gores, margins):
        self.arc = arc
        self.spillhole_radius = spillhole_radius
        self.num_line_segments = num_line_segments
        self.num_gores = num_gores
        self.margins = margins
        self.circumference_ratio = math.pi/num_gores
        self.page_centerline = self.circumference_ratio * arc[0][1] + margins[2]


    def create_template(self):
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

        i = 2
        while True:
            i += 1
            while self.arc[arc_index][0] < segment_length * i:
                if self.spillhole_radius >= self.arc[arc_index][1]:
                    # Stop at specified spillhole diameter
                    self.add_line(lines_left, lines_right, arc_index)
                    # Merge sides and add top cap for spillhole
                    self.height = self.arc[arc_index][0]
                    return self.merge_line_sides(lines_left, lines_right, True)
                arc_index += 1
                if arc_index >= len(self.arc):
                    # Stop at last point (no spillhole)
                    # Set tip x coordinate to zero to ensure that the gore lines form a closed loop
                    del lines_left[-1]
                    del lines_right[-1]
                    self.add_line(lines_left, lines_right, len(self.arc) - 1)
                    self.height = self.arc[-1][0]
                    return self.merge_line_sides(lines_left, lines_right, False)
            self.add_line(lines_left, lines_right, arc_index)


    def create_outline(self, offset):
        outline = []
        # Move all line segments outwards by specified offset
        for line in self.template:
            # Get scaled normal
            norm = [line[3] - line[1], line[0] - line[2]]
            length = math.hypot(norm[0], norm[1])
            if length != 0:
                scale = -offset / length
                norm = [norm[0] * scale, norm[1] * scale]
                # Move line points along normal
                outline.append([line[0] + norm[0], line[1] + norm[1], line[2] + norm[0], line[3] + norm[1]])
            else:
                # Ignore a zero length line
                # This is probably caused by a very tiny spillhole
                self.spillhole_radius = 0

        # Add top cap if no spillhole exists
        if self.spillhole_radius <= 0:
            cap_height = self.template[0][1] + offset
            outline.append([1, cap_height, 0, cap_height])

        # Determine line intersections and connect endpoints
        for i in range(len(outline)):
            second_line_index = (i+1)%len(outline)
            intersection = self.line_intersection(outline[i], outline[second_line_index])
            outline[i][2] = outline[second_line_index][0] = intersection[0]
            outline[i][3] = outline[second_line_index][1] = intersection[1]

        self.outline = outline
        return self.outline


    def get_line_point(self, arc_index):
            return (self.circumference_ratio * self.arc[arc_index][1], self.arc[arc_index][0] + self.margins[1])


    def add_line(self, lines_left, lines_right, arc_index):
        point = self.get_line_point(arc_index)
        # Points on each side are stored in opposite order so the left side can be reversed when forming a continuous
        lines_left.append((self.page_centerline - point[0], point[1], lines_left[-1][0], lines_left[-1][1]))
        lines_right.append((lines_right[-1][2], lines_right[-1][3], self.page_centerline + point[0], point[1]))


    def merge_line_sides(self, lines_left, lines_right, cap_top):
        lines_left.reverse()
        self.template = lines_left + [(lines_left[-1][2], lines_left[-1][3], lines_right[0][0], lines_right[0][1])] + lines_right
        if cap_top:
            self.template += [(lines_right[-1][2], lines_right[-1][3], lines_left[0][0], lines_left[0][1])]
        return self.template


    def det(self, a, b):
        return a[0]*b[1] - a[1]*b[0]


    def line_intersection(self, line1, line2):
        dx = (line1[0] - line1[2], line2[0] - line2[2])
        dy = (line1[1] - line1[3], line2[1] - line2[3])
        div = self.det(dx, dy)
        d = (self.det(line1[:2], line1[2:]), self.det(line2[:2], line2[2:]))
        return (self.det(d, dx) / div, self.det(d, dy) / div)
