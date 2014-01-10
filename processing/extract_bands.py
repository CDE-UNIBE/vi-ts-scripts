#!/usr/bin/env python
#
# Script to extract bands from MODIS imagery
# Copyright (C) 2014 Adrian Weber
# Centre for Development and Environment, University of Bern
#
# This program is free software; you can redistribute it and/or
# modify it under the terms of the GNU General Public License
# as published by the Free Software Foundation; either version 2
# of the License, or (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 51 Franklin Street,
# Fifth Floor, Boston, MA  02110-1301, USA.
#

import sys

import os
import re
try:
    import gdal
except ImportError:
    import osgeo.gdal as gdal
try:
    import gdalconst
except ImportError:
    import osgeo.gdalconst as gdalconst
import gdal_merge

def merge_files(outputPath, index, tile):
    # Delete the stacked raster file if that exists already
    stackedRaster = "%s/%s/%s/%s" % (outputPath, index, tile, "%s.tif" % (index))
    if os.path.exists(stackedRaster):
        os.remove(stackedRaster)
    tifs = []
    # Put the command line options to a Python list
    options = ["gdal_merge.py", "-o", os.path.abspath(stackedRaster), "-of", "GTiff", "-separate"]
    for root, dirs, files in os.walk("%s/%s/%s" % (outputPath, index, tile)):
        for tif in files:
            matchObj = re.search('.*%s.*tif$' % tile, tif)
            if matchObj is not None:
                tifs.append("%s/%s/%s/%s" % (outputPath, index, tile, matchObj.group(0)))
    # Sort the raster files according to their file name
    tifs.sort()
    options.extend(tifs)
    # Call gdal_merge to stack the raster files
    gdal_merge.main(options)

def extract_band(inputFile, outputFile, index):

    gdal.AllRegister()

    hdfDriver = gdal.GetDriverByName("HDF4")
    hdfDriver.Register()

    tifDriver = gdal.GetDriverByName("GTiff")
    tifDriver.Register()

    # If the output file does not yet exist, open the input file
    dataset = gdal.Open(inputFile, gdalconst.GA_ReadOnly)
    # Get the subdataset name
    subdatasetName = dataset.GetSubDatasets()[index]
    # Get the subdataset
    subdataset = gdal.Open("%s" % (subdatasetName[0]), gdalconst.GA_ReadOnly)
    # and its first band
    inBand = subdataset.GetRasterBand(1)
    # Create the output dataset:
    # Like the input subdataset the output dataset needs to be 16bit Signed Integer.
    # The output size is the same as the input size
    outDataset = tifDriver.Create(outputFile,
                                  subdataset.RasterXSize,
                                  subdataset.RasterYSize,
                                  1,
                                  gdalconst.GDT_Int16,
                                  options = ['COMPRESS=LZW', 'PREDICTOR=2', 'TILED=YES', 'INTERLEAVE=BAND'])
    # Set the transformation and projection from the subdataset
    outDataset.SetGeoTransform(subdataset.GetGeoTransform())
    outDataset.SetProjection(subdataset.GetProjection())
    # Read the input raster band
    inRaster = inBand.ReadRaster1(0, 0, subdataset.RasterXSize, subdataset.RasterYSize)
    # Write the raster band to the output dataset
    outDataset.WriteRaster(0, 0, subdataset.RasterXSize, subdataset.RasterYSize, inRaster)
    # Flush the cache and clean up
    outDataset.FlushCache()
    del outDataset
    del inBand
    del subdataset
    # Write a nice message for the user
    sys.stdout.write("File \"%s\" successfully written.\n" % outputFile)

def main(inputFile, tile):

    # Check if VITS_DATA_PATH is set
    if "VITS_DATA_PATH" not in os.environ:
        sys.stdout.write("Variable VITS_DATA_PATH is not set or not a directory.\n")
        sys.exit(1)

    # Path to processed raster bands
    outputPath = "%s/MODIS/processed" % os.environ['VITS_DATA_PATH']

    indicesList = [(0, "NDVI"), (1, "EVI"), (2, "QUAL")]

    # Before opening the input file, it is necessary to check if the output index filename
    # does not yet exist!
    # Loop all indices
    for index in indicesList:
        # Create the absolute output filepath
        inputFileName = re.search("MOD13Q1\.[A-Za-z0-9\.]*\.hdf$", inputFile).group(0)
        outputName = re.sub(".hdf$", ".tif", inputFileName)
        outputFile = "%s/%s/%s/%s" % (outputPath, index[1], tile, "%s_%s" % (index[1], outputName))
        sys.stdout.write("%s\n" % outputFile)

        if not os.path.exists(outputFile):
            # Check if the tile directory already exists
            if not os.path.exists("%s/%s/%s" % (outputPath, index[1], tile)):
                os.mkdir("%s/%s/%s" % (outputPath, index[1], tile))

            extract_band(inputFile, outputFile, index[0])

            # Now the gdal_merge in case we handle NDVI
            if index[0] == 0:
                merge_files(outputPath, index[1], tile)

    return True

if __name__ == '__main__':
    sys.exit(main())