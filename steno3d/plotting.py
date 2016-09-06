from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals

import numpy as np

import steno3d

ARRAY_TYPES = (list, tuple, np.ndarray)

FUNC_DOC = """Steno3D plotting function {func}

    Usage:
        {func}(fig, ...)
        {func}(..., figure=fig)

        fig = {func}(...)

    These methods call fig.{func}(...), creating a new figure
    if one is not provided.

    For full {func} documentation see Figure.{func}.
    """


class Figure(steno3d.Project):
    """class Figure

    A Figure is Steno3D Project with additional plotting functions to
    produce resources
    """

    def scatter(self, x=None, y=None, z=None, data=None, **kwargs):
        """scatter adds steno3d.Point to a Figure

        Usage:
            scatter(coords)
            scatter(x, y, z)

            scatter(..., data)

            scatter(..., **kwargs)

        Inputs:
            coords:     n x 2 or n x 3 matrix corresponding
                        to [x, y] or [x, y, z], respectively
            x, y, z:    n x 1 arrays of equal length. If one is omitted,
                        scatter will produce a 2D dataset
            data:       n x 1 array for color data OR dictionary with
                        data titles as keys and n x 1 arrays as values
            kwargs:     Additional available keyword arguments:
                            title (of scatter plot)
                            color (of points)
                            opacity (of points)

        """
        if x is None:
            x = kwargs.pop('coords', None)

        if x is None and y is None and z is None:
            raise PlotError('No input geometry provided. Please refer to '
                            'documentation for usage.')

        if not (x is None or isinstance(x, ARRAY_TYPES) and
                y is None or isinstance(y, ARRAY_TYPES) and
                z is None or isinstance(z, ARRAY_TYPES)):
            raise PlotError('Scatter geometry must be lists')

        if x is None and (y is None or z is None):
            raise PlotError('Cannot create scatter plot from only y or z data')

        [x, y, z] = [np.array(a).astype(float) if a is not None else None
                     for a in [x, y, z]]

        if x is not None and y is None and z is None:
            if x.ndim != 2 or x.shape[1] not in (2, 3):
                raise PlotError('Geometry input for scatter must be n x 2 '
                                'or n x 3 matrix, or x/y/z must be defined '
                                'separately.')
            if x.shape[1] == 2:
                x = np.c_[x, np.zeros(x.shape[0])]
            xyz = x
        else:
            if x is None:
                x = np.zeros(y.shape[0])
            if y is None:
                y = np.zeros(x.shape[0])
            if z is None:
                z = np.zeros(x.shape[0])

            if any([a.ndim != 1 or a.shape[0] != x.shape[0]
                    for a in [x, y, z]]):
                raise PlotError('x, y, and z must be 1D arrays of equal '
                                'length.')

            xyz = np.c_[x, y, z]

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
        steno3d.Point(
            project=self,
            title=kwargs.pop('title', ''),
            mesh=steno3d.Mesh0D(
                vertices=xyz
            ),
            data=[
                dict(
                    location='N',
                    data=steno3d.DataArray(
                        title=k,
                        array=data[k]
                    )
                ) for k in data
            ],
            opts=dict(
                color=kwargs.pop('color', 'random'),
                opacity=kwargs.pop('opacity', 1)
            )
        )

        self._kwwarn(**kwargs)


    def surf(self, x=None, y=None, z=None, data=None, **kwargs):
        """surf adds steno3d.Surface to a Figure

        Usage:
            surf(Z)
            surf(x, y, z)

            surf(..., data)

            surf(..., **kwargs)

        Inputs:
            Z:      m x n matrix of grid surface height values
            x:      m x 1 array of surface x-values
            y:      n x 1 array of surface y-values
            z:      grid surface height values of
                    shape m x n, n x m, or (m*n) x 1
            data:   grid color data of shape m x n or (m*n) x 1 for node data
                    or (m-1) x (n-1) or (m-1)*(n-1) x 1 for grid cell data
                    - OR -
                    a dictionary with data titles as keys and arrays of the
                    above shapes as values
            kwargs: Additional available keyword arguments:
                        title (of surface plot)
                        color (of surface)
                        opacity (of surface, range 0-1)
                        wireframe (display surface wireframe, boolean)

        """
        if z is None:
            z = kwargs.pop('Z', None)

        if x is None and y is None and z is None:
            raise PlotError('No input geometry provided. Please refer to '
                            'documentation for usage.')

        if not (x is None or isinstance(x, ARRAY_TYPES) and
                y is None or isinstance(y, ARRAY_TYPES) and
                z is None or isinstance(z, ARRAY_TYPES)):
            raise PlotError('Surface geometry must be lists or matrices')

        [x, y, z] = [np.array(a).astype(float) if a is not None else None
                     for a in [x, y, z]]

        if z is None and x.ndim == 2 and 1 not in x.shape:
            z = x
            x = None

        if z is None:
            raise PlotError('No surface z values provided')

        if x is None and y is None:
            if z.ndim == 2 and 1 not in z.shape:
                x = np.array(range(z.shape[0])).astype(float)
                y = np.array(range(z.shape[1])).astype(float)
            else:
                raise PlotError('When not providing, x or y values, z must '
                                'be a 2D matrix')

        if x is None or y is None or z is None:
            raise PlotError('Surface geometry provided is incomplete. Please '
                            'refer to documentation for usage.')

        if x.ndim > 1 or y.ndim > 1:
            raise PlotError('x and y values must be 1D arrays')

        if z.ndim > 2:
            raise PlotError('z value must be 1D array or 2D matrix')

        if z.ndim == 2:
            if z.shape == (y.shape[0], x.shape[0]):
                z = z.flatten('F')
            elif z.shape == (x.shape[0], y.shape[0]):
                z = z.flatten()
            else:
                raise PlotError('x and y lengths do not correspond to z '
                                'dimensions')
        elif z.shape[0] != x.shape[0]*y.shape[0]:
            raise PlotError('Product of x and y lengths does not correspond '
                            'to length of z')

        if data is None:
            data = dict()

        if not isinstance(data, dict):
            data = {'': data}

        for key in data:
            if not isinstance(data[key], ARRAY_TYPES):
                raise PlotError('Data must be provided as an array or a '
                                'dictionary of {title: array}')
            data[key] = np.array(data[key])
            if (
                data[key].ndim == 1 and
                data[key].shape[0] in (
                    x.shape[0]*y.shape[0], (x.shape[0]-1)*(y.shape[0]-1)
                )
            ):
                continue
            if (
                data[key].ndim == 2 and
                data[key].shape in (
                    (y.shape[0], x.shape[0]),
                    (y.shape[0]-1, x.shape[0]-1)
                )
            ):
                data[key] = data[key].flatten('F')
                continue
            if (
                data[key].ndim == 2 and
                data[key].shape in (
                    (x.shape[0], y.shape[0]),
                    (x.shape[0]-1, y.shape[0]-1)
                )
            ):
                data[key] = data[key].flatten()
                continue
            raise PlotError('Data must be 1D array or 2D matrix with shape '
                            'corresponding to x and y geometry')

        self._surf(x, y, z, data, **kwargs)

    def _surf(self, x, y, z, data, **kwargs):
        h1 = np.diff(x)
        h2 = np.diff(y)

        s = steno3d.Surface(
            project=self,
            title=kwargs.pop('title', ''),
            mesh=steno3d.Mesh2DGrid(
                h1=h1,
                h2=h2,
                x0=[x[0], y[0], 0],
                Z=z,
                opts=dict(
                    wireframe=kwargs.pop('wireframe', False)
                )
            ),
            opts=dict(
                color=kwargs.pop('color', 'random'),
                opacity=kwargs.pop('opacity', 1)
            )
        )
        s.data = [
            dict(
                location='N' if data[k].shape[0] == s.mesh.nN else 'CC',
                data=steno3d.DataArray(
                    title=k,
                    array=data[k]
                )
            ) for k in data
        ]

        self._kwwarn(**kwargs)

    @staticmethod
    def _kwwarn(**kwargs):
        for k in kwargs:
            print('Warning: Unused keyword argument \'{}\''.format(k))


def _generate_plotfunc(k, doc):
    """Function to generate generic global plotting functions

    These functions are all nearly identical for every plotting function.
    They simply extract the figure input or create a new figure, then call
    the corresponding figure method
    """

    def plotfunc(*args, **kwargs):
        if len(args) > 0 and isinstance(args[0], Figure):
            fig = args[0]
            args = args[1:]
        else:
            fig = kwargs.pop('figure', Figure())
        getattr(fig, k)(*args, **kwargs)
        return fig

    plotfunc.__doc__ = doc
    return plotfunc

# Create a global plotting function for every Figure plotting method
for k in Figure.__dict__:
    if k[0] == '_' or not callable(Figure.__dict__[k]):
        continue
    globals()[k] = _generate_plotfunc(k, FUNC_DOC.format(func=k))


class PlotError(ValueError):
    pass
