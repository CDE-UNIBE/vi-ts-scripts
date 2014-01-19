#!/usr/bin/env python
#
# Script create a heatmap from accessed locations
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


# Read more about about creating heatmaps with matplotlib:
# http://stackoverflow.com/questions/2369492/generate-a-heatmap-in-matplotlib-using-a-scatter-data-set

import sys

# Import matplotlib add use the AGG backend renderer to enable this script
# in a headless server environment
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import os
try:
    import ogr
except ImportError:
    import osgeo.ogr as ogr
try:
    import osr
except ImportError:
    import osgeo.osr as osr
try:
    import gdal
except ImportError:
    import osgeo.gdal as gdal
try:
    import gdalconst
except ImportError:
    import osgeo.gdalconst as gdalconst

def main(argv=None):

    if argv is None:
        argv = sys.argv

    if len(argv) != 3:
        sys.stderr.write("Usage: %s src_ogr dst_gdal\n" % argv[0])
        sys.exit(1)

    # The file output name
    outputFile = os.path.abspath(argv[2])
    if not outputFile.endswith(".tif"):
        sys.stderr.write("Output dataset must be TIFF.\n")
        sys.exit(1)
    # The file output width
    outputWidth = 4000

    # Get the virtual format driver
    vrtDriver = ogr.GetDriverByName('VRT')

    # Open the virtual format file
    vrtFile = os.path.abspath(argv[1])
    dataSource = vrtDriver.Open(vrtFile, 0)
    if dataSource is None:
        sys.stderr.write("Could not open file %s\n" % vrtFile)
        # Exit the script if the input file is not readable
        sys.exit(1)
    # Get the layer
    layer = dataSource.GetLayer()

    # The global bounding box
    xmin = -180.0
    ymin = -90.0
    xmax = 180.0
    ymax = 90.0

    # Number of columns and rows
    nbrColumns = 360.0
    nbrRows = 180.0

    # Caculate the cell size in x and y direction
    csx = (xmax - xmin) / nbrColumns
    csy = (ymax - ymin) / nbrRows

    rows = []
    i = ymax
    while i > ymin:
        j = xmin
        cols = []
        while j < xmax:
            # Set a spatial filter
            layer.SetSpatialFilterRect(j, (i-csy), (j + csx), i)
            # And count the features
            cols.append(layer.GetFeatureCount())
            j += csx
        rows.append(cols)
        i -= csy

    # Clear the figure
    #plt.clf()
    fig = plt.figure()
    # Set the size
    fig.set_size_inches((outputWidth / 100.0), ((outputWidth / 2.0) / 100.0))

    ax = plt.Axes(fig, [0., 0., 1., 1.])
    ax.set_axis_off()
    fig.add_axes(ax)

    # Create the heatmap
    ax.imshow(rows, extent=[xmin, xmax, ymin, ymax], interpolation='bilinear')

    # Write the image to a temporary PNG file.
    # This intermediate step is necessary since the AGG backend renderer does
    # not support the creation of TIFF files.
    tmpFile = "%s.png" % outputFile.rsplit(".", 1)[0]
    plt.savefig(tmpFile)

    # Get the GDAL PNG driver and register it
    pngDriver = gdal.GetDriverByName("PNG")
    pngDriver.Register()

    # Open the input dataset
    inDataset = gdal.Open(tmpFile, gdalconst.GA_ReadOnly)

    # Get the GDAL TIFF driver and register it
    tifDriver = gdal.GetDriverByName("GTiff")
    tifDriver.Register()

    # Copy the input dataset to an output tiff file
    tifDriver.CreateCopy(outputFile, inDataset, 1, ["COMPRESS=LZW", "PREDICTOR=2"])

    # Open the newly created output TIFF file to update the georeference
    outDataset = gdal.Open(outputFile, gdalconst.GA_Update)
    # Calculate the pixel size in x an y direction
    psx = (xmax - xmin) / outputWidth
    ulx = xmin
    psy = (ymin - ymax) / (outputWidth / 2)
    uly = ymax
    # Set the geographic transformation
    outDataset.SetGeoTransform([ ulx, psx, 0, uly, 0, psy ])
    # Set the projection transformation
    outDataset.SetProjection(osr.SRS_WKT_WGS84)

    # Remove the temporary PNG file
    os.remove(tmpFile)

if __name__ == '__main__':
    sys.exit(main())
