#!/usr/bin/env python2

import datetime
import json
import os.path
import sys

langs = ['java', 'python', 'python3']
basename = os.path.basename(sys.argv[0])
now = datetime.datetime.utcnow()
hdr = 'This file was autogenerated by %s' % (basename)
license = """
LINSTOR - management of distributed storage/DRBD9 resources
Copyright (C) 2017 - %s  LINBIT HA-Solutions GmbH
Author: %s

This program is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with this program.  If not, see <http://www.gnu.org/licenses/>.""" % (
    now.year, ', '.join(['Robert Altnoeder', 'Roland Kammerer', 'Gabor Hernadi']))


def get_type(e):
    try:
        return e['type'].lower()
    except:
        return None


def java(consts):
    indent = ' ' * 4

    print('/*\n * %s\n * %s */\n' % (hdr, ' * '.join([l.strip()+'\n' for l in license.split('\n')])))

    print('package com.linbit.linstor.api;\n')
    print('public class ApiConsts\n{')

    nl, w = '', 0
    for e in consts:
        w += 1
        if w > 1: nl = '\n'

        if 'blockcomment' in e:
            c = e['blockcomment'].replace('\n', '\n'+indent+' * ')
            print('%s%s/*\n %s* %s\n %s*/' % (nl, indent, indent, c, indent))
            continue

        gtype = get_type(e)
        value = e['value']

        if gtype:
            value = [str(x) for x in value]
            if gtype == 'bor':
                value = ' | '.join(value)
            elif gtype == 'band':
                value = ' & '.join(value)
        elif e['java'] == 'String':
            value = '"%s"' % (value)
        elif e['java'] == 'boolean':
            value = str(value).lower()

        c = "%spublic static final %s %s = %s;" % (indent, e['java'], e['name'], value)
        if 'comment' in e:
            c += " // %s" % (e['comment'])
        print(c)

    print('\n    private ApiConsts()\n    {\n    }')
    print('}')


def strip_L(value):
    return value[:-1] if str(value).endswith('L') else value


def python(consts):
    print('# %s\n' % (hdr))
    print('# '.join([l.strip()+'\n' for l in license.split('\n')]))
    print("""import sys
if sys.version_info > (3,):
    long = int
""")

    nl, w = '', 0
    for e in consts:
        w += 1
        nl = '\n' if w > 1 else ''

        if 'blockcomment' in e:
            c = e['blockcomment'].replace('\n', '\n# ')
            print('%s# ## %s ###' % (nl, c))
            continue

        gtype = get_type(e)
        value = e['value']

        if e['py'] == 'long':
            if isinstance(value, list):
                value = [strip_L(x) for x in value]
            else:
                value = strip_L(value)

        if gtype:
            value = [str(x) for x in value]
            if gtype == 'bor':
                value = ' | '.join(value)
            elif gtype == 'band':
                value = ' & '.join(value)
        elif e['py'] == 'str':
            value = "'%s'" % (value)

        c = "%s = %s(%s)" % (e['name'], e['py'], value)
        if 'comment' in e:
            c += "  # %s" % (e['comment'])
        print(c)


if len(sys.argv) != 2:
    sys.stderr.write("%s <language>\n\tcurrently supported: %s\n" % (basename, ', '.join(langs)))
    sys.exit(1)

language = sys.argv[1]
f = 'consts.json'
with open(f) as consts_file:
    try:
        consts = json.load(consts_file)
    except Exception as e:
        sys.stderr.write('The input file (%s) is not valid, better luck next time...\n' % (f))
        sys.stderr.write('Error: %s...\n' % (e))
        sys.exit(1)

    if language == 'java':
        java(consts)
    elif language == 'python':
        python(consts)
    else:
        sys.stderr.write("Language '%s' not valid, valid languages are: %s\n" % (language, ','.join(langs)))
        sys.exit(1)
