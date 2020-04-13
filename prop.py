#!/usr/bin/env python

import re
import os
import sys
from string import Template

worklist = [
    ('app', 'Xiaomi', 'APPS', '$(TARGET_COPY_OUT_VENDOR)', None),
    ('priv-app', 'Xiaomi', 'APPS', '$(TARGET_COPY_OUT_VENDOR)', None),
    ('vendor/app', 'Xiaomi', 'APPS', '$(TARGET_COPY_OUT_VENDOR)', None),
    ('framework', 'Xiaomi', 'JAVA_LIBRARIES', '$(TARGET_COPY_OUT_VENDOR)', None),
    ('lib', 'Xiaomi', 'SHARED_LIBRARIES',  '$(TARGET_COPY_OUT_VENDOR)', '32'),
    ('vendor/lib', 'Xiaomi', 'SHARED_LIBRARIES',  '$(TARGET_COPY_OUT_VENDOR)', '32'),
    ('lib64', 'Xiaomi', 'SHARED_LIBRARIES',  '$(TARGET_COPY_OUT_VENDOR)', '64'),
    ('vendor/lib64', 'Xiaomi', 'SHARED_LIBRARIES',  '$(TARGET_COPY_OUT_VENDOR)', '64'),
    ('etc', 'Xiaomi', 'ETC', '$(TARGET_COPY_OUT_VENDOR)', None),
    ('vendor/etc', 'Xiaomi', 'ETC', '$(TARGET_COPY_OUT_VENDOR)', None),
    ('bin', 'Xiaomi', 'EXECUTABLES', '$(TARGET_COPY_OUT_VENDOR)', None),
    ('vendor/bin', 'Xiaomi', 'EXECUTABLES', '$(TARGET_COPY_OUT_VENDOR)', None),
    ('vendor/firmware', 'Xiaomi', 'ETC', '$(TARGET_COPY_OUT_VENDOR)', None),
    ('vendor/framework', 'Xiaomi', 'JAVA_LIBRARIES', '$(TARGET_COPY_OUT_VENDOR)', None),
    ('vendor/radio', 'Xiaomi', 'ETC', '$(TARGET_COPY_OUT_VENDOR)', None),
    ('vendor/camera', 'Xiaomi', 'ETC', '$(TARGET_COPY_OUT_VENDOR)', None),
    ('vendor/usr', 'Xiaomi', 'ETC', '$(TARGET_COPY_OUT_VENDOR)', None),
]

#
# replace_in_file
#
# replace the section in between the two strings start and
# end with the text text
#
def replace_in_file(path, start, end, text):
    try:
        with open(path, 'r') as f:
            content = f.read()

        head = content[:content.index(start) + len(start)]
        if end:
            tail = content[content.index(end):]
        else:
            tail = ""

        content = "\n".join([head, text, tail])

        with open(path, 'w') as f:
            f.write(content)

    except IOError, err:
        print err
        sys.exit(1)

#
# list_files
#
# generate a sorted list of all files in a directory
#
def list_files(path, relpath):
    files = [os.path.join(subdir, f) for (subdir, dirs, files) in os.walk(path) for f in files]
    if relpath:
        files = [os.path.relpath(f, relpath) for f in files]
    return sorted(files)

#
# generate_module
#
# create a module object from a file name and parameters
#
def generate_module(f, owner, modclass, target_base, multilib):
    name = os.path.basename(f)
    stem, suffix = os.path.splitext(name)
    SEM13BS0 = f.find('SEM13BS0')
    SOI13BS0 = f.find('SOI13BS0')
    SOI25BS4 = f.find('SOI25BS4')

    mod = {}
    mod['files'] = f
    mod['owner'] = owner
    mod['module'] = name.replace('.', '_')
    mod['stem'] = stem
    mod['suffix'] = suffix

    if suffix == '.so' :
        mod['class'] = 'SHARED_LIBRARIES'
        mod['module'] = mod['module'] + '_' + multilib
        mod['class'] = mod['class'] + '\nLOCAL_MULTILIB := ' + multilib
        mod['class'] = mod['class'] + '\nLOCAL_STRIP_MODULE := false'
    else :
        mod['class'] = modclass

    if suffix == '.apk' or suffix == '.jar' :
        mod['class'] = mod['class'] + '\nLOCAL_CERTIFICATE := platform'

    if SEM13BS0 > 0 :
        mod['module'] = 'SEM13BS0_' + name.replace('.', '_')
    if SOI13BS0 > 0 :
        mod['module'] = 'SOI13BS0_' + name.replace('.', '_')
    if SOI25BS4 > 0 :
        mod['module'] = 'SOI25BS4_' + name.replace('.', '_')

    mod['target_base'] = target_base
    mod['target_path'] = os.path.dirname(f)
    return mod

#
# module_definition
#
# turn a mod into a text represenatation that define that module
#
def module_definition_for_colision(mod):
    module_template = Template(
    '''$files''')
    return module_template.substitute(mod)

def module_definition(mod):
    module_template = Template(
    '''$files''')
    return module_template.substitute(mod)

module_list = []
for work in worklist:
    files = list_files(os.path.join('proprietary', work[0]), 'proprietary')
    module_list += [generate_module(f, work[1], work[2], work[3], work[4]) for f in files]

module_count = {}
for module in module_list:
    if not module['stem'] in module_count:
        module_count[module['stem']] = 0
    module_count[module['stem']] += 1

definitions = []
packages = []
for module in module_list:
    if module_count[module['stem']] > 1:
        definitions.append(module_definition_for_colision(module))
        packages.append(module['module'])
    else:
        definitions.append(module_definition(module))
        packages.append(module['stem'])

definitions = "\n".join(definitions)
definitions = definitions + '\n'

packages = "\t" + " \\\n\t".join(packages)

replace_in_file('proprietary-files.txt', '#Begin', '#End', definitions)
