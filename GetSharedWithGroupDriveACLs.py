#!/usr/bin/env python
"""
# Purpose: For a Google Drive User(s), show all drive file ACls for files shared with the desired groups.
# Note: This script can use basic GAM: https://github.com/jay0lee/GAM or advanced GAM: https://github.com/taers232c/GAMADV-X
# Usage:
# 1: Get ACLS for all files, if you don't want all users, replace all users with your user selection in the command below
#  $ Basic: gam all users print filelist id title permissions > filelistperms.csv
#  $ Advanced: gam config auto_batch_min 1 redirect csv ./filelistperms.csv multiprocess all users print filelist id title permissions
# 2: From that list of ACLs, output a CSV file with headers "Owner,driveFileId,driveFileTitle,permissionId,role,emailAddress"
#    that lists the driveFileIds and permissionIds for all ACls with the desired groups
#  $ python GetSharedWithGroupDriveACLs.py filelistperms.csv sharedwithgroup.csv
"""

import csv
import re
import sys

# Substitute your group(s) in the list below, e.g., groupList = ['group1@domain.com',] groupList = ['group1@domain.com', 'group2@domain.com',]
groupList = ['group@domain.com',]

id_n_type = re.compile(r"permissions.(\d+).type")

if (len(sys.argv) > 2) and (sys.argv[2] != '-'):
  outputFile = open(sys.argv[2], 'wb')
else:
  outputFile = sys.stdout
outputFile.write('Owner,driveFileId,driveFileTitle,permissionId,role,emailAddress\n')
if (len(sys.argv) > 1) and (sys.argv[1] != '-'):
  inputFile = open(sys.argv[1], 'rb')
else:
  inputFile = sys.stdin

for row in csv.DictReader(inputFile):
  for k, v in row.iteritems():
    mg = id_n_type.match(k)
    if mg:
      perm_group = mg.group(1)
      emailAddress = row['permissions.{0}.emailAddress'.format(perm_group)]
      if (row['permissions.{0}.type'.format(perm_group)] == u'group') and (emailAddress in groupList):
        outputFile.write('{0},{1},{2},id:{3},{4},{5}\n'.format(row['Owner'],
                                                               row['id'],
                                                               row['title'],
                                                               row['permissions.{0}.id'.format(perm_group)],
                                                               row['permissions.{0}.role'.format(perm_group)],
                                                               emailAddress))

if inputFile != sys.stdin:
  inputFile.close()
if outputFile != sys.stdout:
  outputFile.close()
