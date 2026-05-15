from build123d import Align, Box, Cylinder, Compound, Pos, RigidJoint, Location, Axis, GridLocations

# default export unit is mm
inches = 25.4
feet = 12 * inches
meter = 1000
m = meter

AMAX = Align.MAX
AMIN = Align.MIN
ACEN = Align.CENTER

def UCylinder(height, radius, **kwargs):
    return Cylinder(
        height=height.to('mm').magnitude,
        radius=radius.to('mm').magnitude,
        **kwargs)


def UBox(x, y, z, **kwargs):
    return Box(
        x.to('mm').magnitude,
        y.to('mm').magnitude,
        z.to('mm').magnitude,
        **kwargs)


def ULocation(pos, rot):
    x, y, z = pos
    return Location(
        (x.to('mm').magnitude if x else 0,
         y.to('mm').magnitude if y else 0,
         z.to('mm').magnitude if z else 0),
        rot)


def UPos(x, y, z):
    return Pos(
        x.to('mm').magnitude if x else 0,
        y.to('mm').magnitude if y else 0,
        z.to('mm').magnitude if z else 0)

def UAxis(pos, rot):
    x, y, z = pos
    return Axis(
        (x.to('mm').magnitude if x else 0,
         y.to('mm').magnitude if y else 0,
         z.to('mm').magnitude if z else 0),
        rot)

def UGridLocations(x, y, nx, ny):
    return GridLocations(
        x.to('mm').magnitude,
        y.to('mm').magnitude,
        nx,
        ny)


class mm_class(object):

    def __mul__(self, other):
        return other

    def __rmul__(self, other):
        return other

    def __call__(self, pint_quantity):
        return pint_quantity.to('mm').magnitude

mm = mm_class()

bore_radius_for_screw_type = {
    'm3_loose': 1.6 * mm,
    'm3_tight': 1.4 * mm,
    'm4_tight': 2.0 * mm,
    'm4_loose': 2.15 * mm,
    'm5_loose': 2.65 * mm,
}

# however they must be 44mm apart in order to fasten a nylon nut and washer
# on both sides of the round part of the current mast.
LR_inter_panel_hole_separation = 44 * mm

# this distance affords enough space in between the panels for a 
# small nut or screw head
UL_inter_panel_hole_separation = 35 * mm

upper_mast_radius = 1.25 * inches / 2
lower_mast_radius = 1.5 * inches / 2
mast_sleeve_radius = (1 + 7/8) * inches / 2
thrust_bearing_radius = (2 + 3/16) * inches / 2

def tube(inner_radius, outer_radius, height, arc_size=360, align=(Align.CENTER, Align.CENTER, Align.CENTER), rotation=(0, 0, 0)):
    outer = Cylinder(
        radius=outer_radius,
        height=height,
        arc_size=arc_size,
        align=align,
        rotation=rotation,
        )
    inner = Cylinder(
        radius=inner_radius,
        height=height,
        arc_size=arc_size,
        align=align,
        rotation=rotation,
        )
    return outer - inner


def aluminum_angle(width, length, thickness, x_align=Align.CENTER):
    if not isinstance(width, (int, float)):
        width = width.to('mm').magnitude
    if not isinstance(length, (int, float)):
        length = length.to('mm').magnitude
    if not isinstance(thickness, (int, float)):
        thickness = thickness.to('mm').magnitude
    bottom = Box(
        length,
        width,
        thickness,
        align=(x_align, Align.MIN, Align.MIN))
    side = Box(
        length,
        thickness,
        width,
        align=(x_align, Align.MIN, Align.MIN))
    angle = Compound(
        children=[bottom, side])
    return angle

class Winch(Compound):
    def __init__(self):
        self.housing_dx = 7.55 * inches
        self.housing_dy = 4.6 * inches
        self.housing_dz = 7 * inches
        self.handle_space = Cylinder(height=6 * inches, radius=12 * inches,
                                     rotation=(90, 0, 0))
        self.housing = Box(self.housing_dx, self.housing_dy, self.housing_dz)
            
        super().__init__(
            children=[
                self.handle_space.locate(Pos(0, -5 * inches, 0)),
                self.housing])

        RigidJoint(label='base', to_part=self,
           joint_location=Location(
               (0, 0, -self.housing_dz / 2),
               (0, 0, 0),
           ))
