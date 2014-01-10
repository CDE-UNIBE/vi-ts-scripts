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

import os
import re
from urllib import urlretrieve
from urllib2 import urlopen
from processing import extract_bands

# Check if VITS_DATA_PATH is set
if "VITS_DATA_PATH" not in os.environ:
    print "Variable VITS_DATA_PATH is not set or not a directory."
    sys.exit(1)

product = "MOD13Q1.005"

# Main URL to the remote MODIS archive server
remote_base_url = "http://e4ftl01.cr.usgs.gov/MOLT/%s" % product

# Path to the local storage directory
local_base_path = "%s/MODIS/MOLT/%s" % (os.environ['VITS_DATA_PATH'], product)

# List of MODIS tiles that will be downloaded
#tiles = ["h16v08", "h17v08", "h18v04", "h20v09", "h21v07", "h21v08", "h21v09",
#"h21v10", "h22v07", "h22v08", "h22v09", "h27v06", "h27v07", "h27v08", "h28v06",
#"h28v07", "h28v08"]

tiles = ["h16v08"]

# Read the remote main page to get a list of all available timestamps
mainpage = urlopen(remote_base_url)
mainpage_content = mainpage.read()
# Extract all links that point to a timestamp
ahref_list = re.findall("<a\ href=\"[0-9]*\.[0-9][0-9].[0-9][0-9]\/\">", mainpage_content, re.MULTILINE)
# Get the raw data value from the list of links
ltrimmed_timestamp_list = map(lambda x: re.sub(r"<a\ href=\"", "", x), ahref_list)
timestamp_list = map(lambda x: re.sub(r"\/\">", "", x), ltrimmed_timestamp_list)

for d in timestamp_list[-5:]:
    sys.stdout.write("Start processing timestamp %s\n" % d)

    local_timestamp_path = "%s/%s" % (local_base_path, d)
    if not os.path.exists(local_timestamp_path):
        os.mkdir(local_timestamp_path)

    # Open and read the remote timestamp file directory
    remote_timestamp_url = "%s/%s" % (remote_base_url, d)
    remote_timestamp_page = urlopen("%s/" % remote_timestamp_url)
    remote_timestamp_page_content = remote_timestamp_page.read()

    # Loop through all requested tiles
    for tile in tiles:
        sys.stdout.write("Start processing tile \"%s\"\n" % tile)
        remote_tile_ahref = re.search(r"<a\ href=\"MOD13Q1.[0-9a-zA-Z]*\.%s\.[0-9]*\.[0-9]*\.hdf\">" % tile, remote_timestamp_page_content).group(0)
        #sys.stdout.write("%s\n" % remote_tile_ahref)
        ltrimmed_remote_tile_ahref = re.sub(r"<a\ href=\"", "", remote_tile_ahref)
        tilename = re.sub(r"\">", "", ltrimmed_remote_tile_ahref)
        #sys.stdout.write(tilename)
        local_tile_path = "%s/%s" % (local_timestamp_path, tilename)
        # If the output local file does not yet exists, start downloading and
        # processing it
        if not os.path.exists(local_tile_path):
            remote_tile_url = "%s/%s" % (remote_timestamp_url, tilename)
            sys.stdout.write("Downloading \"%s\"\n" % remote_tile_url)
            urlretrieve(remote_tile_url, local_tile_path)

            # Extract the NDVI, EVI and QUAL bands
            extract_succeeded = extract_bands.main(local_tile_path, tile)

            # Delete the original, downloaded HDF file to save disk space on the
            # server and create a "dummy" replacement file to indicate already
            # processed tiles.
            if extract_succeeded:
                # Delete the input file
                sys.stdout.write("File to delete: \"%s\"\n" % local_tile_path)
                os.remove(local_tile_path)
                # Create a replacement file with an empty content
                replacement_file = open(local_tile_path, "w+")
                # Write an empty string to the file
                replacement_file.write("")
                # Close the dummy file again
                replacement_file.close()