"""surface.py contains the Surface composite resource for steno3d"""

from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals

from builtins import super
from json import dumps

from numpy import max as npmax
from numpy import min as npmin
from traitlets import Union

from .base import BaseMesh
from .base import CompositeResource
from .data import DataArray
from .options import ColorOptions
from .options import MeshOptions
from .texture import Texture2DImage
from .traits import Array, DelayedValidator, KeywordInstance, Repeated, StringChoices, validator, Vector


class _Mesh2DOptions(MeshOptions):
    pass


class _SurfaceOptions(ColorOptions):
    pass


class Mesh2D(BaseMesh):
    """class steno3d.Mesh2D

    Contains spatial information about a 2D surface defined by
    triangular faces.
    """
    vertices = Array(
        help='Mesh vertices',
        shape=('*', 3),
        dtype=float
    )
    triangles = Array(
        help='Mesh triangle vertex indices',
        shape=('*', 3),
        dtype=int
    )
    opts = KeywordInstance(
        help='Mesh2D Options',
        klass=_Mesh2DOptions,
        allow_none=True
    )

    @property
    def nN(self):
        """ get number of nodes """
        return len(self.vertices)

    @property
    def nC(self):
        """ get number of cells """
        return len(self.triangles)

    def _nbytes(self, name=None):
        if name in ('vertices', 'triangles'):
            return getattr(self, name).astype('f4').nbytes
        elif name is None:
            return self._nbytes('vertices') + self._nbytes('triangles')
        raise ValueError('Mesh2D cannot calculate the number of '
                         'bytes of {}'.format(name))

    def _on_property_change(self, name, pre, post):
        try:
            if name in ('vertices', 'triangles'):
                self._validate_file_size(name)
        except ValueError as err:
            setattr(self, '_p_' + name, pre)
            raise err
        super()._on_property_change(name, pre, post)

    @validator
    def validate(self):
        """Check if mesh content is built correctly"""
        if npmin(self.triangles) < 0:
            raise ValueError('Triangles may only have positive integers')
        if npmax(self.triangles) >= len(self.vertices):
            raise ValueError('Triangles expects more vertices than provided')
        self._validate_file_size('vertices')
        self._validate_file_size('triangles')
        return True


    def _get_dirty_files(self, force=False):
        dirty = self._dirty_props
        files = dict()
        if 'vertices' in dirty or force:
            files['vertices'] = \
                self._properties['vertices'].serialize(self.vertices)
        if 'triangles' in dirty or force:
            files['triangles'] = \
                self._properties['triangles'].serialize(self.triangles)
        return files



class Mesh2DGrid(BaseMesh):
    """Contains spatial information of a 2D grid."""
    h1 = Array(
        help='Grid cell widths, x-direction',
        shape=('*',),
        dtype=float
    )
    h2 = Array(
        help='Grid cell widths, y-direction',
        shape=('*',),
        dtype=float
    )
    x0 = Vector(
        help='Origin vector',
        default_value=[0, 0, 0]
    )
    Z = Array(
        help='Node topography',
        shape=('*',),
        dtype=float,
        allow_none=True
    )
    opts = KeywordInstance(
        help='Mesh2D Options',
        klass=_Mesh2DOptions,
        allow_none=True
    )

    @property
    def nN(self):
        """ get number of nodes """
        return (len(self.h1)+1) * (len(self.h2)+1)

    @property
    def nC(self):
        """ get number of cells """
        return len(self.h1) * len(self.h2)

    def _nbytes(self, name=None):
        filenames = ('h1', 'h2', 'x0', 'Z')
        if name in filenames:
            if getattr(self, name, None) is None:
                return 0
            return getattr(self, name).astype('f4').nbytes
        if name is None:
            return sum(self._nbytes(fn) for fn in filenames)
        raise ValueError('Mesh2DGrid cannot calculate the number of '
                         'bytes of {}'.format(name))

    def _on_property_change(self, name, pre, post):
        try:
            if name in ('h1', 'h2', 'x0', 'Z'):
                self._validate_file_size(name)
        except ValueError as err:
            setattr(self, '_p_' + name, pre)
            raise err
        super()._on_property_change(name, pre, post)

    @validator
    def validate(self):
        """Check if mesh content is built correctly"""
        if self.x0.nV != 1:
            raise ValueError('Origin x0 must be only one vector')
        if getattr(self, 'Z', None) is not None and len(self.Z) != self.nN:
            raise ValueError(
                'Length of Z, {zlen}, must equal number of nodes, '
                '{nnode}'.format(
                    zlen=len(self.Z),
                    nnode=self.nN
                )
            )
        self._validate_file_size('h1')
        self._validate_file_size('h2')
        self._validate_file_size('x0')
        self._validate_file_size('Z')
        return True

    def _get_dirty_data(self, force=False):
        datadict = super()._get_dirty_data(force)
        dirty = self._dirty_props
        if ('h1' in dirty or 'h2' in dirty) or force:
            datadict['tensors'] = dumps(dict(
                h1=self.h1.tolist(),
                h2=self.h2.tolist(),
            ))
        if ('h1' in dirty or 'h2' in dirty or 'x0' in dirty) or force:
            datadict['OUV'] = dumps(dict(
                O=self.x0.tolist()[0],
                U=[self.h1.sum().astype(float), 0, 0],
                V=[0, self.h2.sum().astype(float), 0],
            ))
        return datadict

    def _get_dirty_files(self, force=False):
        dirty = self._dirty_props
        files = dict()
        if 'Z' in dirty or (force and getattr(self, 'Z', None) is not None):
            files['Z'] = self._properties['Z'].serialize(self.Z)
        return files


class _SurfaceBinder(DelayedValidator):
    """Contains the data on a 2D surface with location information"""
    location = StringChoices(
        help='Location of the data on mesh',
        choices={
            'CC': ('FACE', 'CELLCENTER'),
            'N': ('NODE', 'VERTEX', 'CORNER')
        }
    )
    data = KeywordInstance(
        help='Data',
        klass=DataArray
    )


class Surface(CompositeResource):
    """Contains all the information about a 2D surface"""
    mesh = Union(
        help='Mesh',
        trait_types=[
            KeywordInstance(klass=Mesh2D),
            KeywordInstance(klass=Mesh2DGrid)
        ]
    )
    data = Repeated(
        help='Data',
        trait=KeywordInstance(klass=_SurfaceBinder),
        allow_none=True
    )
    textures = Repeated(
        help='Textures',
        trait=KeywordInstance(klass=Texture2DImage),
        allow_none=True
    )
    opts = KeywordInstance(
        help='Options',
        klass=_SurfaceOptions,
        allow_none=True
    )

    def _nbytes(self):
        return (self.mesh._nbytes() +
                sum(d.data._nbytes() for d in self.data) +
                sum(t._nbytes() for t in self.textures))

    @validator
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
                    'surface.data[{index}] length {datalen} does not match '
                    '{loc} length {meshlen}'.format(
                        index=ii,
                        datalen=len(dat.data.array),
                        loc=dat.location,
                        meshlen=valid_length
                    )
                )
        super(Surface, self).validate()
        return True


__all__ = ['Surface', 'Mesh2D', 'Mesh2DGrid']
