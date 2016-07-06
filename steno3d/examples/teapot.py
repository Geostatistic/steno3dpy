"""teapot.py provides an example Steno3D project of a teapot"""

from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals

from json import loads

from numpy import array

from .base import BaseExample
from ..point import Mesh0D
from ..point import Point
from ..project import Project
from ..surface import Mesh2D
from ..surface import Surface


class Teapot(BaseExample):
    """Class containing components of teapot project. Components can be
    viewed individually or copied into new resources or projects with
    get_resources() and get_project(), respectively.
    """

    def example_name(self):
        return 'Teapot'

    def filenames(self):
        """teapot json file"""
        return ['teapot.json']

    def data(self):
        """teapot data read from json"""
        json_file = Teapot.fetch_data(filename='teapot.json',
                                      download_if_missing=False,
                                      verbose=False)
        with open(json_file, 'r') as f:
            file_data = loads(f.read())
        return file_data

    def vertices(self):
        """n x 3 numpy array of teapot vertices"""
        return array(self.data['vertices'])

    def triangles(self):
        """n x 3 numpy array of teapot triangle vertex indices"""
        return array(self.data['triangles'])

    def points(self):
        """Steno3D points at teapot vertices"""
        return Point(
            project=self._dummy_project,
            mesh=Mesh0D(
                vertices=self.vertices
            ),
            title='Teapot Vertex Points'
        )

    def surface(self):
        """Steno3D teapot surface"""
        return Surface(
            project=self._dummy_project,
            mesh=Mesh2D(
                vertices=self.vertices,
                triangles=self.triangles
            ),
            title='Teapot Surface'
        )

    def project(self):
        """empty Steno3D project"""
        return Project(
            title='Teapot',
            description='Project with surface and points at vertices'
        )

    def _dummy_project(self):
        """Steno3D project for initializing resources"""
        return Project()

    def get_resources(self):
        """get a copy of teapot resources.

        tuple(teapot surface, teapot points,)
        """
        return (self.surface, self.points,)

    def get_project(self):
        """get a copy of teapot project."""
        proj = self.project
        proj.resources = self.get_resources()
        for r in proj.resources:
            r.project = proj
        return proj
