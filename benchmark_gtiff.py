#!/usr/bin/env python
#
# Script to download and process MODIS imagery
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
from gdalconst import GA_ReadOnly
import os
import timeit


def read_bands(file, x, y):

    gdal.AllRegister()

    tifDriver = gdal.GetDriverByName("GTiff")
    tifDriver.Register()


    # Register GeoTIFF driver
    driver = gdal.GetDriverByName('GTiff')
    driver.Register()

    # open the image
    dataset = gdal.Open(str(file), GA_ReadOnly)

    if dataset is None:
        sys.exit(1)

    result = []

    # get image size
    #rows = ds.RasterYSize
    #cols = ds.RasterXSize
    bands = dataset.RasterCount
    # get georeference info
    transform = dataset.GetGeoTransform()
    xOrigin = transform[0]
    yOrigin = transform[3]
    pixelWidth = transform[1]
    pixelHeight = transform[5]

    # compute pixel offset
    xOffset = int((x - xOrigin) / pixelWidth)
    yOffset = int((y - yOrigin) / pixelHeight)
    # loop through the bands
    for j in range(bands):
        band = dataset.GetRasterBand(j + 1) # 1-based index

        # read data and add the value to the string
        data = band.ReadAsArray(xOffset, yOffset, 1, 1)
        value = data[0, 0]
        result.append(int(value))



def main(argv=None):
    if argv is None:
        argv = sys.argv

    sys.stdout.write("Benchmarking file %s\n" % argv[1])

    t = timeit.timeit('read_bands(file, x, y)',
                      setup="from __main__ import read_bands; x = -1600000; y = 700000; file = '%s';" % os.path.abspath(argv[1]),
                      number=50000)
    sys.stdout.write("%s\n" % t)

if __name__ == "__main__":
    sys.exit(main())




