#!/usr/bin/env python
#encoding:utf-8
#author:ccjensen/Chris
#project:PlexMediaTagger
#repository:http://github.com/ccjensen/plexmediatagger
#license:Creative Commons GNU GPL v2
# (http://creativecommons.org/licenses/GPL/2.0/)

from lxml import etree
from BaseMetadataParser import *
from PartMetadataParser import *

class MediaMetadataParser(BaseMetadataParser):
    """docstring for MediaMetadataParser"""
    def __init__(self, opts, media_item, media_node):
        super(MediaMetadataParser, self).__init__(opts)
        self.opts = opts
        self.media_item = media_item
        self.media_node = media_node
        
        resolution = self.media_node.get('videoResolution', "")
        self.is_HD = resolution.isdigit() and int(resolution) >= 720
        
        part_node = self.media_node.find("Part")
        self.part_parser = PartMetadataParser(self.opts, self, part_node)
    #end def __init__
    
    def tag_string(self):
        tag_string = self.media_item.tag_string()
        
        hd_value = "%d" % (1 if self.is_HD else 0)
        tag_string += self.new_tag_string_entry("HD Video", hd_value)
        
        return tag_string
    #end def tag_string
#end class MediaParser