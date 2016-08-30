from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals

import numpy as np

import steno3d

ARRAY_TYPES = (list, tuple, np.ndarray)

def scatter(*args, **kwargs):
    """scatter adds steno3d.Point to a Figure

    Usage:
        scatter(fig, ...)
        fig = scatter(...)

    These methods call fig.scatter(...), creating a new figure
    if one is not provided.

    For full scatter documentation see Figure.scatter.
    """
    if 'figure' in kwargs:
        fig = kwargs.pop('figure')
    elif len(args) > 0 and isinstance(args[0], Figure):
        fig = args[0]
        args = args[1:]
    else:
        fig = Figure()
    fig.scatter(*args, **kwargs)
    return fig


class Figure(steno3d.Project):
    """class Figure

    A Figure is Steno3D Project with additional plotting functions to
    produce resources
    """

    def scatter(self, x=None, y=None, z=None, data=None, **kwargs):
        """scatter adds steno3d.Point to a Figure

        Usage:
            scatter(XY)
            scatter(XYZ)
            scatter(x, y, z)

            scatter(..., data)

            scatter(..., **kwargs)

        Inputs:
            XY:         n x 2 matrix corresponding to [x, y]
            XYZ:        n x 3 matrix corresponding to [x, y, z]
            x, y, z:    n x 1 arrays of equal length. If one is omitted,
                        scatter will produce a 2D dataset
            data:       n x 1 array for color data OR dictionary with
                        data titles as keys and n x 1 arrays as values
            kwargs:     color

        """

        if 'XY' in kwargs:
            x = kwargs.pop('XY')
        if 'XYZ' in kwargs:
            x = kwargs.pop('XYZ')

        if x is None and y is None and z is None:
            raise PlotError('No input geometry provided. Please refer to '
                            'documentation for usage.')

        if not (x is None or isinstance(x, ARRAY_TYPES) and
                y is None or isinstance(y, ARRAY_TYPES) and
                z is None or isinstance(z, ARRAY_TYPES)):
            raise PlotError('Scatter geometry must be lists')

        if x is None and (y is None or z is None):
            raise PlotError('Cannot create scatter plot from only y or z data')

        [x, y, z] = [np.array(a) if a is not None else None for a in [x, y, z]]

        if x is not None and y is None and z is None:
            if x.ndim != 2 or x.shape[1] not in (2, 3):
                raise PlotError('Geometry input for scatter must be n x 2 '
                                'or n x 3 matrix, or x/y/z must be defined '
                                'separately.')
            if x.shape[1] == 2:
                x = np.c_[x, np.zeros(x.shape[0])]
            xyz = x

        if x is None:
            x = np.zeros(y.shape[0])
        if y is None:
            y = np.zeros(x.shape[0])
        if z is None:
            z = np.zeros(x.shape[0])

        if any([a.ndim != 1 or a.shape[0] != x.shape[0] for a in [x, y, z]]):
            raise PlotError('x, y, and z must be 1D arrays of equal length.')

        xzy = np.c_[x, y, z]

        if data is None:
            data = dict()

        if not isinstance(data, dict):
            data = {'': data}

        for key in data:
            if not isinstance(data[key], ARRAY_TYPES):
                raise PlotError('Data must be provided as an array or a '
                                'dictionary of {title: array}')
            data[key] = np.array(data[key])
            if data[key].ndim != 1 or data[key].shape[0] != xyz.shape[0]:
                raise PlotError('Data must be 1D arrays with length equal '
                                'to corresponding geometry')

        self._scatter(xyz, data, **kwargs)

    def _scatter(self, xyz, data, **kwargs):
        pass






class PlotError(ValueError):
    pass
