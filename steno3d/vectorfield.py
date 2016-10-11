"""point.py contains the Point composite resource for steno3d"""

from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals

from builtins import super
from six import string_types

from numpy import ndarray
from traitlets import observe, validate

from .base import BaseMesh
from .base import CompositeResource
from .data import DataArray
from .options import ColorOptions
from .options import Options
from .texture import Texture2DImage
from .traits import Array, HasSteno3DTraits, KeywordInstance, Repeated, String

from .point import Mesh0D, _PointBinder


class _VectorFieldOptions(ColorOptions):
    pass



class VectorField(CompositeResource):
    """Contains all the information about a vector field"""

    _resource_class = 'vector'

    mesh = KeywordInstance(
        help='Mesh',
        klass=Mesh0D
    )
    vectors = Array(
        help='Vector',
        shape=('*', 3),
        dtype=float
    )
    data = Repeated(
        help='Data',
        trait=KeywordInstance(klass=_PointBinder),
        allow_none=True
    )
    opts = KeywordInstance(
        help='Options',
        klass=_VectorFieldOptions,
        allow_none=True
    )

    def _nbytes(self):
        return (self.mesh._nbytes() + self.vectors.astype('f4').nbytes +
                sum(d.data._nbytes() for d in self.data))

    @validate('data')
    def _validate_data(self, proposal):
        """Check if resource is built correctly"""
        for ii, dat in enumerate(proposal['value']):
            assert dat.location == 'N'
            valid_length = proposal['owner'].mesh.nN
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
        return proposal['value']

    def _get_dirty_files(self, force=False):
        files = {}
        dirty = self._dirty_traits
        if 'vectors' in dirty or force:
            files['vectors'] = \
                self.traits()['vectors'].serialize(self.vectors)
        return files


__all__ = ['VectorField']
