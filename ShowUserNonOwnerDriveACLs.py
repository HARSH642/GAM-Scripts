#!/usr/bin/env python
"""
# Purpose: For a Google Drive User, get all drive file ACls for files except those indicating the user as owner
# 1: Use print filelist to get selected ACLS
#    gam user testuser@domain.com print filelist id title permissions > filelistperms.csv
# 2: From that list of ACLs, output a CSV file with headers "Owner,driveFileId,driveFileTitle,emailAddress"
#    that lists the driveFileIds/Titles for all ACLs except those indicating the user as owner
#  $ python ShowUserNonOwnerDriveACLs.py filelistperms.csv localperms.csv
"""

import csv
import re
import sys

id_n_address = re.compile(r"permissions.(\d+).id")

if (len(sys.argv) > 2) and (sys.argv[2] != '-'):
  outputFile = open(sys.argv[2], 'wb')
else:
  outputFile = sys.stdout
outputCSV = csv.DictWriter(outputFile, ['Owner', 'driveFileId', 'driveFileTitle', 'emailAddress'], lineterminator='\n')
outputCSV.writeheader()

if (len(sys.argv) > 1) and (sys.argv[1] != '-'):
  inputFile = open(sys.argv[1], 'rb')
else:
  inputFile = sys.stdin

for row in csv.DictReader(inputFile):
  for k, v in row.iteritems():
    mg = id_n_address.match(k)
    if mg and v:
      perm_group = mg.group(1)
      emailAddress = row.get('permissions.{0}.emailAddress'.format(perm_group), u'')
      if (row['permissions.{0}.type'.format(perm_group)] in ['user', 'group']
          and (row['permissions.{0}.role'.format(perm_group)] != 'owner' or emailAddress != row['Owner'])):
        outputCSV.writerow({'Owner': row['Owner'],
                            'driveFileId': row['id'],
                            'driveFileTitle': row['title'],
                            'emailAddress': emailAddress})

if inputFile != sys.stdin:
  inputFile.close()
if outputFile != sys.stdout:
  outputFile.close()
