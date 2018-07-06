#!/usr/bin/env python2
"""
# Purpose: Make a CSV file that merges sendas addresses with user data
# Note: This script can use Basic or Advanced GAM:
#	https://github.com/jay0lee/GAM
#	https://github.com/taers232c/GAMADV-X, https://github.com/taers232c/GAMADV-XTD, https://github.com/taers232c/GAMADV-XTD3
# Usage:
# 1: Get Users
#  Basic GAM:
# $  gam print users fields primaryemail,... > ./Users.csv
#  Advanced GAM: use one of the following to select a collection of users
# <UserTypeEntity> ::=
#        (all users)|
#        (users <UserList>)|
#        (group|group_ns <GroupItem>)|
#        (groups|groups_ns <GroupList>)|
#        (ou|ou_ns <OrgUnitItem>)|
#        (ou_and_children|ou_and_children_ns <OrgUnitItem>)|
#        (ous|ous_ns <OrgUnitList>)|
#        (ous_and_children|ous_and_children_ns <OrgUnitList>)|
#        (courseparticipants <CourseIDList>)|
#        (students <CourseIDList>)|
#        (teachers <CourseIDList>)|
#        (file <FileName> [charset <Charset>] [delimiter <Character>])|
#        (csvfile <FileName>(:<FieldName>)+ [charset <Charset>] [columndelimiter <Character>] [quotechar <Character>]
#                [fields <FieldNameList>] (matchfield <FieldName> <RegularExpression>)* [delimiter <Character>])
#  $ gam <UserTypeEntity> print users fields primaryemail,... > ./Users.csv
# 2: Get Sendas addresses
#  $ gam <UserTypeEntity> print sendas > ./Sendas.csv
# 3: Output an updated version of Users.csv with one row for each address in Sendas.csv
#  $ python MergeSendasUsers.py ./Sendas.csv ./Users.csv ./UpdatedUsers.csv
"""

import csv
import sys

QUOTE_CHAR = '"' # Adjust as needed
LINE_TERMINATOR = '\n' # On Windows, you probably want '\r\n'

usersSendasAddresses = {}

if (len(sys.argv) > 1) and (sys.argv[1] != '-'):
  inputFile = open(sys.argv[1], 'rbU')
else:
  inputFile = sys.stdin
for row in csv.DictReader(inputFile, quotechar=QUOTE_CHAR):
  usersSendasAddresses.setdefault(row['User'], [])
  usersSendasAddresses[row['User']].append(row['sendAsEmail'])
if inputFile != sys.stdin:
  inputFile.close()

if len(sys.argv) > 2:
  inputFile = open(sys.argv[2], 'rbU')
else:
  sys.stderr.write('Error: Users file missing')
  sys.exit(1)
inputCSV = csv.DictReader(inputFile, quotechar=QUOTE_CHAR)

if (len(sys.argv) > 3) and (sys.argv[3] != '-'):
  outputFile = open(sys.argv[3], 'wb')
else:
  outputFile = sys.stdout
outputFieldnames = inputCSV.fieldnames[:]
outputFieldnames.append('sendAsEmail')
outputCSV = csv.DictWriter(outputFile, outputFieldnames, lineterminator=LINE_TERMINATOR, quotechar=QUOTE_CHAR)
outputCSV.writeheader()

for row in inputCSV:
  for sendAs in usersSendasAddresses.get(row['primaryEmail'], []):
    row['sendAsEmail'] = sendAs
    outputCSV.writerow(row)

inputFile.close()
if outputFile != sys.stdout:
  outputFile.close()
