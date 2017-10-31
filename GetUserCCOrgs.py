#!/usr/bin/env python
"""
# Purpose: Move root users to an Org Unit based on their work address countryCode
# Note: This script requires advanced GAM: https://github.com/taers232c/GAMADV-X
# Usage:
# 1: Get primaryEmail, orgUnitPath, addresses for all root users
#  $ gam redirect csv ./UserAddresses.csv org "/" print users fields primaryemail,orgunitpath,addresses
# 2: From that list of users, output a CSV file with headers "Org,primaryEmail"
#    that lists the Org Unit derived from the root user's work address and their primaryEmail
#  $ python GetUserCCOrgs.py ./UserAddresses.csv ./UserCCOrgs.csv
# 3: Inspect UserCCOrgs.csv, verify that it makes sense and then proceed
# 4: Move the users
#  $ gam update orgs csvkmd ./UserCCOrgs.csv keyfield Org datafield primaryEmail add csvdata primaryEmail
"""

import csv
import re
import sys

id_n_type = re.compile(r"addresses.(\d+).type")
# Change format as desired, {0} is replaced by countryCode
org_unit_map = '{0}'

if (len(sys.argv) > 2) and (sys.argv[2] != '-'):
  outputFile = open(sys.argv[2], 'wb')
else:
  outputFile = sys.stdout
outputCSV = csv.DictWriter(outputFile, ['Org', 'primaryEmail'], lineterminator='\n')
outputCSV.writeheader()

if (len(sys.argv) > 1) and (sys.argv[1] != '-'):
  inputFile = open(sys.argv[1], 'rb')
else:
  inputFile = sys.stdin

for row in csv.DictReader(inputFile):
  for k, v in row.iteritems():
    if row['orgUnitPath'] == '/':
      mg = id_n_type.match(k)
      if mg:
        addr_group = mg.group(1)
        if v:
          if row['addresses.{0}.type'.format(addr_group)] == 'work':
            org = org_unit_map.format(row['addresses.{0}.countryCode'.format(addr_group)])
            if org:
              outputCSV.writerow({'Org': org,
                                  'primaryEmail': row['primaryEmail']})

if inputFile != sys.stdin:
  inputFile.close()
if outputFile != sys.stdout:
  outputFile.close()
