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
${VITS_DATA_PATH:?"Variable VITS_DATA_PATH is not set."}

if [ -d $HOME/bin ]; then
    export PATH=$HOME/bin:$PATH
fi

inputPath="$VITS_DATA_PATH/MODIS/MOLT"
outputPath="$VITS_DATA_PATH/MODIS/processed/NDVI"

product="MOD13Q1.005"

tiles="h16v08 h17v08 h18v04 h20v09 h21v07 h21v08 h21v09 h21v10 h22v07 h22v08 h22v09 h27v06 h27v07 h27v08 h28v06 h28v07 h28v08"

for timeDir in `find $inputPath/$product/* -type d`
do
    # Loop all tiles
    for tile in $tiles
    do
        # Create an output tile directory if not yet existing
        if [ ! -d "$outputPath/$tile" ]; then
            mkdir "$outputPath/$tile"
        fi
        hdfFileName=`ls "$timeDir/" | grep "${tile}.*hdf$"`
        if [ -f "$timeDir/$hdfFileName" ]; then
            subdatasetName=`gdalinfo $timeDir/$hdfFileName | grep -o SUBDATASET_1_NAME=.* | sed 's/SUBDATASET_1_NAME=//g'`
            if [ ! -d "$outputPath/$tile" ]; then
                mkdir "$outputPath/$tile"
            fi
            #echo "$subdatasetName"
            outputFileName=NDVI_`echo "'$subdatasetName'" | grep -o "MOD13Q1\.[0-9a-zA-Z\.]*\.hdf" | sed 's/\.hdf$/\.tif/g'`
            #echo $outputPath/$tile/$outputFileName
            #echo $subdatasetName
            if [ ! -f "$outputPath/$tile/$outputFileName" ]; then
                gdal_translate "$subdatasetName" "$outputPath/$tile/$outputFileName"
            fi
        fi
    done
done
