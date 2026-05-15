
import io
import tempfile

from build123d import Compound, ExportSVG, LineType
import imageio
import cairosvg
import numpy as np


from pdr import SolarPDR

def animated_gif(
        poses,
        output_file='animation.gif',
        loop=0,
        scale=None,
        ):

    images = []
    durations = []
    with tempfile.TemporaryDirectory() as tmpdirname:

        for ii, pose in enumerate(poses):
            spdr = SolarPDR(**pose['pdr'])
            visible, hidden = spdr.project_to_viewport(
                pose['view_port_origin'],
                (0, 0, 1),
                look_at=(0, 0, 0))

            # TODO draw a frame around the visible things, so that
            # the SVGs always cover the same field of view, and
            # the frame can be removed below.
            if scale is None:
                max_dimension = max(*Compound(children=visible + hidden).bounding_box().size)
                scale = 100 / max_dimension

            exporter = ExportSVG(scale=scale)
            exporter.add_layer("Visible")
            exporter.add_layer("Hidden",
                               line_color=(99, 99, 99),
                               line_type=LineType.ISO_DOT)
            exporter.add_shape(visible, layer="Visible")
            exporter.add_shape(hidden, layer="Hidden")
            exporter.write(f"{tmpdirname}/{ii:04d}.svg")

            cairosvg.svg2png(url=f"{tmpdirname}/{ii:04d}.svg",
                             write_to=f"{tmpdirname}/{ii:04d}.png")
            img = imageio.v2.imread(f"{tmpdirname}/{ii:04d}.png")
            N = 400
            dst = np.zeros((N, N, 4), dtype=np.uint8)
            off0 = int( (N - img.shape[0]) / 2)
            off1 = int( (N - img.shape[1]) / 2)
            dst[N - img.shape[0]:N, off1:off1 + img.shape[1], :] = img
            dst[:, :, :3] = 255 - dst[:, :, 3:4]
            dst[:, :, 3] = 255
            images.append(dst)
            durations.append(pose['duration'])

    if len(durations) > 1:
        imageio.mimsave(output_file, images, duration=durations, loop=loop)
    else:
        imageio.mimsave(output_file, images, duration=durations[0], loop=loop)


def write_tacking_animation():
    poses = []
    def frame(sa, vpy, lmr):
        poses.append(dict(
            pdr=dict(sail_angle=sa,
                     mast_angle=0,
                     lower_mast_rotation=90 - (lmr-90)),
            duration=.2,
            view_port_origin=(100, vpy, 0),
            ))

    frame(0, -104, 135)
    frame(0, -103, 135)
    frame(0, -102, 135)
    frame(0, -101, 135)
    frame(10, -100, 135)
    frame(20, -100, 135)
    frame(30, -100, 135)
    frame(40, -100, 135)
    frame(50, -100, 135)
    frame(60, -100, 135)
    frame(70, -100, 135)
    frame(80, -100, 135)
    frame(90, -100, 135)
    frame(90, -75, 125)
    frame(90, -50, 115)
    frame(90, -25, 105)
    frame(90, 0, 90)
    frame(90, 25, 75)
    frame(90, 50, 65)
    frame(90, 75, 55)
    frame(90, 100, 45)
    frame(100, 100, 45)
    frame(110, 100, 45)
    frame(120, 100, 45)
    frame(130, 100, 45)
    frame(140, 100, 45)
    frame(150, 100, 45)
    frame(160, 100, 45)
    frame(170, 100, 45)
    frame(180, 100, 45)
    frame(180, 101, 45)
    frame(180, 102, 45)
    frame(180, 103, 45)
    frame(180, 104, 45)
    for pose in reversed(poses[:-1]):
        poses.append(pose)

    animated_gif(poses,
                 output_file='tacking.gif')


def write_hoist_animation():

    poses = []
    def frame(ma, sa, lma):
        poses.append(dict(
            pdr=dict(sail_angle=sa,
                     mast_angle=ma,
                     lower_mast_rotation=lma),
            duration=.2,
            view_port_origin=(0, 100, 0),
            ))

    frame(90, 0, 0)
    frame(89.5, 0.5, 0)
    frame(89.25, .75, 0)
    frame(89.1, .9, 0)
    frame(89, 1, 0)
    frame(80, 10, 0)
    frame(70, 20, 0)
    frame(60, 30, 0)
    frame(50, 40, 0)
    frame(40, 50, 0)
    frame(30, 60, 0)
    frame(20, 70, 0)
    frame(10, 80, 0)
    frame(0, 90, 0)
    frame(0, 90, 20)
    frame(0, 90, 30)
    frame(0, 90, 40)
    frame(0, 90, 50)
    frame(0, 80, 50)
    frame(0, 70, 50)
    frame(0, 60, 50)
    frame(0, 50, 50)
    frame(0, 40, 50)
    frame(0, 30, 50)
    frame(0, 20, 50)
    frame(0, 10, 50)
    frame(0, 9, 49.5)
    frame(0, 9, 49.25)
    frame(0, 0, 49.1)
    frame(0, 0, 49)

    for pose in reversed(poses[:-1]):
        poses.append(pose)

    animated_gif(poses,
                 scale=.025,
                 output_file='hoist.gif')
