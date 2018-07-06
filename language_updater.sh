#!/bin/bash

blurtdir=~/.config/blurt
sentences=$blurtdir/sentences.corpus
sourcefile=$blurtdir/commands.conf
langdir=$blurtdir/language
tempfile=$blurtdir/url.txt
lmtoolurl=http://www.speech.cs.cmu.edu/cgi-bin/tools/lmtool/run

cd $blurtdir

sed -f - $sourcefile > $sentences <<EOFcommands
  /^$/d
  /^#/d
  s/\:.*$//
EOFcommands

# upload corpus file, find the resulting dictionary file url
curl -L -F corpus=@"$sentences" -F formtype=simple $lmtoolurl \
  |grep -A 1 "base name" |grep http \
  | sed -e 's/^.*\="//' | sed -e 's/\.tgz.*$//' | sed -e 's/TAR//' > $tempfile

# download the .dic and .lm files
curl -C - -O $(cat $tempfile).dic
curl -C - -O $(cat $tempfile).lm

# mv em to the right name/place
mv *.dic $langdir/dic
mv *.lm $langdir/lm

rm $tempfile
