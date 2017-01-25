#!/usr/bin/env python

from __future__ import print_function

import jinja2
import argparse
import cv2
import os
import fnmatch
import numpy as np
import rospkg
import numpy as np
import pylab as pl
import scipy
from scipy import interpolate

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    # parser.add_argument('filename')
    args = parser.parse_args()
    env = jinja2.Environment()
    rospack = rospkg.RosPack()
    fla_path= rospack.get_path('fla_description')
    texture_path = os.path.join('materials', 'textures')
    script_path = os.path.join('materials', 'scripts')

    script_dir = os.path.dirname(os.path.realpath(__file__))

    with open('material.jinja') as f:
        material_template_str = f.read()
    material_template = env.from_string(material_template_str)

    with open('model.jinja') as f:
        model_template_str = f.read()
    model_template = env.from_string(model_template_str)

    data = {}

    # create texture images for yard markers
    try:
        os.makedirs(texture_path)
    except os.error as e:
        pass

    for i in range(10, 60, 5):
        # texture
        img = np.zeros((300, 400, 4), dtype=np.uint8)
        img[:, :, 0] = 0
        img[:, :, 1] = 0
        img[:, :, 2] = 0
        img[:, :, 3] = 0
        img = cv2.putText(img, str(i), (0, 270), cv2.FONT_HERSHEY_SIMPLEX,
                10, (255, 255, 255, 255), 30, cv2.LINE_AA)
        name = 'yard_{:d}'.format(i)
        texture_file = os.path.join('{:s}.png'.format(name))
        cv2.imwrite(os.path.join(texture_path, texture_file), img)

        # material
        data_material = {
            'name': name,
            'texture_file': texture_file,
        }
        material_file = os.path.join('{:s}.material'.format(name))
        result = material_template.render(data_material)
        filename_out = os.path.join(script_path, material_file)
        with open(filename_out, 'w') as f_out:
            f_out.write(result)

    
    result = model_template.render(data)
    filename_out = os.path.join(script_dir, 'stadium.sdf')
    with open(filename_out, 'w') as f_out:
        f_out.write(result)


#  vim: set et fenc=utf-8 ff=unix sts=0 sw=4 ts=4 : 
