# coding=utf-8
"""
    File:           awdp_file_metadata.py
    Version:        1.0
    Date Version:   23/03/2017
    Author:         Gonzalo Déniz

    NAME
        awdp_file_metadata - Returns the metadata of a file

    SYNOPSIS:
        python awdp_file_metadata.py { -f file | -d directory [-r] }  [-o file_dest ] [-e ext1,ext2,ext...]

    DESCRIPTION
        The metadata files can contain local file paths, user account names, operating system...
        This script extracts that data.

    OPTIONS
        file            Path and filename that will be processed to extract the metadata. Only one file.
        directory       Path and folder that will be process to extract the metadata.
        -r              Search files in directory and subdirectory.
        -o file_dest    File with the result of execution. If '-o' no exists, then the result is written in console.
        -e ext1,ext2... Filters by file extension. Extensions must be separated by a single comma.
                        Do not write blanks.
    FILES
        awdp_file_metadata.py          Executable file
        lib_file_metadta.py       Class FileMetadata.

    PACKAGE
        openxmllib                openxmllib is a set of tools that deals with the new ECMA 376 office
                                  file formats known as OpenXML. https://pypi.python.org/pypi/openxmllib
        hachoir_core              Library hachoir to extract metadata. https://pypi.python.org/pypi/hachoir-core/1.3.3
        hachoir_metadata          Library hachoir to extract metadata. https://pypi.python.org/pypi/hachoir-metadata/1.3.3
        hachoir_parse             Library hachoir to extract metadata. https://pypi.python.org/pypi/hachoir-parser/1.3.4

    EXAMPLE OF USE
        # Extract metadata of all disc F, of files with extension docx and pptx, and write results in salida.txt
        python awdp_file_metadata.py -d F:\ -e docx,pptx -r -o .\salida.txt

        # Extract metadata of file word.docx and show results in console.
        python awdp_file_metadata.py -f word.docx
"""

import os.path
import sys
from awdp_lib_file_metadata import FileMetadata


def __man():
    man = '''
    NAME
        awdp_file_metadata - Returns the metadata of a file

    SYNOPSIS:

        python awdp_file_metadata.py { -f file | -d directory [-r] }  [-o file_dest ] [-e ext1,ext2,ext...]

    DESCRIPTION
        The metadata files can contain local file paths, user account names, operating system...
        This script extracts that data.

    OPTIONS
        file            Path and filename that will be processed to extract the metadata. Only one file.
        directory       Path and folder that will be process to extract the metadata.
        -r              Search files in directory and subdirectory.
        -o file_dest    File with the result of execution. If '-o' no exists, then the result is written in console.
        -e ext1,ext2... Filters by file extension. Extensions must be separated by a single comma.
                        Do not write blanks.
    FILES
        awdp_file_metadata.py          Executable file
        lib_file_metadta.py       Class FileMetadata.

    PACKAGE
        openxmllib                openxmllib is a set of tools that deals with the new ECMA 376 office
                                  file formats known as OpenXML. https://pypi.python.org/pypi/openxmllib
        hachoir_core              Library hachoir to extract metadata. https://pypi.python.org/pypi/hachoir-core/1.3.3
        hachoir_metadata          Library hachoir to extract metadata. https://pypi.python.org/pypi/hachoir-metadata/1.3.3
        hachoir_parse             Library hachoir to extract metadata. https://pypi.python.org/pypi/hachoir-parser/1.3.4

    EXAMPLE OF USE
        # Extract metadata of all disc F, of files with extension docx and pptx, and write results in salida.txt
        python awdp_file_metadata.py -d F:\ -e docx,pptx -r -o .\salida.txt

        # Extract metadata of file word.docx and show results in console.
        python awdp_file_metadata.py -f word.docx
        '''
    return man

def __argument(argv):

    MIN_NARG = 3    # Minimum number of arguments

    argv_d = {'source_file': None,
              'source_dir': None,
              'file_output': None,
              'filter_ext': None,
              'recursive': False
              }

    # Help
    if '-h' in argv:                    # Help
        print(__man())                  # Return help
        sys.exit(0)

    # Minimum number of arguments
    if len(sys.argv) < MIN_NARG:
        print('Error syntax. To view help: awdp_file_metadata.py -h')
        sys.exit(1)

    # Mandatory arguments
    if argv[1] == '-f':                 # Search in a file
        argv_d['source_file'] = argv[2]
    elif argv[1] == '-d':               # Search in a directory
        argv_d['source_dir'] = argv[2]
    else:
        print('Error syntax. To view help: awdp_file_metadata.py -h')
        sys.exit(1)


    # Optional arguments
    if '-o' in argv:                    # File Output
        pos = argv.index('-o')
        argv_d['file_output'] = argv[pos+1]
    if '-e' in argv:                    # Extensions
        pos = argv.index('-e')
        argv_d['filter_ext'] = argv[pos+1]
    if '-r' in argv:                    # Recursive
        argv_d['recursive'] = True

    return argv_d

def main():

    print ('Extracting metadata...')
    # Initialize variables
    arg_d = __argument(sys.argv)
    filter_ext = FileMetadata.ext_supported()
    output = ''

    # Filter extensions
    if arg_d['filter_ext'] is not None:
        filter_ext = arg_d['filter_ext'].split(',')

    # Single file
    if arg_d['source_file'] is not None and os.path.exists(arg_d['source_file']):
        file = arg_d['source_file']
        ext = os.path.splitext(file)[1][1:]
        if filter_ext is not None and ext in filter_ext:
            oxml = FileMetadata(arg_d['source_file'])
            output += oxml.properties_all_str()
            output += '\n|--\n'

    # Files of a directory
    if arg_d['source_dir'] is not None and os.path.exists(arg_d['source_dir']):
        dir = str(arg_d['source_dir'])
        # Search files in directory and subdirectory
        if arg_d['recursive']:
            for dir_name, subdir_list, file_list in os.walk(dir):
                # List all files of directory
                for file in file_list:
                    ext = os.path.splitext(file)[1][1:]
                    if filter_ext is not None and ext in filter_ext:
                        oxml = FileMetadata(dir_name + '\\' + file)
                        try:
                            output += oxml.properties_all_str()
                        except UnicodeDecodeError:
                            pass
                        output += '\n|--\n\n'
        else:
            # Only one folder
            for file in os.listdir(dir):
                ext = os.path.splitext(file)[1][1:]
                if filter_ext is not None and ext in filter_ext:
                    oxml = FileMetadata(dir + os.sep + file)
                    output += oxml.properties_all_str()
                    output += '\n|--\n\n'


        # Output a file
    if arg_d['file_output'] is not None:
        f = open(arg_d['file_output'], 'w')
        f.write(output)
        f.close()
    else:
        print(output)

    print('Finished')




if __name__ == '__main__':
    main()
