#!/usr/bin/python3

"""
    Source:
        https://github.com/rshk/render-tiles

"""

from collections import namedtuple
import math
import mapnik
import worker


# ============================================================
#                      MAP TILE SETTINGS
# ============================================================

MIN_ZOOM_LEVEL = 1
MAX_ZOOM_LEVEL = 22

def _unitsPerPixel(zoomLevel):
    return 0.703125 / math.pow(2, zoomLevel)

# Google Mercator - EPSG:900913
GOOGLEMERC = ('+proj=merc +a=6378137 +b=6378137 +lat_ts=0.0 +lon_0=0.0 '
              '+x_0=0.0 +y_0=0 +k=1.0 +units=m +nadgrids=@null +no_defs')
DATA_PROJECTION = mapnik.Projection(GOOGLEMERC)
TILE_WIDTH = 256
TILE_HEIGHT = 256

def deg2num(lat_deg, lon_deg, zoom):
    """Convert coordinates to tile number"""
    lat_rad = math.radians(lat_deg)
    n = 2.0 ** zoom
    xtile = int((lon_deg + 180.0) / 360.0 * n)
    ytile = int((
        1.0 - math.log(math.tan(lat_rad) + (1 / math.cos(lat_rad)))
        / math.pi) / 2.0 * n)
    tile_coords = namedtuple('TileCoords', 'x,y')
    return tile_coords(x=xtile, y=ytile)

def num2deg(xtile, ytile, zoom):
    """Convert tile number to coordinates (of the upper corner)"""
    n = 2.0 ** zoom
    lon_deg = xtile / n * 360.0 - 180.0
    lat_rad = math.atan(math.sinh(math.pi * (1 - 2 * ytile / n)))
    lat_deg = math.degrees(lat_rad)
    return mapnik.Coord(y=lat_deg, x=lon_deg)



# ============================================================
#                        TILE RENDERER
# ============================================================

class TiledMapRenderer(object):
    """ Mapnik Slippy Map - Tile Renderer
    """
    def __init__(self, mapobj):
        self.jobs = {}
        self.m = mapobj
        self.GOOGLEMERC = ('+proj=merc +a=6378137 +b=6378137 +lat_ts=0.0 +lon_0=0.0 '
              '+x_0=0.0 +y_0=0 +k=1.0 +units=m +nadgrids=@null +no_defs')
        self.DATA_PROJECTION = mapnik.Projection(GOOGLEMERC)
        self.TILE_WIDTH = 256
        self.TILE_HEIGHT = 256

    def deg2num(self, lat_deg, lon_deg, zoom):
        """Convert coordinates to tile number"""
        lat_rad = math.radians(lat_deg)
        n = 2.0 ** zoom
        xtile = int((lon_deg + 180.0) / 360.0 * n)
        ytile = int((
            1.0 - math.log(math.tan(lat_rad) + (1 / math.cos(lat_rad)))
            / math.pi) / 2.0 * n)
        tile_coords = namedtuple('TileCoords', 'x,y')
        return tile_coords(x=xtile, y=ytile)

    def num2deg(self, xtile, ytile, zoom):
        """Convert tile number to coordinates (of the upper corner)"""
        n = 2.0 ** zoom
        lon_deg = xtile / n * 360.0 - 180.0
        lat_rad = math.atan(math.sinh(math.pi * (1 - 2 * ytile / n)))
        lat_deg = math.degrees(lat_rad)
        return mapnik.Coord(y=lat_deg, x=lon_deg)

    def renderTile(self, z, x, y, job_id, responseHandler=None):
        """
        renders map tile
            :param z: Zoom level
            :param x: Tile horizontal position
            :param y: Tile vertical position
        """
        # Set Tile Bounds
        topleft = self.num2deg(x, y, z)
        bottomright = self.num2deg(x + 1, y + 1, z)
        # Bounding box for the tile
        bbox = mapnik.Box2d(topleft, bottomright)
        bbox = self.DATA_PROJECTION.forward(bbox)
        # Zoom to bounding box
        self.m.zoom_to_box(bbox)
        # Set buffer
        MIN_BUFFER = 256
        self.m.buffer_size = max(self.m.buffer_size, MIN_BUFFER)
        # Render image with default Agg renderer
        im = mapnik.Image(TILE_WIDTH, TILE_WIDTH)

        if not responseHandler:
            mapnik.render(self.m, im)
            return im

        # cancel requests -->
        im = worker.RenderTile(job_id, self.m, im)
        responseHandler.sendPngResponse(im)
        return im

    def cancelTile(self, job_id):
        worker.CancelTileRender(job_id)



class TiledMaps(object):

    def __init__(self):
        self._mmaps = {}

    def addMap(self, layer_id, m_map):
        if self.hasMap(layer_id):
            raise ValueError(layer_id, 'already exists')
        self._mmaps[layer_id] = TiledMapRenderer(m_map)

    def getMap(self, layer_id):
        if self.hasMap(layer_id):
            return self._mmaps[layer_id]
        return None

    def hasMap(self, layer_id):
        return layer_id in self._mmaps

    def getKeys(self):
        return list(self._mmaps.keys())
