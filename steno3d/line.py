"""line.py contains the Line composite resource for steno3d"""

from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals

from builtins import super

from numpy import max as npmax
from numpy import min as npmin
import properties

from .base import BaseMesh
from .base import CompositeResource
from .options import ColorOptions
from .options import Options


class _Mesh1DOptions(Options):
    pass


class _LineOptions(ColorOptions):
    pass


class Mesh1D(BaseMesh):
    """Contains spatial information of a 1D line set"""
    vertices = properties.Array(
        'Mesh vertices',
        shape=('*', 3),
        dtype=float,
        required=True
    )
    segments = properties.Array(
        'Segment endpoint indices',
        shape=('*', 2),
        dtype=int,
        required=True
    )
    opts = properties.Pointer(
        'Options',
        ptype=_Mesh1DOptions
    )

    @property
    def nN(self):
        """ get number of nodes """
        return len(self.vertices)

    @property
    def nC(self):
        """ get number of cells """
        return len(self.segments)

    def nbytes(self, name=None):
        if name in ('segments', 'vertices'):
            return getattr(self, name).nbytes
        elif name is None:
            return self.nbytes('segments') + self.nbytes('vertices')
        raise ValueError('Mesh1D cannot calculate the number of '
                         'bytes of {}'.format(name))

    def _on_property_change(self, name, pre, post):
        try:
            if name in ('segments', 'vertices'):
                self._validate_file_size(name)
        except ValueError as err:
            setattr(self, '_p_' + name, pre)
            raise err
        super()._on_property_change(name, pre, post)


    @properties.validator
    def validate(self):
        """Check if mesh content is built correctly"""
        if npmin(self.segments) < 0:
            raise ValueError('Segments may only have positive integers')
        if npmax(self.segments) >= len(self.vertices):
            raise ValueError('Segments expects more vertices than provided')
        self._validate_file_size('segments')
        self._validate_file_size('vertices')
        return True

    def _get_dirty_files(self, force=False):
        dirty = self._dirty_props
        files = dict()
        if 'vertices' in dirty or force:
            files['vertices'] = \
                self._properties['vertices'].serialize(self.vertices)
        if 'segments' in dirty or force:
            files['segments'] = \
                self._properties['segments'].serialize(self.segments)
        return files


class _LineBinder(properties.PropertyClass):
    """Contains the data on a 1D line set with location information"""
    location = properties.String(
        'Location of the data on mesh',
        required=True,
        choices={
            'CC': ('LINE', 'FACE', 'CELLCENTER', 'EDGE', 'SEGMENT'),
            'N': ('VERTEX', 'NODE', 'ENDPOINT')
        }
    )
    data = properties.Pointer(
        'Data',
        ptype='DataArray',
        required=True
    )


class Line(CompositeResource):
    """Contains all the information about a 1D line set"""
    mesh = properties.Pointer(
        'Mesh',
        ptype=Mesh1D,
        required=True
    )
    data = properties.Pointer(
        'Data',
        ptype=_LineBinder,
        repeated=True
    )
    opts = properties.Pointer(
        'Options',
        ptype=_LineOptions
    )

    def nbytes(self):
        return self.mesh.nbytes() + sum(d.data.nbytes() for d in self.data)

    @properties.validator
    def validate(self):
        """Check if resource is built correctly"""
        for ii, dat in enumerate(self.data):
            assert dat.location in ('N', 'CC')
            valid_length = (
                self.mesh.nC if dat.location == 'CC'
                else self.mesh.nN
            )
            if len(dat.data.array) != valid_length:
                raise ValueError(
                    'line.data[{index}] length {datalen} does not match '
                    '{loc} length {meshlen}'.format(
                        index=ii,
                        datalen=len(dat.data.array),
                        loc=dat.location,
                        meshlen=valid_length
                    )
                )
        super(Line, self).validate()
        return True


__all__ = ['Line', 'Mesh1D']
