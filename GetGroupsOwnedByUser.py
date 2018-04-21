#!/usr/bin/env python2
"""
# Purpose: Make a CSV file showing groups owned by users
# Note: This script can use Basic or Advanced GAM:
#	https://github.com/jay0lee/GAM
#	https://github.com/taers232c/GAMADV-X, https://github.com/taers232c/GAMADV-XTD, https://github.com/taers232c/GAMADV-XTD3
# Customize: Set SelectedUsers or pass a CSV file:field reference on the command line
# Usage:
# 1: Get group owners
#  $ gam print groups owners delimiter " " > ./GroupOwners.csv
# 2: From that list of groups, output a CSV file with headers "User,GroupsOwnedByUser
#  $ python GetGroupsOwnedByUser.py ./GroupOwners.csv ./GroupsOwnedByUser.csv
# 3: If you only want groups owned by a select list of users, specify the CSV file name and field name that lists the users
#  $ python GetGroupsOwnedByUser.py ./GroupOwners.csv ./GroupsOwnedByUser.csv ./<Filename>:<FieldName>
"""

import csv
import sys

QUOTE_CHAR = '"' # Adjust as needed
LINE_TERMINATOR = '\n' # On Windows, you probably want '\r\n'

# Leave SelectedUsers empty to show groups owned by any user
# Set to a specific set of users, e.g., SelectedUsers = set('user1@domain.com', 'user2@domain.com')
# Set to a list of users read from a CSV file passed on the command line
SelectedUsers = set()

GroupsOwnedByUser = {}

if len(sys.argv) > 3:
  filename, fieldname = sys.argv[3].split(':')
  inputFile = open(filename, 'rbU')
  for row in csv.DictReader(inputFile, quotechar=QUOTE_CHAR):
    SelectedUsers.add(row[fieldname].lower())
  inputFile.close()

if (len(sys.argv) > 2) and (sys.argv[2] != '-'):
  outputFile = open(sys.argv[2], 'wb')
else:
  outputFile = sys.stdout
outputCSV = csv.DictWriter(outputFile, ['User', 'GroupsOwnedByUser'], lineterminator=LINE_TERMINATOR, quotechar=QUOTE_CHAR)
outputCSV.writeheader()

if (len(sys.argv) > 1) and (sys.argv[1] != '-'):
  inputFile = open(sys.argv[1], 'rbU')
else:
  inputFile = sys.stdin

for row in csv.DictReader(inputFile, quotechar=QUOTE_CHAR):
  for k, v in row.iteritems():
    if row['OwnersCount'] != '0':
      for owner in row['Owners'].lower().split(' '):
        if (not SelectedUsers) or (owner in SelectedUsers):
          GroupsOwnedByUser.setdefault(owner, [])
          GroupsOwnedByUser[owner].append(row['Email'])
for user, groups in sorted(GroupsOwnedByUser.iteritems()):
  outputCSV.writerow({'User': user,
                      'GroupsOwnedByUser': ' '.join(groups)})

if inputFile != sys.stdin:
  inputFile.close()
if outputFile != sys.stdout:
  outputFile.close()
