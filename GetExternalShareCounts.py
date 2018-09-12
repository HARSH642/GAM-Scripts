#!/usr/bin/env python2
"""
# Purpose: For a Google Drive User(s), output a CSV file showing the share type counts for files shared by the user(s) externally
# Note: This script can use Basic or Advanced GAM:
#	https://github.com/jay0lee/GAM
#	https://github.com/taers232c/GAMADV-X, https://github.com/taers232c/GAMADV-XTD, https://github.com/taers232c/GAMADV-XTD3
# Customize: Set DOMAIN_LIST to the list of domains you consider internal
# Usage:
# 1: Get ACLs for all files, if you don't want all users, replace all users with your user selection in the command below
#  $ Example, Basic GAM: gam all users print filelist id title owners permissions > filelistperms.csv
#  $ Example, Advanced GAM: gam config auto_batch_min 1 redirect csv ./filelistperms.csv multiprocess all users print filelist id title owners permissions
# 2: From that list of ACLs, output a CSV file with headers:
#      Type,ExternalShare,Count
#  $ python GetExternalShareCounts.py filelistperms.csv externalsharecounts.csv
"""

import csv
import re
import sys

# Substitute your internal domain(s) in the list below, e.g., DOMAIN_LIST = ['domain.com',] DOMAIN_LIST = ['domain1.com', 'domain2.com',]
DOMAIN_LIST = ['domain.com',]

QUOTE_CHAR = '"' # Adjust as needed
LINE_TERMINATOR = '\n' # On Windows, you probably want '\r\n'

PERMISSIONS_N_TYPE = re.compile(r"permissions.(\d+).type")

if (len(sys.argv) > 2) and (sys.argv[2] != '-'):
  outputFile = open(sys.argv[2], 'wb')
else:
  outputFile = sys.stdout
outputCSV = csv.DictWriter(outputFile, ['Type', 'ExternalShare', 'Count'], lineterminator=LINE_TERMINATOR, quotechar=QUOTE_CHAR)
outputCSV.writeheader()

if (len(sys.argv) > 1) and (sys.argv[1] != '-'):
  inputFile = open(sys.argv[1], 'rbU')
else:
  inputFile = sys.stdin

anyoneShareCount = anyoneWithLinkShareCount = 0
domainShareCounts = {}
domainWithLinkShareCounts = {}
groupShareCounts = {}
userShareCounts = {}
for row in csv.DictReader(inputFile, quotechar=QUOTE_CHAR):
  for k, v in row.iteritems():
    mg = PERMISSIONS_N_TYPE.match(k)
    if mg and v:
      permissions_N = mg.group(1)
      if row['permissions.{0}.role'.format(permissions_N)] == 'owner':
        continue
      if row.get('permissions.{0}.deleted'.format(permissions_N)) == 'True':
        continue
      if v == 'anyone':
        if row['permissions.{0}.withLink'.format(permissions_N)] == 'True':
          anyoneWithLinkShareCount += 1
        else:
          anyoneShareCount += 1
      elif v == 'domain':
        domain = row['permissions.{0}.domain'.format(permissions_N)]
        if domain in DOMAIN_LIST:
          continue
        if row['permissions.{0}.withLink'.format(permissions_N)] == 'True':
          domainWithLinkShareCounts.setdefault(domain, 0)
          domainWithLinkShareCounts[domain] += 1
        else:
          domainShareCounts.setdefault(domain, 0)
          domainShareCounts[domain] += 1
      else: # group, user
        emailAddress = row['permissions.{0}.emailAddress'.format(permissions_N)]
        domain = row.get('permissions.{0}.domain'.format(permissions_N), u'')
        if not domain:
          domain = emailAddress[emailAddress.find(u'@')+1:]
        if domain in DOMAIN_LIST:
          continue
        if v == 'group':
          groupShareCounts.setdefault(emailAddress, 0)
          groupShareCounts[emailAddress] += 1
        else:
          userShareCounts.setdefault(emailAddress, 0)
          userShareCounts[emailAddress] += 1
outputCSV.writerow({'Type': 'anyone', 'Count': anyoneShareCount})
outputCSV.writerow({'Type': 'anyoneWithLink', 'Count': anyoneWithLinkShareCount})
for externalShare, count in sorted(domainShareCounts.iteritems()):
  outputCSV.writerow({'Type': 'domain', 'ExternalShare': externalShare, 'Count': count})
for externalShare, count in sorted(domainWithLinkShareCounts.iteritems()):
  outputCSV.writerow({'Type': 'domainWithLink', 'ExternalShare': externalShare, 'Count': count})
for externalShare, count in sorted(groupShareCounts.iteritems()):
  outputCSV.writerow({'Type': 'group', 'ExternalShare': externalShare, 'Count': count})
for externalShare, count in sorted(userShareCounts.iteritems()):
  outputCSV.writerow({'Type': 'user', 'ExternalShare': externalShare, 'Count': count})

if inputFile != sys.stdin:
  inputFile.close()
if outputFile != sys.stdout:
  outputFile.close()
