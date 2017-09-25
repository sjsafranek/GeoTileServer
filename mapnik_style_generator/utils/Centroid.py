#Centriod Batch Recorder
#Stefan Safranek
'''
    This code goes through every shape file in a folder, adds a
    c_lat" and "c_lng" field, iterates through each feature, calculates
    the centriod and inputs the centriod lat/lng values in to
    corrisponding field.
'''

import sys, os, glob
from osgeo import ogr
shps = glob.glob('C:\\Users\\Stefan\\Desktop\\shapefile_processing\\clip_output\\*.shp')

for shp in shps:
    f = os.path.basename(shp)
    driver = ogr.GetDriverByName('ESRI Shapefile')
    dataSource = driver.Open(shp, 1)
    layer = dataSource.GetLayer()

    fldDefLat = ogr.FieldDefn('intptlat', ogr.OFTInteger)
    fldDefLng = ogr.FieldDefn('intptlon', ogr.OFTInteger)
    layer.CreateField(fldDefLat)
    layer.CreateField(fldDefLng)

    i = 1
    
    feature = layer.GetNextFeature()
    while feature:
        geom = feature.GetGeometryRef()
        centroid = geom.Centroid()
        centroid = str(centroid)
        centroid = centroid.replace('POINT (',"")
        centroid = centroid.replace(')',"")
        centroid = centroid.split(" ")
        lng = float(centroid[0])
        lat = float(centroid[1])
        feature.SetField('intptlat', lat)
        feature.SetField('intptlon', lng)
        layer.SetFeature(feature)
        feature = layer.GetNextFeature()
        print "Centroid of " + str(f) + " feature " + str(i) + " = "+ str(centroid[0]) +", "+ str(centroid[1])
        i += 1
    driver = None

print "Done!"
print ":-D"
