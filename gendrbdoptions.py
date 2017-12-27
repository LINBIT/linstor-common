#!/usr/bin/env python2
import argparse
import sys
import subprocess
import xml.etree.ElementTree as ET


"""
This script translates xml output from drbdsetup options to an usable languages presentation
in implemented languages
"""


def get_drbd_setup_xml(from_file=None):
    if from_file:
        with open(from_file) as f:
            return f.read()

    drbdsetup_cmd = ['/usr/sbin/drbdsetup', 'xml-help']
    opts = ['disk-options', 'peer-device-options', 'resource-options', 'net-options']
    try:
        xml_opts = [subprocess.check_output(drbdsetup_cmd + [x]) for x in opts]
    except OSError as oe:
        sys.stderr.write("Unable to execute drbdsetup: {cmd}\n".format(cmd=" ".join(drbdsetup_cmd)))
        sys.stderr.write("  " + str(oe) + '\n')
        sys.exit(9)

    return '<root>\n' + "".join(xml_opts) + '</root>'


def parse_drbd_setup_xml(xmlout):
    root = ET.fromstring(xmlout)

    config = {}
    for command in root:
        cmd_name = command.attrib['name']
        for child in command:
            if child.tag == 'summary':
                config['help'] = child.text
            elif child.tag == 'argument':
                # ignore them
                pass
            elif child.tag == 'option':
                opt = child.attrib['name']
                config[opt] = {
                    'type': child.attrib['type'],
                    'category': cmd_name
                }
                if child.attrib['name'] == 'set-defaults':
                    continue
                if child.attrib['type'] == 'boolean':
                    config[opt]['default'] = True if child.find('default').text == 'yes' else False
                if child.attrib['type'] == 'handler':
                    config[opt]['handlers'] = [h.text for h in child.findall('handler')]
                elif child.attrib['type'] == 'numeric':
                    for v in ('unit_prefix', 'unit'):
                        val = child.find(v)
                        if val is not None:
                            config[opt][v] = val.text
                    for v in ['min', 'max', 'default']:
                        val = child.find(v)
                        if val is not None:
                            config[opt][v] = int(val.text)
    return config


def gen_java(output_target):
    return 1


def gen_python(output_target):
    # xml = get_drbd_setup_xml('drbdsetup.xml')
    xml = get_drbd_setup_xml()
    conf = parse_drbd_setup_xml(xml)
    import pickle
    import json
    with open(output_target, 'wt') as f:
        # header with a readable dump
        f.write('"""\nDo not edit, this file is generated.\n\n')
        f.write('Json representation for viewing:\n')
        f.write(json.dumps(conf, f, indent=2))
        f.write('\n"""\n\n')
        # actual usable dump
        f.write('drbdoptions_raw = """' + pickle.dumps(conf) + '"""')

    return 0


def main():
    parser = argparse.ArgumentParser(description="generates prepared code containing drbd options")
    parser.add_argument("language", choices=['python', 'java'])
    parser.add_argument("output_target")

    args = parser.parse_args()

    lang_map = {
        'python': gen_python,
        'java': gen_java
    }

    sys.exit(lang_map[args.language](args.output_target))


if __name__ == '__main__':
    main()
