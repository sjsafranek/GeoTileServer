#!/bin/python

''' Recursively navigates directory tree 
	finds all rasters and gets their extent
	saves results to csv file
'''

import os
import sys
import glob
import arcpy

def get_extent(file):
	elevRaster = arcpy.sa.Raster(file)
	myExtent = elevRaster.extent
	return myExtent

def get_subdirectories(directory):
	results = []
	dirs = os.walk(directory)
	for sub in dirs:
		results.append(sub[0])
	return results

def run(directory):
	results = {}
	directories = get_subdirectories(directory)
	for directory in directories:
		for raster in glob.glob(os.path.join(directory,"*.tiff")):
			results[raster] = get_extent(raster)
	return results


if __main__ == "__name__":
	directory = sys.argv[1]
	extents = run(directory)
	print(extents)


'''

gen = os.walk("C:\\Users\\Stefan\\Desktop\\db4oit")
for d in gen:
	print(d[0]) # files


'''