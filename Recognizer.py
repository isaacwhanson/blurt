#This is part of Blather
# -- this code is licensed GPLv3
# Copyright 2013 Jezra


import os.path
import sys

import gi
gi.require_version('Gst', '1.0')
from gi.repository import GObject, Gst

#initialize gst
Gst.init(None)

#define some global variables
this_dir = os.path.dirname( os.path.abspath(__file__) )


class Recognizer(GObject.GObject):
  __gsignals__ = {
    'finished' : (GObject.SIGNAL_RUN_LAST, GObject.TYPE_NONE, (GObject.TYPE_STRING,))
  }
  def __init__(self, language_file, dictionary_file, src = None):
    GObject.GObject.__init__(self)
    self.commands = {}
    if src:
      audio_src = 'alsasrc device="hw:%d,0"' % (src)
    else:
      audio_src = 'autoaudiosrc'

    #build the pipeline
    cmd = audio_src+' ! audioconvert ! audioresample ! pocketsphinx name=asr ! appsink sync=false'
    try:
      self.pipeline=Gst.parse_launch( cmd )
    except Exception as e:
      print( e)
      print( "You may need to install gstreamer pocketsphinx")
      raise e

    '''messages come from the pipeline bus now'''
    #get the pipeline bus
    bus = self.pipeline.get_bus()
    #hey bus, start emitting signals!
    bus.add_signal_watch()
    #connect messages from elements to our parser
    bus.connect('message::element', self.parse_bus_element_message)

    #get the Auto Speech Recognition piece
    asr=self.pipeline.get_by_name('asr')
    asr.set_property('lm', language_file)
    asr.set_property('dict', dictionary_file)

  def parse_bus_element_message(self, bus, message):
    #get the message's structure
    message_struct = message.get_structure()
    #get the message's ... ahem ... type
    message_type = message_struct.get_name()
    #is this pocket sphinx?
    if message_type != 'pocketsphinx':
      #get outa here!
      return

    # is this the final decided text?
    if message_struct.get_value('final'):
      #hypothesis is the string we want
      text = message_struct.get_value('hypothesis')
      #emit finished
      self.emit("finished", text)
    #TODO: find a way to utilize partial matches and match confidence



  def listen(self):
    print("listen")
    self.pipeline.set_state(Gst.State.PLAYING)

  def pause(self):
    self.pipeline.set_state(Gst.State.PAUSED)

  def result(self, asr, text, uttid):
    #emit finished
    self.emit("finished", text)

