#!/usr/bin/python

import urllib2
import base64
import json
import ConfigParser

Config = ConfigParser.ConfigParser()
Config.read("config.ini")
BASE_SERVER = "https://"+Config.get('access','server')+".api.mailchimp.com/3.0"
# Single list for now
LISTNUM = Config.get('access','listnum')

HEADERS = {"Content-Type": "application/json",
  "Authorization": "Basic "+base64.encodestring(Config.get('access','username')+":"+Config.get('access','api_key')).replace('\n','')}

def GetLists():
  request = urllib2.Request(BASE_SERVER+"/lists", None, HEADERS)
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
  request = urllib2.Request(BASE_SERVER+"/lists/"+listnum, data, HEADERS)
  # Can fail if we try to insert a user previously put on the cleaned category
  VALUE = urllib2.urlopen(request)

  JSON = json.loads(VALUE.read())
  print(json.dumps(JSON, indent=4, sort_keys=True))
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
  
  u['status'] = 'subscribed'
  return u

#GetLists()
#BatchUser(LISTNUM, "userbatch_1.json")
sendlist = ReadCSV("importlist.csv")

# Send 500 by 500
for pack in sendlist:
  SendList(LISTNUM, json.dumps(pack))
