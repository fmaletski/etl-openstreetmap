import xml.etree.cElementTree as ET
from collections import defaultdict
import re
import pprint

OSMFILE = "curitiba.osm"
street_type_re = re.compile(r'^\S+', re.IGNORECASE) # Searches for the first word of a
                                                    # sentence (brazilian street names
                                                    # always start with the street type)

# Expected values
expected = ["Rua", "Avenida", "Travessa", "Praça", "Rodovia", "Alameda", "Estrada", "Linha", "Largo", "Marginal"]

# Dictionary to correct most problems found in the data
mapping = { "Av": "Avenida",
            "Av.": "Avenida",
            "R.": "Rua",
            'rua': 'Rua',
            'RUA': 'Rua'
          }


def audit_street_type(street_types, street_name):
    """
    Audit whether or not a street name (street_name) has an expected street type
    if not, adds the name to a problematic street names dictionary (street_types)

    Args:
        street_name: a street name
        street_types: problematic street names dictionary

    Returns:
        Nothing
    """
    m = street_type_re.search(street_name)
    if m:
        street_type = m.group()
        if street_type not in expected:
            street_types[street_type].add(street_name)


def is_street_name(elem):
    """
    Checks if an element is a street name

    Args:
        elem: XML element

    Returns:
        The element if it is a street name
    """
    return elem.attrib['k'] == "addr:street"


def audit(osmfile):
    """
    Audits a OSM XML file for street names

    Args:
        osmfile: OSM XML file path

    Returns:
        street_types: problematic street names dictionary
    """
    osm_file = open(osmfile, "r", encoding='UTF-8')
    street_types = defaultdict(set)
    for event, elem in ET.iterparse(osm_file, events=("start",)):
        if elem.tag == "node" or elem.tag == "way":
            for tag in elem.iter("tag"):
                if is_street_name(tag):
                    audit_street_type(street_types, tag.attrib['v'])
    osm_file.close()
    return street_types


def update_name(name, mapping):
    """
    Updates a street type to a better one if found in the mapping dictionary,
    if not, returns the name unchanged

    Args:
        name: name to update
        mapping: dictionary to correct most problems found in the data

    Returns:
        name: updated name
    """

    n = name.split(' ')
    if n[0] in mapping.keys():
        n[0] = mapping[n[0]]
        name = n[0]
        for word in n[1:]:
            name = name + ' {}'.format(word)
    return name


def execute(osmFile, highlightUnchanged=False, prints=False, overrides={}, specialOverrides={}):
    """
    Main function of this module:

    Args:
        osmFile: OSM XML file to parse
        highlightUnchanged: highlights names that should be fixed, but weren't with a * if True
        prints: If True, prints every change to be made to the data
        overrides: Dictionary of manual overrides
        specialOverrides: Dictionary of special cases

    Returns:
        A dictionary of every change to be made to the data to be used in the osmparser module
    """

    st_types = audit(osmFile)
    changeDict = {}
    for st_type, ways in st_types.items():
        for name in ways:
            better_name = update_name(name, mapping) # Tries to update the names automatically
            if name in overrides.keys(): # If the name is in the overrides ditionary, use it instead
                better_name = overrides[name]
            if name not in specialOverrides.keys(): # If the name is not a special case, add if to
                                                    # the dictionary to be returned
                changeDict[name] = better_name
            if prints is True:
                if highlightUnchanged is True and name == better_name: # Highlight unchanged names if
                                                                    # highlightUnchanged is True
                    name = '* {}'.format(name)
                print(name, "=>", better_name)
    return changeDict


if __name__ == '__main__':
    # If the module is used directly, execute the main function with standard arguments
    # To use the module with the cleaning dictionaries, first import it to a script, as
    # seen in main.py
    execute('curitiba.osm', True, True)
