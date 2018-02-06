#!/usr/bin/env python3

import subprocess
import sys, os.path
import re

def update_language():
  #set some variables
  downloader = None
  sentences_file = "~/.config/blather/sentences.corpus"
  abs_sentences = os.path.expanduser(sentences_file)
  HOST = "www.speech.cs.cmu.edu"
  URL = "/cgi-bin/tools/lmtool/run"
  TARGET = HOST+URL

  #make sure curl is installed
  try:
    output = subprocess.check_output("which curl", shell = True)
    downloader = "curl"
  except Exception as e: 
    print(e)
    print("Please install `curl`")
    #pffftttt  we're out of here!
    sys.exit()
  
  #define the curl command to upload the corus file
  cmd = "curl -s -L -F corpus=@{} -F formtype=simple {}".format(abs_sentences,TARGET) 
  print(cmd)
  #go for it, bruh!
  try:
    output = subprocess.check_output(cmd, shell = True)
    #decode the output, should this be utf-8? 
    output = output.decode('utf-8')

  except Exception as e: 
    print(e)
    print("failed to update language")
    sys.exit()
      
  print(output)

    
  #create a regex to find the base name
  namefinder = re.search(r"The base name for this set is <b>(?P<base_name>.*)<", output)
  base_name = namefinder.group("base_name")
  print(base_name)

  #use regex to find the http path to the files we want
  pathfinder = re.search(r"(http://www.speech.cs.cmu.edu/tools/product/.*/)TAR",output)
  http_path = pathfinder.group(1)
  #where are the files we need?
  lm_remote = http_path+base_name+".lm"
  dic_remote = http_path+base_name+".dic"

  #do more downloading
  if downloader == 'curl':
    #get the lang file
    cmd = "curl -s {} > ~/.config/blather/lm.tmp".format(lm_remote)
    try:
      output = subprocess.check_output(cmd, shell = True)
    except Exception as e: 
      print(e)
      print("Failed to download {}".format(lm_remote))
      sys.exit()
      
    cmd = "curl -s {} > ~/.config/blather/dic.tmp".format(dic_remote)
    try:
      output = subprocess.check_output(cmd, shell = True)
    except Exception as e: 
      print(e)
      print("Failed to download {}".format(lm_remote))
      sys.exit()

    # if we made it this far, mv the temp files to their proper location
    cmd = "mv ~/.config/blather/dic.tmp ~/.config/blather/language/dic"
    subprocess.call(cmd, shell = True)
    cmd = "mv ~/.config/blather/lm.tmp ~/.config/blather/language/lm"
    subprocess.call(cmd, shell = True)

