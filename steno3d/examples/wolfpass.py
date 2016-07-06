"""wolfpass.py is a project example using resources from Wolf Pass"""

from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals

from numpy import load as npload

from .base import BaseExample
from ..data import DataArray
from ..line import Line
from ..line import Mesh1D
from ..point import Mesh0D
from ..point import Point
from ..project import Project
from ..surface import Mesh2D
from ..surface import Surface
from ..texture import Texture2DImage
from ..volume import Mesh3DGrid
from ..volume import Volume


class Wolfpass(BaseExample):

    def example_name(self):
        return 'Wolfpass'

    def filenames(self):
        return [
            'AG_gpt.line.npy',
            'AS_ppm.line.npy',
            'AU_gpt.line.npy',
            'CU_pct.line.npy',
            'CU_pct.vol.npy',
            'CU_pct_0.75_1.0_t.cusurf.npy',
            'CU_pct_0.75_1.0_v.cusurf.npy',
            'CU_pct_1.0_1.25_t.cusurf.npy',
            'CU_pct_1.0_1.25_v.cusurf.npy',
            'CU_pct_1.25_1.5_t.cusurf.npy',
            'CU_pct_1.25_1.5_v.cusurf.npy',
            'CU_pct_gt_1.5_t.cusurf.npy',
            'CU_pct_gt_1.5_v.cusurf.npy',
            'CU_pct_lt_0.75_t.cusurf.npy',
            'CU_pct_lt_0.75_v.cusurf.npy',
            'Density.line.npy',
            'MO_ppm.line.npy',
            'Recov.line.npy',
            'S_pct.line.npy',
            'basement_t.lithsurf.npy',
            'basement_v.lithsurf.npy',
            'boreholes_s.line.npy',
            'boreholes_v.line.npy',
            'dacite_data.line.npy',
            'dacite_t.lithsurf.npy',
            'dacite_v.lithsurf.npy',
            'diorite_early_t.lithsurf.npy',
            'diorite_early_v.lithsurf.npy',
            'diorite_late_t.lithsurf.npy',
            'diorite_late_v.lithsurf.npy',
            'dist_to_borehole.lithsurf.npy',
            'dist_to_borehole.vol.npy',
            'drill_loc_v.point.npy',
            'elevation.toposurf.npy',
            'lithology.xsurf.npy',
            'maxdepth.point.npy',
            'ovb_t.lithsurf.npy',
            'ovb_v.lithsurf.npy',
            'section_number.xsurf.npy',
            'topo_t.toposurf.npy',
            'topo_v.toposurf.npy',
            'topography.png',
            'trench.point.npy',
            'vol_h1.vol.npy',
            'vol_h2.vol.npy',
            'vol_h3.vol.npy',
            'vol_x0.vol.npy',
            'xsect_t.xsurf.npy',
            'xsect_v.xsurf.npy',
        ]

    # Borehole Collar Points:
    def collar_vertices(self):
        """collar point vertices"""
        return npload(Wolfpass.fetch_data(filename='drill_loc_v.point.npy',
                                          download_if_missing=False,
                                          verbose=False))

    def collar_data(self):
        """collar raw data

        list of dicts of 'location' and 'data' with 'title' and 'array'
        """
        raw_data = []
        for npyfile in self.filenames:
            if not npyfile.endswith('.point.npy'):
                continue
            if npyfile.endswith('_v.point.npy'):
                continue
            raw_data += [dict(
                location='N',
                data=DataArray(
                    title=npyfile.split('.')[0],
                    array=npload(Wolfpass.fetch_data(filename=npyfile,
                                                     download_if_missing=False,
                                                     verbose=False))
                )
            )]
        return raw_data

    def collar_points(self):
        """Steno3D point resource for borehole collars"""
        return Point(
            project=self._dummy_project,
            mesh=Mesh0D(
                vertices=self.collar_vertices
            ),
            data=self.collar_data,
            title='Borehole Collar Locations'
        )

    # Borehole Lines:
    def borehole_vertices(self):
        """borehole line vertices"""
        return npload(Wolfpass.fetch_data(filename='boreholes_v.line.npy',
                                          download_if_missing=False,
                                          verbose=False))

    def borehole_segments(self):
        """borehole segment vertex indices"""
        return npload(Wolfpass.fetch_data(filename='boreholes_s.line.npy',
                                          download_if_missing=False,
                                          verbose=False))

    def borehole_data(self):
        """borehole raw data

        list of dicts of 'location' and 'data' with 'title' and 'array'
        """
        raw_data = []
        for npyfile in self.filenames:
            if not npyfile.endswith('.line.npy'):
                continue
            if (npyfile.endswith('_v.line.npy') or
                    npyfile.endswith('_s.line.npy')):
                continue
            raw_data += [dict(
                location='CC',
                data=DataArray(
                    title=npyfile.split('.')[0],
                    array=npload(Wolfpass.fetch_data(filename=npyfile,
                                                     download_if_missing=False,
                                                     verbose=False))
                )
            )]
        return raw_data

    def borehole_lines(self):
        """Steno3D line resource for boreholes"""
        return Line(
            project=self._dummy_project,
            mesh=Mesh1D(
                vertices=self.borehole_vertices,
                segments=self.borehole_segments
            ),
            data=self.borehole_data,
            title='Boreholes'
        )

    # CU Percentage Surfaces:
    def cu_prefixes(self):
        """list of prefixes for the different cu pct surfaces"""
        return [fname[:-13] for fname in self.filenames
                if fname.endswith('_v.cusurf.npy')]

    def cu_vertices(self):
        """list of cu pct surface vertices"""
        return [npload(Wolfpass.fetch_data(filename=prefix + '_v.cusurf.npy',
                                           download_if_missing=False,
                                           verbose=False))
                for prefix in self.cu_prefixes]

    def cu_triangles(self):
        """list of cu pct surface triangles"""
        return [npload(Wolfpass.fetch_data(filename=prefix + '_t.cusurf.npy',
                                           download_if_missing=False,
                                           verbose=False))
                for prefix in self.cu_prefixes]

    def cu_surfaces(self):
        """tuple of  Steno3D surface resources for each CU percent range"""
        cu_surfs = tuple()
        for i, prefix in enumerate(self.cu_prefixes):
            cu_surfs += (Surface(
                project=self._dummy_project,
                mesh=Mesh2D(
                    vertices=self.cu_vertices[i],
                    triangles=self.cu_triangles[i]
                ),
                title=prefix
            ),)
        return cu_surfs

    # Lithology Surfaces:
    def lith_prefixes(self):
        """list of prefixes for the different lithology surfaces"""
        return [fname[:-15] for fname in self.filenames
                if fname.endswith('_v.lithsurf.npy')]

    def lith_vertices(self):
        """list of lithology surface vertices"""
        return [npload(Wolfpass.fetch_data(filename=prefix + '_v.lithsurf.npy',
                                           download_if_missing=False,
                                           verbose=False))
                for prefix in self.lith_prefixes]

    def lith_triangles(self):
        """list of lithology surface triangles"""
        return [npload(Wolfpass.fetch_data(filename=prefix + '_t.lithsurf.npy',
                                           download_if_missing=False,
                                           verbose=False))
                for prefix in self.lith_prefixes]

    def lith_diorite_early_data(self):
        """data for early diorite surface"""
        return dict(
            location='N',
            data=DataArray(
                title='dist_to_borehole',
                array=npload(
                    Wolfpass.fetch_data(
                        filename='dist_to_borehole.lithsurf.npy',
                        download_if_missing=False,
                        verbose=False
                    )
                )
            )
        )

    def lith_surfaces(self):
        """tuple of  Steno3D surface resources for each CU percent range"""
        lith_surfs = tuple()
        for i, prefix in enumerate(self.lith_prefixes):
            if prefix == 'diorite_early':
                lith_data = [self.lith_diorite_early_data]
            else:
                lith_data = []
            lith_surfs += (Surface(
                project=self._dummy_project,
                mesh=Mesh2D(
                    vertices=self.lith_vertices[i],
                    triangles=self.lith_triangles[i]
                ),
                data=lith_data,
                title=prefix
            ),)
        return lith_surfs

    # Topography Surfaces:
    def topo_vertices(self):
        """topography vertices"""
        return npload(Wolfpass.fetch_data(filename='topo_v.toposurf.npy',
                                          download_if_missing=False,
                                          verbose=False))

    def topo_triangles(self):
        """topography triangles"""
        return npload(Wolfpass.fetch_data(filename='topo_t.toposurf.npy',
                                          download_if_missing=False,
                                          verbose=False))

    def topo_texture(self):
        """topography surface image texture"""
        return Texture2DImage(
            O=[443200, 491750, 0],
            U=[4425, 0, 0],
            V=[0, 3690, 0],
            image=Wolfpass.fetch_data(filename='topography.png',
                                      download_if_missing=False,
                                      verbose=False)
        )

    def topo_data(self):
        """elevation data"""
        return dict(
            location='N',
            data=DataArray(
                title='elevation',
                array=npload(Wolfpass.fetch_data(filename='elevation.toposurf.npy',
                                                 download_if_missing=False,
                                                 verbose=False))
            )
        )

    def topo_surface(self):
        """Steno3D surface resource with topo data and surface imagery"""
        return Surface(
            project=self._dummy_project,
            mesh=Mesh2D(
                vertices=self.topo_vertices,
                triangles=self.topo_triangles
            ),
            data=self.topo_data,
            textures=self.topo_texture,
            title='Topography Surface'
        )

    # Cross-section Surface:
    def xsect_vertices(self):
        """cross section vertices"""
        return npload(Wolfpass.fetch_data(filename='xsect_v.xsurf.npy',
                                          download_if_missing=False,
                                          verbose=False))

    def xsect_triangles(self):
        """cross section triangles"""
        return npload(Wolfpass.fetch_data(filename='xsect_t.xsurf.npy',
                                          download_if_missing=False,
                                          verbose=False))

    def xsect_data(self):
        """cross section raw data"""
        raw_data = []
        for npyfile in self.filenames:
            if not npyfile.endswith('.xsurf.npy'):
                continue
            if (npyfile.endswith('_v.xsurf.npy') or
                    npyfile.endswith('_t.xsurf.npy')):
                continue
            raw_data += [dict(
                location='CC',
                data=DataArray(
                    title=npyfile.split('.')[0],
                    array=npload(Wolfpass.fetch_data(filename=npyfile,
                                                     download_if_missing=False,
                                                     verbose=False))
                    )
            )]
        return raw_data

    def xsect_surface(self):
        """Steno3D surface resource of cross sections"""
        return Surface(
            project=self._dummy_project,
            mesh=Mesh2D(
                vertices=self.xsect_vertices,
                triangles=self.xsect_triangles
            ),
            data=self.xsect_data,
            title='Cross-Sections'
        )

    # Lithology Volume:
    def lith_tensor(self):
        """(h1, h2, h3, x0) for lith volume"""
        return (
            npload(Wolfpass.fetch_data(filename='vol_h1.vol.npy',
                                       download_if_missing=False,
                                       verbose=False)),
            npload(Wolfpass.fetch_data(filename='vol_h2.vol.npy',
                                       download_if_missing=False,
                                       verbose=False)),
            npload(Wolfpass.fetch_data(filename='vol_h3.vol.npy',
                                       download_if_missing=False,
                                       verbose=False)),
            npload(Wolfpass.fetch_data(filename='vol_x0.vol.npy',
                                       download_if_missing=False,
                                       verbose=False))
        )

    def lith_data(self):
        """raw data for lith volume"""
        raw_data = []
        for npyfile in self.filenames:
            if not npyfile.endswith('.vol.npy'):
                continue
            if npyfile.startswith('vol_'):
                continue
            raw_data += [dict(
                location='CC',
                data=DataArray(
                    title=npyfile.split('.')[0],
                    array=npload(Wolfpass.fetch_data(filename=npyfile,
                                                     download_if_missing=False,
                                                     verbose=False))
                )
            )]
        return raw_data

    def lith_volume(self):
        """Steno3D volume resource of lithology"""
        return Volume(
            project=self._dummy_project,
            mesh=Mesh3DGrid(
                h1=self.lith_tensor[0],
                h2=self.lith_tensor[1],
                h3=self.lith_tensor[2],
                x0=self.lith_tensor[3]
            ),
            data=self.lith_data,
            title='Lithology Volume'
        )

    def project(self):
        """empty Steno3D project"""
        return Project(
            title='Wolf Pass'
        )

    def _dummy_project(self):
        """Steno3D project for initializing resources"""
        return Project()

    def get_resources(self):
        """get a copy of the Wolfpass resources"""
        res = (self.collar_points, self.borehole_lines,)
        res += self.cu_surfaces
        res += self.lith_surfaces
        res += (self.topo_surface, self.xsect_surface, self.lith_volume)
        return res

    def get_project(self):
        """get a copy of the Wolfpass project"""
        proj = self.project
        proj.resources = self.get_resources()
        for r in proj.resources:
            r.project = proj
        return proj

    def get_project_topo(self):
        res = (self.collar_points, self.topo_surface,)
        proj = self.project
        proj.resources = res
        proj.title = 'Topography'
        proj.description = ('Topography, surface imagery, '
                            'and borehole collar locations')
        for r in proj.resources:
            r.project = proj
        return proj

    def get_project_dacite(self):
        res = (self.borehole_lines,)
        res += tuple([r for r in self.lith_surfaces
                      if r.title == 'ovb' or r.title == 'dacite'])
        proj = self.project
        proj.resources = res
        proj.title = 'Wolf Pass'
        proj.description = 'Boreholes and dacite formation'
        for r in proj.resources:
            r.project = proj
        return proj
