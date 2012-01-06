#!/usr/bin/env python
#encoding:utf-8
#author:ccjensen/Chris
#project:PlexMediaTagger
#repository:http://github.com/ccjensen/plexmediatagger
#license:Creative Commons GNU GPL v2
# (http://creativecommons.org/licenses/GPL/2.0/)

import logging
import sys
import os
import glob
import subprocess
from Statistics import *
from DataTokens import *

class VideoItemProcessor:
    """docstring for VideoItemProcessor"""
    def __init__(self, opts, video_item):
        self.opts = opts
        self.video_item = video_item
        self.media_item = self.video_item.media_item
        self.part_items = [self.media_item.part_item]
    #end def __init__
    
    def canTag(self, part_item):
        if part_item.file_type == '.m4v' or part_item.file_type == '.mp4':
            return True
        else:
            logging.info("PlexMediaTagger cannot tag '%s' files" % part_item.file_type)
            return False
        #end if
    #end def canTag
    
    def shouldTag(self, part_item):
        if self.opts.force:
            return True
        
        comment_tag_contents = self.getFileCommentTagContents(part_item)
        for word in comment_tag_contents.split(" "):
            if word.startswith(DataTokens.itunes_tag_data_token):
                logging.info("File previously tagged")
                for item in word.split(DataTokens.tag_data_delimiter):
                    if item.startswith(DataTokens.updated_at_token):
                        tag_data_updated_at = item.split(DataTokens.updated_at_token)[1]
                        metadata_updated_at = self.video_item.updated_at
                        logging.debug("file:%s vs. pms:%s" % (tag_data_updated_at, metadata_updated_at)))
                        if (metadata_updated_at > tag_data_updated_at):
                            logging.info("Metadata has changed since last time")
                            return True
                        else:
                            logging.info("No change to the metadata since last time")
                            return False
                    #end inf
                #end for
                logging.info("Updated at token missing, will re-tag the file")
        return True
    #end def shouldTag
    
    def getFileCommentTagContents(self, part_item):
        """docstring for getFileCommentTagContents"""
        AtomicParsley = os.path.join(sys.path[0], "AtomicParsley32")
        comment_tag = "Atom \"©cmt\""

        #Create the command line string
        get_tags_cmd = ['%s' % AtomicParsley]
        get_tags_cmd.append('%s' % part_item.modified_file_path())
        get_tags_cmd.append('-t')
        
        #check if file has already been tagged
        result = subprocess.Popen(get_tags_cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE).communicate()[0]
        
        #error checking
        if 'AtomicParsley error' in result:
            logging.critical("Failed to determine file tagged status")
            return nil
        #end if 'AtomicParsley error' in result:
        
        for line in result.split("\n"):
            if comment_tag in line:
               return line

        logging.info("File untagged")
        return ""
        #end if tagString in result
    #end getFileCommentTagContents
    
    def execute_command(self, actionable_file_path, command, action_description):
        logging.debug("'%s' arguments: %s" % (action_description, command))
        if self.opts.dryrun:
            result = "dryrun"
        else:
            #check if file exists
            if os.path.isfile(actionable_file_path):
                #run command
                result = subprocess.Popen(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE).communicate()[0]
            else:
                result = "Error: Unable to find file."
            #end if isfile
                
        #end if dryrun
        if "Error" in result:
            logging.critical("Failed %s for %s: %s" % (action_description, actionable_file_path, result.strip()) )
            return False
        else:
            #success
            logging.warning("'%s': %s" % (action_description, actionable_file_path))
            return True
        #end if "Error"
    #end def execute_command
    
    def remove_tags(self, part_item):
        SublerCLI = os.path.join(sys.path[0], "SublerCLI-v010")
        filepath = part_item.modified_file_path()
        #removal of artwork doesn't seem to work
        all_tags = ["{Artwork:}", "{HD Video:}", "{Gapless:}", "{Content Rating:}", "{Media Kind:}", "{Name:}", "{Artist:}", "{Album Artist:}", "{Album:}", "{Grouping:}", "{Composer:}", "{Comments:}", "{Genre:}", "{Release Date:}", "{Track #:}", "{Disk #:}", "{TV Show:}", "{TV Episode #:}", "{TV Network:}", "{TV Episode ID:}", "{TV Season:}", "{Description:}", "{Long Description:}", "{Rating:}", "{Rating Annotation:}", "{Studio:}", "{Cast:}", "{Director:}", "{Codirector:}", "{Producers:}", "{Screenwriters:}", "{Lyrics:}", "{Copyright:}", "{Encoding Tool:}", "{Encoded By:}", "{contentID:}"]#these are currently not supported in subler cli tool, "{XID:}", "{iTunes Account:}", "{Sort Name:}", "{Sort Artist:}", "{Sort Album Artist:}", "{Sort Album:}", "{Sort Composer:}", "{Sort TV Show:}"]
        
        logging.warning("removing tags...")
        
        #Create the command line command
        tag_removal_cmd = ['%s' % SublerCLI]
        
        if self.opts.optimize:
            action_description = "Tags removed and optimized"
            tag_removal_cmd.append("-O")
        else:
            action_description = "Tags removed"
        #end if optimize
        
        tag_removal_cmd.append("-t")
        tag_removal_cmd.append("".join(all_tags))
        tag_removal_cmd.append("-i")
        tag_removal_cmd.append(filepath)
        
        success = self.execute_command(filepath, tag_removal_cmd, action_description)
        if success:
            Statistics().metadata_removal_succeeded()
        else:
            Statistics().metadata_removal_failed()
        #end success
    #end remove_tags
    
    def tag(self, part_item):
        SublerCLI = os.path.join(sys.path[0], "SublerCLI-v010")
        filepath = part_item.modified_file_path()
        
        logging.warning("tagging...")
        
        #Create the command line command
        tag_cmd = ['%s' % SublerCLI]

        if self.opts.optimize:
            action_description = "Tags added and optimized"
            tag_cmd.append("-O")
        else:
            action_description = "Tags added"
        #end if optimize

        tag_cmd.append("-t")
        tag_cmd.append(part_item.tag_string()) #also downloads the artwork
        tag_cmd.append("-i")
        tag_cmd.append(filepath)
        
        success = self.execute_command(filepath, tag_cmd, action_description)
        if success:
            Statistics().metadata_embedded_succeeded()
        else:
            Statistics().metadata_embedded_failed()
        #end success
    #end tag
    
    def optimize(self, part_item):
        SublerCLI = os.path.join(sys.path[0], "SublerCLI-v010")
        filepath = part_item.modified_file_path()
        
        logging.warning("optimizing file...")
        
        action_description = "Tags optimized"
        #Create the command line command
        optimize_cmd = ['%s' % SublerCLI]
        optimize_cmd.append("-O")
        optimize_cmd.append("-i")
        optimize_cmd.append(filepath)
        
        success = self.execute_command(filepath, optimize_cmd, action_description)
        if success:
            Statistics().metadata_optimized_succeeded()
        else:
            Statistics().metadata_optimized_failed()
        #end success
    #end remove_tags
    
    def export_resources(self, part_item):
        part_item_file_path = part_item.modified_file_path()
        directory = os.path.dirname(part_item_file_path)
        filename = os.path.basename(part_item_file_path)
        filename_without_extension = os.path.splitext(filename)[0]
        
        os.chdir(directory)
        #=== subtitles ===
        #build up language_code dict
        if self.opts.export_subtitles:
            logging.warning("attempting to export subtitles...")
            subtitle_stream_type = "3"
            all_non_embedded_subtitles = []
            for stream_item in part_item.stream_items:
                if stream_item.stream_type == subtitle_stream_type and stream_item.key != "":
                    all_non_embedded_subtitles.append(stream_item)
                #end if
            #end for
            number_of_non_embedded_subtitles = len(all_non_embedded_subtitles)
            if number_of_non_embedded_subtitles == 0:
                logging.warning("no subtitles found")
            else:
                logging.warning("found %d subtitle(s)" % number_of_non_embedded_subtitles)
                
                categorized_subtitles = {}
                for subtitle in all_non_embedded_subtitles:
                    key = (subtitle.language_code, subtitle.codec)
                    if categorized_subtitles.has_key(key):
                        categorized_subtitles[key].append(subtitle)
                    else:
                        categorized_subtitles[key] = [subtitle]
                    #end if has_key
                #end for all_subtitles
                
                exported_subtitles = 0
                for key, subtitles in categorized_subtitles.iteritems():
                    #key = (eng, srt), (eng, sub), (fre, srt), etc.
                    language_code = key[0]
                    codec = key[1]
                    #get all existing sub files. example filename: Sopranos - S01E01 - The Pilot*.eng.srt
                    glob_str = "%s*.%s.%s" % (filename_without_extension, language_code, codec)
                    if len(glob.glob(glob_str)) > 0:
                        logging.warning("Subtitle file(s) with language code '%s' of type '%s' already exist. Skipping all matching..." % (language_code, codec))
                        continue
                    #end if
                
                    #export subs
                    i = 0
                    for subtitle in subtitles:
                        if i == 0:
                            subtitle_filename = "%s.%s.%s" % (filename_without_extension, language_code, codec)
                        else:
                            subtitle_filename = "%s.%02d.%s.%s" % (filename_without_extension, i, language_code, codec)
                        #end if
                        subtitle_full_path = os.path.join(directory, subtitle_filename)
                        success = subtitle.export_to_path(subtitle_full_path)
                        if success:
                            i += 1
                            exported_subtitles += 1
                            Statistics().subtitle_export_succeeded()
                        else:
                            Statistics().subtitle_export_failed()
                        #end success
                    #end for subtitles
                #end for categorized_subtitles
                logging.warning( "exported %d subtitle(s), skipped %d" % ( exported_subtitles, (number_of_non_embedded_subtitles-exported_subtitles) ) )
            #end if len(all_non_embedded_subtitles) == 0:
        #end if subtitles
        
        if self.opts.export_artwork:
            logging.error("artwork export not yet implemented...")
            #logging.warning("attempting to export artwork...")
        
    #end export_resources
    
    def process(self):
        skipped_all = True
        
        for part_item in self.part_items:
            if self.opts.removetags and self.canTag(part_item):
                skipped_all = False
                self.remove_tags(part_item)
            #end if removetags
            if self.opts.tag and self.canTag(part_item) and self.shouldTag(part_item):
                skipped_all = False
                self.tag(part_item)
            #end if tag   
            if self.opts.optimize and not self.opts.tag and not self.opts.removetags and self.canTag(part_item):
                #optimize is done together with tagging or removing, so only needs to be done here if it's the exclusive action
                skipped_all = False
                self.optimize(part_item)
            #end if optimize
            if self.opts.export_resources:
                skipped_all = False
                self.export_resources(part_item)
            #end if export_resouces
        if skipped_all:
            logging.warning("skipping: no valid files for specified tasks")
        #end if skipped_all
    #end def process_item
#end MediaPartProcessor