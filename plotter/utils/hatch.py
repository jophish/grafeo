from plotter.generators.Line import Line
from shapely.geometry import LineString, MultiPolygon, MultiLineString
from shapely.ops import polygonize, unary_union
from shapely import affinity
from py5 import Py5Vector
import more_itertools


# Makes a potentially non-simple polygon out of two lines
def make_multi_polygon_from_lines(line_a: Line, line_b: Line) -> LineString:
    points = line_a.get_points() + list(reversed(line_b.get_points()))
    ls = LineString(points)
    lr = LineString(ls.coords[:] + ls.coords[0:1])
    mls = unary_union(lr)
    return MultiPolygon(list(polygonize(mls)))

# From https://gist.github.com/NelsonMinar/16b876fb74ecbdac0431288e8f5ae7b9
def hatch_lines(line_a: Line, line_b: Line, pen_num: int, spacing: float = 10, rotation: float = 45, tolerance: float = 5, inset: float = 0) -> list[Line]:
    multi_poly = make_multi_polygon_from_lines(line_a, line_b)
    hatch_results = []
    lines = []
    for polygon in multi_poly.geoms:
        poly_hatch_results = hatch(polygon, spacing, rotation, tolerance, inset)
        hatch_results.append(poly_hatch_results)
        for ls in poly_hatch_results.geoms:
            coords = list(ls.coords)
            lines.append(
                Line([Py5Vector(coord[0], coord[1]) for coord in coords], pen_num)
            )
    return lines

def hatch(polygon, spacing: float = 1, rotation: float = 0, tolerance: float = 5, inset: float = 0) -> MultiLineString:
	"""
        Fill a polygon with hatched lines.
	Note this code is unit-independent. The default spacing of 1 was chosen with the idea of the units being
	millimeters and the pen width being 0.5mm, for a 50% fill.

        :param polygon: the shape to generate a hatch for
        :param spacing: space between hatch lines
        :param rotation: rotation of hatch lines (in degrees)
        :param tolerance: limit on length of joining lines to make hatches a single line. Multiples of spacing.
	:param inset: absolute amount of spacing to give inside the polygon before hatch lines. Can be negative.
        :return: a collection of lines that represent the hatching
        """
	hatch_polygon = polygon
	if inset != 0:
		hatch_polygon = polygon.buffer(-inset)
	# Make a square big enough to cover the whole object, even when rotated 45 degrees.
	# sqrt(2) should be big enough but it seemed wise to pad this out a bit
	hatch_box = affinity.scale(hatch_polygon, 1.6, 1.6)
	xmin, ymin, xmax, ymax = hatch_box.bounds  # type:ignore

	# Draw horizontal lines to fill the box
	lines = tuple(((xmin, y), (xmax, y)) for y in more_itertools.numeric_range(ymin, ymax, spacing))
	mls = MultiLineString(lines)

	# Rotate the lines
	mls = affinity.rotate(mls, rotation)

	# And intersect them with the polygon
	cropped = mls.intersection(hatch_polygon)

	# Now try to merge the lines boustrophedonically. This algorithm relies on the lines being sorted nicely by
	# intersection(). It does not work on messy polygons: concave or those with holes. The intersection operation
	# seems to mostly preserve ordering of the line collection but if it has to break a line it seems to insert new
	# lines in-place when putting them at the end would be more helpful to this algorithm. I think complex polyognos
	# could be supported by making the code actually search for the closest next line to join to, instead of relying
	# on intersection() returning lines in a useful order. for the small number of lines a simple scan would
	# probably work. Optimizations would be to counter-rotate the lines back to horizontal and sort by Y, or maybe
	# build a full spatial index.
	lines = list(cropped.geoms)  # type: ignore
	merged = []  # collection of new merged lines
	to_merge = list(lines[0].coords)  # accumulate the next new merged line here
	which_end = 1  # whether we're at the left end of the line or the right
	join_limit = (spacing * tolerance)**2  # squared to avoid sqrt in distance calculation
	for line in lines[1:]:
		# Endpoint of the previous line we're building up
		old_x, old_y = to_merge[-1]
		# New candidate line and the point we're considering merging in
		lc = line.coords
		new_x, new_y = lc[which_end]
		# Check the distance of the new candidate joining line
		if ((new_x - old_x)**2 + (new_y - old_y)**2) < join_limit:
			# Small enough? Attach candidate line to the line we're building
			to_merge.append((new_x, new_y))
			to_merge.append(lc[1 - which_end])
		else:
			# Too far away; start a new line
			merged.append(to_merge)
			to_merge = list(lc)
		which_end = 1 - which_end  # turn the ox around
	merged.append(to_merge)  # bring in the final line

	# print(f'{len(merged)} lines in hatch pattern')
	# And return the hatch lines as a collection
	return MultiLineString(merged)
