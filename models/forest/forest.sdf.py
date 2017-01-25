#!/usr/bin/env python

from __future__ import print_function

import jinja2
import argparse
import os
import fnmatch
import numpy as np
import rospkg
import numpy as np
import pylab as pl
import scipy
from scipy import interpolate

script_dir = os.path.dirname(os.path.realpath(__file__))

def populate_map(**kwargs):
    rospack = rospkg.RosPack()
    fla_path= rospack.get_path('fla_description')
    data = {
        'width': 100,
        'height': 1,
        'n_items': 100,
        'seed': 1234,
        'roll_pitch_yaw_range_deg': [[-10, 10], [-10, -10], [-180, 180]],
        'model_options': ["tree_maple", "tree_oak", "tree_pine", "fern"],
        'heightmap_file': "model://forest/materials/textures/heightmap.png",
        'model_list': [],
    }
    for key in data.keys():
        if key in kwargs.keys():
            data[key] = kawrgs[key]

    with open(data['heightmap_file'].replace('model://forest', script_dir), 'r') as f:
        heightmap_img = pl.imread(f)

    pl.seed(data['seed'])
    img_width, img_height = heightmap_img.shape

    img_z_max = heightmap_img.max()
    img_z_min = heightmap_img.min()
    img_z_range = img_z_max - img_z_min

    i_item = 0
    while i_item < data['n_items']:
        pos = data['width']*pl.rand(2)
        i_img = int(round(pos[0]*img_width/data['width']))
        j_img = int(round(pos[1]*img_width/data['width']))
        f_z = interpolate.interp2d(
                x=range(0, img_width), y=range(0, img_width),
                z=(heightmap_img - img_z_min)*data['height']/img_z_range)
        z = f_z(i_img, j_img)[0]
        model = pl.choice(data['model_options'])
        x = 1*(pos[1] - data['width']/2)
        y = -1*(pos[0] - data['width']/2)
        angle = pl.zeros(3)
        for i, angle_range in enumerate(data['roll_pitch_yaw_range_deg']):
            angle[i] = pl.rand()*pl.deg2rad((angle_range[1] - angle_range[0]) + angle_range[0])
        data['model_list'] += [{
            'name' : model,
            'pose': [x, y, z] + list(angle),
        }]
        i_item += 1
    return data

template_str = """<?xml version="1.0" ?>
<sdf version="1.5">
  <model name="Forest">

    <static>true</static>

    {% for model in model_list %}
    <include>
      <uri>model://{{ model.name }}</uri>
      <pose> {{ model.pose | join(' ') }}</pose>
    </include>
    {% endfor %}

    <link name="link">
      <collision name="collision">
        <geometry>
          <heightmap>
            <uri>{{ heightmap_file }}</uri>
            <size> {{ width }} {{ width }} {{ height }} </size>
            <pos>0 0 0.0</pos>
          </heightmap>
        </geometry>
      </collision>

      <visual name="visual">
        <geometry>
          <heightmap>
            <texture>
              <diffuse>file://media/materials/textures/dirt_diffusespecular.png</diffuse>
              <normal>file://media/materials/textures/flat_normal.png</normal>
              <size> {{ height * 0.4 }}</size>
            </texture>
            <texture>
              <diffuse>file://media/materials/textures/grass_diffusespecular.png</diffuse>
              <normal>file://media/materials/textures/flat_normal.png</normal>
              <size> {{ height * 0.4 }}</size>
            </texture>
            <texture>
              <diffuse>file://media/materials/textures/fungus_diffusespecular.png</diffuse>
              <normal>file://media/materials/textures/flat_normal.png</normal>
              <size> {{ height * 0.4 }}</size>
            </texture>
            <blend>
              <min_height> {{ height * 0.1 }} </min_height>
              <fade_dist> {{ height * 0.1 }} </fade_dist>
            </blend>
            <blend>
              <min_height>{{ height * 0.9 }} </min_height>
              <fade_dist>{{ height * 0.1 }} </fade_dist>
            </blend>
            <uri>{{ heightmap_file }}</uri>
            <size> {{ width }} {{ width }} {{ height }} </size>
            <pos>0 0 0.0</pos>
          </heightmap>
        </geometry>
      </visual>

    </link>
  </model>
</sdf>
"""

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    # parser.add_argument('filename')
    args = parser.parse_args()
    env = jinja2.Environment()
    template = env.from_string(template_str)
    data = populate_map()
    result = template.render(data)
    filename_out = os.path.join(script_dir, 'forest.sdf')
    with open(filename_out, 'w') as f_out:
        f_out.write(result)
