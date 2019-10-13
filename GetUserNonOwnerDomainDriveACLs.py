#!/usr/bin/env python2
"""
# Purpose: For a Google Drive User, delete all drive file ACLs for files shared with a list of specified domains
# except those indicating the user as owner
# Note: This script can use Basic or Advanced GAM:
#	https://github.com/jay0lee/GAM
#	https://github.com/taers232c/GAMADV-XTD3
# Customize: Set DOMAIN_LIST and DESIRED_ALLOWFILEDISCOVERY.
# 1: Use print filelist to get selected ACLs
#    Basic: gam user testuser@domain.com print filelist id title permissions owners > filelistperms.csv
#    Advanced: gam user testuser@domain.com print filelist fields id,title, permissions,owners.emailaddress > filelistperms.csv
# 2: From that list of ACLs, output a CSV file with headers "Owner,driveFileId,driveFileTitle,permissionId,role,type,emailAddress,domain"
#    that lists the driveFileIds and permissionIds for all ACLs from the specified domains except those indicating the user as owner
#  $ python GetUserNonOwnerDomainDriveACLs.py filelistperms.csv deleteperms.csv
# 3: Inspect deleteperms.csv, verify that it makes sense and then proceed
# 4: Delete the ACLs
#  $ gam csv deleteperms.csv gam user "~Owner" delete drivefileacl "~driveFileId" "~permissionId"
"""

import csv
import re
import sys

FILE_NAME = 'name'
ALT_FILE_NAME = 'title'

# If you want to limit finding ACLS for a specific list of domains, use the list below, e.g., DOMAIN_LIST = ['domain.com',] DOMAIN_LIST = ['domain1.com', 'domain2.com',]
DOMAIN_LIST = []
# Specify desired value of allowFileDiscovery field: True, False, Any (matches True and False)
DESIRED_ALLOWFILEDISCOVERY = 'Any'

QUOTE_CHAR = '"' # Adjust as needed
LINE_TERMINATOR = '\n' # On Windows, you probably want '\r\n'

PERMISSIONS_N_TYPE = re.compile(r"permissions.(\d+).type")

if (len(sys.argv) > 2) and (sys.argv[2] != '-'):
  outputFile = open(sys.argv[2], 'wb')
else:
  outputFile = sys.stdout
outputCSV = csv.DictWriter(outputFile, ['Owner', 'driveFileId', 'driveFileTitle', 'permissionId', 'role', 'type', 'emailAddress', 'domain'], lineterminator=LINE_TERMINATOR, quotechar=QUOTE_CHAR)
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
        allowFileDiscovery = row.get('permissions.{0}.allowFileDiscovery'.format(permissions_N), str(row.get('permissions.{0}.withLink'.format(permissions_N)) == 'False'))
        if DESIRED_ALLOWFILEDISCOVERY not in ('Any', allowFileDiscovery):
          continue
        domain = row['permissions.{0}.domain'.format(permissions_N)]
        emailAddress = ''
      elif v in ['user', 'group']:
        if row.get('permissions.{0}.deleted'.format(permissions_N)) == 'True':
          continue
        emailAddress = row['permissions.{0}.emailAddress'.format(permissions_N)]
        domain = emailAddress[emailAddress.find('@')+1:]
      else:
        continue
      if (not DOMAIN_LIST or domain in DOMAIN_LIST) and (v != 'user' or row['permissions.{0}.role'.format(permissions_N)] != 'owner' or emailAddress != row['owners.0.emailAddress']):
        outputCSV.writerow({'Owner': row['owners.0.emailAddress'],
                            'driveFileId': row['id'],
                            'driveFileTitle': row.get(FILE_NAME, row.get(ALT_FILE_NAME, 'Unknown')),
                            'permissionId': 'id:{0}'.format(v),
                            'role': row['permissions.{0}.role'.format(permissions_N)],
                            'type': v,
                            'emailAddress': emailAddress,
                            'domain': domain})

if inputFile != sys.stdin:
  inputFile.close()
if outputFile != sys.stdout:
  outputFile.close()
