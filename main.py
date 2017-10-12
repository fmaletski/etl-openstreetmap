"""
This script executes all the code necessary to create a clean SQLite3 database from the
curitiba.osm OpenStreetMap XML file
It is commented, but further details can be found on the Project.ipynb file
"""

import osmparser
import sqlcreator
import audit_streetnames
import audit_postcodes
# Imports the necessary modules

from overrides import streetOverrides, specialStreetOverrides
# Imports the override dictionaries

fixedStreetNames = audit_streetnames.execute('curitiba.osm', True, True,
                                             overrides=streetOverrides,
                                             specialOverrides=specialStreetOverrides)
# Creates a dictionary of street names to fix using both the automatic and the override fixes
# And print the changes

fixedPostcodes = audit_postcodes.execute('curitiba.osm', True, True)
# Creates a dictionary of postal codes to fix using both the automatic fixes
# And print the changes

osmparser.execute('curitiba.osm', validate=True, fixedStreetNames=fixedStreetNames,
                  specialStreetOverrides=specialStreetOverrides,
                  fixedPostcodes=fixedPostcodes)
# Using the above mentioned dictionaries and the specialStreetOverrides one, creates a set of
# CSVs using the OSM XML
# Obs: set validate to False to not use the schema validation processs (it can take a long time)

sqlcreator.execute('curitiba.db')
# Creates the SQLite3 database using the cleaned CSVs previously generated
