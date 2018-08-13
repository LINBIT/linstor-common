#!/usr/bin/env python2
import argparse
import sys
import subprocess
import xml.etree.ElementTree as ET


"""
This script translates xml output from drbdsetup options to an usable languages presentation
in implemented languages
"""


def get_drbd_setup_xml(from_file):
    drbdsetup_cmd = ['/usr/sbin/drbdsetup', 'xml-help']
    opts = ['disk-options', 'peer-device-options', 'resource-options', 'new-peer']
    try:
        xml_opts = [subprocess.check_output(drbdsetup_cmd + [x]) for x in opts]
    except OSError as oe:
        sys.stderr.write("Unable to execute drbdsetup: {cmd}\nUsing local file {f}\n".format(
            cmd=" ".join(drbdsetup_cmd),
            f=from_file)
        )
        with open(from_file) as f:
            return f.read()

    return '<root>\n' + "".join(xml_opts) + '</root>'


def parse_drbd_setup_xml(xmlout):
    root = ET.fromstring(xmlout)

    options = {}
    for command in root:
        cmd_name = command.attrib['name']
        for child in command:
            if child.tag == 'summary':
                #options['help'] = child.text
                pass
            elif child.tag == 'argument':
                # ignore them
                pass
            elif child.tag == 'option':
                opt = child.attrib['name']
                if opt in ['set-defaults', '_name']:
                    continue

                options[opt] = {
                    'type': child.attrib['type'] if child.attrib['type'] != 'handler' else 'symbol',
                    'category': cmd_name
                }
                if child.attrib['type'] == 'boolean':
                    options[opt]['default'] = True if child.find('default').text == 'yes' else False
                if child.attrib['type'] == 'handler':
                    options[opt]['symbols'] = [h.text for h in child.findall('handler')]
                elif child.attrib['type'] == 'numeric':
                    for v in ('unit_prefix', 'unit'):
                        val = child.find(v)
                        if val is not None:
                            options[opt][v] = val.text
                    for v in ['min', 'max', 'default']:
                        val = child.find(v)
                        if val is not None:
                            options[opt][v] = int(val.text)
                elif child.attrib['type'] == 'numeric-or-symbol':
                    options[opt]['symbols'] = [h.text for h in child.findall('symbol')]
                    options[opt]['min'] = child.find('min').text
                    options[opt]['max'] = child.find('max').text

    return {
        "options": options,
        "filters": {
            "resource": [x for x in options.keys() if options[x]['category'] in _FilterResource],
            "volume": [x for x in options.keys() if options[x]['category'] in _FilterVolume],
            "peer-device-options": [x for x in options.keys() if options[x]['category'] in _FilterPeerDevice]
        }
    }


_CategoyMap = {
    'new-peer': "DrbdOptions/Net",
    'disk-options': "DrbdOptions/Disk",
    'resource-options': "DrbdOptions/Resource",
    'peer-device-options': "DrbdOptions/PeerDevice"
}

_FilterResource = ['disk-options', 'resource-options', 'new-peer', 'peer-device-options']
_FilterVolume = ['disk-options']  # TODO add volume connection -> 'peer-device-options'
_FilterPeerDevice = ['peer-device-options', 'new-peer']


def whitelist(conf):
    props = {}
    objs = {}

    for opt_name in conf['options']:
        opt = conf['options'][opt_name]
        is_range = opt['type'] == 'numeric' and 'min' in opt
        props[opt_name] = {
            'key': _CategoyMap[opt['category']] + '/' + opt_name,
            'internal': True,
            'type': 'range' if is_range else opt['type']
        }

        if is_range or opt['type'] == 'numeric-or-symbol':
            props[opt_name]['min'] = opt['min']
            props[opt_name]['max'] = opt['max']

        if opt['type'] == 'symbol' or opt['type'] == 'numeric-or-symbol':
            props[opt_name]['values'] = opt['symbols']

    objs['controller'] = [x for x in conf['options']]
    objs['resource-definition'] = [x for x in conf['options'] if conf['options'][x]['category'] in _FilterResource]
    objs['volume-definition'] = [x for x in conf['options'] if conf['options'][x]['category'] in _FilterVolume]
    objs['rsc-conn'] = [x for x in conf['options'] if conf['options'][x]['category'] in _FilterPeerDevice]
    return {
        'properties': props,
        'objects': objs
    }


def gendrbd(output_target, python_code):
    xml = get_drbd_setup_xml('drbdsetup.xml')
    conf = parse_drbd_setup_xml(xml)
    import json
    import pprint

    white = whitelist(conf)

    with open(output_target, 'wt') as f:
        f.write(json.dumps(white, f, indent=2))

    if python_code:
        with open(python_code, 'wt') as f:
            # header with a readable dump
            f.write('"""\nDo not edit, this file is generated."""\n\n')
            # f.write('Json representation for viewing:\n')
            # f.write(json.dumps(conf, f, indent=2))
            # f.write('\n"""\n\n')
            # actual usable dump
            #f.write('drbdoptions_raw = """' + pickle.dumps(conf) + '"""')
            f.write('drbd_options = ')
            pprint.pprint(conf, stream=f, indent=4)

    return 0


def main():
    parser = argparse.ArgumentParser(description="generates prepared code containing drbd options")
    parser.add_argument("drbdoptions")
    parser.add_argument("python_code", nargs='?')

    args = parser.parse_args()

    sys.exit(gendrbd(args.drbdoptions, args.python_code))


if __name__ == '__main__':
    main()
