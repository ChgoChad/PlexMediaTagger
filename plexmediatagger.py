#!/usr/bin/env python
#encoding:utf-8
#author:ccjensen/Chris
#project:PlexMediaTagger
#repository:http://github.com/ccjensen/plexmediatagger
#license:Creative Commons GNU GPL v2
# (http://creativecommons.org/licenses/GPL/2.0/)
 
"""
plexmediatagger.py
Automatically tags compatible media items.
Uses data from the PlexMediaServer (http://www.plexapp.com/)

thanks goes to:
the Subler team (http://code.google.com/p/subler/) for their excellent CLI tool to used to write the information to the media files
"""

__author__ = "ccjensen/Chris"
__version__ = "0.5"

import sys
import os
import re
import glob
import unicodedata
import signal
import logging

from lxml import etree
from optparse import OptionParser
from ColorizingStreamHandler import *
from PmsRequestHandler import *
from SectionProcessor import *


def main():
    signal.signal(signal.SIGINT, signal_handler)
    
    root = logging.getLogger()
    root.setLevel(logging.WARNING)
    root.addHandler(ColorizingStreamHandler())
    
    parser = OptionParser(usage="\
%prog [options]\n\
Example 1: %prog --tag\n\
Example 2: %prog -bq --tag --remove-all-tags --optimize -ip 192.168.0.2 --port 55400\n\
%prog -h for full list of options\n\n\
Filepaths to media items in PMS need to be the same as on machine that is running this script.\
")
    parser.add_option(  "-t", "--tag", action="store_true", dest="tag",
                        help="Will tag all compatible file types, and will update any previously tagged files (if metadata in plex has changed).")
    parser.add_option(  "-r", "--remove-all-tags", action="store_true", dest="removetags",
                        help="Removes all compatible tags from the files. Files will have to be retagged.")
    parser.add_option(  "-f", "--force", action="store_true", dest="force",
                        help="Ignores previous work and steams ahead with task (like tagging previously tagged files, etc.).")
    parser.add_option(  "-o", "--optimize", action="store_true", dest="optimize",
                        help="Interleaves the audio and video samples, and puts the \"MooV\" atom at the beginning of the file.")
                        
    parser.add_option(  "-i", "--ip", action="store", dest="ip", type='string',
                        help="Specifies an alternate IP address that hosts a PMS that we wish to connect to (default is localhost).")
    parser.add_option(  "-p", "--port", action="store", dest="port", type='int',
                        help="Specifies an alternate port number to use when connecting to the PMS (default is 32400).")
    
    parser.add_option(  "-b", "--batch", action="store_false", dest="interactive",
                        help="Disables interactive. Requires no human intervention once launched, and will perform operations on all files.")
    parser.add_option(  "--interactive", action="store_true", dest="interactive",
                        help="interactivly select files to operate on [default].")

    parser.add_option(  "-v", "--verbose", dest="verbose", action="callback", 
                        callback=setLogLevel, help='Increase verbosity (can be supplied 0-2 times).')
    parser.add_option(  "-q", "--quiet", action="store_true", dest="quiet",
                        help="For ninja-like processing (Can only be used when in batch mode).")
    parser.add_option(  "-d", "--dry-run", action="store_true", dest="dryrun",
                        help="Pretends to do the job, but never actually changes or exports anything. Will pretend that all tasks would have succeeded. Useful for testing purposes.")

    parser.set_defaults( tag=False, remove_tags=False, optimize=False, force_tagging=False, interactive=True, quiet=False, dryrun=False,
                        ip="localhost", port=32400)
    
    opts, args = parser.parse_args()
    
    if not opts.tag and not opts.removetags and not opts.optimize:
        parser.error("No task to perform. Our work here is done...")
    
    if opts.quiet:
        root.setLevel(logging.ERROR)
    
    if opts.interactive and not root.isEnabledFor(logging.INFO):
        root.setLevel(logging.INFO)
    
    if opts.dryrun:
        logging.critical( "WARNING, RUNNING IN 'DRY RUN MODE'. NO ACTION WILL BE PERFORMED" )
    elif opts.removetags:
        logging.critical( "WARNING, TAGS WILL BE REMOVED PERMANENTLY" )
    
    logging.error( "============ Plex Media Tagger Started ============" )
    
    request_handler = PmsRequestHandler()
    request_handler.ip = opts.ip
    request_handler.port = opts.port
    
    section_processor = SectionProcessor(opts, request_handler)
    
    logging.error( "Connecting to PMS at %s:%d" % (opts.ip, opts.port) )
    sections_container = request_handler.get_sections_container()
    media_container = sections_container.getroot()
    title = media_container.attrib['title1']
    section_elements = media_container.getchildren()
    
    section_element_choice = '' #default is empty == all
    if opts.interactive:
        logging.info( "List of sections for %s" % title )
        for index, section_element in enumerate(section_elements):
            logging.info( "%d. %s" %(index, section_element.attrib['title']) )
        #end for
        if len(section_elements) == 0:
            logging.error( "No sections found" )
        else:    
            logging.warning( "empty input equals all" )
    
            #ask user what sections should be processed
            section_element_choice = raw_input("Section to process $")
            if section_element_choice != '':
                try:
                    section_element_choice = int(section_element_choice)
                except ValueError, e:
                    logging.debug(e)
                    logging.critical( "'%s' is not a valid section number" % input )
                    sys.exit(1)
                #end try
            #end if section_element_choice
        #end if len(section_elements)
    #end if opts.interactive
    
    if section_element_choice == '': #all
        section_elements_to_process = section_elements
    else:
        section_elements_to_process = [section_elements[section_element_choice]]
    #end if
    
    logging.error( "Processing sections..." )
    for index, section_element in enumerate(section_elements_to_process):
        section_title = section_element.attrib['title']
        logging.error( "Processing section %d/%d : '%s'..." % (index+1, len(section_element), section_title) )
        section_processor.process_section(section_element)
        logging.warning( "Section '%s' processed" % section_title )
    #end for
    logging.error( "Processing sections completed" )
    logging.error( "============ Plex Media Tagger Completed ============" )
#end main


def setLogLevel(*args, **kwargs):
    logging.root.setLevel(logging.root.level - 10)


def signal_handler(signal, frame):
    logging.critical( "\r============ Terminating Plex Media Tagger ============" )
    sys.exit(0)
#end signal_handler

if __name__ == '__main__':
        sys.exit(main())
#end if __name__