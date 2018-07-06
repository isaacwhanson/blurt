#!/usr/bin/env python3

# -- this code is licensed GPLv3
# Copyright 2018 Isaac W Hanson
# Copyright 2013 Jezra

import sys
import signal
import os.path
import subprocess

import gi
from gi.repository import GObject

from optparse import OptionParser

import UpdateLanguage

#where are the files?
conf_dir = os.path.expanduser("~/.config/blurt")
lang_dir = os.path.join(conf_dir, "language")
command_file = os.path.join(conf_dir, "commands.conf")
strings_file = os.path.join(conf_dir, "sentences.corpus")
history_file = os.path.join(conf_dir, "blurt.history")
opt_file = os.path.join(conf_dir, "options.conf")
lang_file = os.path.join(lang_dir,'lm')
dic_file = os.path.join(lang_dir,'dic')
#make the lang_dir if it doesn't exist
if not os.path.exists(lang_dir):
  os.makedirs(lang_dir)

class Blurt:
  def __init__(self, opts):
    #import the recognizer so Gst doesn't clobber our -h
    from Recognizer import Recognizer
    #set variables
    self.ui = None
    self.options = {}
    ui_continuous_listen = False
    self.continuous_listen = False
    self.commands = {}

    #read the commands
    self.load_commands_file()
    #load the options file
    print("load the options")
    self.load_options_file()

    #merge the opts
    for k,v in opts.__dict__.items():
      if (not k in self.options) or opts.override:
        self.options[k] = v

    # should we be updating?
    if self.options['update']:
      #make the sentences corpus
      self.generate_sentences_corpus()
      #run the update stuff
      UpdateLanguage.update_language()


    from GtkTrayUI import UI

    self.ui = UI(args, self.options['continuous'])
    self.ui.connect("command", self.process_command)
    #can we load the icon resource?
    icon = self.load_resource("icon.png")
    if icon:
      self.ui.set_icon_active_asset(icon)
    #can we load the icon_inactive resource?
    icon_inactive = self.load_resource("icon_inactive.png")
    if icon_inactive:
      self.ui.set_icon_inactive_asset(icon_inactive)

    if self.options['history']:
      self.history = []

    #create the recognizer
    try:
      self.recognizer = Recognizer(lang_file, dic_file, self.options['microphone'] )
    except Exception as e:
      print(e)
      #no recognizer? bummer
      sys.exit()

    self.recognizer.connect('finished',self.recognizer_finished)

    print( "Using Options: ", self.options )

  def read_key_val_file(self, file_path, lowercase_key = False, lowercase_value = False):
    print(file_path)
    file_text = open(file_path)
    return_struct = {}
    for line in file_text:
        #trim the white spaces
        line = line.strip()
        #if the line has length and the first char isn't a hash
        if len(line) and line[0]!="#":
          #this is a parsible line
          (key,value) = line.split(":",1)
          key = key.strip()
          value = value.strip()
          print(key, value)
          if lowercase_key:
            key = key.lower()
          if lowercase_value:
            value = value.lower()
          if value == "None" or value=="null":
            value = None
          if value == "True" or value=="true":
            value = True
          if value == "False" or value=="false":
            value = False
          return_struct[key] = value

    return return_struct

  def load_commands_file(self):
    #read the.commands file
    self.commands = self.read_key_val_file(command_file)

  def generate_sentences_corpus(self):
    file_lines = open(command_file)
    strings = open(strings_file, "w")
    for i in self.commands:
      strings.write( i.lower()+"\n")

    #close the strings file
    strings.close()

  def load_options_file(self):
    #is there an opt file?
    try:
      self.options = self.read_key_val_file(opt_file)
      #if there is a microphone option, convert value to int
      if 'microphone' in self.options:
       self.options['microphone'] = int(self.options['microphone'])
    except:
      print("failed to read options file")


  def log_history(self,text):
    if self.options['history']:
      self.history.append(text)
      if len(self.history) > self.options['history']:
        #pop off the first item
        self.history.pop(0)

      #open and truncate the blurt history file
      hfile = open(history_file, "w")
      for line in self.history:
        hfile.write( line+"\n")
      #close the  file
      hfile.close()


  # Print the cmd and then run the command
  def run_command(self, cmd):
    print (cmd)
    subprocess.call(cmd, shell=True)


  def recognizer_finished(self, recognizer, text):
    t = text.lower()
    #is there a matching command?
    if t in self.commands:
      #run the valid_sentence_command if there is a valid sentence command
      if self.options['valid_sentence_command']:
        subprocess.call(self.options['valid_sentence_command'], shell=True)
      cmd = self.commands[t]
      #should we be passing words?
      if self.options['pass_words']:
        cmd+=" "+t
        self.run_command(cmd)
      else:
        self.run_command(cmd)
      self.log_history(text)
    else:
      #run the invalid_sentence_command if there is a valid sentence command
      if self.options['invalid_sentence_command']:
        subprocess.call(self.options['invalid_sentence_command'], shell=True)
      print( "no matching command %s" %(t))
    #if there is a UI and we are not continuous listen
    if self.ui:
      if not self.continuous_listen:
        #stop listening
        self.recognizer.pause()
      #let the UI know that there is a finish
      self.ui.finished(t)


  def run(self):
    #is a UI going to be used?
    if self.ui:
      self.ui.run()
    else:
      blurt.recognizer.listen()

  def quit(self):
    sys.exit()

  def process_command(self, UI, command):
    print (command)
    if command == "listen":
      self.recognizer.listen()
    elif command == "stop":
      self.recognizer.pause()
    elif command == "continuous_listen":
      self.continuous_listen = True
      self.recognizer.listen()
    elif command == "continuous_stop":
      self.continuous_listen = False
      self.recognizer.pause()
    elif command == "quit":
      self.quit()

  def load_resource(self,string):
    local_data = os.path.join(os.path.dirname(__file__), 'data')
    paths = ["/usr/share/blurt/","/usr/local/share/blurt", local_data]
    for path in paths:
      resource = os.path.join(path, string)
      if os.path.exists( resource ):
        return resource
    #if we get this far, no resource was found
    return False


if __name__ == "__main__":
  parser = OptionParser()

  parser.add_option("-u", "--update", default=False,
    action="store_true", dest="update",
    help="update the language files (requires internet access)")

  parser.add_option("-c", "--continuous",
    action="store_true", dest="continuous", default=False,
    help="starts interface with 'continuous' listen enabled")

  parser.add_option("-p", "--pass-words",
    action="store_true", dest="pass_words", default=False,
    help="passes the recognized words as arguments to the shell command")

  parser.add_option("-o", "--override",
    action="store_true", dest="override", default=False,
    help="override config file with command line options")

  parser.add_option("-H", "--history", type="int",
    action="store", dest="history",
    help="number of commands to store in history file")

  parser.add_option("-m", "--microphone", type="int",
    action="store", dest="microphone", default=None,
    help="Audio input card to use (if other than system default)")

  parser.add_option("--valid-sentence-command",  type="string", dest="valid_sentence_command",
    action='store',
    help="command to run when a valid sentence is detected")

  parser.add_option( "--invalid-sentence-command",  type="string", dest="invalid_sentence_command",
    action='store',
    help="command to run when an invalid sentence is detected")

  (options, args) = parser.parse_args()
  #make our blurt object
  blurt = Blurt(options)
  #init gobject threads
  GObject.threads_init()
  #we want a main loop
  main_loop = GObject.MainLoop()
  #handle sigint
  signal.signal(signal.SIGINT, signal.SIG_DFL)
  #run the blurt
  print("run blurt")
  blurt.run()
  #start the main loop

  try:
    main_loop.run()
  except:
    print( "time to quit")
    main_loop.quit()
    sys.exit()


