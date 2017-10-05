#!/usr/bin/python3


import os
from os import getpid
import glob
import json
import uuid
from PIL import Image
from io import BytesIO
import mapnik
import tornado.gen
import tornado.web
from tornado.web import asynchronous
from tornado.web import RequestHandler
from tornado.concurrent import run_on_executor
from concurrent.futures import ThreadPoolExecutor

# from osgeo import ogr
# from osgeo import osr

import config
import tile


Maps = tile.TiledMaps()

if not os.path.exists(config.CACHE_DIR):
    os.mkdir(config.CACHE_DIR)


def cache_map_tile(img, layer, z, x, y):
    ''' @method cache_map_tile
        @description writes map tile to disk
        @param img {mapnik.Image} - mapnik Image to save to disk
        @param layer {str} - layer id/name
        @param z {int} - tile zoom
        @param x {int} - tile column
        @param y {int} - tile row
    '''
    layer_dir = '{0}/{1}'.format(config.CACHE_DIR, layer)
    if not os.path.exists(layer_dir):
        os.mkdir(layer_dir)

    layer_z_dir = '{0}/{1}/{2}'.format(config.CACHE_DIR, layer, z)
    if not os.path.exists(layer_z_dir):
        os.mkdir(layer_z_dir)

    layer_zx_dir = '{0}/{1}/{2}/{3}'.format(config.CACHE_DIR, layer, z, x)
    if not os.path.exists(layer_zx_dir):
        os.mkdir(layer_zx_dir)

    filename = '{0}/{1}/{2}/{3}/{4}.png'.format(config.CACHE_DIR, layer, z, x, y)
    img.save(filename)


def get_cached_map_tile(layer, z, x, y):
    ''' @method get_cached_map_tile
        @description fetches map tile from disk. Returns None if file is not found/
        @param layer {str} - layer id/name
        @param z {int} - tile zoom
        @param x {int} - tile column
        @param y {int} - tile row
        @returns Image.Image
        TODO:
            - Return mapnik.Image
    '''
    filename = '{0}/{1}/{2}/{3}/{4}.png'.format(config.CACHE_DIR, layer, z, x, y)
    if os.path.exists(filename):
        return Image.open(filename)
    return None




class MainHandler(RequestHandler):
    def get(self):
        # source: http://patorjk.com/software/taag/#p=display&f=Slant&t=GeoTileServer
        self.write("GeoTileServer")


class BaseHandler(RequestHandler):

    def generateRequestId(self):
        self.request_id  = uuid.uuid4()

    def getRequestId(self):
        return self.request_id

    def sendXmlResponse(self, xml_data):
        self.set_status(200)
        self.set_header('Content-Type', 'text/xml')
        self.write(xml_data)

    def sendPngResponse(self, img):
        self.set_status(200)
        self.set_header('Content-Type', 'image/png')
        try:
            self.write(img.tostring('png'))
        except:
            output = BytesIO()
            img.save(output, 'png')
            content = output.getvalue()
            self.write(content)


# https://wiki.osgeo.org/wiki/Tile_Map_Service_Specification

class ApiRoot(BaseHandler):
    def get(self):
        baseURL = '/tms'
        xml = ''
        xml += ('<?xml version="1.0" encoding="utf-8" ?>')
        xml += ('<Services>')
        xml += (' <TileMapService title="Tile Map Service" version="1.0" href="' + baseURL + '/1.0"/>')
        xml += ('</Services>')
        self.sendXmlResponse(xml)


class ApiService(BaseHandler):
    def get(self):
        baseURL = '/tms/1.0'
        xml = ''
        xml += ('<?xml version="1.0" encoding="utf-8" ?>')
        xml += ('<TileMapService version="1.0" services="' + baseURL + '">')
        xml += (' <Title>Find Tile Map Service</Title>')
        xml += (' <Abstract></Abstract>')
        xml += (' <TileMaps>')
        directory = os.path.join(config.LAYER_DIR,"*")
        baselayers = glob.glob(directory)
        for baselayer in baselayers:
            layer = os.path.basename(baselayer)
            xml += ('<TileMap title="' + layer + '" srs="EPSG:4326" href="' + baseURL + '/' + layer + '"/>')
        xml += (' </TileMaps>')
        xml += ('</TileMapService>')
        self.sendXmlResponse(xml)


class ApiTileMap(BaseHandler):
    def get(self, layer):
        folder = os.path.join(config.LAYER_DIR,layer)
        if not os.path.exists(folder):
            raise ValueError("files not found")
        baseURL = '/tms/1.0/' + layer
        xml = ''
        xml += ('<?xml version="1.0" encoding="utf-8" ?>')
        xml += ('<TileMap version="1.0" tilemapservice="' + baseURL + '">')
        xml += (' <Title>' + layer + '</Title>')
        xml += (' <Abstract></Abstract>')
        xml += (' <SRS>EPSG:4326</SRS>')
        xml += (' <BoundingBox minx="-180" miny="-90" maxx="180" maxy="90"/>')
        xml += (' <Origin x="-180" y="-90"/>')
        xml += (' <TileFormat width="' + str(tile.TILE_WIDTH) + '" height="' + str(tile.TILE_HEIGHT) + '" ' + 'mime-type="image/png" extension="png"/>')
        xml += (' <TileSets profile="global-geodetic">')
        for zoomLevel in range(0, tile.MAX_ZOOM_LEVEL+1):
            unitsPerPixel = tile._unitsPerPixel(zoomLevel)
            xml += ('<TileSet href="' + baseURL + '/' + str(zoomLevel) + '" units-per-pixel="'+str(unitsPerPixel) + '" order="' + str(zoomLevel) + '"/>')
        xml += (' </TileSets>')
        xml += ('</TileMap>')
        self.sendXmlResponse(xml)


class ApiTileError(BaseHandler):
    def get(self, layer, **args):
        self.write('Oops! Do you mean /tms/1.0/'+layer+'/{z}/{x}/{y}')


class ApiTile(BaseHandler):
    # https://gist.github.com/methane/2185380
    executor = ThreadPoolExecutor(max_workers=config.MAX_WORKERS)

    # def sendTile(self, tile):
        # cache_map_tile(tile, layer, z, x, y)
        # Return image
        # self.sendPngResponse(tile)

    @run_on_executor
    def background_task(self, layer_id, z, x, y):
        folder = os.path.join(config.LAYER_DIR,layer_id)
        if not os.path.exists(folder):
            raise ValueError("files not found")

        if not Maps.hasMap(layer_id):
            # Create map
            m = mapnik.Map(tile.TILE_WIDTH, tile.TILE_HEIGHT)
            # Load mapnik xml stylesheet
            stylesheet = os.path.join(config.LAYER_DIR, str(layer_id), config.STYLESHEET)
            mapnik.load_map(m, stylesheet)
            # Zoom to all features
            m.zoom_all()
            # Render Map Tile
            Maps.addMap(layer_id, m)

        job_id = self.getRequestId()

        renderer = Maps.getMap(layer_id)
        # im = renderer.renderTile(z, x, y, job_id, responseHandler=self)
        im = renderer.renderTile(z, x, y, job_id)
        return im

    @asynchronous
    @tornado.gen.coroutine
    def get(self, layer, z, x, y):
        # TODO:
        #  - Move to __init__()
        self.generateRequestId()
        self.layer_id = layer

        z = int(z)
        x = int(x)
        y = y.replace('.png', '')
        y = int(y)

        im = get_cached_map_tile(layer, z, x, y)
        if im:
            self.sendPngResponse(im)
            return


        im = yield self.background_task(layer, z, x, y)

        # save map tile
        cache_map_tile(im, layer, z, x, y)

        # Return image
        self.sendPngResponse(im)

    # Cancel tile rendering
    # https://stackoverflow.com/questions/25327455/right-way-to-timeout-a-request-in-tornado
    def on_connection_close(self):
        # TODO: cancel tile rendering
        print('closed', self)
        Maps.getMap(self.layer_id).cancelTile(
                                self.getRequestId())
        # self.finish()
