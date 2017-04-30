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
import argparse

ALLOWED_FORMATS = ('png', 'gif', 'jpg', 'jpeg', 'bmp', 'pdf')

def batch_convert(src_dir, input_pattern, output_ext = None, dest_dir = None):
    input_files = glob.glob(src_dir + '/' + input_pattern)

    if len(input_files) < 1:
        print("No files with specified pattern found. Try another pattern.")
        return 0

    print("Found %s matched files:" % len(input_files))

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

                print("Converting %s ===> %s" % (temp_file_name, out_file))

                im = Image.open(in_file)
                im.save(final_out)
            else:
                print("The input file %s cannot be read!" % in_file)
        else:
            print("The path %s is not a file!" % in_file)

    return 0

def parse_input():
    parser = argparse.ArgumentParser(description='Process Images in batches.')
    parser.add_argument("-s", "--source-dir", dest="src_dir", help="Source directory to fetch images")
    parser.add_argument("-d", "--dest-dir", dest="dest_dir", help="Destination directory to writen processed images")
    parser.add_argument("-i", "--input-pattern", dest="input_pattern", help="Look for files that match some pattern. E.g. *.png or pic*cool*")
    parser.add_argument("-o", "--output-format", dest="output_ext", help="Output format/extension to save all images. If empty, original format of images is preserved. Allowed output extensions: %s" % str(ALLOWED_FORMATS))
    parser.add_argument("-q", "--quiet", action="store_true", dest="accept_quietly", help="Convert files without confirmation")
    args = parser.parse_args()
    cwd = os.getcwd()

    # Mandate input pattern
    if not args.input_pattern:
        parser.print_help()
        return -1

    # Verify output formats
    if args.output_ext:
        args.output_ext = str(args.output_ext).lower()
        if args.output_ext not in ALLOWED_FORMATS:
            print("Output formats must be in %s" % str(ALLOWED_FORMATS))
            return -1

    # If source directory is missing, assign current working directory
    if not args.src_dir:
        args.src_dir = cwd

    # If destination directory is missing, assign current working directory
    if not args.dest_dir:
        args.dest_dir = cwd

    # Verify existense of source directory
    if not os.path.isdir(args.src_dir):
        print('Invalid the SOURCE directory!')
        return -1

    # Verify existense of destination directory
    if not os.path.isdir(args.dest_dir):
        print('Invalid the DESTINATION directory!')
        return -1

    # Verify that user has permission to read source directory
    if not os.access(args.src_dir, os.R_OK):
        print('You do not have permission to read the SOURCE directory!')
        return -1

    # Verify that user has permission to write destination directory
    if not os.access(args.dest_dir, os.W_OK):
        print('You do not have permission to write to the DESTINATION directory!')
        return -1

    # Convert source & destination directories to their full absolute paths
    args.src_dir = os.path.realpath(args.src_dir)
    args.dest_dir = os.path.realpath(args.dest_dir)

    return args

def process_images(args):
    # Note template to the user
    summary = """
    Please review before proceeding to batch coversion:
----------------------------------------------------------------
    The source dir: %s
    The destination dir: %s
    The input pattern: %s
    The output format: %s
    """
    summary = summary % (args.src_dir, args.dest_dir, args.input_pattern, args.output_ext)
    ask_user = 'Do you want to proceed? [Y/n] '

    # Print summary of inputs
    print(summary)

    if args.accept_quietly:
        user_input = 'Y'
    else:
        # Get confirmation to proceed
        user_input = input(ask_user)

    if ('' == user_input) or (user_input[0] in ('y', 'Y')):
        # Proceed if user wants
        batch_convert(src_dir=args.src_dir, input_pattern=args.input_pattern, output_ext=args.output_ext, dest_dir=args.dest_dir)
    else:
        print('Bye!')

def main():
    process_images(parse_input())

if __name__ == "__main__":
    main()
