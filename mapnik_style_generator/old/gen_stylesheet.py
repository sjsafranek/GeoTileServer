#!/usr/bin/env python

import mapnik
from osgeo import ogr
from osgeo import osr


shp_file = "data/world_merc.shp"
label_field = 'NAME'


def getFieldInShapefile(shapefile, field):
    datasource = ogr.Open(shapefile)
    layer = datasource.GetLayer(0)
    layerDefinition = layer.GetLayerDefn()
    for i in range(layerDefinition.GetFieldCount()):
        if field == layerDefinition.GetFieldDefn(i).GetName():
            return True
    return False

def getProj4FromShapefile(shapefile):
    '''Get epsg from shapefile'''
    # Read prj file
    prj_file = shapefile[0:-4] + '.prj'
    prj_filef = open(prj_file, 'r')
    prj_txt = prj_filef.read()
    prj_filef.close()
    # Create spatial reference object
    srs = osr.SpatialReference()
    srs.ImportFromESRI([prj_txt])
    srs.AutoIdentifyEPSG()
    return srs.ExportToProj4()

def _normalizeGeomTypes(geom_types):
    normalized = set()
    for geom_type in geom_types:
        geom_type = geom_type.replace('MULTI', '')
        normalized.add(geom_type)
    return list(normalized)

def getGeometryTypes(shapefile):
    geom_types = set()
    driver = ogr.GetDriverByName("ESRI Shapefile")
    datasource = driver.Open(shapefile, 0)
    layer = datasource.GetLayer()
    for feature in layer:
        geom = feature.GetGeometryRef()
        geom_type = geom.GetGeometryName()
        geom_types.add(geom_type)
    geom_types = list(geom_types)
    geom_types = _normalizeGeomTypes(geom_types)
    return geom_types


def getLineStyle():
    # add style
    style = mapnik.Style() # style object to hold rules
    rule = mapnik.Rule() # rule object to hold symbolizers
    # to add outlines to a polygon we create a LineSymbolizer
    line_symbolizer = mapnik.LineSymbolizer()
    line_symbolizer.stroke = mapnik.Color('black')
    line_symbolizer.stroke_width = 0.1
    rule.symbols.append(line_symbolizer) # add the symbolizer to the rule object
    style.rules.append(rule) # now add the rule to the style and we're done
    return style

def getPolygonStyle():
    # add style
    style = mapnik.Style() # style object to hold rules
    rule = mapnik.Rule() # rule object to hold symbolizers
    # to fill a polygon we create a PolygonSymbolizer
    polygon_symbolizer = mapnik.PolygonSymbolizer()
    polygon_symbolizer.fill = mapnik.Color('#f2eff9')
    rule.symbols.append(polygon_symbolizer) # add the symbolizer to the rule object
    # to add outlines to a polygon we create a LineSymbolizer
    line_symbolizer = mapnik.LineSymbolizer()
    line_symbolizer.stroke = mapnik.Color('black')
    line_symbolizer.stroke_width = 0.1
    rule.symbols.append(line_symbolizer) # add the symbolizer to the rule object
    style.rules.append(rule) # now add the rule to the style and we're done
    return style

def getPointStyle():
    # add style
    style = mapnik.Style() # style object to hold rules
    rule = mapnik.Rule() # rule object to hold symbolizers
    marker = mapnik.MarkersSymbolizer()
    # marker.fill_opacity = .5
    # marker.opacity = .5
    marker.height =  mapnik.Expression("3")
    marker.width =  mapnik.Expression("3")
    marker.fill = mapnik.Color('black')
    rule.symbols.append(marker)
    style.rules.append(rule)
    return style

def getTextStyle(fieldname):
    style = mapnik.Style() # style object to hold rules
    rule = mapnik.Rule() # rule object to hold symbolizers
    # print(help(mapnik.TextSymbolizer))
    print(mapnik.mapnik_version())
    symbolizer = mapnik.TextSymbolizer(
        mapnik.Expression('['+fieldname+']'),
        'DejaVu Sans Book',
        10,
        mapnik.Color('black')
    )

    # symbolizer = mapnik.TextSymbolizer()

    # print(symbolizer, dir(symbolizer))

    # print(symbolizer.properties.format_tree.text)

    # symbolizer.face_name = mapnik.FormattingText('DejaVu Sans Book')
    # symbolizer.face_name = 'DejaVu Sans Book'
    # symbolizer.properties.format_tree = mapnik.FormattingText('DejaVu Sans Book')
    # symbolizer.name = mapnik.Expression('['+fieldname+']')


    symbolizer.halo_fill = mapnik.Color('white')
    symbolizer.halo_radius = 1
    symbolizer.label_placement = label_placement.LINE_PLACEMENT # POINT_PLACEMENT is default
    symbolizer.allow_overlap = False
    symbolizer.avoid_edges = True
    rule.symbols.append(symbolizer)
    style.rules.append(rule)
    return style


def main():
    # print( getFieldInShapefile(shp_file, label_field) )

    geom_types = getGeometryTypes(shp_file)

    epsg = getProj4FromShapefile(shp_file)

    m = mapnik.Map(600,300)

    for geom_type in geom_types:
        if 'POLYGON' == geom_type:
            s = getPolygonStyle()
            m.append_style('Polygon Style', s) # Styles are given names only as they are applied to the map
        elif 'LINESTRING' == geom_type:
            s = getLineStyle()
            m.append_style('LineString Style', s) # Styles are given names only as they are applied to the map
        elif 'POINT'  == geom_type:
            s = getPointStyle()
            m.append_style('Point Style', s) # Styles are given names only as they are applied to the map
        else:
            raise ValueError('Uncaught geometry type: ' + geom_type)

    # if label_field and getFieldInShapefile(shp_file, label_field):
        # s = getTextStyle(label_field)
        # m.append_style('Label Style', s)


    s = getPointStyle()
    m.append_style('Point Style',s) # Styles are given names only as they are applied to the map

    # add datasource
    ds = mapnik.Shapefile(file=shp_file)

    # add layer
    layer = mapnik.Layer('Layer')
    # note: layer.srs will default to '+proj=longlat +ellps=WGS84 +datum=WGS84 +no_defs'
    layer.datasource = ds
    layer.styles.append('Polygon Style')
    layer.styles.append('LineString Style')
    layer.styles.append('Point Style')

    # add layer to map
    m.layers.append(layer)
    m.zoom_all()

    print(mapnik.save_map_to_string(m))
    mapnik.save_map(m, 'style.xml')

    mapnik.render_to_file(m,'sample.png', 'png')



if __name__ == '__main__':
    main()


# getEpsg2Mapnik(epsg)
