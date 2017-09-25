#MASS CLIPPING (ogr2ogr)
#Stefan Safranek
#Shape Files by US-States

import os, glob
import subprocess
from osgeo import ogr

# Input folders
saveFolder = "C:\\Users\\Stefan\\Desktop\\CLIPPING\\statesClipped"

# Input layers
folderOne = glob.glob("C:\\Users\\Stefan\\Desktop\\CLIPPING\\states\\*.shp")
folderTwo = glob.glob("C:\\Users\\Stefan\\Desktop\\CLIPPING\\National\\*.shp")
i = 1

for fileTwo in folderTwo:
    for fileOne in folderOne:
        saveName = str(fileTwo).replace('__1','')
        saveName = saveName.replace('.shp','')
        saveName = saveName.split('\\')
        stateName = str(fileOne).split('\\')
        stateName = stateName[6].split('_')
        saveFile = saveFolder + "\\CLIPPED_" + saveName[6] + "_" + stateName[5]

    #OGR2OGR METHOD
        subprocess.call(["ogr2ogr", "-f", "ESRI Shapefile", "-clipsrc", fileOne, saveFile, fileTwo], shell=True)

        print "layer clipped by " + stateName[5]
        i += 1

print "Done!"
print str(i) + " layers clipped"
print ":-D"
