#!/usr/bin/python

import urllib2
import base64
import json
import ConfigParser
import sys
import datetime
import os

Config = ConfigParser.ConfigParser()
Config.read("config.ini")
BASE_SERVER = "https://{}.api.mailchimp.com/3.0".format(Config.get('access','server'))
# Single list for now
LISTNUM = Config.get('access','listnum')

HEADERS = {"Content-Type": "application/json",
  "Authorization": "Basic "+base64.encodestring(Config.get('access','username')+":"+Config.get('access','api_key')).replace('\n','')}
#print(HEADERS)

def GetLists():
  url = "{}/lists".format(BASE_SERVER)
  request = urllib2.Request(url, None, HEADERS)
  VALUE = urllib2.urlopen(request)

  JSON = json.loads(VALUE.read())
  print(json.dumps(JSON, indent=4, sort_keys=True))
  return

def GetListDetail(listnum):
  url = "{}/lists/{}".format(BASE_SERVER, listnum)
  request = urllib2.Request(url, None, HEADERS)
  VALUE = urllib2.urlopen(request)

  JSON = json.loads(VALUE.read())
  print(json.dumps(JSON, indent=4, sort_keys=True))
  return

def BatchUser( listnum, filename ):
  f = open(filename, 'r')
  content = f.read()
  f.close()
  SendList(listnum, content)
  return

def SendList( listnum, data ):
  url = "{}/lists/{}".format(BASE_SERVER, listnum)
  request = urllib2.Request(url, data, HEADERS)
  # Can fail if we try to insert a user previously put on the cleaned category
  try:
    output = open('output.{}.json'.format(datetime.datetime.now()), 'w')
    VALUE = urllib2.urlopen(request)
    retval = VALUE.read()
    JSON = json.loads(retval)
    output.write(retval)
    output.close()
    print(json.dumps(JSON, indent=4, sort_keys=True))
  except urllib2.HTTPError, e:
    print('Error: {} @ {}'.format(e.code, url))
    if e.code == 404:
      raise
  except:
    print("Unexpected error: ", sys.exc_info()[0])

  return

def ReadCSV( filename ):
  f = open(filename, 'r')
  lines = f.read().splitlines()
  # Packs of 500 to be sent
  mails = []
  mails.append({})
  mails[-1]['members'] = []
  mails[-1]['update_existing'] = True
  packcount = 0
  for line in lines:
    u = ProcessUser(line)
    mails[-1]['members'].append(u)
    packcount = packcount+1
    if packcount >= 500:
      packcount = 0
      mails.append({})
      mails[-1]['members'] = []
      mails[-1]['update_existing'] = True
  return mails

def ProcessUser(line):
  spl = line.split(";")
  u = {}
  name = {}
  # No switch
  num = len(spl)
  if num > 0:
    u['email_address'] = spl[0]
  if num > 1:
    name['FNAME'] = spl[1]
  if num > 2:
    #name['LNAME'] = spl[2]
    u['language'] = spl[2]
  # Append name if defined
  if len(name) > 0:
    u['merge_fields'] = name
  
  u['status_if_new'] = 'subscribed'
  #u['status'] = 'subscribed'
  return u

#GetLists()
#GetListDetail(LISTNUM)
#BatchUser(LISTNUM, "userbatch_1.json")
sendlist = []
sendlist = ReadCSV("importlist.csv")

# Send 500 by 500
for pack in sendlist:
  #print(json.dumps(pack))
  SendList(LISTNUM, json.dumps(pack))
