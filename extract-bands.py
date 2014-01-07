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

import re
import os
import sys
try:
    import gdal
except ImportError:
    import osgeo.gdal as gdal
try:
    import gdalconst
except ImportError:
    import osgeo.gdalconst as gdalconst
import gdal_merge

# Check if VITS_DATA_PATH is set
if "VITS_DATA_PATH" not in os.environ:
    print "Variable VITS_DATA_PATH is not set or not a directory."
    sys.exit(1)

inputPath = "%s/MODIS/MOLT" % os.environ['VITS_DATA_PATH']
# Path to processed raster bands
outputPath = "%s/MODIS/processed" % os.environ['VITS_DATA_PATH']

product = "MOD13Q1.005"

# List of MODIS tiles
tiles=["h16v08", "h17v08", "h18v04", "h20v09", "h21v07",\
"h21v08", "h21v09", "h21v10", "h22v07", "h22v08", "h22v09",\
"h27v06", "h27v07", "h27v08", "h28v06", "h28v07", "h28v08"]

gdal.AllRegister()

hdfDriver = gdal.GetDriverByName("HDF4")
hdfDriver.Register()

tifDriver = gdal.GetDriverByName("GTiff")
tifDriver.Register()

indicesList = [(0, "NDVI"), (1, "EVI"), (2, "QUAL")]

for root, dirs, files in os.walk("%s/%s" % (inputPath, product)):
    for d in dirs:
        currentDirectory = "%s/%s/%s" % (inputPath, product, d)
        for root, dirs, files in os.walk(currentDirectory):
            # Loop all HDF files in the current directory
            for f in files:
                # For each file loop through the requested MODIS tiles
                for tile in tiles:
                    # Check if the current file matches the current MODIS tile
                    matchObj = re.search('.*%s.*hdf$' % tile, f)
                    if matchObj is not None:
                        # Get the full file input path
                        filename = matchObj.group(0)
                        inputFile = "%s/%s/%s/%s" % (inputPath, product, d, filename)
                        
                        # Before opening the input file, it is necessary to check if the output index filename
                        # does not yet exist!
                        # Loop all indices
                        for index in indicesList:
                            # Create the absolute output filepath
                            outputName = re.sub(".hdf$", ".tif", filename)
                            output = "%s/%s/%s/%s" % (outputPath, index[1], tile, "%s_%s" % (index[1], outputName))

                            if not os.path.exists(output):
                                # If the output file does not yet exist, open the input file
                                dataset = gdal.Open(inputFile, gdalconst.GA_ReadOnly)
                                # Get the subdataset name
                                subdatasetName = dataset.GetSubDatasets()[index[0]]
                                # Get the subdataset
                                subdataset = gdal.Open("%s" % (subdatasetName[0]), gdalconst.GA_ReadOnly)
                                # and its first band
                                inBand = subdataset.GetRasterBand(1)
                                # Create the output dataset:
                                # Like the input subdataset the output dataset needs to be 16bit Signed Integer.
                                # The output size is the same as the input size
                                outDataset = tifDriver.Create(os.path.abspath(output), subdataset.RasterXSize, subdataset.RasterYSize, 1, gdalconst.GDT_Int16)
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
                                print "File \"%s\" successfully written" % os.path.abspath(output)

                                # Now the gdal_merge:
                                # Delete the stacked raster file if that exists already
                                stackedRaster = "%s/%s/%s/%s" % (outputPath, index[1], tile, "%s.tif" % (index[1]))
                                if os.path.exists(stackedRaster):
                                    os.remove(stackedRaster)
                                tifs = []
                                # Put the command line options to a Python list
                                options = ["gdal_merge.py", "-o", os.path.abspath(stackedRaster), "-of", "GTiff", "-separate"]
                                for root, dirs, files in os.walk("%s/%s/%s" % (outputPath, index[1], tile)):
                                    for tif in files:
                                        matchObj = re.search('.*%s.*tif$' % tile, tif)
                                        if matchObj is not None:
                                            tifs.append("%s/%s/%s/%s" % (outputPath, index[1], tile, matchObj.group(0)))
                                # Sort the raster files according to their file name
                                tifs.sort()
                                options.extend(tifs)
                                # Call gdal_merge to stack the raster files
                                gdal_merge.main(options)
