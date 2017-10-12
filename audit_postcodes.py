import xml.etree.cElementTree as ET
from collections import defaultdict
import re

postalCodeRe = re.compile(r'^\d{5}-\d{3}') #It'll return only if the postal code is perfect

def test_postcode(value):
    """
    Tests if a postal code is within the acceptable range for the Curitiba Metropolitan Region

    Args:
        value: postal code to test

    Returns:
        True, if within acceptable range
        False, if not, or if the .replace fails
    """
    try:
        testCode = int(value.replace('-', ''))
        if testCode >= 80000001 and testCode <= 83800999:
            return True
        else:
            return False
    except:
        return False # If the .replace fails, it means the post code is not in a valid format

def audit_postcode(postal_codes, value):
    """
    Audit whether or not a postal code is in the correct format and within the acceptable range
    
    Args:
        postal_codes: problematic postal codes dictionary
        value: postal code to audit
    Returns:
        Nothing
    """
    correct = postalCodeRe.search(value)
    if correct:
        if not test_postcode(value): # If it's not in the acceptable range
            postal_codes[value] = 'Invalid Postal Code'
    if not correct: # If the postal code is not in the standard format
        if len(value) == 8: # If the postal code is only missing the dash (-) it should be
                            # just 8 characters long
            correctValue = value[:5] + '-' + value[5:] # Adds the dash
            if not test_postcode(correctValue): # If it's not in the acceptable range
                correctValue = 'Invalid Postal Code'
        elif '.' in value: # If it has a dot
            correctValue = value.replace('.', '')
            if not test_postcode(correctValue): # If it's not in the acceptable range
                correctValue = 'Invalid Postal Code'
        else:
            correctValue = 'Invalid Postal Code'
        postal_codes[value] = (correctValue)


def is_postcode(elem):
    """
    Tests if an element is a postal code

    Args:
        elem: XML element

    Returns:
        The element if it is a postal code
    """

    if elem.attrib['k'] == "addr:postcode" or elem.attrib['k'] == "postal_code":
        return True


def audit(osmfile):
    """
    Audits a OSM XML file for postal codes

    Args:
        osmfile: OSM XML file path

    Returns:
        postal_codes: problematic postal codes dictionary
    """
    osm_file = open(osmfile, "r", encoding='UTF-8')
    postal_codes = defaultdict(set)
    for event, elem in ET.iterparse(osm_file, events=("start",)):
        if elem.tag == "node" or elem.tag == "way":
            for tag in elem.iter("tag"):
                if is_postcode(tag):
                    audit_postcode(postal_codes, tag.attrib['v'])
    osm_file.close()
    return postal_codes


def execute(osmFile, highlightUnchanged=False, prints=False):
    """
    Main function of this module:

    Args:
        osmFile: OSM XML file to parse
        highlightUnchanged: highlights names that should be fixed, but weren't with a * if True
        prints: If True, prints every change to be made to the data

    Returns:
        A dictionary of every change to be made to the data to be used in the osmparser module
    """
    postal_codes = audit(osmFile)
    if prints is True:
        for value, correctValue in postal_codes.items():
            if highlightUnchanged == True and correctValue == 'Invalid Postal Code':
                value = '* {}'.format(value)
            print(value, "=>", correctValue)
    return postal_codes


if __name__ == '__main__':
    # If the module is used directly, execute the main function with standard arguments
    execute('curitiba.osm', True, True)
    