# -*- coding: utf-8 -*-

import xml.etree.cElementTree as ET
import codecs
import re
import pprint
import unicodecsv as csv # Uses unicodecsv module to handle encoding
import schema
import cerberus

NODES_PATH = "nodes.csv"
NODE_TAGS_PATH = "nodes_tags.csv"
WAYS_PATH = "ways.csv"
WAY_NODES_PATH = "ways_nodes.csv"
WAY_TAGS_PATH = "ways_tags.csv"

PROBLEMCHARS = re.compile(r'[=\+/&<>;\'"\?%#$@\,\. \t\r\n]')

SCHEMA = schema.schema

# Make sure the fields order in the csvs matches the column order in the sql table schema
NODE_FIELDS = ['id', 'lat', 'lon', 'user', 'uid', 'version', 'changeset', 'timestamp']
NODE_TAGS_FIELDS = ['id', 'key', 'value', 'type']
WAY_FIELDS = ['id', 'user', 'uid', 'version', 'changeset', 'timestamp']
WAY_TAGS_FIELDS = ['id', 'key', 'value', 'type']
WAY_NODES_FIELDS = ['id', 'node_id', 'position']

def validate_element(element, validator, schema=SCHEMA):
    """
    Raise ValidationError if element does not match schema

        Args:
            element: element to validade
            validator: cerberus Validator object
            schema: schema to validate

       Returns:
            Nothing
    
    """
    if validator.validate(element, schema) is not True:
        field, errors = next(validator.errors.iteritems())
        message_string = "\nElement of type '{0}' has the following errors:\n{1}"
        error_string = pprint.pformat(errors)
        raise Exception(message_string.format(field, error_string))

def get_element(osm_file, tags=('node', 'way', 'relation')):
    """
    Yield element if it is the right type of tag

        Args:
            osm_file: OSM XML file to parse
            tags: elements to search

        Yields:
            elem: element
    """

    context = ET.iterparse(osm_file, events=('start', 'end'))
    _, root = next(context)
    for event, elem in context:
        if event == 'end' and elem.tag in tags:
            yield elem
            root.clear()

def append_tag_dic(tags, id_, k, v, tp):
    """
    Create a dictionary of the tag data and append it to the 'tags' dictionary

        Args:
            tags: Tags dictionary
            id_: id of parent element
            k: key
            v: value
            tp: type

        Returns:
            Nothing
    """
    dic = {'id': id_,
           'key': k,
           'value': v,
           'type': tp}
    tags.append(dic)

def shape_tags(tagElements, id_, tags, problem_chars, default_tag_type,
               fixedStreetNames, specialStreetOverrides, fixedPostcodes):
    """
    Shapes the tags to the and appends to the tags dictionary

    Args:
        tagElements: Tag elements
        id_: id
        tags: Tags dictionary
        problem_chars: a regular expression to search for problematic characters
        default_tag_type: type to be used if no type is specified at the tag
        fixedStreetNames: dictionary of fixed street names provided by the audit_streetnames module
        specialStreetOverrides: dictionary of special street names that were fixed by hand
        fixedPostcodes: dictionary of fixed postal codes provided by the audit_postcodes module

    Returns:
        Nothing
    """
    for item in tagElements:
        key = item.attrib['k']
        if problem_chars.search(key):
            continue # If we have problematics characters, ignore the tag
        keylist = key.split(':') # Splits the tag if they have a :
        if len(keylist) > 1:
            tp = keylist[0] # If we have a :, the type is the first word, before the :
            if len(keylist[1:]) > 1: # If we have more than 1 :, the ramaining words are
                                     # treated as a key
                k = keylist[1]
                for key in keylist[2:]:
                    k = k + ':{}'.format(key)
            else:
                k = keylist[1]
        else:
            k = keylist[0]
            tp = default_tag_type # If we don't have a :, the type used is the default "regular"
        v = item.attrib['v']
        if k == 'street' and tp == 'addr': # If we have a street adress tag
            if v in fixedStreetNames.keys(): # Checks if the name was fixed using the
                                             # audit_streetnames module
                v = fixedStreetNames[v] # Uses the cleaned name
                append_tag_dic(tags, id_, k, v, tp)
            elif v in specialStreetOverrides.keys(): # If we have a special override, use it
                listDics = specialStreetOverrides[v]
                for dic in listDics:
                    tags.append(dic)
            else:
                append_tag_dic(tags, id_, k, v, tp)

        elif k == 'postal_code' or k == 'postcode': # If we have a postal code tag
            if v in fixedPostcodes.keys(): # Checks if the name was fixed using the
                                           # audit_postcodes module
                v = fixedPostcodes[v] # Uses the cleaned name
                if v != 'Invalid Postal Code': # Only appends valid postal codes to the dictionary
                    append_tag_dic(tags, id_, k, v, tp)
            else:
                append_tag_dic(tags, id_, k, v, tp)
        else:
            append_tag_dic(tags, id_, k, v, tp)


def shape_element(element, fixedStreetNames, specialStreetOverrides, fixedPostcodes,
                  node_attr_fields=NODE_FIELDS, way_attr_fields=WAY_FIELDS,
                  problem_chars=PROBLEMCHARS, default_tag_type='regular'):
    """
    Clean and shape node or way XML element to Python dict
    Args:
        element: XML emelement to shape
        fixedStreetNames: dictionary of fixed street names provided by the audit_streetnames module
        specialStreetOverrides: dictionary of special street names that were fixed by hand
        fixedPostcodes: dictionary of fixed postal codes provided by the audit_postcodes module
        node_attr_fields: standard node attributes declared before
        way_attr_fields: standard way attributes declared before
        problem_chars: a regular expression to search for problematic characters
        default_tag_type: type to be used if no type is specified at the tag

    Returns:
        A dictionary specific to the input element
    """
    node_attribs = {}
    way_attribs = {}
    way_nodes = []
    tags = []  # Handle secondary tags the same way for both node and way elements

    if element.tag == 'node':
        attr = element.attrib
        id_ = attr['id'] # Stores the ID to be used when parsing the tags
        for field in node_attr_fields:
            node_attribs[field] = attr[field]
    if element.tag == 'way':
        attr = element.attrib
        for field in way_attr_fields:
            way_attribs[field] = attr[field]
        waynd = element.iter('nd')
        id_ = attr['id'] # Stores the ID to be used when parsing the tags
        pos = 0
        for nd in waynd:
            node = {'id': id_,
                    'node_id': nd.attrib['ref'],
                    'position': pos}
            way_nodes.append(node)
            pos += 1
    tagElements = element.iter('tag')
    shape_tags(tagElements, id_, tags, problem_chars, default_tag_type, fixedStreetNames,
               specialStreetOverrides, fixedPostcodes)
    if element.tag == 'node':
        return {'node': node_attribs, 'node_tags': tags}
    elif element.tag == 'way':
        return {'way': way_attribs, 'way_nodes': way_nodes, 'way_tags': tags}

def execute(osmPath, validate=False, fixedStreetNames={},
            specialStreetOverrides={}, fixedPostcodes={}):
    """
    Main function of this module:
    Iteratively process each XML element and write to CSV files
    Args:
        osmPath: path and/or name of the OpenStreetMap XML file to parse
        validate: if True, use cerberus to validate the schema (slow)
        fixedStreetNames: dictionary of fixed street names provided by the audit_streetnames module
        specialStreetOverrides: dictionary of special street names that were fixed by hand
        fixedPostcodes: dictionary of fixed postal codes provided by the audit_postcodes module

        -> The last 3 defaults of empty dictionaries so this module can be used to parse dirty data
        -> and to fix it afterwards.
    Returns:
        Nothing
        Writes 5 csv files:
            - nodes.csv
            - nodes_tags.csv
            - ways.csv
            - ways_nodes.csv
            - ways_tags.csv
    """

    with codecs.open(NODES_PATH, 'wb') as nodes_file, \
         codecs.open(NODE_TAGS_PATH, 'wb') as nodes_tags_file, \
         codecs.open(WAYS_PATH, 'wb') as ways_file, \
         codecs.open(WAY_NODES_PATH, 'wb') as way_nodes_file, \
         codecs.open(WAY_TAGS_PATH, 'wb') as way_tags_file:

        nodes_writer = csv.DictWriter(nodes_file, NODE_FIELDS)
        node_tags_writer = csv.DictWriter(nodes_tags_file, NODE_TAGS_FIELDS)
        ways_writer = csv.DictWriter(ways_file, WAY_FIELDS)
        way_nodes_writer = csv.DictWriter(way_nodes_file, WAY_NODES_FIELDS)
        way_tags_writer = csv.DictWriter(way_tags_file, WAY_TAGS_FIELDS)

        nodes_writer.writeheader()
        node_tags_writer.writeheader()
        ways_writer.writeheader()
        way_nodes_writer.writeheader()
        way_tags_writer.writeheader()

        validator = cerberus.Validator()

        for element in get_element(osmPath, tags=('node', 'way')):
            el = shape_element(element, fixedStreetNames=fixedStreetNames, 
                               specialStreetOverrides=specialStreetOverrides,
                               fixedPostcodes=fixedPostcodes)
            if el:
                if validate is True:
                    validate_element(el, validator)

                if element.tag == 'node':
                    nodes_writer.writerow(el['node'])
                    node_tags_writer.writerows(el['node_tags'])
                elif element.tag == 'way':
                    ways_writer.writerow(el['way'])
                    way_nodes_writer.writerows(el['way_nodes'])
                    way_tags_writer.writerows(el['way_tags'])

if __name__ == '__main__':
    # If the module is used directly, execute the main function with standard arguments,
    # creating a dirty set of CSVs
    # To use the module with the cleaning dictionaries, first import it to a script, as
    # seen in main.py
    execute("curitiba.osm", validate=False)
