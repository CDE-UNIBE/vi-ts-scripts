#!/usr/bin/env python
#
# Some utilities methods
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

import numpy
import os
import osgeo.gdal as gdal
import osgeo.gdalconst as gdalconst

def get_time_array(dataset, x, y):
    """
    Extract a time series as numpy.array from NDVI imagery at the requested pixel
    position.
    """
    
    result = []

    # Get the number of raster bands
    bands = dataset.RasterCount

    # Loop all bands
    for j in range(bands):
        # 1-based index
        band = dataset.GetRasterBand(j + 1)

        # Read the data and add the value to the string
        data = band.ReadAsArray(x, y, 1, 1)
        value = float(data[0, 0])
        result.append(value)

    # Return a numpy array
    return numpy.array(result)

def write_to_gtiff(filename, value, pixel, size, projection, geotransform, bandtype=gdalconst.GDT_Byte):
    """
    Write a pixel value to a file at the specified position. If the file does not
    exist it is created first. Exisiting files are opened and the pixel is overwritten
    with the new value.
    """

    # Get the GeoTIFF driver and register it
    driver = gdal.GetDriverByName("GTiff")
    driver.Register()
    
    # Check if the output file already exists. If yes, it is opened and get the
    # first band.
    if os.path.exists(filename):
        dataset = gdal.Open(filename, gdalconst.GA_Update)
        band = dataset.GetRasterBand(1)
    else:
        # Create a new file if it does not yet exist
        dataset = driver.Create(filename, size[0], size[1], 1, bandtype, ['COMPRESS=LZW', 'PREDICTOR=2', 'BLOCKXSIZE=128', 'BLOCKYSIZE=128', 'TILED=YES'])
        # Set the input projection and transformation
        dataset.SetProjection(projection)
        dataset.SetGeoTransform(geotransform)
        # Get the first band
        band = dataset.GetRasterBand(1)
        # Set the NODATA value
        band.SetNoDataValue(0)
    
    # Write the single value to the specified pixel position
    band.WriteArray(numpy.array([[value]]), pixel[0], pixel[1])
    # Flush the cache
    band.FlushCache()
    
    # Close the dataset in order to write the data persistently to the file
    dataset = None