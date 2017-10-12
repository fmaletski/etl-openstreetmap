Files in this project:

audit_postcodes.py - Module to audit postal codes and clean them
audit_streetnames.py - Module to audit street names and clean them
link_to_map.txt - Link to the map of the region used on the project and link to download the complete OSM XML file
main.py - Python Script that does all the cleaning process and creates the cleaned database
osmparser.py - OSM XML parser and CSV creator, has funcionality to clean the data too if requested
overrides.py - Contains the override dictionaries
plot_map.py - Module to print the map used in the Project-Report
Project.ipynb - Main project Jupyter Notebook
Project.html - HTML version
Project-Report.ipynb - The Jupyter Notebook used to generate the report to be graded
Project-Report.html - HTML version
Project-Report.pdf - PDF version
README.txt - This file
references.txt - References used for this project
sample.osm - Sample of the dataset as requested
sample_generator.py - Script used to generate the sample
schema.py - Schema file used by cerberus
sqlcreator.py - Module that creates SQLite3 databases from the CSV files
sqloperations.py - Module used to communicate with the SQLite3 databases

Recommended Python version:

Anaconda 4.3.1 using Python 3 64 bits with all the current updates
- Installation of the 'cerberus' module is necessary (I used pip)

Changelog - rev 1

- Created the project report (ipynb, html and pdf), simplified version of the Project within the length contraints
- Removed Project.pdf
- Created main.py, a module that does all the process documented in the Project notebooks
- Created overrides.py, contains the override dictionaries created during the data cleaning
- Created plot_map.py, plots the map used in the report
- Updated all the docsstrings to the PEP 484 standard
- Created an analysis of the problems in implementing the idea to fix the postal codes (Google Maps API)