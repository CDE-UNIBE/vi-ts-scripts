#!/bin/bash
#                                         
# Bash script to download MODIS imagery
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

#${VITS_DATA_PATH:?"Variable VITS_DATA_PATH is not set."}
if [ ! -d "$VITS_DATA_PATH" ]; then
    echo "Variable VITS_DATA_PATH is not set or not a directory."
    exit 1
fi

baseUrl="http://e4ftl01.cr.usgs.gov/MOLT"
product="MOD13Q1.005"

localPath="$VITS_DATA_PATH/MODIS/MOLT"

tiles="h16v08 h17v08 h18v04 h20v09 h21v07 h21v08 h21v09 h21v10 h22v07 h22v08 h22v09 h27v06 h27v07 h27v08 h28v06 h28v07 h28v08"

for d in `wget -q -O - "$baseUrl/$product/" | grep -o "<a\ href=\"[0-9]*\.[0-9][0-9].[0-9][0-9]\/\">" | sed 's/<a\ href=\"//g' | sed 's/\/\">//g'`
do
    echo "Start processing timestamp $d"
    if [ ! -d "$localPath/$product/$d" ]; then
        mkdir "$localPath/$product/$d"
    fi
    timeUrl="$baseUrl/$product/$d"
    # Get the directory for the current timestamp
    wget -q -O timeIndex "$timeUrl/"
    # Loop all requested MODIS tiles
    for tile in $tiles
    do
        echo "Start processing tile $tile"
        # Extract the tile name for the current tile and time stamp
        tilename=`cat timeIndex | grep -io "<a\ href=\"MOD13Q1.[0-9a-zA-Z]*\.$tile\.[0-9]*\.[0-9]*\.hdf\">" | sed 's/<a\ href=\"//g' | sed 's/\">//g'`
        if [ ! -f "$localPath/$product/$d/$tilename" ]; then
            wget -O "$localPath/$product/$d/$tilename" "$timeUrl/$tilename"
        fi
        if [ ! -f "$localPath/$product/$d/$tilename.xml" ]; then
            wget -O "$localPath/$product/$d/$tilename.xml" "$timeUrl/$tilename.xml"
        fi
    done
    # Clean up
    rm -f timeIndex
done
