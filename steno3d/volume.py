"""volume.py contains the Volume composite resource for steno3d"""

from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals

from builtins import super
from json import dumps

import properties

from .base import BaseMesh
from .base import CompositeResource
from .options import ColorOptions
from .options import MeshOptions


class _Mesh3DOptions(MeshOptions):
    pass


class _VolumeOptions(ColorOptions):
    pass


class Mesh3DGrid(BaseMesh):
    """Contains spatial information of a 3D grid volume."""

    h1 = properties.Array(
        'Tensor cell widths, x-direction',
        shape=('*',),
        dtype=float,
        required=True
    )
    h2 = properties.Array(
        'Tensor cell widths, y-direction',
        shape=('*',),
        dtype=float,
        required=True
    )
    h3 = properties.Array(
        'Tensor cell widths, z-direction',
        shape=('*',),
        dtype=float,
        required=True
    )
    x0 = properties.Vector(
        'Origin vector',
        default=[0, 0, 0]
    )
    opts = properties.Pointer(
        'Mesh3D Options',
        ptype=_Mesh3DOptions
    )

    @property
    def nN(self):
        """ get number of nodes """
        return (len(self.h1)+1) * (len(self.h2)+1) * (len(self.h3)+1)

    @property
    def nC(self):
        """ get number of cells """
        return len(self.h1) * len(self.h2) * len(self.h3)

    def nbytes(self, name=None):
        filenames = ('h1', 'h2', 'h3', 'x0')
        if name in filenames:
            return getattr(self, name).nbytes
        elif name is None:
            return sum(getattr(self, fn).nbytes for fn in filenames)
        raise ValueError('Mesh3DGrid cannot calculate the number of '
                         'bytes of {}'.format(name))

    def _on_property_change(self, name, pre, post):
        try:
            if name in ('h1', 'h2', 'h3', 'x0'):
                self._validate_file_size(name)
        except ValueError as err:
            setattr(self, '_p_' + name, pre)
            raise err
        super()._on_property_change(name, pre, post)

    @properties.validator
    def validate(self):
        """Check if mesh content is built correctly"""
        if self.x0.nV != 1:
            raise ValueError('Origin x0 must be only one vector')
        self._validate_file_size('h1')
        self._validate_file_size('h2')
        self._validate_file_size('h3')
        self._validate_file_size('x0')
        return True

    def _get_dirty_data(self, force=False):
        datadict = super()._get_dirty_data(force)
        dirty = self._dirty_props
        # datadict = dict()
        if force or ('h1' in dirty or 'h2' in dirty or 'h3' in dirty):
            datadict['tensors'] = dumps(dict(
                h1=self.h1.tolist(),
                h2=self.h2.tolist(),
                h3=self.h3.tolist()
            ))
        if force or ('h1' in dirty or 'h2' in dirty or 'h3' in dirty or
                     'x0' in dirty):
            datadict['OUVZ'] = dumps(dict(
                O=self.x0.tolist()[0],
                U=[self.h1.sum(), 0, 0],
                V=[0, self.h2.sum(), 0],
                Z=[0, 0, self.h3.sum()]
            ))
        return datadict


class _VolumeBinder(properties.PropertyClass):
    """Contains the data on a 3D volume with location information"""
    location = properties.String(
        'Location of the data on mesh',
        required=True,
        choices={
            'CC': ('CELLCENTER'),
            # 'N': ('NODE', 'VERTEX', 'CORNER')
        }
    )
    data = properties.Pointer(
        'Data',
        ptype='DataArray',
        required=True
    )


class Volume(CompositeResource):
    """Contains all the information about a 3D volume"""
    mesh = properties.Pointer(
        'Mesh',
        ptype=Mesh3DGrid,
        required=True
    )
    data = properties.Pointer(
        'Data',
        ptype=_VolumeBinder,
        repeated=True,
        required=True
    )
    opts = properties.Pointer(
        'Options',
        ptype=_VolumeOptions
    )

    def nbytes(self):
        return self.mesh.nbytes() + sum(d.data.nbytes() for d in self.data)

    @properties.validator
    def validate(self):
        """Check if resource is built correctly"""
        for ii, dat in enumerate(self.data):
            assert dat.location == 'CC'  # in ('N', 'CC')
            valid_length = (
                self.mesh.nC if dat.location == 'CC'
                else self.mesh.nN
            )
            if len(dat.data.array) != valid_length:
                raise ValueError(
                    'volume.data[{index}] length {datalen} does not match '
                    '{loc} length {meshlen}'.format(
                        index=ii,
                        datalen=len(dat.data.array),
                        loc=dat.location,
                        meshlen=valid_length
                    )
                )
        super(Volume, self).validate()
        return True


__all__ = ['Volume', 'Mesh3DGrid']
