"""airports.py provides an example Steno3D project of airports"""

from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals

import numpy as np

from .base import BaseExample
from ..point import Mesh0D
from ..point import Point
from ..project import Project


class Airports(BaseExample):
    """Class containing components of airport project. Components can be
    viewed individually or copied into new resources or projects with
    get_resources() and get_project(), respectively.
    """

    def example_name(self):
        return 'Airports'

    def filenames(self):
        """teapot json file"""
        return ['latitude.npy', 'longitude.npy', 'altitude.npy']

    def latitude(self):
        return np.load(Airports.fetch_data(filename='latitude.npy',
                                           download_if_missing=False,
                                           verbose=False))

    def longitude(self):
        return np.load(Airports.fetch_data(filename='longitude.npy',
                                           download_if_missing=False,
                                           verbose=False))

    def altitude(self):
        return np.load(Airports.fetch_data(filename='altitude.npy',
                                           download_if_missing=False,
                                           verbose=False))

    def x(self):
        return (
            (6371 + self.altitude) *
            np.cos(self.latitude*np.pi/180) *
            np.cos(self.longitude*np.pi/180)
        )

    def y(self):
        return (
            (6371 + self.altitude) *
            np.cos(self.latitude*np.pi/180) *
            np.sin(self.longitude*np.pi/180)
        )

    def z(self):
        return (
            (6371 + self.altitude) *
            np.sin(self.latitude*np.pi/180)
        )

    def vertices(self):
        return np.c_[self.x, self.y, self.z]

    def points(self):
        """Steno3D points at airports"""
        return Point(
            project=self._dummy_project,
            mesh=Mesh0D(
                vertices=self.vertices
            ),
            title='Airport Points'
        )

    def project(self):
        """empty Steno3D project"""
        return Project(
            title='Airport',
            description='Project with airport points'
        )

    def _dummy_project(self):
        """Steno3D project for initializing resources"""
        return Project()

    def get_resources(self):
        """get a copy of airport resources.

        tuple(airport points,)
        """
        return (self.points,)

    def get_project(self):
        """get a copy of airport project."""
        proj = self.project
        proj.resources = self.get_resources()
        return proj
