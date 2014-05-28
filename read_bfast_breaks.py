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
import rpy2.rinterface as rinterface
import rpy2.robjects as robjects
from rpy2.robjects.packages import importr

# Variable log needs to be global
log = None

def list_of_images():
    
    images = [
    "A2000049",
    "A2000065",
    "A2000081",
    "A2000097",
    "A2000113",
    "A2000129",
    "A2000145",
    "A2000161",
    "A2000177",
    "A2000193",
    "A2000209",
    "A2000225",
    "A2000241",
    "A2000257",
    "A2000273",
    "A2000289",
    "A2000305",
    "A2000321",
    "A2000337",
    "A2000353",
    "A2001001",
    "A2001017",
    "A2001033",
    "A2001049",
    "A2001065",
    "A2001081",
    "A2001097",
    "A2001113",
    "A2001129",
    "A2001145",
    "A2001161",
    "A2001177",
    "A2001193",
    "A2001209",
    "A2001225",
    "A2001241",
    "A2001257",
    "A2001273",
    "A2001289",
    "A2001305",
    "A2001321",
    "A2001337",
    "A2001353",
    "A2002001",
    "A2002017",
    "A2002033",
    "A2002049",
    "A2002065",
    "A2002081",
    "A2002097",
    "A2002113",
    "A2002129",
    "A2002145",
    "A2002161",
    "A2002177",
    "A2002193",
    "A2002209",
    "A2002225",
    "A2002241",
    "A2002257",
    "A2002273",
    "A2002289",
    "A2002305",
    "A2002321",
    "A2002337",
    "A2002353",
    "A2003001",
    "A2003017",
    "A2003033",
    "A2003049",
    "A2003065",
    "A2003081",
    "A2003097",
    "A2003113",
    "A2003129",
    "A2003145",
    "A2003161",
    "A2003177",
    "A2003193",
    "A2003209",
    "A2003225",
    "A2003241",
    "A2003257",
    "A2003273",
    "A2003289",
    "A2003305",
    "A2003321",
    "A2003337",
    "A2003353",
    "A2004001",
    "A2004017",
    "A2004033",
    "A2004049",
    "A2004065",
    "A2004081",
    "A2004097",
    "A2004113",
    "A2004129",
    "A2004145",
    "A2004161",
    "A2004177",
    "A2004193",
    "A2004209",
    "A2004225",
    "A2004241",
    "A2004257",
    "A2004273",
    "A2004289",
    "A2004305",
    "A2004321",
    "A2004337",
    "A2004353",
    "A2005001",
    "A2005017",
    "A2005033",
    "A2005049",
    "A2005065",
    "A2005081",
    "A2005097",
    "A2005113",
    "A2005129",
    "A2005145",
    "A2005161",
    "A2005177",
    "A2005193",
    "A2005209",
    "A2005225",
    "A2005241",
    "A2005257",
    "A2005273",
    "A2005289",
    "A2005305",
    "A2005321",
    "A2005337",
    "A2005353",
    "A2006001",
    "A2006017",
    "A2006033",
    "A2006049",
    "A2006065",
    "A2006081",
    "A2006097",
    "A2006113",
    "A2006129",
    "A2006145",
    "A2006161",
    "A2006177",
    "A2006193",
    "A2006209",
    "A2006225",
    "A2006241",
    "A2006257",
    "A2006273",
    "A2006289",
    "A2006305",
    "A2006321",
    "A2006337",
    "A2006353",
    "A2007001",
    "A2007017",
    "A2007033",
    "A2007049",
    "A2007065",
    "A2007081",
    "A2007097",
    "A2007113",
    "A2007129",
    "A2007145",
    "A2007161",
    "A2007177",
    "A2007193",
    "A2007209",
    "A2007225",
    "A2007241",
    "A2007257",
    "A2007273",
    "A2007289",
    "A2007305",
    "A2007321",
    "A2007337",
    "A2007353",
    "A2008001",
    "A2008017",
    "A2008033",
    "A2008049",
    "A2008065",
    "A2008081",
    "A2008097",
    "A2008113",
    "A2008129",
    "A2008145",
    "A2008161",
    "A2008177",
    "A2008193",
    "A2008209",
    "A2008225",
    "A2008241",
    "A2008257",
    "A2008273",
    "A2008289",
    "A2008305",
    "A2008321",
    "A2008337",
    "A2008353",
    "A2009001",
    "A2009017",
    "A2009033",
    "A2009049",
    "A2009065",
    "A2009081",
    "A2009097",
    "A2009113",
    "A2009129",
    "A2009145",
    "A2009161",
    "A2009177",
    "A2009193",
    "A2009209",
    "A2009225",
    "A2009241",
    "A2009257",
    "A2009273",
    "A2009289",
    "A2009305",
    "A2009321",
    "A2009337",
    "A2009353",
    "A2010001",
    "A2010017",
    "A2010033",
    "A2010049",
    "A2010065",
    "A2010081",
    "A2010097",
    "A2010113",
    "A2010129",
    "A2010145",
    "A2010161",
    "A2010177",
    "A2010193",
    "A2010209",
    "A2010225",
    "A2010241",
    "A2010257",
    "A2010273",
    "A2010289",
    "A2010305",
    "A2010321",
    "A2010337",
    "A2010353",
    "A2011001",
    "A2011017",
    "A2011033",
    "A2011049",
    "A2011065",
    "A2011081",
    "A2011097",
    "A2011113",
    "A2011129",
    "A2011145",
    "A2011161",
    "A2011177",
    "A2011193",
    "A2011209",
    "A2011225",
    "A2011241",
    "A2011257",
    "A2011273",
    "A2011289",
    "A2011305",
    "A2011321",
    "A2011337",
    "A2011353",
    "A2012001",
    "A2012017",
    "A2012033",
    "A2012049",
    "A2012065",
    "A2012081",
    "A2012097",
    "A2012113",
    "A2012129",
    "A2012145",
    "A2012161",
    "A2012177",
    "A2012193",
    "A2012209",
    "A2012225",
    "A2012241",
    "A2012257",
    "A2012273",
    "A2012289",
    "A2012305",
    "A2012321",
    "A2012337",
    "A2012353",
    "A2013001",
    "A2013017",
    "A2013033",
    "A2013049",
    "A2013065",
    "A2013081",
    "A2013097",
    "A2013113",
    "A2013129",
    "A2013145",
    "A2013161",
    "A2013177",
    "A2013193",
    "A2013209",
    "A2013225",
    "A2013241",
    "A2013257",
    "A2013273",
    "A2013289",
    "A2013305",
    "A2013321",
    "A2013337",
    "A2013353",
    "A2014001",
    "A2014017",
    "A2014033",
    "A2014049",
    "A2014065",
    "A2014081",
    "A2014097",
    "A2014113"]
    
    return images
    
def get_time_array(dataset, x, y):
    """
    Extract a time series Python array from NDVI imagery at the requested pixel
    position.
    """
    
    result = []

    bands = dataset.RasterCount

    # loop through the bands
    for j in range(bands):
        band = dataset.GetRasterBand(j + 1) # 1-based index

        # read data and add the value to the string
        data = band.ReadAsArray(x, y, 1, 1)
        value = float(data[0, 0])
        result.append(value / 10000.0)

    # figure out how long the script took to run
    #log.debug('It took ' + str(endTime - startTime) + ' seconds to read the input raster file.')

    return result

def write_to_raster(tile, index, pixel, size, projection, geotransform):
    """
    Write a positive value in the BREAK image at the pixel position.
    """
    
    
    # Be careful: R indexes are zero-based!
    name = list_of_images()[index-1]
    
    # Check if the output image already exists:
    filename = "%s/MODIS/processed/BREAK/%s/BREAK_MOD13Q1.%s.%s.tif" % (os.environ['VITS_DATA_PATH'], tile, name, tile)
    
    log.debug("Selecting file \"%s\"" % filename)
    
    driver = gdal.GetDriverByName("GTiff")
    driver.Register()
    
    if os.path.exists(filename):
        dataset = gdal.Open(filename, gdalconst.GA_Update)
        band = dataset.GetRasterBand(1)
    else:
        dataset = driver.Create(filename, size[0], size[1], 1, gdalconst.GDT_Byte, ['COMPRESS=LZW', 'PREDICTOR=2'])
        dataset.SetProjection(projection)
        dataset.SetGeoTransform(geotransform)
        band = dataset.GetRasterBand(1)
    
    band.WriteArray(numpy.array([[1]]), pixel[0], pixel[1])
    band.FlushCache()
    
def calc_bfast(data_array):
    """
    Calculate the BFast statistics
    """
    
    def _is_in_sea(arr):
        for i in arr:
            if i != float(-0.3):
                return False
        return True


    if _is_in_sea(data_array):
        return []

    # Start R timing
    startTime = time.time()

    # Initialize R
    rinterface.initr()

    r = robjects.r

    # Import the bfast package
    bfast = importr('bfast')

    # Create a R vector from the Python array
    b = robjects.FloatVector(data_array)

    # Create a R timeseries from R vector
    b_ts = r.ts(b, start=robjects.IntVector([2000, 4]), frequency=23)

    # Calculate BFast
    h = 23.0 / float(len(b_ts))
    b_bfast = r.bfast(b_ts, h=h, season="harmonic", max_iter=2)

    # Get the "output" attribute from the BFast result
    output = b_bfast[b_bfast.names.index("output")]
    # Number of iteration
    nbrOfIter = len(output)
    # Get the break points
    breakpointsOutput = output.rx2(nbrOfIter).rx("bp.Vt")[0]
    # Get the break points as a "breakpoints" R object, see also:
    # http://cran.r-project.org/web/packages/strucchange/strucchange.pdf#Rfn.breakpoints
    breakpoints = breakpointsOutput[breakpointsOutput.names.index("breakpoints")]

    endTime = time.time()
    # Figure out how long the script took to run
    log.debug('It took ' + str(endTime - startTime) + ' seconds to calculate the BFast breakpoints.')

    if(breakpoints[0] == robjects.NA_Logical):
        return []

    # Return the list of breakpoints as Python array
    return [int(breakpoints[b]) for b in range(len(breakpoints))]

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

        # Open the image
        if "VITS_DATA_PATH" not in os.environ:
            log.error('"VITS_DATA_PATH" is not set in the environment.')
            sys.exit(1)
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
                # Get the time series for the current pixel
                log.debug("Accessing pixel x: %s, y: %s" % (col, row))
                time_array = get_time_array(ds, col, row)
                log.debug(time_array)
                # Calculate the BFast breakpoints
                breakpoints = calc_bfast(time_array)
                log.debug(breakpoints)
                # Variable "breakpoints" is an array with length greater than 0
                # if there are any breaks. If no breaks are found the array has
                # no elements.
                if len(breakpoints) > 0:
                    # Write a pixel for each found element
                    for b in breakpoints:
                        write_to_raster(tile, b, (col, row), (nbrOfCols, nbrOfRows), proj, trans)
                    
if __name__ == "__main__":
    sys.exit(main())