#!/usr/bin/env python
# -*- Mode: Python; coding: utf-8; indent-tabs-mode: nil; tab-width: 4 -*-
### BEGIN LICENSE
# This file is in the public domain
### END LICENSE

###################### DO NOT TOUCH THIS (HEAD TO THE SECOND PART) ######################

import os
import sys

try:
    import DistUtilsExtra.auto
except ImportError:
    print >> sys.stderr, 'To build podio-task-list you need https://launchpad.net/python-distutils-extra'
    sys.exit(1)
assert DistUtilsExtra.auto.__version__ >= '2.18', 'needs DistUtilsExtra.auto >= 2.18'

def update_config(values = {}):

    oldvalues = {}
    try:
        fin = file('podio_task_list_lib/podio_task_listconfig.py', 'r')
        fout = file(fin.name + '.new', 'w')

        for line in fin:
            fields = line.split(' = ') # Separate variable from value
            if fields[0] in values:
                oldvalues[fields[0]] = fields[1].strip()
                line = "%s = %s\n" % (fields[0], values[fields[0]])
            fout.write(line)

        fout.flush()
        fout.close()
        fin.close()
        os.rename(fout.name, fin.name)
    except (OSError, IOError), e:
        print ("ERROR: Can't find podio_task_list_lib/podio_task_listconfig.py")
        sys.exit(1)
    return oldvalues


def update_desktop_file(datadir):

    try:
        fin = file('podio-task-list.desktop.in', 'r')
        fout = file(fin.name + '.new', 'w')

        for line in fin:            
            if 'Icon=' in line:
                line = "Icon=%s\n" % (datadir + 'media/podio-task-list.svg')
            fout.write(line)
        fout.flush()
        fout.close()
        fin.close()
        os.rename(fout.name, fin.name)
    except (OSError, IOError), e:
        print ("ERROR: Can't find podio-task-list.desktop.in")
        sys.exit(1)


class InstallAndUpdateDataDirectory(DistUtilsExtra.auto.install_auto):
    def run(self):
        values = {'__podio_task_list_data_directory__': "'%s'" % (self.prefix + '/share/podio-task-list/'),
                  '__version__': "'%s'" % self.distribution.get_version()}
        previous_values = update_config(values)
        update_desktop_file(self.prefix + '/share/podio-task-list/')
        DistUtilsExtra.auto.install_auto.run(self)
        update_config(previous_values)


        
##################################################################################
###################### YOU SHOULD MODIFY ONLY WHAT IS BELOW ######################
##################################################################################

DistUtilsExtra.auto.setup(
    name='podio-task-applet',
    version='0.1',
    #license='MIT',
    #author='Nikhil Ben Kuruvilla',
    #author_email='me@nikhilben.com',
    #description='Podio Task Applet',
    #long_description='Applet to display daily Podio tasks.',
    #url='https://launchpad.net/podio-task-list',
    cmdclass={'install': InstallAndUpdateDataDirectory}
    )

