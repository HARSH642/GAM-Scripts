#!/usr/bin/env python2
"""
# Purpose: For a Google Drive User(s), show all shared drive files
# Note: This script can use Basic or Advanced GAM:
#	https://github.com/jay0lee/GAM
#	https://github.com/taers232c/GAMADV-XTD3
# Usage:
# 1: Get ACLs for all files, if you don't want all users, replace all users with your user selection in the command below
#  $ Basic: gam all users print filelist id title permissions > filelistperms.csv
#  $ Basic: gam user user@domain.com print filelist id title permissions > filelistperms.csv
#  $ Advanced: gam config auto_batch_min 1 redirect csv ./filelistperms.csv multiprocess all users print filelist fields id,title,permissions
#  $ Advanced: gam redirect csv ./filelistperms.csv user user@domain.com print filelist fields id,title,permissions
# 2: From that list of ACLs, output a CSV file that lists only the shared files.
#  $ python GetSharedFiles.py filelistperms.csv sharedfiles.csv
"""

import csv
import re
import sys

FILE_NAME = 'name'
ALT_FILE_NAME = 'title'

QUOTE_CHAR = '"' # Adjust as needed
LINE_TERMINATOR = '\n' # On Windows, you probably want '\r\n'

PERMISSIONS_N_TYPE = re.compile(r"permissions.(\d+).type")

if (len(sys.argv) > 2) and (sys.argv[2] != '-'):
  outputFile = open(sys.argv[2], 'wb')
else:
  outputFile = sys.stdout

if (len(sys.argv) > 1) and (sys.argv[1] != '-'):
  inputFile = open(sys.argv[1], 'rbU')
else:
  inputFile = sys.stdin

inputCSV = csv.DictReader(inputFile, quotechar=QUOTE_CHAR)
outputCSV = csv.DictWriter(outputFile, inputCSV.fieldnames, lineterminator=LINE_TERMINATOR, quotechar=QUOTE_CHAR)
outputCSV.writeheader()

for row in inputCSV:
  shared = False
  for k, v in row.iteritems():
    mg = PERMISSIONS_N_TYPE.match(k)
    if mg:
      if v == 'user':
        permissions_N = mg.group(1)
        role = row['permissions.{0}.role'.format(permissions_N)]
        emailAddress = row.get('permissions.{0}.emailAddress'.format(permissions_N), '')
        if (role and role != 'owner') or (emailAddress and emailAddress != row['Owner']):
          shared = True
      elif v:
        shared = True
  if shared:
    outputCSV.writerow(row)

if inputFile != sys.stdin:
  inputFile.close()
if outputFile != sys.stdout:
  outputFile.close()
