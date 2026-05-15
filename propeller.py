from build123d import *
import numpy as np

class SimpleProp(Compound):
    def __init__(self, hub_radius, blade_radius, hub_height, n_blades=3, blade_thickness=None):

        self.n_blades = n_blades
        self.hub_radius = hub_radius
        self.blade_radius = blade_radius
        self.hub_height = hub_height
        self.blade_thickness = blade_thickness

        self.hub_radius_mm = hub_radius.to('mm').magnitude
        self.blade_radius_mm = blade_radius.to('mm').magnitude
        self.hub_height_mm = hub_height.to('mm').magnitude
        self.blade_thickness_mm = (
            blade_thickness.to('mm').magnitude
            if blade_thickness is not None
            else self.hub_radius_mm / 10)

        hub = Cylinder(height=self.hub_height_mm, radius=self.hub_radius_mm)

        n_blades = 3
        children = [hub]

        for ii in range(n_blades):
            theta = np.pi * 2 / n_blades * ii
            blade_arc = np.pi * 2 / n_blades * .6
            inner_arc = Edge.make_three_point_arc(
                (self.hub_radius_mm * np.cos(theta),
                 self.hub_radius_mm * np.sin(theta),
                 -self.hub_height_mm / 2),
                (self.hub_radius_mm * np.cos(theta + blade_arc / 2),
                 self.hub_radius_mm * np.sin(theta + blade_arc / 2),
                 0),
                (self.hub_radius_mm * np.cos(theta + blade_arc),
                 self.hub_radius_mm * np.sin(theta + blade_arc),
                 self.hub_height_mm / 2))

            outer_arc = Edge.make_three_point_arc(
                (self.blade_radius_mm * np.cos(theta),
                 self.blade_radius_mm * np.sin(theta),
                 -self.hub_height_mm / 2),
                (self.blade_radius_mm * np.cos(theta + blade_arc / 2),
                 self.blade_radius_mm * np.sin(theta + blade_arc / 2),
                 0),
                (self.blade_radius_mm * np.cos(theta + blade_arc),
                 self.blade_radius_mm * np.sin(theta + blade_arc),
                 self.hub_height_mm / 2))

            blade_surface = Face.make_surface_from_curves(
                wire1=Wire(Edge.make_three_point_arc(inner_arc @ .25, inner_arc @ .5, inner_arc @ .75)),
                wire2=Wire(Edge.make_three_point_arc(outer_arc @ .35, outer_arc @ .5, outer_arc @ .95)),
            )
            children.append(thicken(blade_surface, self.blade_thickness_mm))

        super().__init__(children=children)
