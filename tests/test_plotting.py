from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals

import unittest

import numpy as np

import steno3d
from steno3d import plotting as plt

class TestPlotting(unittest.TestCase):

    def test_scatter(self):
        x = np.array([0., 1, 2, 3, 4])
        y = [5, 6, 7, 8, 9]
        z = (10., 11, 12, 13, 14)

        XY = np.c_[x, y]
        XYZ = np.c_[x, y, z]

        d1 = [15, 16, 17, 18, 19]
        d2 = [20., 21, 22, 23, 24]

        # documented to work
        fig = plt.scatter(x, y, z)
        plt.scatter(fig, x, y, z)

        fig.scatter(XY)
        fig.scatter(XYZ)
        fig.scatter(x, y)
        fig.scatter(x, y, z)
        fig.scatter(x, y, z, d1)
        fig.scatter(x, y, z, {'D1': d1, 'D2': d2})
        fig.scatter(x, y, z, title='pts', color='r', opacity=.5)

        fig.scatter(x=x, z=z)
        fig.scatter(y=y, z=z)
        fig.scatter(data=d1, coords=XYZ)

        # Should display warning then ignore size
        fig.scatter(x, y, z, size=d1)

        # test to make sure they worked
        assert isinstance(fig, steno3d.Project)
        assert len(fig.resources) == 13
        assert isinstance(fig.resources[0], steno3d.Point)
        assert np.all(
            fig.resources[0].mesh.vertices == fig.resources[1].mesh.vertices
        )
        assert np.all(
            fig.resources[0].mesh.vertices == fig.resources[3].mesh.vertices
        )
        assert np.all(
            fig.resources[2].mesh.vertices == fig.resources[4].mesh.vertices
        )
        assert np.all(
            fig.resources[0].mesh.vertices == fig.resources[5].mesh.vertices
        )
        assert np.all(
            fig.resources[0].mesh.vertices == fig.resources[6].mesh.vertices
        )
        assert len(fig.resources[6].data) == 1
        assert np.all(
            fig.resources[0].mesh.vertices == fig.resources[7].mesh.vertices
        )
        assert len(fig.resources[7].data) == 2
        t1 = fig.resources[7].data[0].data.title
        t2 = fig.resources[7].data[1].data.title
        assert t1 in ('D1', 'D2') and t2 in ('D1', 'D2') and t1 != t2
        assert np.all(
            fig.resources[0].mesh.vertices == fig.resources[8].mesh.vertices
        )
        assert fig.resources[8].title == 'pts'
        assert fig.resources[8].opts.color == (255, 0, 0)
        assert fig.resources[8].opts.opacity == .5
        assert np.all(
            fig.resources[0].mesh.vertices == fig.resources[11].mesh.vertices
        )
        assert np.all(
            fig.resources[0].mesh.vertices == fig.resources[12].mesh.vertices
        )

        # should error
        self.assertRaises(plt.PlotError, lambda: fig.scatter())
        self.assertRaises(plt.PlotError, lambda: fig.scatter(x))
        self.assertRaises(plt.PlotError, lambda: fig.scatter(y=y))
        self.assertRaises(plt.PlotError, lambda: fig.scatter(x, y, [0, 1, 2]))
        self.assertRaises(plt.PlotError, lambda:
                          fig.scatter(x, y, z, [0, 1, 2]))
        self.assertRaises(plt.PlotError, lambda: fig.scatter(XY, z))
        self.assertRaises(plt.PlotError, lambda: fig.scatter(XYZ, z))


    def test_surf(self):
        x = [0, 1, 2, 3, 4, 5]
        y = [0, 2, 4, 6, 8]
        Z = [[0, 0, 0, 0, 0],
             [0, 1, 1, 1, 0],
             [0, 1, 2, 1, 0],
             [0, 1, 2, 1, 0],
             [0, 1, 1, 1, 0],
             [0, 0, 0, 0, 0]]
        Zface = (np.array(Z)[:-1, :-1] + np.array(Z)[1:, 1:])/2

        # documented to work
        fig = plt.surf(x, y, Z)
        plt.surf(fig, x, y, Z)

        fig.surf(Z)
        fig.surf(x, y, Z)
        fig.surf(x, y, np.array(Z).T)
        fig.surf(x, y, np.array(Z).flatten())

        fig.surf(x, y, Z, data=Z)
        fig.surf(x, y, Z, data={'D1': Z,
                                'D2': np.array(Z).T,
                                'D3': np.array(Z).flatten(),
                                'D4': Zface,
                                'D5': Zface.T,
                                'D6': Zface.flatten()})






if __name__ == '__main__':
    unittest.main()
