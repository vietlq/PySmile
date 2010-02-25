#!/usr/bin/env python

"""
@author             Le Quoc Viet
@version            0.4
@brief              
@description        
@modified           
"""

import os, sys, glob
from PIL import Image
from optparse import OptionParser

ALLOWED_FORMATS = ('png', 'gif', 'jpg', 'jpeg', 'bmp', 'pdf')

def batch_convert(src_dir, input_pattern, output_ext = None, dest_dir = None):
    input_files = glob.glob(src_dir + '/' + input_pattern)
    
    if len(input_files) < 1:
        print "No files with specified pattern found. Try another pattern."
        return 0
    
    print "Found %s matched files:" % len(input_files)
    
    for in_file in input_files:
        if os.path.isfile(in_file):
            if os.access(in_file, os.R_OK):
                (temp, temp_file_name) =  os.path.split(in_file)
                (in_file_no_ext, in_file_ext) = os.path.splitext(temp_file_name)
                
                if output_ext:
                    out_file = in_file_no_ext + '.' + output_ext
                else:
                    out_file = temp_file_name
                
                final_out = dest_dir + '/' + out_file
                
                print "Converting %s ===> %s" % (temp_file_name, out_file)
                
                im = Image.open(in_file)
                im.save(final_out)
            else:
                print "The file %s is cannot be read!" % in_file
        else:
            print "The path %s is not a file!" % in_file
    
    return 0

def main():
    #print sys.argv
    parser = OptionParser()
    parser.add_option("-s", "--source-dir", dest="src_dir", help="Source directory to fetch images")
    parser.add_option("-d", "--dest-dir", dest="dest_dir", help="Destination directory to writen processed images")
    parser.add_option("--ip", "--input-pattern", dest="input_pattern", help="Look for files that match some pattern. E.g. *.png or pic*cool*")
    parser.add_option("-o", "--output-format", dest="output_ext", help="Output format/extension to save all images. If empty, original format of images is preserved. Allowed output extensions: %s" % str(ALLOWED_FORMATS))
    parser.add_option("-q", "--quiet", action="store_true", dest="accept_quietly", help="Convert files without confirmation")
    (options, args) = parser.parse_args()
    cwd = os.getcwd()
    #print options
    
    # Mandate input pattern
    if not options.input_pattern:
        parser.print_help()
        return -1
    
    # Verify output formats
    if options.output_ext:
        options.output_ext = str(options.output_ext).lower()
        if options.output_ext not in ALLOWED_FORMATS:
            print "Output formats must be in %s" % str(ALLOWED_FORMATS)
            return -1
    
    # If source directory is missing, assign current working directory
    if not options.src_dir:
        options.src_dir = cwd
    
    # If destination directory is missing, assign current working directory
    if not options.dest_dir:
        options.dest_dir = cwd
    
    # Verify existense of source directory
    if not os.path.isdir(options.src_dir):
        print 'Invalid the SOURCE directory!'
        return -1
    
    # Verify existense of destination directory
    if not os.path.isdir(options.dest_dir):
        print 'Invalid the DESTINATION directory!'
        return -1
    
    # Verify that user has permission to read source directory
    if not os.access(options.src_dir, os.R_OK):
        print 'You do not have permission to read the SOURCE directory!'
        return -1
    
    # Verify that user has permission to write destination directory
    if not os.access(options.dest_dir, os.W_OK):
        print 'You do not have permission to write to the DESTINATION directory!'
        return -1
    
    # Convert source & destination directories to their full absolute paths
    options.src_dir = os.path.realpath(options.src_dir)
    options.dest_dir = os.path.realpath(options.dest_dir)
    
    # Note template to the user
    note = """
    Please review before proceeding to batch coversion:
----------------------------------------------------------------
    The source dir: %s
    The destination dir: %s
    The input pattern: %s
    The output format: %s
    """
    note = note % (options.src_dir, options.dest_dir, options.input_pattern, options.output_ext)
    ask_user = 'Do you want to proceed? [Y/n] '
    
    print note
    
    if options.accept_quietly:
        user_input = 'Y'
    else:
        # Print summary and get confirmation to proceed
        user_input = raw_input(ask_user)
    
    if ('' == user_input) or (user_input[0] in ('y', 'Y')):
        # Proceed if user wants
        batch_convert(src_dir=options.src_dir, input_pattern=options.input_pattern, output_ext=options.output_ext, dest_dir=options.dest_dir)
    else:
        print 'Bye!'

if __name__ == "__main__":
    main()
