"""airports.py provides an example Steno3D project of airports"""

from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals

import numpy as np

from .base import BaseExample, exampleproperty
from ..point import Mesh0D
from ..point import Point
from ..project import Project


class Airports(BaseExample):
    """Class containing components of airport project. Components can be
    viewed individually or copied into new resources or projects with
    get_resources() and get_project(), respectively.
    """

    @exampleproperty
    def example_name(self):
        return 'Airports'

    @exampleproperty
    def filenames(self):
        """teapot json file"""
        return ['latitude.npy', 'longitude.npy', 'altitude.npy', 'license.txt']

    @exampleproperty
    def latitude(self):
        return np.load(Airports.fetch_data(filename='latitude.npy',
                                           download_if_missing=False,
                                           verbose=False))

    @exampleproperty
    def longitude(self):
        return np.load(Airports.fetch_data(filename='longitude.npy',
                                           download_if_missing=False,
                                           verbose=False))

    @exampleproperty
    def altitude(self):
        return np.load(Airports.fetch_data(filename='altitude.npy',
                                           download_if_missing=False,
                                           verbose=False))

    @classmethod
    def get_project(self):
        r = 6371
        d2r = np.pi/180
        alt = self.altitude
        lat = self.latitude
        lon = self.longitude

        proj = Project(
            title='Airport',
            description='Project with airport points'
        )
        Point(
            project=proj,
            mesh=Mesh0D(
                vertices=np.c_[
                    (r + alt) * np.cos(lat*d2r) * np.cos(lon*d2r),
                    (r + alt) * np.cos(lat*d2r) * np.sin(lon*d2r),
                    (r + alt) * np.sin(lat*d2r)
                ]
            ),
            title='Airport Points'
        )
        return proj
