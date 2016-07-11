"""point.py contains the Point composite resource for steno3d"""

from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals

from builtins import super

import properties

from .base import BaseMesh
from .base import CompositeResource
from .options import ColorOptions
from .options import Options


class _Mesh0DOptions(Options):
    pass


class _PointOptions(ColorOptions):
    pass


class Mesh0D(BaseMesh):
    """Contains spatial information of a 0D point cloud."""
    vertices = properties.Array(
        'Point locations',
        shape=('*', 3),
        dtype=float,
        required=True
    )
    opts = properties.Pointer(
        'Mesh0D Options',
        ptype=_Mesh0DOptions
    )

    @property
    def nN(self):
        """ get number of nodes """
        return len(self.vertices)

    def nbytes(self, name=None):
        if name is None or name == 'vertices':
            return self.vertices.astype('f4').nbytes
        raise ValueError('Mesh0D cannot calculate the number of '
                         'bytes of {}'.format(name))

    def _on_property_change(self, name, pre, post):
        try:
            if name == 'vertices':
                self._validate_file_size(name)
        except ValueError as err:
            setattr(self, '_p_' + name, pre)
            raise err
        super()._on_property_change(name, pre, post)

    @properties.validator
    def validate(self):
        """Check if mesh content is built correctly"""
        self._validate_file_size('vertices')
        return True

    def _get_dirty_files(self, force=False):
        dirty = self._dirty_props
        files = dict()
        if 'vertices' in dirty or force:
            files['vertices'] = \
                self._properties['vertices'].serialize(self.vertices)
        return files


class _PointBinder(properties.PropertyClass):
    """Contains the data on a 0D point cloud"""
    location = properties.String(
        'Location of the data on mesh',
        default='N',
        required=True,
        choices={
            'N': ('NODE', 'CELLCENTER', 'CC', 'VERTEX')
        }
    )
    data = properties.Pointer(
        'Data',
        ptype='DataArray',
        required=True
    )


class Point(CompositeResource):
    """Contains all the information about a 0D point cloud"""
    mesh = properties.Pointer(
        'Mesh',
        ptype=Mesh0D,
        required=True
    )
    data = properties.Pointer(
        'Data',
        ptype=_PointBinder,
        repeated=True
    )
    textures = properties.Pointer(
        'Textures',
        ptype='Texture2DImage',
        repeated=True
    )
    opts = properties.Pointer(
        'Options',
        ptype=_PointOptions
    )

    def nbytes(self):
        return (self.mesh.nbytes() + sum(d.data.nbytes() for d in self.data) +
                sum(t.nbytes() for t in self.textures))

    @properties.validator
    def validate(self):
        """Check if resource is built correctly"""
        for ii, dat in enumerate(self.data):
            assert dat.location == 'N'
            valid_length = self.mesh.nN
            if len(dat.data.array) != valid_length:
                raise ValueError(
                    'point.data[{index}] length {datalen} does not match '
                    '{loc} length {meshlen}'.format(
                        index=ii,
                        datalen=len(dat.data.array),
                        loc=dat.location,
                        meshlen=valid_length
                    )
                )
        super(Point, self).validate()
        return True


__all__ = ['Point', 'Mesh0D']
