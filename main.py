#
# Client-side python app for photoapp, this time working with
# web service, which in turn uses AWS S3 and RDS to implement
# a simple photo application for photo storage and viewing.
#
# Authors:
#   
#   Satya Bharadwaj Pakki
#
#   Starter code: Prof. Joe Hummel
#   Northwestern University
#

import requests  # calling web service
import jsons  # relational-object mapping

import uuid
import pathlib
import logging
import sys
import os
import base64
import time

from configparser import ConfigParser

# doesn't work in docker (not easily):
# import matplotlib.pyplot as plt
# import matplotlib.image as img


###################################################################
#
# classes
#
class User:
  userid: int  # these must match columns from DB table
  email: str
  lastname: str
  firstname: str
  bucketfolder: str


class Asset:
  assetid: int  # these must match columns from DB table
  userid: int
  assetname: str
  bucketkey: str


class BucketItem:
  Key: str
  LastModified: str
  ETag: str
  Size: int
  StorageClass: str


###################################################################
#
# web_service_get
#
# When calling servers on a network, calls can randomly fail. 
# The better approach is to repeat at least N times (typically 
# N=3), and then give up after N tries.
#
def web_service_get(url):
  """
  Submits a GET request to a web service at most 3 times, since 
  web services can fail to respond e.g. to heavy user or internet 
  traffic. If the web service responds with status code 200, 400 
  or 500, we consider this a valid response and return the response.
  Otherwise we try again, at most 3 times. After 3 attempts the 
  function returns with the last response.
  
  Parameters
  ----------
  url: url for calling the web service
  
  Returns
  -------
  response received from web service
  """

  try:
    retries = 0
    
    while True:
      response = requests.get(url)
        
      if response.status_code in [200, 400, 500]:
        #
        # we consider this a successful call and response
        #
        break;

      #
      # failed, try again?
      #
      retries = retries + 1
      if retries < 3:
        # try at most 3 times
        time.sleep(retries)
        continue
          
      #
      # if get here, we tried 3 times, we give up:
      #
      break

    return response

  except Exception as e:
    print("**ERROR**")
    logging.error("web_service_get() failed:")
    logging.error("url: " + url)
    logging.error(e)
    return None
  
###################################################################
#
# web_service_post
#
def web_service_post(url, data):
    """
    Submits a POST request to a web service at most 3 times.
    """
    try:
        retries = 0
        while True:
            response = requests.post(url, json=data)

            if response.status_code in [200, 400, 500]:
                # we consider this a successful call and response
                break

            retries += 1
            if retries < 3:
                time.sleep(retries)
                continue

            break

        return response

    except Exception as e:
        logging.error("web_service_post() failed:")
        logging.error("url: " + url)
        logging.error(e)
        return None


###################################################################
#
# prompt
#
def prompt():
  """
  Prompts the user and returns the command number
  
  Parameters
  ----------
  None
  
  Returns
  -------
  Command number entered by user (0, 1, 2, ...)
  """

  try:
    print()
    print(">> Enter a command:")
    print("   0 => end")
    print("   1 => stats")
    print("   2 => users")
    print("   3 => assets")
    print("   4 => download")
    print("   5 => download and display")
    print("   6 => bucket contents")
    print("   7 => add user")
    print("   8 => upload")

    cmd = int(input())
    return cmd

  except Exception as e:
    print("ERROR")
    print("ERROR: invalid input")
    print("ERROR")
    return -1


###################################################################
#
# stats
#
def stats(baseurl):
  """
  Prints out S3 and RDS info: bucket status, # of users and 
  assets in the database
  
  Parameters
  ----------
  baseurl: baseurl for web service
  
  Returns
  -------
  nothing
  """

  try:
    #
    # call the web service:
    #
    api = '/stats'
    url = baseurl + api

    # res = requests.get(url)
    res = web_service_get(url)

    #
    # let's look at what we got back:
    #
    if res.status_code != 200:
      # failed:
      print("Failed with status code:", res.status_code)
      print("url: " + url)
      if res.status_code in [400, 500]:  # we'll have an error message
        body = res.json()
        print("Error message:", body["message"])
      #
      return

    #
    # deserialize and extract stats:
    #
    body = res.json()
    #
    print("bucket status:", body["message"])
    print("# of users:", body["db_numUsers"])
    print("# of assets:", body["db_numAssets"])

  except Exception as e:
    logging.error("stats() failed:")
    logging.error("url: " + url)
    logging.error(e)
    return


###################################################################
#
# users
#
def users(baseurl):
  """
  Prints out all the users in the database
  
  Parameters
  ----------
  baseurl: baseurl for web service
  
  Returns
  -------
  nothing
  """

  try:
    #
    # call the web service:
    #
    api = '/users'
    url = baseurl + api

    # res = requests.get(url)
    res = web_service_get(url)

    #
    # let's look at what we got back:
    #
    if res.status_code != 200:
      # failed:
      print("Failed with status code:", res.status_code)
      print("url: " + url)
      if res.status_code in [400, 500]:  # we'll have an error message
        body = res.json()
        print("Error message:", body["message"])
      #
      return

    #
    # deserialize and extract users:
    #
    body = res.json()
    #
    # let's map each dictionary into a User object:
    #
    users = []
    for row in body["data"]:
      user = jsons.load(row, User)
      users.append(user)
    #
    # Now we can think OOP:
    #
    for user in users:
      print(user.userid)
      print(" ", user.email)
      print(" ", user.lastname, ",", user.firstname)
      print(" ", user.bucketfolder)

  except Exception as e:
    logging.error("users() failed:")
    logging.error("url: " + url)
    logging.error(e)
    return


###################################################################
#
# assets
#
def assets(baseurl):
  """
  Prints out all the assets in the database
  
  Parameters
  ----------
  baseurl: baseurl for web service
  
  Returns
  -------
  nothing
  """

  try:
    #
    # call the web service:
    #
    api = '/assets'
    url = baseurl + api

    # res = requests.get(url)
    res = web_service_get(url)

    #
    # let's look at what we got back:
    #
    if res.status_code != 200:
      # failed:
      print("Failed with status code:", res.status_code)
      print("url: " + url)
      if res.status_code in [400, 500]:  # we'll have an error message
        body = res.json()
        print("Error message:", body["message"])
      #
      return

    #
    # deserialize and extract assets:
    #
    body = res.json()
    #
    # let's map each dictionary into an Asset object:
    #
    assets = []
    for row in body["data"]:
      asset = jsons.load(row, Asset)
      assets.append(asset)
    #
    # Now we can think OOP:
    #
    for asset in assets:
      print(asset.assetid)
      print(" ", asset.userid)
      print(" ", asset.assetname)
      print(" ", asset.bucketkey)

  except Exception as e:
    logging.error("assets() failed:")
    logging.error("url: " + url)
    logging.error(e)
    return


###################################################################
#
# download
#
def download(baseurl, display=False):
  try:
      print("Enter asset id>")
      assetid = input()

      # Call the web service:
      api = '/image'
      url = baseurl + api + '/' + assetid

      res = web_service_get(url)

      # Check the response:
      if res.status_code != 200:
          # Handle specific error messages:
          if res.status_code in [400, 500]:
              body = res.json()
              print(body["message"])
          else:
              print("Failed with status code:", res.status_code)
          return

      # Process successful response:
      body = res.json()
      userid = body["user_id"]
      assetname = body["asset_name"]
      bucketkey = body["bucket_key"]
      data = body["data"]

      print("userid:", userid)
      print("asset name:", assetname)
      print("bucket key:", bucketkey)

      # Write the binary data to a file:
      decoded_bytes = base64.b64decode(data)
      outfile = open(assetname, "wb")
      outfile.write(decoded_bytes)
      outfile.close()

      print("Downloaded from S3 and saved as '", assetname, "'")

      # Display image if requested:
      if display:
          print('Oops...')
          print('Docker is not setup to display images, see if you can open and view locally...')
          print('Oops...')

  except Exception as e:
      logging.error("download() failed:")
      logging.error("url: " + url)
      logging.error(e)
      return


###################################################################
#
# bucket_contents
#
def bucket_contents(baseurl):
    try:
        api = '/bucket'
        url = baseurl + api

        lastkey = ""

        while True:
            # Make a request...
            if lastkey != "":
                url = baseurl + api + "?startafter=" + lastkey
            else:
                url = baseurl + api

            res = web_service_get(url)

            if res.status_code != 200:
                if res.status_code in [400, 500]:
                    body = res.json()
                    print("Error message:", body["message"])
                break  # break out of loop

            body = res.json()
            data = body["data"]

            if len(data) == 0:
                print("No more data.")
                break  # break out of loop

            # Map each dictionary into a BucketItem object:
            items = []
            for item in data:
                bucket_item = jsons.load(item, BucketItem)
                items.append(bucket_item)

            # Display items in the specified format:
            for item in items:
                print(item.Key)
                print("  " + item.LastModified)
                print("  " + str(item.Size))

            # Update lastkey to the last key in the items
            lastkey = items[-1].Key

            # If fewer than 12 items are returned, no more pages
            if len(items) < 12:
                break

            # Prompt for the next page
            print("another page? [y/n]")
            answer = input()
            if answer.lower() == 'y':
                continue
            else:
                break

    except Exception as e:
        logging.error("bucket_contents() failed:")
        logging.error("url: " + url)
        logging.error(e)
        return


###################################################################
#
# add_user
#
def add_user(baseurl):
  """
  Prompts the user for the new user's email,
  last name, and first name, and then inserts
  this user into the database. But if the user's
  email already exists in the database, then we
  update the user's info instead of inserting
  a new user.
  
  Parameters
  ----------
  baseurl: baseurl for web service
  
  Returns
  -------
  nothing
  """

  try:
    print("Enter user's email>")
    email = input()

    print("Enter user's last (family) name>")
    last_name = input()

    print("Enter user's first (given) name>")
    first_name = input()

    # generate unique folder name:
    folder = str(uuid.uuid4())

   # Build the data packet
    data = {
        "email": email,
        "lastname": last_name,
        "firstname": first_name,
        "bucketfolder": folder
    }

    # Set the endpoint URL for the /user API
    api = '/user'
    url = baseurl + api

    # Send the PUT request to the server
    res = requests.put(url, json=data)

    # Check the response status code
    if res is None or res.status_code != 200:
      print("Failed with status code:", res.status_code)
      print("url: " + url)
      if res.status_code in [400, 500]:  # Error message expected in body
          body = res.json()
          print("Error message:", body["message"])
      return

    # Success, extract userid and message
    body = res.json()
    userid = body["userid"]
    message = body["message"]

    print("User", userid, "successfully", message)

  except Exception as e:
    logging.error("add_user() failed:")
    logging.error("url: " + url)
    logging.error(e)
    return


###################################################################
#
# upload
#
def upload(baseurl):
  """
  Prompts the user for a local filename and user id, 
  and uploads that asset (image) to the user's folder 
  in the bucket. The asset is given a random, unique 
  name. The database is also updated to record the 
  existence of this new asset in S3.
  """
  try:
      print("Enter local filename>")
      local_filename = input()

      if not pathlib.Path(local_filename).is_file():
          print("Local file '", local_filename, "' does not exist...")
          return

      print("Enter user id>")
      userid = input()

      #
      # build the data packet:
      #
      infile = open(local_filename, "rb")
      bytes_read = infile.read()
      infile.close()

      #
      # now encode the image as base64. Note b64encode returns
      # a bytes object, not a string. So then we have to convert
      # (decode) the bytes -> string, and then we can serialize
      # the string as JSON for upload to server:
      #
      data_encoded = base64.b64encode(bytes_read)
      datastr = data_encoded.decode()

      data = {"assetname": local_filename, "data": datastr}

      #
      # call the web service:
      #
      api = '/image'
      url = baseurl + api + "/" + userid

      res = web_service_post(url, data)

      #
      # let's look at what we got back:
      #
      if res is None or res.status_code != 200:
          # failed:
          print("Failed with status code:", res.status_code)
          print("url: " + url)
          if res and res.status_code in [400, 500]:  # we'll have an error message
              body = res.json()
              print("Error message:", body["message"])
          #
          return

      #
      # success, extract assetid:
      #
      body = res.json()

      assetid = body["assetid"]

      print("Image uploaded, asset id =", assetid)

  except Exception as e:
      logging.error("upload() failed:")
      logging.error("url: " + url)
      logging.error(e)
      return


#########################################################################
# main
#
print('** Welcome to PhotoApp v2 **')
print()

# eliminate traceback so we just get error message:
sys.tracebacklimit = 0

#
# what config file should we use for this session?
#
config_file = 'photoapp-client-config.ini'

print("What config file to use for this session?")
print("Press ENTER to use default (photoapp-client-config.ini),")
print("otherwise enter name of config file>")
s = input()

if s == "":  # use default
  pass  # already set
else:
  config_file = s

#
# does config file exist?
#
if not pathlib.Path(config_file).is_file():
  print("**ERROR: config file '", config_file, "' does not exist, exiting")
  sys.exit(0)

#
# setup base URL to web service:
#
configur = ConfigParser()
configur.read(config_file)
baseurl = configur.get('client', 'webservice')

#
# make sure baseurl does not end with /, if so remove:
#
if len(baseurl) < 16:
  print("**ERROR**")
  print("**ERROR: baseurl '", baseurl, "' in .ini file is empty or not nearly long enough, please fix")
  sys.exit(0)

if baseurl.startswith('https'):
  print("**ERROR**")
  print("**ERROR: baseurl '", baseurl, "' in .ini file starts with https, which is not supported (use http)")
  sys.exit(0)

lastchar = baseurl[len(baseurl) - 1]
if lastchar == "/":
  baseurl = baseurl[:-1]

# print(baseurl)

#
# main processing loop:
#
cmd = prompt()

while cmd != 0:
  #
  if cmd == 1:
    stats(baseurl)
  elif cmd == 2:
    users(baseurl)
  elif cmd == 3:
    assets(baseurl)
  elif cmd == 4:
    download(baseurl, display=False)
  elif cmd == 5:
    download(baseurl, display=True)
  elif cmd ==6:
    bucket_contents(baseurl)
  elif cmd ==7:
    add_user(baseurl)
  elif cmd == 8:
    upload(baseurl)
  #
  #
  # TODO: add calls to command functions for 4 - 7
  #
  #
  elif cmd == 8:
    upload(baseurl)
  else:
    print("** Unknown command, try again...")
  #
  cmd = prompt()

#
# done
#
print()
print('** done **')
