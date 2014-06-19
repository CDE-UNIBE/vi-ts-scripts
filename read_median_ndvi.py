#!/usr/bin/env python
#
# Script which reads MODIS NDVI images and detect BFast breakpoints
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

import os
import os.path
import sys
import time
import logging
import logging.config
import numpy
try:
    import gdal
except ImportError:
    import osgeo.gdal as gdal
try:
    import gdalconst
except ImportError:
    import osgeo.gdalconst as gdalconst
from processing.utilities import get_time_array
from processing.utilities import write_to_gtiff

# Variable log needs to be global
log = None
    
def main(argv=None):
    if argv is None:
        argv = sys.argv
        
    logging.config.fileConfig(argv[0].replace("py", "ini"))
    # Get the root logger from the config file
    global log
    log = logging.getLogger(__name__)
    
    # Register the GeoTiff driver
    driver = gdal.GetDriverByName("GTiff")
    driver.Register()
    
    # Process MODIS tiles
    for tile in ["h16v08"]:
        
        # Check if VITS_DATA_PATH is set as environment variable
        if "VITS_DATA_PATH" not in os.environ:
            log.error('"VITS_DATA_PATH" is not set in the environment.')
            sys.exit(1)
        # Open the image
        filename = '%s/MODIS/processed/NDVI/%s/NDVI.tif' % (os.environ['VITS_DATA_PATH'], tile)
        # Open the NDVI file for reading
        ds = gdal.Open(filename, gdalconst.GA_ReadOnly)
        if ds is None:
            log.error('Raster file "%s" could not be opened.' % filename)
            sys.exit(1)
            
        # Get the file size in pixels
        nbrOfCols =  ds.RasterXSize
        nbrOfRows = ds.RasterYSize
        # Get the projection and transformation
        proj = ds.GetProjection()
        trans = ds.GetGeoTransform()

        # An NDVI with three breaks for development purposes only!
        #time_array = [0.4699, 0.5812, 0.5151, 0.5268, 0.5817, 0.6956, 0.8073, 0.4094, 0.7977, 0.6813, 0.7665, 0.8393, 0.5579, 0.8372, 0.8697, 0.7994, 0.7557, 0.7399, 0.6887, 0.616, 0.5656, 0.5859, 0.4995, 0.4796, 0.4983, 0.591, 0.6365, 0.5829, 0.6478, 0.4136, 0.2835, 0.8021, 0.808, 0.8743, 0.8564, 0.5159, 0.83, 0.8462, 0.7753, 0.7111, 0.7215, 0.7009, 0.6174, 0.5442, 0.4575, 0.5131, 0.4787, 0.4692, 0.3766, 0.3593, 0.4811, 0.4859, 0.2918, 0.5839, 0.5787, 0.7177, 0.4905, 0.7669, 0.3004, 0.8627, 0.8348, 0.8583, 0.8581, 0.6952, 0.6772, 0.5765, 0.5343, 0.6784, 0.6106, 0.5293, 0.4472, 0.4583, 0.4983, 0.5865, 0.4464, 0.7009, 0.6327, 0.6708, 0.6662, 0.8168, 0.6312, 0.8143, 0.9271, 0.8422, 0.7944, 0.6622, 0.6448, 0.5202, 0.4989, 0.5163, 0.4151, 0.476, 0.5631, 0.6078, 0.5181, 0.5975, 0.6366, 0.7052, 0.7856, 0.8009, 0.8374, 0.5689, 0.6034, 0.7886, 0.193, 0.767, 0.8187, 0.724, 0.7063, 0.6798, 0.5559, 0.4764, 0.4968, 0.49, 0.4169, 0.4021, 0.4007, 0.4254, 0.4435, 0.562, 0.5544, 0.3487, 0.1932, 0.7365, 0.7612, 0.7163, 0.4523, 0.5983, 0.8211, 0.8265, 0.6628, 0.6705, 0.6224, 0.5515, 0.5064, 0.5429, 0.5166, 0.4005, 0.411, 0.3674, 0.389, 0.5968, 0.4891, 0.7215, 0.6387, 0.5233, 0.5695, 0.7493, 0.6392, 0.4378, 0.7656, 0.8708, 0.7901, 0.7384, 0.658, 0.6116, 0.5968, 0.5355, 0.4763, 0.4622, 0.4155, 0.3808, 0.4453, 0.4557, 0.5119, 0.5328, 0.6221, 0.6967, 0.7779, 0.6975, 0.8646, 0.6298, 0.8332, 0.6163, 0.7919, 0.7697, 0.5261, 0.4741, 0.3212, 0.2601, 0.2374, 0.226, 0.2462, 0.229, 0.2343, 0.2049, 0.2196, 0.3492, 0.295, 0.3658, 0.2836, 0.2958, 0.249, 0.2807, 0.2285, 0.2911, 0.3363, 0.3386, 0.3344, 0.1941, 0.2835, 0.2658, 0.2331, 0.2459, 0.2241, 0.1528, 0.176, 0.1769, 0.1799, 0.428, 0.4012, 0.3887, 0.3985, 0.4486, 0.3387, 0.33, 0.5279, 0.4426, 0.5819, 0.6952, 0.5136, 0.6162, 0.6201, 0.6445, 0.6281, 0.5837, 0.6507, 0.6536, 0.6946, 0.6498, 0.6209, 0.6782, 0.6557, 0.522, 0.562, 0.5359, 0.4994, 0.5717, 0.3815, 0.6081, 0.3841, 0.6375, 0.5472, 0.562, 0.6947, 0.6398, 0.618, 0.6131, 0.5747, 0.5931, 0.5931, 0.6092, 0.5638, 0.5216, 0.5267, 0.5051, 0.5997, 0.728, 0.5743, 0.6727, 0.6522, 0.7366, 0.757, 0.4227, 0.7737, 0.7038, 0.4549, 0.9319, 0.6907, 0.664, 0.69, 0.6093, 0.5804, 0.601, 0.6448, 0.6279, 0.5867, 0.647, 0.7907, 0.6902, 0.665, 0.6063, 0.4854, 0.5989, 0.1883, 0.6123, 0.392, 0.5697, 0.7146, 0.7765, 0.7432, 0.6993, 0.6561, 0.6711, 0.6917, 0.6472, 0.5742, 0.6203, 0.5964, 0.5452, 0.6326, 0.5123, 0.6165, 0.617, 0.6766, 0.4937, 0.5586, 0.7056, 0.4808, 0.8469, 0.8021, 0.5232, 0.9127, 0.6997, 0.6871, 0.6355, 0.6425, 0.6174, 0.6037, 0.6037, 0.5846, 0.5444, 0.5479, 0.6665, 0.527, 0.5534, 0.659]
        #result = calc_bfast(time_array)
        #log.debug(result)

        # Loop over each pixel
        for row in range(0, nbrOfRows):
            for col in range(0, nbrOfCols):
                starttime = time.time()
                # Get the time series for the current pixel
                time_array = get_time_array(ds, col, row)
                filename = "%s/MODIS/processed/MEDIAN/%s/MEDIAN_MOD13Q1.%s.tif" % (os.environ['VITS_DATA_PATH'], tile, tile)
                #log.debug("Selecting file \"%s\"" % filename)
                write_to_gtiff(filename, int(numpy.median(time_array)), (col, row), (nbrOfCols, nbrOfRows), proj, trans, gdalconst.GDT_Int16)
                endtime = time.time()
                log.debug("It took %s" % (endtime - starttime))
                    
if __name__ == "__main__":
    sys.exit(main())