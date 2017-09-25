#!/usr/bin/env python
import argparse
import mapnik
import numpy
import math
from osgeo import ogr
from osgeo import osr


# label_font = "DejaVu Sans Book"
label_font = "DejaVu Sans Bold"


def getAreaStatistics(shapefile):
    areas = []
    driver = ogr.GetDriverByName("ESRI Shapefile")
    datasource = driver.Open(shapefile, 0)
    layer = datasource.GetLayer()
    for feature in layer:
        geom = feature.GetGeometryRef()
        areas.append( geom.GetArea() )
    return {
        'mean',   numpy.mean(areas),
        'stddev', numpy.std(areas),
        'min',   numpy.min(areas),
        'max',   numpy.max(areas)
    }


# http://wiki.openstreetmap.org/wiki/MinScaleDenominator
zoomScales = {
    '0':  559082264,
    '1':  279541132,
    '2':  139770566,
    '3':  69885283,
    '4':  34942642,
    '5':  17471321,
    '6':  8735660,
    '7':  4367830,
    '8':  2183915,
    '9':  1091958,
    '10': 545979,
    '11': 272989,
    '12': 136495,
    '13': 68247,
    '14': 34124,
    '15': 17062,
    '16': 8531,
    '17': 4265,
    '18': 2133,
    '19': 1066,
    '20': 533,
    '21': 1     # set limit
}

zoomFontSizes = {
    '0':  5,
    '1':  5,
    '2':  6,
    '3':  7,
    '4':  8,
    '5':  8,
    '6':  10,
    '7':  12,
    '8':  14,
    '9':  16,
    '10': 17,
    '11': 18,
    '12': 19,
    '13': 20,
    '14': 22,
    '15': 24,
    '16': 24,
    '17': 26,
    '18': 26,
    '19': 28,
    '20': 30
}

def getBaseFontSizeByZoom(zoom):
    if zoom < 0:
        raise ValueError('Cannot have negative zoom level')
    elif zoom > 20:
        raise ValueError('Zoom out of range')
    print(zoom, zoomFontSizes[str(zoom)])
    return zoomFontSizes[str(zoom)]
    # min_size = 6
    # max_size = 34
    # k = 0.1
    # font_size = 24 * ((math.e**(k*zoom)-1)/(math.e**(20*k) - 1)) + 6
    # font_size = int(font_size)
    # print(zoom, font_size)
    # return font_size


def getFontSizeByZoom(zoom):
    font_size = getBaseFontSizeByZoom(zoom)
    return font_size

def getMinScaleByZoom(zoom):
    if zoom < 0:
        raise ValueError('Cannot have negative zoom level')
    elif zoom > 20:
        raise ValueError('Zoom out of range')
    return zoomScales[str(zoom+1)]-1

def getMaxScaleByZoom(zoom):
    if zoom < 0:
        raise ValueError('Cannot have negative zoom level')
    elif zoom > 20:
        raise ValueError('Zoom out of range')
    return zoomScales[str(zoom)]


def getLabelStyleForZooms(shapefile, label_field):
    stats = getAreaStatistics(shapefile)
    rules = ''
    for z in range(0,21):
        base_font_size = getFontSizeByZoom(z)
        rule = '''<Rule>
                    <Filter>([mapnik::geometry_type]=3)</Filter>   <!-- Polyon -->
                    <MaxScaleDenominator>{0}</MaxScaleDenominator>
                    <MinScaleDenominator>{1}</MinScaleDenominator>
                    <TextSymbolizer avoid-edges="true" face-name="{4}" size="{2}" halo-radius="0.85">[{3}]</TextSymbolizer>
                </Rule>
                <Rule>
                    <Filter>([mapnik::geometry_type]=2)</Filter>   <!-- LineString -->
                    <MaxScaleDenominator>{0}</MaxScaleDenominator>
                    <MinScaleDenominator>{1}</MinScaleDenominator>
                    <TextSymbolizer avoid-edges="true" face-name="{4}" size="{2}" halo-radius="0.85">[{3}]</TextSymbolizer>
                </Rule>
                <Rule>
                    <Filter>([mapnik::geometry_type]=1)</Filter>   <!-- Point -->
                    <MaxScaleDenominator>{0}</MaxScaleDenominator>
                    <MinScaleDenominator>{1}</MinScaleDenominator>
                    <TextSymbolizer avoid-edges="true" face-name="{4}" size="{2}" halo-radius="0.85">[{3}]</TextSymbolizer>
                </Rule>'''.format( getMaxScaleByZoom(z), getMinScaleByZoom(z), base_font_size, label_field, label_font )
        rules += rule
    return rules


def buildStylesheet(shapefile, projection, label_style):
    stylesheet = '''<?xml version="1.0" encoding="utf-8"?>
    <Map srs="+proj=merc +a=6378137 +b=6378137 +lat_ts=0.0 +lon_0=0.0 +x_0=0.0 +y_0=0 +k=1.0 +units=m +nadgrids=@null +no_defs +over">
        <Style name="layer">
            <Rule>
                <Filter>([mapnik::geometry_type]=3)</Filter>
                <PolygonSymbolizer fill="rgb(242,239,249)"/>
                <LineSymbolizer stroke-width="0.15"/>
            </Rule>
            <Rule>
                <Filter>([mapnik::geometry_type]=2)</Filter>
                <LineSymbolizer stroke-width="0.5"/>
            </Rule>
            <Rule>
                <Filter>([mapnik::geometry_type]=1)</Filter>
                <MarkersSymbolizer fill="rgb(0,0,0)" width="3" height="3"/>
            </Rule>
            {2}
        </Style>
        <Layer name="layer" srs="{1}">
            <StyleName>layer</StyleName>
            <Datasource>
                <Parameter name="file">{0}</Parameter>
                <Parameter name="type">shape</Parameter>
            </Datasource>
        </Layer>
    </Map>'''
    return stylesheet.format(shapefile, projection, label_style)

# def getLabelStyle(label_field):
#     return '''<Rule>
#                 <TextSymbolizer avoid-edges="true" face-name="DejaVu Sans Book" size="8" halo-radius="0.85">[{0}]</TextSymbolizer>
#             </Rule>'''.format(label_field)

def getProj4FromShapefile(shapefile):
    '''Get epsg from shapefile'''
    # Read prj file
    prj_file = shapefile[0:-4] + '.prj'
    prj_txt = ''
    with open(prj_file, 'r') as fh:
        prj_txt = fh.read()
    # Create spatial reference object
    srs = osr.SpatialReference()
    srs.ImportFromESRI([prj_txt])
    srs.AutoIdentifyEPSG()
    return srs.ExportToProj4()

def isFieldInShapefile(shapefile, field):
    datasource = ogr.Open(shapefile)
    layer = datasource.GetLayer(0)
    layerDefinition = layer.GetLayerDefn()
    for i in range(layerDefinition.GetFieldCount()):
        if field == layerDefinition.GetFieldDefn(i).GetName():
            datasource.Destroy()
            return True
    datasource.Destroy()
    return False


def main(shapefile, label_field=None, output="style.xml"):

    # getAreaStatistics(shapefile)
    projection = getProj4FromShapefile(shapefile)

    label_style = ''
    if label_field:
        label_style = getLabelStyleForZooms(shapefile, label_field)

    stylesheet = buildStylesheet(shapefile, projection, label_style)

    image = 'tmp.png'
    m = mapnik.Map(900, 600)
    mapnik.load_map_from_string(m, stylesheet)
    m.zoom_all()
    m.zoom(0.05)
    # m.zoom(0.25)
    # m.zoom(0.5)
    mapnik.render_to_file(m, image)

    # print(mapnik.save_map_to_string(m))

    mapnik.save_map(m, output)

    # Google = ('+proj=merc +a=6378137 +b=6378137 +lat_ts=0.0 +lon_0=0.0 '
    #               '+x_0=0.0 +y_0=0 +k=1.0 +units=m +nadgrids=@null +no_defs +over')
    # bbox = mapnik.Projection(Google).inverse(m.envelope())
    # scale = m.scale()
    # print(bbox, scale)



if __name__ == "__main__":

    parser = argparse.ArgumentParser(description='Mapnik Style Generator')

    parser.add_argument('-f',
    					type=str,
    					required=True,
    					help='shapefile')

    parser.add_argument('-l',
    					type=str,
    				 	required=False,
                        default=None,
    					help='label field')

    parser.add_argument('-o',
    					type=str,
    				 	required=False,
                        default='style.xml',
    					help='output stylesheet')

    args = parser.parse_args()

    main(args.f, args.l, args.o)
