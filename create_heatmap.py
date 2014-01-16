#!/usr/bin/env python

# see also:
# http://stackoverflow.com/questions/2369492/generate-a-heatmap-in-matplotlib-using-a-scatter-data-set

import sys

import matplotlib.pyplot as plt
import os
import osgeo.ogr
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

    # The file output name
    outputFile = os.path.abspath(argv[2])
    if not outputFile.endswith(".tif"):
        sys.stderr.write("Output dataset must be TIFF.\n")
        sys.exit(1)
    # The file output width
    outputWidth = 4000

    # get the shape file driver
    shpDriver = osgeo.ogr.GetDriverByName('VRT')

    # Open shape file with points
    shpFile = os.path.abspath(argv[1])
    dataSource = shpDriver.Open(shpFile, 0)
    if dataSource is None:
        print 'Could not open file ' + shpFile
        sys.exit(1)
    # Get the layer
    layer = dataSource.GetLayer()

    # The global bounding box
    xmin = -180.0
    ymin = -90.0
    xmax = 180.0
    ymax = 90.0

    # Number of columns and rows
    nbrColumns = 200.0
    nbrRows = 100.0

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

    # Write the image to a TIFF file
    plt.savefig(outputFile)

    # Open the TIFF file and append the georeference
    tifDriver = gdal.GetDriverByName("GTiff")
    tifDriver.Register()

    dataset = gdal.Open(outputFile, gdalconst.GA_Update)
    psx = (xmax - xmin) / outputWidth
    ulx = xmin
    psy = (ymin - ymax) / (outputWidth / 2)
    uly = ymax
    dataset.SetGeoTransform([ ulx, psx, 0, uly, 0, psy ])
    dataset.SetProjection(osr.SRS_WKT_WGS84)

if __name__ == '__main__':
    sys.exit(main())