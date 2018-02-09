#!/usr/bin/env python2
"""
# Purpose: Create a CSV file with columns: User, Alias; from EMC exported data with columns: DisplayName, PrimarySmtpAddress, EmailAddresses.
# For each alias email address in the space separated list "EmailAddresses", output a row with PrimarySmtpAddress in the User column and the alias email address in the Alias column.
# Usage:
# 1: Export EMC data to EMCData.csv
# 2: python GetEMCAliases.py EMCData.csv EMCAliases.csv
# 3: Inspect EMCAliases.csv to make sure that it is reasonable
# 4: Create the aliases in Gam
#  $ gam csv EMCAliases.csv gam create alias "~Alias" user "~User"
"""

import csv
import sys

if (len(sys.argv) > 2) and (sys.argv[2] != '-'):
  outputFile = open(sys.argv[2], 'wb')
else:
  outputFile = sys.stdout
outputCSV = csv.DictWriter(outputFile, ['User', 'Alias'], lineterminator='\n')
outputCSV.writeheader()

if (len(sys.argv) > 1) and (sys.argv[1] != '-'):
  inputFile = open(sys.argv[1], 'rbU')
else:
  inputFile = sys.stdin

for row in csv.DictReader(inputFile):
  for alias in row['EmailAddresses'].split():
    outputCSV.writerow({'User': row['PrimarySmtpAddress'],
                        'Alias': alias})

if inputFile != sys.stdin:
  inputFile.close()
if outputFile != sys.stdout:
  outputFile.close()
