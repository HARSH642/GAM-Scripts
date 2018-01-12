#!/usr/bin/env python
"""
# Purpose: For a Google Drive User, get all drive file ACLs for files shared with a list of specified domains
# except those indicating the user as owner
# 1: Use print filelist to get selected ACLs
#    gam user testuser@domain.com print filelist id title permissions > filelistperms.csv
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

id_n_address = re.compile(r"permissions.(\d+).id")
# Substitute your domain(s) in the list below, e.g., domainList = ['domain.com',] domainList = ['domain1.com', 'domain2.com',]
domainList = []

if (len(sys.argv) > 2) and (sys.argv[2] != '-'):
  outputFile = open(sys.argv[2], 'wb')
else:
  outputFile = sys.stdout
outputCSV = csv.DictWriter(outputFile, ['Owner', 'driveFileId', 'driveFileTitle', 'permissionId', 'role', 'type', 'emailAddress', 'domain'], lineterminator='\n')
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
      domain = row['permissions.{0}.domain'.format(perm_group)]
      emailAddress = row['permissions.{0}.emailAddress'.format(perm_group)]
      if (domain in domainList) and (row['permissions.{0}.type'.format(perm_group)] != 'user'
                                     or row['permissions.{0}.role'.format(perm_group)] != 'owner'
                                     or emailAddress != row['Owner']):
        outputCSV.writerow({'Owner': row['Owner'],
                            'driveFileId': row['id'],
                            'driveFileTitle': row['title'],
                            'permissionId': 'id:{0}'.format(v),
                            'role': row['permissions.{0}.role'.format(perm_group)],
                            'type': row['permissions.{0}.type'.format(perm_group)],
                            'emailAddress': row['permissions.{0}.emailAddress'.format(perm_group)],
                            'domain': row['permissions.{0}.domain'.format(perm_group)]})

if inputFile != sys.stdin:
  inputFile.close()
if outputFile != sys.stdout:
  outputFile.close()
