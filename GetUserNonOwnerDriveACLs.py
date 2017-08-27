#!/usr/bin/env python
"""
# Purpose: For a Google Drive User, delete all drive file ACls except those indicating the user as owner
# Note: This script can use basic GAM: https://github.com/jay0lee/GAM or advanced GAM: https://github.com/taers232c/GAMADV-X
# Usage:
# 1: Use print filelist to get selected ACLS
#    Suntax, basic GAM:    gam <UserTypeEntity> print filelist [anyowner] [query <QueryDriveFile>] [fullquery <QueryDriveFile>]
#    Example, basic GAM: gam user testuser@domain.com print filelist id title permissions > filelistperms.csv
#    Syntax, advanced GAM: gam <UserTypeEntity> print filelist [anyowner|(showownedby any|me|others)]
#				[query <QueryDriveFile>] [fullquery <QueryDriveFile>] [select <DriveFileEntity>|orphans] [depth <Number>]
#    Example, advanced GAM: gam redirect csv ./filelistperms.csv user testuser@domain.com print filelist id permissions
# 2: From that list of ACLs, output a CSV file with headers "Owner,driveFileId,title,permissionId,emailAddress"
#    that lists the driveFileIds and permissionIds for all ACls except those indicating the user as owner
#    (n.b., emailAddress and title are not used in the next step, they are included for documentation purposes)
#  $ python GetUserNonOwnerDriveACLs.py filelistperms.csv deleteperms.csv
# 3: Inspect deleteperms.csv, verify that it makes sense and then proceed
# 4: Delete the ACLS
#  $ gam csv deleteperms.csv gam user "~Owner" delete drivefileacl "~driveFileId" "~permissionId"
"""

import csv
import re
import sys

id_n_address = re.compile(r"permissions.(\d+).id")

if (len(sys.argv) > 2) and (sys.argv[2] != '-'):
  outputFile = open(sys.argv[2], 'wb')
else:
  outputFile = sys.stdout
outputFile.write('Owner,driveFileId,title,permissionId,emailAddress\n')
if (len(sys.argv) > 1) and (sys.argv[1] != '-'):
  inputFile = open(sys.argv[1], 'rb')
else:
  inputFile = sys.stdin

for row in csv.DictReader(inputFile):
  for k, v in row.iteritems():
    mg = id_n_address.match(k)
    if mg:
      perm_group = mg.group(1)
      if v:
        if (row['permissions.{0}.type'.format(perm_group)] != 'user'
            or row['permissions.{0}.role'.format(perm_group)] != 'owner'
            or row.get('permissions.{0}.emailAddress'.format(perm_group), '') != row['Owner']):
          outputFile.write('{0},{1},{2},id:{3},{4}\n'.format(row['Owner'],
                                                             row['id'],
                                                             row['title'],
                                                             row['permissions.{0}.id'.format(perm_group)],
                                                             row.get('permissions.{0}.emailAddress'.format(perm_group), '')))

if inputFile != sys.stdin:
  inputFile.close()
if outputFile != sys.stdout:
  outputFile.close()
