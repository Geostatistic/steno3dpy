"""point.py contains the Point composite resource for steno3d"""

from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals

from builtins import super

from .base import BaseMesh
from .base import CompositeResource
from .options import ColorOptions
from .options import Options
from .texture import Texture2DImage
from .traits import Array, DelayedValidator, KeywordInstance, Repeated, StringChoices, validator


class _Mesh0DOptions(Options):
    pass


class _PointOptions(ColorOptions):
    pass


class Mesh0D(BaseMesh):
    """Contains spatial information of a 0D point cloud."""
    vertices = Array(
        help='Point locations',
        shape=('*', 3),
        dtype=float
    )
    opts = KeywordInstance(
        help='Mesh0D Options',
        klass=_Mesh0DOptions,
        allow_none=True
    )

    @property
    def nN(self):
        """ get number of nodes """
        return len(self.vertices)

    def _nbytes(self, name=None):
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

    @validator
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


class _PointBinder(DelayedValidator):
    """Contains the data on a 0D point cloud"""
    location = StringChoices(
        help='Location of the data on mesh',
        default_value='N',
        choices={
            'N': ('NODE', 'CELLCENTER', 'CC', 'VERTEX')
        }
    )
    data = KeywordInstance(
        help='Data',
        klass='DataArray'
    )


class Point(CompositeResource):
    """Contains all the information about a 0D point cloud"""
    mesh = KeywordInstance(
        help='Mesh',
        klass=Mesh0D
    )
    data = Repeated(
        help='Data',
        trait=KeywordInstance(klass=_PointBinder),
        allow_none=True
    )
    textures = Repeated(
        help='Textures',
        trait=KeywordInstance(klass=Texture2DImage),
        allow_none=False
    )
    opts = KeywordInstance(
        help='Options',
        klass=_PointOptions
    )

    def _nbytes(self):
        return (self.mesh._nbytes() +
                sum(d.data._nbytes() for d in self.data) +
                sum(t._nbytes() for t in self.textures))

    @validator
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
