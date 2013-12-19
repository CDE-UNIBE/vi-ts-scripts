#!/bin/bash

###########################################
#                                         #
# Bash script to download MODIS imagery   #
#                                         #
###########################################

baseUrl="http://e4ftl01.cr.usgs.gov/MOLT"

localPath="/home/webuser/Data/MODIS/MOLT"

product="MOD13Q1.005"

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
