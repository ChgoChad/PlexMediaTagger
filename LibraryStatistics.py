#!/usr/bin/env python
#encoding:utf-8
#author:ccjensen/Chris
#project:PlexMediaTagger
#repository:http://github.com/ccjensen/plexmediatagger
#license:Creative Commons GNU GPL v2
# (http://creativecommons.org/licenses/GPL/2.0/)

from datetime import datetime, timedelta
from Items.MovieItem import MovieItem
from Items.EpisodeItem import EpisodeItem

class LibraryStatistics:
    __shared_state = {}
    def __init__(self):
        self.__dict__ = self.__shared_state
        
        if not 'total_duration_episodes' in self.__dict__:
            self.total_duration_episodes = 0
            self.total_duration_movies = 0
            
            self.number_of_episodes = 0
            self.number_of_movies = 0
        #end def if not
    #end def init

    def results(self):
        results = []
        seperator = "-"*45
        
        total_number_of_items = self.number_of_episodes+self.number_of_movies
        results.append("Number of items: \t\t%d" % ( total_number_of_items ))
        
        results.append(seperator)
        results.append("Number of Movies: \t\t%d" % ( self.number_of_movies ))
        results.append("Number of TV Episodes: \t\t%d" % ( self.number_of_episodes ))
        
        results.append(seperator)
        total_duration = self.total_duration_episodes + self.total_duration_movies
        results.append("Total Duration: \t\t%s" % ( self.time_formatted_string(total_duration) ))
        average = self.average(total_duration, total_number_of_items)
        results.append("Average Duration: \t\t%s" % ( self.time_formatted_string(average) ))
        
        results.append(seperator)
        results.append("Total TV Episodes Duration: \t%s" % ( self.time_formatted_string(self.total_duration_episodes) ))
        average = self.average(self.total_duration_episodes, self.number_of_episodes)
        results.append("Average TV Episode Duration: \t%s" % ( self.time_formatted_string(average) ))
        
        results.append(seperator)
        results.append("Total Movies Duration: \t\t%s" % ( self.time_formatted_string(self.total_duration_movies) ))
        average = self.average(self.total_duration_movies, self.number_of_movies)
        results.append("Average Movie Duration: \t%s" % ( self.time_formatted_string(average) ))
        
        return results
    #end def results
    
    def time_labelled(self, number, non_pluralized_label):
        label = non_pluralized_label
        if number > 1:
            label += "s"
        return "%d %s" % (number, label)
    #end def time_labelled
    
    def time_formatted_string(self, duration):
        time = []
        delta = timedelta(milliseconds=duration)
        d = datetime(1,1,1) + delta
        years = d.year - 1
        months = d.month - 1
        days = d.day - 1
        hours = d.hour
        minutes = d.minute
        seconds = d.second
        
        if years > 0:
            time_str = self.time_labelled(years, "year")
            if len(time_str) > 0:
                time.append(time_str)
        
        if months > 0 or len(time) > 0:
            time_str = self.time_labelled(months, "month")
            if len(time_str) > 0:
                time.append(time_str)
        
        if days > 0 or len(time) > 0:
            time_str = self.time_labelled(days, "day")
            if len(time_str) > 0:
                time.append(time_str)
        
        if hours > 0 or len(time) > 0:
            time_str = self.time_labelled(hours, "hour")
            if len(time_str) > 0:
                time.append(time_str)
                
        if minutes > 0 or len(time) > 0:
            time_str = self.time_labelled(minutes, "minute")
            if len(time_str) > 0:
                time.append(time_str)
                
        if seconds > 0 or len(time) > 0:
            time_str = self.time_labelled(seconds, "second")
            if len(time_str) > 0:
                time.append(time_str)
        
        return ", ".join(time)
    #end def time_formatted_string
    
    def average(self, amount, number_of_items):
        if amount == 0:
            return 0
        else:
            return amount/number_of_items
    #end def 
    
    def add_item(self, video_item):        
        video_item_class = video_item.__class__
        
        if video_item_class == EpisodeItem:
            self.number_of_episodes += 1
        elif video_item_class == MovieItem:
            self.number_of_movies += 1
        
        media_item = video_item.media_item
        part_items = [media_item.part_item]
        
        for i, part_item in enumerate(part_items):
            duration = part_item.duration
            if duration == "":
                print "ERROR: No duration!!! Let the developer know about this"
                duration = 0
                
            milliseconds = int(duration)
            if video_item_class == EpisodeItem:
                self.total_duration_episodes += milliseconds
            elif video_item_class == MovieItem:
                self.total_duration_movies += milliseconds
            #end if
        #end for
    #end def add_item
#end def class LibraryStatistics