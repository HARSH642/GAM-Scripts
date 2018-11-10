#!/usr/bin/env python2
"""
# Purpose: Print an Org Unit tree with Users/CrOS devices fields
# Note: This script can use Basic or Advanced GAM:
#	https://github.com/jay0lee/GAM
#	https://github.com/taers232c/GAMADV-X, https://github.com/taers232c/GAMADV-XTD, https://github.com/taers232c/GAMADV-XTD3
# Customize: Change QUOTE_CHAR, SHOW_EMPTY_OUS, SHOW_LABELS, FIELD_DELIMITER, INDENT_SPACES, LINE_TERMINATOR as required/desired
# Usage:
# 1: Get Org Units
#  $ gam print ous > OrgUnits.csv
# 1: Get Users/CrOS devices, specify the fields you want displayed: orgUnitPath must be specified
#  $ gam print users fields primaryEmail,orgunitpath,name > Users.csv
#  $ gam print cros fields deviceid,orgunitpath,notes > CrOS.csv
# 3: From the lists of Org Units and Users/CrOS devices, print a tree
#    Omit the third parameter or specify - to write to stdout
#  $ python PrintOrgUnitTree.py ./OrgUnits.csv ./Users.csv ./OrgUnitTree.txt
#  $ python PrintOrgUnitTree.py ./OrgUnits.csv ./CrOS.csv
# 4: You can pipe data into the script, replace the second parameter with -
#  $ gam print users fields primaryEmail,orgunitpath,name | python PrintOrgUnitTree.py ./OrgUnits.csv - ./OrgUnitTree.txt
# 5: With Advanced GAM you can select subsets of Users/CrOS devices; this requires an additional API call per User/CrOS device to get the specified fields
#  $ gam group students print users fields primaryEmail,orgunitpath,name | python PrintOrgUnitTree.py ./OrgUnits.csv - ./OrgUnitTree.txt
"""

import csv
import sys

QUOTE_CHAR = '"' # Adjust as needed to properly read CSV files

SHOW_EMPTY_OUS = True # Should empty OUs be displayed
SHOW_LABELS = True # Should field labels be displayed
SELECTED_FIELDS = [] # Only display selected fields ['primaryEmail',] ['deviceId', 'notes']
FIELD_DELIMITER = ', '# Delimiter between fields
INDENT_SPACES = '  ' # How much to indent data
LINE_TERMINATOR = '\n' # On Windows, you probably want '\r\n'

orgUnits = ['/',]
orgUnitsTree = {'/': []}

if (len(sys.argv) > 3) and (sys.argv[3] != '-'):
  outputFile = open(sys.argv[3], 'wb')
else:
  outputFile = sys.stdout

inputFile = open(sys.argv[1], 'rbU')
inputCSV = csv.DictReader(inputFile, quotechar=QUOTE_CHAR)
inputFieldNames = inputCSV.fieldnames
if 'orgUnitPath' not in inputFieldNames:
  sys.stderr.write('Error: no header orgUnitPath in Org Units file {0} field names: {1}\n'.format(sys.argv[1], ','.join(inputFieldNames)))
  sys.exit(1)
for row in inputCSV:
  orgUnits.append(row['orgUnitPath'])
  orgUnitsTree[row['orgUnitPath']] = []
inputFile.close()

if sys.argv[2] != '-':
  inputFile = open(sys.argv[2], 'rbU')
else:
  inputFile = sys.stdin
inputCSV = csv.DictReader(inputFile, quotechar=QUOTE_CHAR)
inputFieldNames = inputCSV.fieldnames
if inputFieldNames is None:
  sys.stderr.write('Error: no headers in Org Units file {0}\n'.format(sys.argv[2]))
  sys.exit(2)
if SELECTED_FIELDS:
  fieldNames = []
  for field in SELECTED_FIELDS:
    if field not in inputFieldNames:
      sys.stderr.write('Error: selected field {0} is not in Data file {1} field names: {2}\n'.format(field, sys.argv[2], ','.join(inputFieldNames)))
      sys.exit(3)
    fieldNames.append(field)
else:
  fieldNames = inputFieldNames[:]
  fieldNames.remove('orgUnitPath')
if 'orgUnitPath' not in inputFieldNames:
  sys.stderr.write('Error: no header orgUnitPath in Data file {0} field names: {1}\n'.format(sys.argv[2], ','.join(inputFieldNames)))
  sys.exit(4)
for row in inputCSV:
  if row['orgUnitPath'] is not None:
    orgUnitsTree[row['orgUnitPath']].append(row)
if inputFile != sys.stdin:
  inputFile.close()

for orgUnitPath in orgUnits:
  count = len(orgUnitsTree[orgUnitPath])
  if SHOW_EMPTY_OUS or count > 0:
    outputFile.write('{0}: {1}\n'.format(orgUnitPath, count))
    if count > 0:
      for child in orgUnitsTree[orgUnitPath]:
        if SHOW_LABELS:
          outputFile.write(INDENT_SPACES+FIELD_DELIMITER.join(['{0}: {1}'.format(field, child[field]) for field in fieldNames])+LINE_TERMINATOR)
        else:
          outputFile.write(INDENT_SPACES+FIELD_DELIMITER.join([child[field] for field in fieldNames])+LINE_TERMINATOR)
if outputFile != sys.stdout:
  outputFile.close()
