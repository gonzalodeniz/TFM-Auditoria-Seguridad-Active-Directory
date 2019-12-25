# coding=utf-8
"""
    FILE            awdp_lib_file_metadata.py
    Version:        1.0
    Date Version:   23/03/2017
    Author:         Gonzalo Déniz Acosta

"""

import os
import sys
import zipfile

import hachoir_core
import hachoir_core.cmd_line
import hachoir_metadata
import hachoir_parser

try:
    import openxmllib
except ImportError:
    print('No found openxmllib. Make "pip install lxml"')
    sys.exit(0)



class FileMetadata(object):
    """ Extract metadata from multiple files.

        You can extract metadata in text or dictionary format.

        Attributes:
            EXT_SUPPORT_MO2007: List indicating the extensions allowed by opmenxmllib.
            EXT_SUPPORT_HACHOIR: List indicating the extensions allowed by hachoir.
            file: string indicating the file to be processed.
    """

    # Extensions supported
    EXT_SUPPORT_MO2007 = ['docx', 'xlsx', 'pptx']
    EXT_SUPPORT_HACHOIR = ['bzip2', 'cab', 'gzip', 'mar', 'tar', 'zip', 'aiff',
                            'mpg', 'mpeg', 'mp1', 'mp2', 'mp3','ra','mkv',
                            'ogg', 'rm','riff','bmp','gif','ico','jpg','jpeg',
                            'pxc', 'png','psd','targa','tga','tiff','wmf','xcf',
                            'ole20','pcf','torrent','tff','exe','asf','flv','mov','pdf','txt'
                           ]

    @classmethod
    def ext_supported(self):
        """Returns list with supported extensions."""
        return self.EXT_SUPPORT_MO2007 + self.EXT_SUPPORT_HACHOIR

    def __init__(self, file=None):
        """ Constructor.

            Args:
                file:   String indicating the file to be processed.
        """
        self.__prop_d = {}
        self.file = None
        if file is not None:
            self.load(file)

    def load(self, file):
        """ Load and processed the metadata extraction.

            Args:
                file:   String indicating the file to be processed.
        """
        self.__prop_d = {}
        self.file = file

        # Extract Metadata
        self.__prop_d['Filename'] = os.path.basename(self.file)
        self.__prop_d['AbsPath'] = os.path.abspath(self.file)

        # Check if extensión is valid
        if os.path.splitext(file)[1][1:] in self.EXT_SUPPORT_MO2007:
            self.__get_meta_openxmllib(file)
        elif os.path.splitext(file)[1][1:] in self.EXT_SUPPORT_HACHOIR:
            self.__get_meta_hachoir(file)



    def __get_meta_openxmllib(self, file):
        """ Extract metadatas using openxmllib.

            Args:
                file:   File to be processed.
            """
        properties_all_d = []
        try:
            properties_all_d = openxmllib.openXmlDocument(file).allProperties
        except zipfile.BadZipfile as e:
            print(e.message)
            pass

        # Discard nulls
        for key_prop in properties_all_d:
            if properties_all_d[key_prop] is not None:
                self.__prop_d[key_prop] = properties_all_d[key_prop]

    def __get_meta_hachoir(self, file):
        """ Extrat metadatas using hachoir.

            Args:
                file:   File to be process
        """
        text = ""
        try:
            file, realname = awdp_file_metadata.hachoir_core.cmd_line.unicodeFilename(file), file
            parser = hachoir_parser.createParser(file, realname)
        except hachoir_core.stream.input.InputStreamError:
            parser = None

        if not parser:
            print >> sys.stderr, "Unable to parse file"
            return text

        try:
            metadata = hachoir_metadata.extractMetadata(parser)
        except HachoirError, err:
            print "Metadata extraction error: %s" % unicode(err)
            metadata = None

        if not metadata:
            print >> sys.stderr, "Unable to extract metadata"
            return text

        properties_all_d = metadata.exportDictionary(line_prefix='')
        # Discard nulls
        for key_prop in properties_all_d:
            if properties_all_d[key_prop] is not None:
                self.__prop_d[key_prop] = properties_all_d[key_prop]


    def properties_all_str(self):
        """ Return a string with all metadatas not null."""
        txt = ''
        txt += 'Filename: ' + self.__prop_d['Filename'] + '\n'
        txt += 'AbsPath: ' + self.__prop_d['AbsPath'] + '\n'
        for key_prop in self.__prop_d:
            if key_prop not in ['Filename', 'AbsPath']:
                try:
                    txt += key_prop + ': ' + self.__prop_d[key_prop] + '\n'
                except UnicodeDecodeError:
                    pass
        return txt

    def properties_all_d(self):
        """ Return a dictionary with all metadatas not null."""
        return self.__prop_d

    def propertie(self, key):
        """ Return a string with a metadatas of a key.

            Args:
                key:    Name of a propertie
        """
        try:
            return self.__prop_d[key]
        except KeyError:
            return None

