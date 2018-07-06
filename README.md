# Blather

Blather is a speech recognizer that will run commands when a user speaks preset phrases.

## Requirements

1. pocketsphinx
2. gstreamer-1.x (and what ever plugin has pocket sphinx support)
3. Python3
4. GI (GObject Introspection)
5.  pyQt (only required for the Qt based UI)
6. curl (only required when running the language file updater)

## Usage

0. move commands.conf.tmp to ~/.config/blather/commands.conf and fill the file with sentences and command to run
1. Run `Blather.py -u` , this will:
	* generate ~/.config/blather/sentences.corpus based on sentences in the 'commands' file
	* upload the corpus file to Carnegie Melon University's Sphinx language tools 
	* download the lexicon and language files from CMU

2. run Blather.py
    * for Qt GUI, run Blather.py -i q
    * for Gtk GUI, run Blather.py -i g
    * for Gtk Tray GUI, run Blather.py -i gt
    * to start a UI in 'continuous' listen mode, use the -c flag
    * to use a microphone other than the system default, use the -m flag
3. start talking

**Note:** to start Blather without needing to enter command line options all the time, copy options.conf.tmp to ~/.config/blather/options.conf and edit accordingly.


### Examples

* To run blather with the GTK UI and start in continuous listen mode:
`./Blather.py -i g -c`

* To run blather with no UI and using a USB microphone recognized and device 2:
`./Blather.py -m 2`

* To have blather pass the matched sentence to the executing command:
 `./Blather.py -p`

 	**explanation:** if the commands.conf contains:
 **good morning world : example_command.sh**
 then 3 arguments, 'good', 'morning', and 'world' would get passed to example_command.sh as
 `example_command.sh good morning world`

* To run a command when a valid sentence has been detected:
	`./Blather.py --valid-sentence-command=/path/to/command`
	**note:** this can be set in the options.conf  file
* To run a command when a invalid sentence has been detected:
	`./Blather.py --invalid-sentence-command=/path/to/command`
	**note:** this can be set in the options.conf file

### Finding the Device Number of a USB microphone
There are a few ways to find the device number of a USB microphone.

* `cat /proc/asound/cards`
* `arecord -l`
	**note:** this can be set in the options.conf file
