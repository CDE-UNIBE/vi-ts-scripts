#!/usr/bin/env python
#
# Script to detect corrupt GeoTIFF files
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

import gdal
import os
import re

# Check if VITS_DATA_PATH is set
if "VITS_DATA_PATH" not in os.environ:
    print "Variable VITS_DATA_PATH is not set or not a directory."
    sys.exit(1)

# Path to processed raster bands
path = "%s/MODIS/processed" % os.environ['VITS_DATA_PATH']

gdal.AllRegister()

indicesList = [(0, "NDVI"), (1, "EVI"), (2, "QUAL")]

for index in indicesList:
    indexpath = "%s/%s" % (path, index[1])
    for root, dirs, files in os.walk(indexpath):
        for dir in dirs:
            tilepath = "%s/%s" % (indexpath, dir)
            for root, dirs, files in os.walk(tilepath):
                for file in files:
                    matchObj = re.search('.*%s.*\.tif$' % dir, file)
                    if matchObj is not None:
                        filepath = "%s/%s" % (tilepath, file)
                        sys.stdout.write("Validating file \'%s\': " % filepath)
                        ds = gdal.Open(filepath)
                        for i in range(ds.RasterCount):
                            ds.GetRasterBand(1).Checksum()
                            if gdal.GetLastErrorType() != 0:
                                sys.stdout.write("NOT VALID\n")
                            else:
                                sys.stdout.write("OK\n")