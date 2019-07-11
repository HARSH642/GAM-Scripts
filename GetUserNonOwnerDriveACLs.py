#!/usr/bin/env python2
"""
# Purpose: For a Google Drive User, delete all drive file ACLs except those indicating the user as owner
# Note: This script can use Basic or Advanced GAM:
#	https://github.com/jay0lee/GAM
#	https://github.com/taers232c/GAMADV-X, https://github.com/taers232c/GAMADV-XTD, https://github.com/taers232c/GAMADV-XTD3
# Customize: Set FILE_NAME and ALT_FILE_NAME based on your environment.
# Usage:
# 1: Use print filelist to get selected ACLs
#    Syntax, Basic GAM: gam <UserTypeEntity> print filelist [anyowner] [query <QueryDriveFile>] [fullquery <QueryDriveFile>]
#    Example, Basic GAM: gam user testuser@domain.com print filelist id title permissions owners > filelistperms.csv
#    Syntax, Advanced GAM: gam <UserTypeEntity> print filelist [anyowner|(showownedby any|me|others)]
#				[query <QueryDriveFile>] [fullquery <QueryDriveFile>] [select <DriveFileEntity>|orphans] [depth <Number>] [showparent]
#    For a full description of print filelist, see: https://github.com/taers232c/GAMADV-XTD/wiki/Users-Drive-Files
#    Example, Advanced GAM: gam redirect csv ./filelistperms.csv user testuser@domain.com print filelist fields id,title,permissions,owners.emailaddress
# 2: From that list of ACLs, output a CSV file with headers "Owner,driveFileId,driveFileTitle,permissionId,emailAddress,domain,allowFileDiscovery"
#    that lists the driveFileIds and permissionIds for all ACLs except those indicating the user as owner
#    (n.b., driveFileTitle, role, type, emailAddress, domain and allowFileDiscovery are not used in the next step, they are included for documentation purposes)
#  $ python GetUserNonOwnerDriveACLs.py filelistperms.csv deleteperms.csv
# 3: Inspect deleteperms.csv, verify that it makes sense and then proceed
# 4: Delete the ACLs
#  $ gam csv deleteperms.csv gam user "~Owner" delete drivefileacl "~driveFileId" "~permissionId"
"""

import csv
import re
import sys

# For GAM, GAMADV-X or GAMADV-XTD/GAMADV-XTD3 with drive_v3_native_names = false
#FILE_NAME = 'title'
#ALT_FILE_NAME = 'name'
# For GAMADV-XTD/GAMADV-XTD3 with drive_v3_native_names = true
FILE_NAME = 'name'
ALT_FILE_NAME = 'title'

QUOTE_CHAR = '"' # Adjust as needed
LINE_TERMINATOR = '\n' # On Windows, you probably want '\r\n'

PERMISSIONS_N_TYPE = re.compile(r"permissions.(\d+).type")

if (len(sys.argv) > 2) and (sys.argv[2] != '-'):
  outputFile = open(sys.argv[2], 'wb')
else:
  outputFile = sys.stdout
outputCSV = csv.DictWriter(outputFile, ['Owner', 'driveFileId', 'driveFileTitle', 'permissionId', 'role', 'type', 'emailAddress', 'domain', 'allowFileDiscovery'],
                           lineterminator=LINE_TERMINATOR, quotechar=QUOTE_CHAR)
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
      if v == 'domain':
        domain = row['permissions.{0}.domain'.format(permissions_N)]
        emailAddress = ''
        allowFileDiscovery = row.get('permissions.{0}.allowFileDiscovery'.format(permissions_N), str(row.get('permissions.{0}.withLink'.format(permissions_N)) == 'False'))
      elif v in ['user', 'group']:
        if row['permissions.{0}.deleted'.format(permissions_N)] == 'True':
          continue
        emailAddress = row['permissions.{0}.emailAddress'.format(permissions_N)]
        domain = emailAddress[emailAddress.find('@')+1:]
        allowFileDiscovery = ''
      else:
        domain = emailAddress = ''
        allowFileDiscovery = row.get('permissions.{0}.allowFileDiscovery'.format(permissions_N), str(row.get('permissions.{0}.withLink'.format(permissions_N)) == 'False'))
      if v != 'user' or row['permissions.{0}.role'.format(permissions_N)] != 'owner' or emailAddress != row['owners.0.emailAddress']:
        outputCSV.writerow({'Owner': row['owners.0.emailAddress'],
                            'driveFileId': row['id'],
                            'driveFileTitle': row.get(FILE_NAME, row.get(ALT_FILE_NAME, 'Unknown')),
                            'permissionId': 'id:{0}'.format(row['permissions.{0}.id'.format(permissions_N)]),
                            'role': row['permissions.{0}.role'.format(permissions_N)],
                            'type': v,
                            'emailAddress': emailAddress,
                            'allowFileDiscovery': allowFileDiscovery})

if inputFile != sys.stdin:
  inputFile.close()
if outputFile != sys.stdout:
  outputFile.close()
