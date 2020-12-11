#!/usr/bin/env python3
import argparse
import sys
import subprocess
import xml.etree.ElementTree as ET


"""
This script translates xml output from drbdsetup options to JSON
"""


_CategoryNamespaces = {
    'new-peer': "DrbdOptions/Net",
    'disk-options': "DrbdOptions/Disk",
    'resource-options': "DrbdOptions/Resource",
    'peer-device-options': "DrbdOptions/PeerDevice"
}

# map a CategoryNamespace to a .res file section
_ResfileSections = {
    'DrbdOptions/Net': 'net',
    'DrbdOptions/Disk': 'disk',
    'DrbdOptions/Resource': 'options',
    'DrbdOptions/PeerDevice': 'disk',
    'DrbdOptions/Handlers': 'handlers'
}

_ObjectCategories = {
    "controller": ['disk-options', 'resource-options', 'new-peer', 'peer-device-options'],
    "resource-definition": ['disk-options', 'resource-options', 'new-peer', 'peer-device-options'],
    "volume-definition": ['disk-options'],  # TODO add volume connection -> 'peer-device-options'
    "rsc-conn": ['peer-device-options', 'new-peer']
}


def get_drbd_setup_xml(from_file):
    if from_file:
        with open(from_file) as f:
            return f.read()

    drbdsetup_cmd = ['/usr/sbin/drbdsetup', 'xml-help']
    opts = ['disk-options', 'peer-device-options', 'resource-options', 'new-peer']
    xml_opts = []
    try:
        xml_opts = [subprocess.check_output(drbdsetup_cmd + [x]) for x in opts]
    except OSError as oe:
        sys.stderr.write("Unable to execute drbdsetup: {cmd}\nUsing local file {f}\n".format(
            cmd=" ".join(drbdsetup_cmd),
            f=from_file)
        )

    return '<root>\n' + "".join(xml_opts) + '</root>'


def create_and_add_handlers_option(properties, option_name):
    if option_name in properties:
        raise RuntimeError("drbd option name already in use: " + option_name)

    cmd_namespace = 'DrbdOptions/Handlers'
    properties[option_name] = {
        'internal': True,
        'key':  cmd_namespace + '/' + option_name,
        'drbd_option_name': option_name,
        'drbd_res_file_section': _ResfileSections[cmd_namespace],
        'type': 'string'
    }

    return properties


def add_handlers(objects, properties):
    handlers = [
        "after-resync-target",
        "before-resync-target",
        "before-resync-source",
        "out-of-sync",
        "quorum-lost",
        "fence-peer",
        "unfence-peer",
        "initial-split-brain",
        "local-io-error",
        "pri-lost",
        "pri-lost-after-sb",
        "pri-on-incon-degr",
        "split-brain"
    ]

    for h in handlers:
        create_and_add_handlers_option(properties, h)
        objects["controller"].append(h)
        objects["resource-definition"].append(h)

    return properties


def parse_drbd_setup_xml(xmlout):
    root = ET.fromstring(xmlout)

    objects = {k: [] for k in _ObjectCategories.keys()}
    properties = {}
    for command in root:
        cmd_name = command.attrib['name']
        cmd_namespace = _CategoryNamespaces[cmd_name]

        cmd_properties = {}
        for option in command.findall('option'):
            option_name = option.attrib['name']
            if option_name not in ['set-defaults', '_name']:
                cmd_properties[option_name] = convert_option(cmd_namespace, option_name, option)

        for obj, categories in _ObjectCategories.items():
            if cmd_name in categories:
                objects[obj].extend(cmd_properties.keys())
        properties.update(cmd_properties)

    # add handlers section options
    add_handlers(objects, properties)

    # patch resync-after to be type `string`, the type is still wrong in the drbdsetup.xml
    properties['resync-after']['type'] = "string"
    del properties['resync-after']['max']
    del properties['resync-after']['min']
    del properties['resync-after']['default']
    del properties['resync-after']['unit_prefix']

    return {
        "objects": objects,
        "properties": properties
    }


def convert_option(cmd_namespace, option_name, option):
    option_type = option.attrib['type']

    prop = {
        'internal': True,
        'key': cmd_namespace + '/' + option_name,
        'drbd_option_name': option_name,
        'drbd_res_file_section': _ResfileSections[cmd_namespace]
    }

    if option_type == 'string':
        prop_type = option_type
    elif option_type == 'boolean':
        prop_type = option_type
        prop['default'] = True if option.find('default').text == 'yes' else False
    elif option_type == 'handler':
        prop_type = 'symbol'
        prop['values'] = [h.text for h in option.findall('handler')]
    elif option_type == 'numeric':
        for v in ('unit_prefix', 'unit'):
            val = option.find(v)
            if val is not None:
                prop[v] = val.text
        for v in ['min', 'max', 'default']:
            val = option.find(v)
            if val is not None:
                prop[v] = int(val.text)
        prop_type = 'range' if 'min' in prop.keys() else 'numeric'
    elif option_type == 'numeric-or-symbol':
        prop_type = option_type
        prop['values'] = [h.text for h in option.findall('symbol')]
        prop['min'] = option.find('min').text
        prop['max'] = option.find('max').text
    else:
        raise RuntimeError('Unknown option type ' + option_type)

    prop['type'] = prop_type

    return prop


def gendrbd(output_target):
    xml = get_drbd_setup_xml('drbdsetup.xml')
    props = parse_drbd_setup_xml(xml)
    import json

    with open(output_target, 'wt') as f:
        json.dump(props, f, indent=2, separators=(',', ': '))

    return 0


def main():
    parser = argparse.ArgumentParser(description="generates prepared code containing drbd options")
    parser.add_argument("drbdoptions")

    args = parser.parse_args()

    sys.exit(gendrbd(args.drbdoptions))


if __name__ == '__main__':
    main()
