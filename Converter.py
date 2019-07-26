#!/usr/bin/python

import os
import os.path
import shlex

from ffmpeg import FFMpeg, FFMpegConvertError, FFMpegError

FFMPEG_CLI = 'C:\\Users\\Chad\\Documents\\GitHub\\PlexMediaTagger\\ffmpeg\\ffmpeg.exe'
FFPROBE_CLI = 'C:\\Users\\Chad\\Documents\\GitHub\\PlexMediaTagger\\ffmpeg\\ffprobe.exe'

class ConverterError(Exception):
    pass


class Converter(object):
    """
    Converter class, encapsulates formats and codecs.

    >>> c = Converter()
    """
    def __init__(self, ffmpeg_path=FFMPEG_CLI, ffprobe_path=FFPROBE_CLI):
        """
        Initialize a new Converter object.
        """
        self.ffmpeg = FFMpeg(ffmpeg_path=ffmpeg_path, ffprobe_path=ffprobe_path)
    #end __init__


    def convert(self, infile, outfile, options, timeout=10):
            """
            Convert media file (infile) according to specified options, and
            save it to outfile. 

            Multiple audio/video streams are not supported. The output has to
            have at least an audio or a video stream (or both).

            Convert returns a generator that needs to be iterated to drive the
            conversion process. The generator will periodically yield timecode
            of currently processed part of the file (ie. at which second in the
            content is the conversion process currently).

            The optional timeout argument specifies how long should the operation
            be blocked in case ffmpeg gets stuck and doesn't report back. This
            doesn't limit the total conversion time, just the amount of time
            Converter will wait for each update from ffmpeg. As it's usually
            less than a second, the default of 10 is a reasonable default. To
            disable the timeout, set it to None. You may need to do this if
            using Converter in a threading environment, since the way the
            timeout is handled (using signals) has special restriction when
            using threads.

            >>> conv = c.convert('test1.ogg', '/tmp/output.mkv', {
            ...    'format': 'mkv',
            ...    'audio': { 'codec': 'aac' },
            ...    'video': { 'codec': 'h264' }
            ... })

            >>> for timecode in conv:
            ...   pass # can be used to inform the user about the progress
            """

            #if not isinstance(options, dict):
            #    raise ConverterError('Invalid options')

            if not os.path.exists(infile):
                raise ConverterError("Source file doesn't exist: " + infile)

            info = self.ffmpeg.probe(infile)
            if info is None:
                raise ConverterError("Can't get information about source file")

            if not info.video and not info.audio:
                raise ConverterError('Source file has no audio or video streams')

            if info.format.duration < 0.01:
                raise ConverterError('Zero-length media')

            optlist = shlex.split(''.join(options))

            #optlist = self.parse_options(options, twopass)
            for timecode in self.ffmpeg.convert(infile, outfile, optlist, timeout=timeout):
                yield int((100.0 * timecode) / info.format.duration)
    #end convert    


    def probe(self, fname):
        """
        Examine the media file. See the documentation of
        converter.FFMpeg.probe() for details.
        """
        return self.ffmpeg.probe(fname)
    #end probe


    def thumbnail(self, fname, time, outfile, size=None):
        """
        Create a thumbnail of the media file. See the documentation of
        converter.FFMpeg.thumbnail() for details.
        """
        return self.ffmpeg.thumbnail(fname, time, outfile, size)
    #emd thumbnail
