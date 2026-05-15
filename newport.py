from build123d import *
import numpy as np
from common import UCylinder, ULocation, UPos, UBox, AMAX, AMIN, ACEN
from vessel_base import ureg as u
from propeller import SimpleProp

class Newport_46(Compound):

    

    def __init__(self, label="Newport 46"):
        # shaft length is advertised as 30", but I think I'm modelling it differently
        modelled_shaft_length = 33 * u.inches
        # TODO: measure all this # approx
        self.tiller = UCylinder(height=20 * u.inches, radius=.5 * u.inches, align=(ACEN, ACEN, AMIN), rotation=(0, 90, 0))
        self.shaft = UCylinder(height=modelled_shaft_length, radius=.5 * u.inches, align=(ACEN, ACEN, AMAX))
        self.motor = UCylinder(height=14 * u.inches, radius=2 * u.inches, rotation=(0, 90, 0)).locate(UPos(-2 * u.inches, 0, -modelled_shaft_length))
        self.tiller_housing = UBox(12 * u.inches, 4 * u.inches, 4 * u.inches)
        self.clamp_assembly = UBox(12 * u.inches, 6 * u.inches, 6 * u.inches).locate(UPos(3 * u.inches, 0, -8 * u.inches))

        self.prop = SimpleProp(hub_radius=5 * u.cm, blade_radius=15 * u.cm, hub_height=10 * u.cm)
        self.prop.locate(ULocation((-10 * u.inches, 0, -modelled_shaft_length), (0, -90, 0)))
        super().__init__(
            children=[
                self.tiller,
                self.tiller_housing,
                self.shaft,
                self.clamp_assembly,
                self.motor,
                self.prop],
            label=label)