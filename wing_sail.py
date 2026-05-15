import math
import numpy as np
import scipy

from build123d import *

from common import inches, mm  # to del
from common import tube, UPos, UBox, ULocation, aluminum_angle
from vessel_base import ureg as u

panel_width_mm = 600 # mm
panel_length_mm = 1000 # mm
panel_rows = 4
panel_columns = 2
centre_spacing = 50 # mm

sail_surface_width = panel_columns * panel_length_mm + centre_spacing

def tube_sail_properties(radius) -> dict[str, float]:
    circumference = 2 * np.pi * radius
    if sail_surface_width > circumference / 2:
        return {}
    angle_rad = sail_surface_width / circumference * 2 * np.pi
    x0 = 1 * radius
    y0 = 0
    x1 = np.cos(angle_rad) * radius
    y1 = np.sin(angle_rad) * radius
    len_chord = np.sqrt((x1 - x0) ** 2 + (y1 - y0) ** 2)
    chord_centre_x = .5 * x0 + .5 * x1
    chord_centre_y = .5 * y0 + .5 * y1
    d_to_chord_centre = np.sqrt(chord_centre_x ** 2 + chord_centre_y ** 2)
    thickness = radius - d_to_chord_centre
    return locals()


class WingSail(Compound):

    def __init__(self, arc_thickness_mm=200):
        result = scipy.optimize.root_scalar(
            lambda x: tube_sail_properties(x)['thickness'] - arc_thickness_mm,
            bracket=[sail_surface_width / 2, sail_surface_width * 100])

        self.radius_mm = result.root
        self.tube_sail_props = tube_sail_properties(self.radius_mm)
        self.angle_degrees = self.tube_sail_props['angle_rad'] / (2 * math.pi) * 360

        self.panel_rows = panel_rows
        self.sail_height_mm = panel_rows * panel_width_mm
        self.sail_height = self.sail_height_mm * u.mm
        
        sail_thickness = 10 * mm

        assert self.angle_degrees < 180, (sail_width_mm, self.radius_mm)
        arc = CenterArc(
            center=(0, 0),
            radius=self.radius_mm,
            start_angle=-self.angle_degrees / 2,
            arc_size=self.angle_degrees)
        arc2 = CenterArc(
            center=(-sail_thickness, 0),
            radius=self.radius_mm,
            start_angle=self.angle_degrees / 2,
            arc_size=-self.angle_degrees)
        sail_face = extrude(
            make_face([arc,
                       Line(arc@1, arc2@0),
                       arc2,
                       Line(arc2@1, arc@0)]),
            amount=self.sail_height_mm)

        # TODO: parameterize
        plate_width = 3 * inches
        forward_offset = .5 * inches
        sail_plates = [
            Box(3 * inches, 12 * inches, 1/4 * inches).locate(Pos(forward_offset, 0, zpos))
                for zpos in np.linspace(-self.sail_height_mm / 2, self.sail_height_mm / 2, panel_rows + 1)]

        span_star = aluminum_angle(
            width=1 * u.inch,
            length=8 * u.feet,
            thickness=1/8 * u.inch).locate(
                ULocation((-arc_thickness_mm * u.mm + 1 * u.inch,
                           3 * u.inches,
                           0), (0, -90, 0)))

        span_port = aluminum_angle(
            width=1 * u.inch,
            length=8 * u.feet,
            thickness=1/8 * u.inch).locate(
                ULocation((-arc_thickness_mm * u.mm + 1 * u.inch,
                           -3 * u.inches,
                           0), (180, -90, 0)))

        super().__init__(
            children=[
                sail_face.locate(Pos(
                    forward_offset + plate_width / 2 + sail_thickness - self.radius_mm,
                    0, -self.sail_height_mm / 2)),
                span_star,
                span_port,
            ],
            color=Color((.3, .3, .8, 1.0)))
                    
        RigidJoint(
            label='mast_hole',
            to_part=self,
            joint_location=Location(
                (-arc_thickness_mm, # lift the sail up so it always sits above the upper mast
                 0,
                 0),
                (90, 180, 0)))


class WingSailUpperMast(Compound):
    mass_kg = 2 # approx!
    def __init__(self, length, pivot_length, radius, thickness):

        # sail angle is the amount by which the sail is rotated around the mast
        # i.e. by pulling the trim lines
        self.pivot_length = pivot_length
        self.upper_mast_length = length

        length_mm = length.to('mm').magnitude
        pivot_length_mm = pivot_length.to('mm').magnitude
        upper_mast_tube = tube(
            height=200, #approx
            outer_radius=radius.to('mm').magnitude,
            inner_radius=(radius - thickness).to('mm').magnitude)

        upper_mast_tube_star = tube(
            height=length_mm, #approx
            outer_radius=radius.to('mm').magnitude,
            inner_radius=(radius - thickness).to('mm').magnitude)

        upper_mast_tube_port = tube(
            height=length_mm, #approx
            outer_radius=radius.to('mm').magnitude,
            inner_radius=(radius - thickness).to('mm').magnitude)

        super().__init__(
            children=[
                upper_mast_tube,
                upper_mast_tube_star.locate(UPos(radius * 2, 0, 0)),
                upper_mast_tube_port.locate(UPos(-radius * 2, 0, 0)),
                UBox(7.5 * u.inches, 1.5 * u.inches, 4.5 * u.inches).locate(
                    UPos(0, 2 * u.inches, -24 * u.inches)),
            ],
            color=Color((.3, .8, .3, 1.0)))

        # this joint is where the upper mast intersects
        # the U-joint of the lower mast
        RigidJoint(
            label='elbow',
            to_part=self,
            joint_location=Location(
                (0,
                 0,
                 -length_mm / 2
                 + pivot_length_mm),
                (0, -90, 0)))

        # this joint pivots the sail up and over for tacking
        # it is located near the upper end of the tube
        RevoluteJoint(
            label='sail_rotation',
            to_part=self,
            axis=Axis(
                (0,
                 0,
                 length_mm / 2 # TODO: offset for mounting bracket
                 ),
                (1, 0, 0)))
