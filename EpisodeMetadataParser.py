#!/usr/bin/env python
#encoding:utf-8
#author:ccjensen/Chris
#project:PlexMediaTagger
#repository:http://github.com/ccjensen/plexmediatagger
#license:Creative Commons GNU GPL v2
# (http://creativecommons.org/licenses/GPL/2.0/)

from lxml import etree
import logging
import sys
import os
from MediaItemMetadataParser import *
from PmsRequestHandler import *

class EpisodeMetadataParser(MediaItemMetadataParser):
    """docstring for EpisodeMetadataParser"""
    def __init__(self, opts, episode_metadata_container, season):
        super(EpisodeMetadataParser, self).__init__(opts, episode_metadata_container)
        self.season = season
        self.show = season.show
        
        self.key = self.video.attrib['key']
        self.type = self.video.get('type', "")
        self.title = self.video.get('title', "")
        self.summary = self.video.get('summary', "")
        self.index = self.video.get('index', "")
        self.rating = self.video.get('rating', "") #not used        
        self.thumb = self.video.get('thumb', "")
        self.originally_available_at = self.video.get('originallyAvailableAt', "")

        self.writer_names = self.array_of_attributes_with_key_from_child_nodes_with_name(self.video, "Writer", "tag")
        self.writers = ', '.join(self.writer_names)

        self.director_names = self.array_of_attributes_with_key_from_child_nodes_with_name(self.video, "Director", "tag")
        self.directors = ', '.join(self.director_names)
        
        #other metadata can/will be retreived from the season object which holds a link to the show object
    #end def __init__
    
    def name(self):
        return "%sE%02d - %s" % (self.season.name(), int(self.index), self.title)
    #end def name
    
    def get_local_image_path(self):
        request_handler = PmsRequestHandler()
        #partial_image_url = self.thumb #use the season thumb instead
        partial_image_url = self.season.thumb
        logging.info("Downloading artwork...")
        self.local_image_path = request_handler.download_image(self.name(), partial_image_url)
    #end image_path
            
    
    def tag_string(self):
        tag_string = super(EpisodeMetadataParser, self).tag_string()
        
        if self.local_image_path == "":
            self.get_local_image_path()
        tag_string += self.new_tag_string_entry("Artwork", self.local_image_path)
        
        tag_string += self.new_tag_string_entry("Studio", self.show.studio)
        tag_string += self.new_tag_string_entry("Media Kind", "TV Show")
        tag_string += self.new_tag_string_entry("Name", self.title)
        tag_string += self.new_tag_string_entry("Rating", self.show.content_rating)
        tag_string += self.new_tag_string_entry("Long Description", self.summary)
        tag_string += self.new_tag_string_entry("Release Date", self.originally_available_at)
        tag_string += self.new_tag_string_entry("Description", self.summary)
        
        tag_string += self.new_tag_string_entry("Genre", self.show.genre) #single genre
        tag_string += self.new_tag_string_entry("Screenwriters", self.writers)
        tag_string += self.new_tag_string_entry("Director", self.directors)
        
        #no cast currently available for show/season/episode
        #tag_string += self.new_tag_string_entry("Cast", self.cast)
        
        hd_value = "%d" % (1 if self.is_HD() else 0)
        tag_string += self.new_tag_string_entry("HD Video", hd_value)
        
        #tv episode specific
        tag_string += self.new_tag_string_entry("TV Network", self.show.studio)
        tag_string += self.new_tag_string_entry("TV Show", self.show.title)
        tag_string += self.new_tag_string_entry("TV Season", self.season.index)
        tag_string += self.new_tag_string_entry("TV Episode #", self.index)
        tag_string += self.new_tag_string_entry("TV Episode ID", self.season.index+self.index)
        
        return tag_string.strip()
    #end def tag_string
#end class EpisodeMetadataParser