from build123d import *
import copy
import math

from vessel_base import VesselBase, ureg as u
from wing_sail import WingSail, WingSailUpperMast
from newport import Newport_46
from common import (inches, feet, UBox, UPos, UCylinder, UAxis, ULocation, AMIN, AMAX, ACEN)

gravity = 9.81 * u.meter / u.second / u.second

wall_thickness = 1 / 4 * inches

safety_factor = .75


def pdr_wall():
    with BuildPart() as wall:
        with BuildSketch(Plane.XZ) as sketch:
            with BuildLine() as line:
                lp = Line((0, 0), (-8 * feet, 0))
                for ii, mark in enumerate([6, 2 + 5/8, 5/8, 0, 0, 1, 2 + 3/8, 4 + 3/8]):
                    lp = Line(lp @ 1, (-(8 - ii) * feet, -(18 - mark) * inches))
                lp = Line(lp @ 1, (-6 * inches, -12 * inches))
                #l2 = JernArc(l1 @ 1, (1, -.26, 0), 15.1 * feet, 29)
                lp = Line(lp @ 1, (0.0))
            make_face()
        extrude(amount = wall_thickness)
    return wall.part


def pdr_hull():
    wall = pdr_wall()
    stern_transom = Box(12 * inches, 4 * feet, wall_thickness,
                        rotation=(0, 90, 0))

    stern_bulkhead_height = 15.5 * inches
    stern_bulkhead = Box(
        stern_bulkhead_height,
        4 * feet - 0.5 * inches,
        wall_thickness,
        rotation=(0, 90, 0))
    
    bow_bulkhead_height = 14.75 * inches
    bow_bulkhead = Box(
        bow_bulkhead_height,
        4 * feet - 0.5 * inches,
        wall_thickness,
        rotation=(0, 90, 0))
    
    bow_transom = Box(13 * inches + wall_thickness, 4 * feet, wall_thickness)
        
    locs = GridLocations(
        0,
        4 * feet - wall_thickness,
        1,
        2).local_locations
    
    return Compound(
        children=[
            copy.copy(wall).locate(loc).move(Pos(0, wall_thickness / 2, 0)) for loc in locs
        ] + [
            copy.copy(stern_transom).locate(Pos(-8 * feet - wall_thickness / 2, 0, -6 * inches)),
            copy.copy(stern_bulkhead).locate(Pos(-7 * feet, 0, -stern_bulkhead_height / 2)),
            copy.copy(bow_bulkhead).locate(Pos(-18 * inches, 0, -bow_bulkhead_height / 2)),
            copy.copy(bow_transom).locate(Location((-70, 0, -bow_bulkhead_height / 2 + 35), (0, -63, 0))),
            
        ])


class BackstayAssembly(Compound):

    drum_diameter = 3.5 * u.cm
    line_diameter = 1/8 * u.inches  # https://www.homedepot.ca/product/everbilt-1-8-inch-x50-feet-nylon-diamond-braid-white/1000799809
    line_load_limit = 45 * u.pounds * gravity * safety_factor


    def __init__(self, working_line_length=9 * u.feet, label="Backstay Assembly"):
        children = []
        self.working_line_length = working_line_length

        drum_circumference = self.drum_diameter * math.pi
        max_wraps = (working_line_length / drum_circumference) * u.count
        self.drum_height = max_wraps * self.line_diameter
        
        backstay_drum = UCylinder(height=self.drum_height, radius=self.drum_diameter / 2, rotation=(90, 0, 0))
        children.append(backstay_drum)

        super().__init__(children=children, label=label)


class SolarPDR(Compound, VesselBase):
    name = "Solar PDR"

    sail_area = 60 * u.cm * 4 * 100 * u.cm * 2
    
    halyard_drum_diameter = 3.5 * u.cm

    #halyard_line_diameter = 3/16 * u.inches  # https://www.homedepot.ca/product/everbilt-3-16-inch-x50-feet-nylon-diamond-braid-white/1000799808
    #halyard_line_load_limit = 100 * u.pounds * gravity * safety_factor

    halyard_line_diameter = 1/8 * u.inches  # https://www.homedepot.ca/product/everbilt-1-8-inch-x50-feet-nylon-diamond-braid-white/1000799809
    halyard_line_load_limit = 45 * u.pounds * gravity * safety_factor

    
    def init_foredeck_mount(self, children, lr):
        rval = UBox(
            26 * u.inches,
            1.5 * u.inches,
            5.5 * u.inches,
            align=(Align.MIN, Align.MIN if lr < 0 else Align.MAX, Align.MIN),
        )
        rval.locate(UPos(-18 * u.inches, lr * 24 * u.inches, 0))
        children.append(rval)
        return rval

    def init_prop(self, children):
        self.newport = Newport_46().locate(UPos(-8 * u.feet - 4 * u.inches, 0, 12 * u.inches))
        self.newport.color = Color(.3, .3, .3)
        prop = self.newport.prop
        children.append(self.newport)
        return prop

    def init_rear_rack(self, children):
        rack_children = []

        z_drop = 36 * 25.4
        board = Solid.extrude(
            Face.make_surface_from_curves(
                Edge.make_line((-z_drop / 2, 0), (0, z_drop)),
                Edge.make_line((-z_drop / 2 + 5.5 * 25.4 * math.cos(-30 * math.pi / 180),
                                5.5 * 25.4 * math.sin(-30 * math.pi / 180)),
                               (0, z_drop + 5.5 * 25.4 * math.tan(-60 * math.pi / 180)))),
            direction=(0, 0, 1.5 * 25.4))
        board.locate(ULocation((-1.5 * u.inches, 0, -z_drop * u.mm + 30 * u.inches), (90, 90, 0)))
        rack_children.append(board)
        rack_children.append(board.located(ULocation((0, 0, -z_drop * u.mm + 30 * u.inches), (90, -90, 0))))
        
        transom_mount = UBox(1.5 * u.inches, 24 * u.inches, 5.5 * u.inches, align=(AMIN, ACEN, AMIN))
        rack_children.append(transom_mount)

        backstay_assembly = BackstayAssembly().locate(UPos(8 * u.inches, 0, 24 * u.inches))
        rack_children.append(backstay_assembly)
        
        steering_servo = UBox(2 * u.inches, 2 * u.inches, 2 * u.inches).locate(UPos(2 * u.inches, -8 * u.inches, 11 * u.inches))
        rack_children.append(steering_servo)

        cradle = UBox(
            1.5 * u.inches,
            5.5 * u.inches,
            6 * u.inches,
            align=(Align.MAX, Align.CENTER, Align.MIN),
        ).locate(UPos(1.5 * u.inches, 0, 24 * u.inches))
        rack_children.append(cradle)

        # TODO: are these lines more like a halyard? fore and aft halyard lines?
        # TODO: forestay drum
        # TODO: backstay drum
        # TODO: re-designed rear rack
        # TODO: pillow-block and shaft selection
        # TODO: mount for motor
        children.append(Compound(children=rack_children, label="Rear Rack")
            .locate(UPos(-8 * u.feet - wall_thickness * u.mm, 0, wall_thickness * u.mm)))
        
        return children[-1]

    def init_workshop_entrance(self, children):
        top = UBox(
            1.5 * u.inches,
            80 * u.inches,
            10 * u.inches,
            align=(Align.MAX, Align.CENTER, Align.MIN),
        ).locate(UPos(1.5 * u.inches, 0, 0 * u.inches))
        entrance_children = [top]

        children.append(
            Compound(
                children=entrance_children,
                label='Workshop Entrance')
            .locate(UPos(0 * u.inches, 0 * u.inches, (79-36) * u.inches)))

    
    def __init__(self, mast_angle=0, sail_angle=0, lower_mast_rotation=0, show_workshop_entrance=False):
        self.length = 8 * u.feet
        self.LWL = 7 * u.feet + 6 * u.inches
        self.sail_width = 2 * u.m
        self.sail_height = 4 * 60 * u.cm
        self.solar_sail_area = self.sail_width * self.sail_height
        self.displacement = 150 * u.pounds
        children = [pdr_hull()]

        self.rudder = UBox(
            14 * u.inches,
            2 * u.inches,
            18 * u.inches,
            align=(Align.MAX, Align.CENTER, Align.MAX),
            )
        self.rudder.locate(UPos(-7.75 * u.feet, 0, -14 * u.inches))
        children.append(self.rudder)

        self.leeboard = UBox(
            12 * u.inches,
            3/4 * u.inches,
            (36 + 18) * u.inches,
            align=(Align.MAX, Align.CENTER, Align.MAX),
            )
        self.leeboard.locate(UPos(-16 * u.inches, 25 * u.inches, 0))
        children.append(self.leeboard)

        wingsail_thickness_mm = 200
        self.sail = WingSail(arc_thickness_mm=wingsail_thickness_mm)
        children.append(self.sail)

        self.upper_mast = WingSailUpperMast(
            length=56 * u.inches,
            pivot_length = 24 * u.inches,
            radius=1.5 / 2 * u.inches,
            thickness=.5 * u.cm,
            )
        children.append(self.upper_mast)


        self.lower_mast = UCylinder(
            height=45 * u.inches,
            radius=(1 + 7/8) / 2 * u.inches,
            align=(Align.CENTER, Align.CENTER, Align.MIN),
            )
        RigidJoint(
            label='bar',
            to_part=self.lower_mast)
        self.lower_mast.locate(UPos(-19 * u.inches, 0, -15 * u.inches))
        children.append(Compound(children=[self.lower_mast], color=(.7, .4, .7, 1.0)))

        self.star_foredeck_mount = self.init_foredeck_mount(children, lr=-1)
        self.port_foredeck_mount = self.init_foredeck_mount(children, lr=1)
        self.prop = self.init_prop(children)
        self.rear_rack = self.init_rear_rack(children)

        if show_workshop_entrance:
            self.workshop_entrance = self.init_workshop_entrance(children)

        if 1:
            self.lower_mast_sleeve = UCylinder(
                height=18 * u.inches,
                radius=2 * (1 + 7/8) / 2 * u.inches,
                align=(Align.CENTER, Align.CENTER, Align.MIN),
                )
            RevoluteJoint(
                label='foo',
                to_part=self.lower_mast_sleeve,
            )
            self.lower_mast_sleeve.locate(UPos(-19 * u.inches, 0, -15 * u.inches))
            children.append(self.lower_mast_sleeve)
    
        # should be just just forward of  top of lower mast
        RevoluteJoint(
            label='mast_rotation',
            to_part=self.lower_mast,
            axis=UAxis(
                (-19. * u.inches, # abaft of bow 
                 0, # centred
                 43. * u.inches # clearance of workshop door above deck
                 - wingsail_thickness_mm * u.mm # thickness of sail
                 - 4 * u.inches # TODO placeholder for actual bracket width
                ), #
                (0, 1, 0))
        )
        self.lower_mast_sleeve.joints['foo'].connect_to(
            self.lower_mast.joints['bar'],
            angle=lower_mast_rotation)


        self.lower_mast.joints['mast_rotation'].connect_to(
            self.upper_mast.joints['elbow'],
            angle=360 - mast_angle)

        self.upper_mast.joints['sail_rotation'].connect_to(
            self.sail.joints['mast_hole'],
            angle=sail_angle + 90)

        super().__init__(children=children)
