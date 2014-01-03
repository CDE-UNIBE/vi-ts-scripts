#!/bin/bash
#
# Script to extract bands from MODIS imagery
# Copyright (C) 2013-2014 Adrian Weber
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
# Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston, MA  02110-1301, USA.
#

# Check if VITS_DATA_PATH is set
if [ ! -d "$VITS_DATA_PATH" ]; then
    echo "Variable VITS_DATA_PATH is not set or not a directory."
    exit 1
fi

inputPath="$VITS_DATA_PATH/MODIS/MOLT"
# Path to processed NDVI raster bands
ndviOutputPath="$VITS_DATA_PATH/MODIS/processed/NDVI"
# Path to processed EVI raster bands
eviOutputPath="$VITS_DATA_PATH/MODIS/processed/EVI"
# Path to Quality raster bands
qualOutputPath="$VITS_DATA_PATH/MODIS/processed/QUAL" 

product="MOD13Q1.005"

# List of MODIS tiles
tiles="h16v08 h17v08 h18v04 h20v09 h21v07 h21v08 h21v09 h21v10 h22v07 h22v08 h22v09 h27v06 h27v07 h27v08 h28v06 h28v07 h28v08"

for timeDir in `find $inputPath/$product/* -type d`
do
    # Loop all tiles
    for tile in $tiles
    do
        hdfFileName=`ls "$timeDir/" | grep "${tile}.*hdf$"`
        # Handle NDVI raster band first
        # Create an output tile directory if not yet existing
        if [ ! -d "$ndviOutputPath/$tile" ]; then
            mkdir "$ndviOutputPath/$tile"
        fi
        if [ -f "$timeDir/$hdfFileName" ]; then
            ndviSubdatasetName=`gdalinfo $timeDir/$hdfFileName | grep -o SUBDATASET_1_NAME=.* | sed 's/SUBDATASET_1_NAME=//g'`
            if [ ! "$ndviSubdatasetName" == '' ]; then
                if [ ! -d "$ndviOutputPath/$tile" ]; then
                    mkdir "$ndviOutputPath/$tile"
                fi
                ndviOutputFileName=NDVI_`echo "'$ndviSubdatasetName'" | grep -o "MOD13Q1\.[0-9a-zA-Z\.]*\.hdf" | sed 's/\.hdf$/\.tif/g'`
                if [ ! -f "$ndviOutputPath/$tile/$ndviOutputFileName" ]; then
                    gdal_translate "$ndviSubdatasetName" "$ndviOutputPath/$tile/$ndviOutputFileName"
                fi
            else
                echo "$timeDir/$hdfFileName is not a valid GDAL raster"
                rm -rv "$timeDir/$hdfFileName"
                rm -rv "$timeDir/$hdfFileName.xml"
            fi
        fi
        # Handle EVI raster band
        # Create an output tile directory if not yet existing
        if [ ! -d "$eviOutputPath/$tile" ]; then
            mkdir "$eviOutputPath/$tile"
        fi
        if [ -f "$timeDir/$hdfFileName" ]; then
            eviSubdatasetName=`gdalinfo $timeDir/$hdfFileName | grep -o SUBDATASET_2_NAME=.* | sed 's/SUBDATASET_2_NAME=//g'`
            if [ ! "$eviSubdatasetName" == '' ]; then
                if [ ! -d "$eviOutputPath/$tile" ]; then
                    mkdir "$eviOutputPath/$tile"
                fi
                eviOutputFileName=EVI_`echo "'$eviSubdatasetName'" | grep -o "MOD13Q1\.[0-9a-zA-Z\.]*\.hdf" | sed 's/\.hdf$/\.tif/g'`
                if [ ! -f "$eviOutputPath/$tile/$eviOutputFileName" ]; then
                    gdal_translate "$eviSubdatasetName" "$eviOutputPath/$tile/$eviOutputFileName"
                fi
            else
                echo "$timeDir/$hdfFileName is not a valid GDAL raster"
                rm -rv "$timeDir/$hdfFileName"
                rm -rv "$timeDir/$hdfFileName.xml"
            fi
        fi
        # Handle QUAL raster band
        # Create an output tile directory if not yet existing
        if [ ! -d "$qualOutputPath/$tile" ]; then
            mkdir "$qualOutputPath/$tile"
        fi
        if [ -f "$timeDir/$hdfFileName" ]; then
            qualSubdatasetName=`gdalinfo $timeDir/$hdfFileName | grep -o SUBDATASET_3_NAME=.* | sed 's/SUBDATASET_3_NAME=//g'`
            if [ ! "$qualSubdatasetName" == '' ]; then
                if [ ! -d "$qualOutputPath/$tile" ]; then
                    mkdir "$qualOutputPath/$tile"
                fi
                qualOutputFileName=QUAL_`echo "'$qualSubdatasetName'" | grep -o "MOD13Q1\.[0-9a-zA-Z\.]*\.hdf" | sed 's/\.hdf$/\.tif/g'`
                if [ ! -f "$qualOutputPath/$tile/$qualOutputFileName" ]; then
                    gdal_translate "$qualSubdatasetName" "$qualOutputPath/$tile/$qualOutputFileName"
                fi
            else
                echo "$timeDir/$hdfFileName is not a valid GDAL raster"
                rm -rv "$timeDir/$hdfFileName"
                rm -rv "$timeDir/$hdfFileName.xml"
            fi
        fi
    done
done
