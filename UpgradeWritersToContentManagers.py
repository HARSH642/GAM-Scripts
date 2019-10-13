#!/usr/bin/env python2
"""
# Purpose: Upgrade users with writer access on Team Drives to fileOrganizer access (aka content manager)
# Note: This script requires Advanced GAM:
#	https://github.com/taers232c/GAMADV-XTD3
# Usage:
# 1: Get all Team Drives
#  $ gam redirect csv ./teamdrives.csv print teamdrives
# 2: Get ACLs for all Team Drives
#  $ gam redirect csv ./teamdriveacls.csv multiprocess csv ./teamdrives.csv gam print drivefileacls teamdriveid ~id
# 3: From that list of ACLs, output a CSV file with headers "teamDriveId,permissionId,type,emailAddress"
#    that lists the teamDriveIds and permissionIds for all ACLs with role writer.
#  $ python UpgradeWritersToContentManagers.py ./teamdriveacls.csv upgradetdacls.csv
# 4: Inspect upgradetdacls.csv, verify that it makes sense and then proceed
# 5: Upgrade the ACLs
#  $ gam redirect stdout ./upgradetdacls.out multiprocess redirect stderr stdout multiprocess csv upgradetdacls.csv gam update drivefileacl teamdriveid "~teamDriveId" "~permissionId" role fileOrganizer
"""

import csv
import re
import sys

QUOTE_CHAR = '"' # Adjust as needed
LINE_TERMINATOR = '\n' # On Windows, you probably want '\r\n'

PERMISSIONS_N_TYPE = re.compile(r"permissions.(\d+).type")

if (len(sys.argv) > 2) and (sys.argv[2] != '-'):
  outputFile = open(sys.argv[2], 'wb')
else:
  outputFile = sys.stdout
outputCSV = csv.DictWriter(outputFile, ['teamDriveId', 'permissionId', 'type', 'emailAddress'], lineterminator=LINE_TERMINATOR, quotechar=QUOTE_CHAR)
outputCSV.writeheader()

if (len(sys.argv) > 1) and (sys.argv[1] != '-'):
  inputFile = open(sys.argv[1], 'rbU')
else:
  inputFile = sys.stdin

for row in csv.DictReader(inputFile, quotechar=QUOTE_CHAR):
  for k, v in row.iteritems():
    mg = PERMISSIONS_N_TYPE.match(k)
    if mg and v:
      permissions_N = mg.group(1)
      role = row['permissions.{0}.role'.format(permissions_N)]
      if role != 'writer' or v not in ['user', 'group']:
        continue
      if row.get('permissions.{0}.deleted'.format(permissions_N)) == 'True':
        continue
      outputCSV.writerow({'teamDriveId': row['id'],
                          'permissionId': 'id:{0}'.format(row['permissions.{0}.id'.format(permissions_N)]),
                          'type': v,
                          'emailAddress': row['permissions.{0}.emailAddress'.format(permissions_N)]})

if inputFile != sys.stdin:
  inputFile.close()
if outputFile != sys.stdout:
  outputFile.close()
