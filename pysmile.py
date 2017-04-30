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
RESIZE_RATIO    = 1
RESIZE_WIDTH    = 2
RESIZE_HEIGHT   = 3

class ResizeArg(object):
    def __init__(self, type, value):
        self.type = type
        self.value = value

    def __str__(self):
        if self.type == RESIZE_RATIO:
            return 'ResizeArg(ratio, %d)' % self.value
        elif self.type == RESIZE_WIDTH:
            return 'ResizeArg(width, %d)' % self.value
        elif self.type == RESIZE_HEIGHT:
            return 'ResizeArg(height, %d)' % self.value
        else:
            return 'ResizeArg(%d, %d)' % (self.type, self.value)

def batch_convert(input_pattern, dest_dir, resize_arg, output_ext = None):
    # Expand ~ to $HOME, then pass to glob
    input_files = []
    for pat in input_pattern:
        input_files += glob.glob(os.path.expanduser(pat))

    if len(input_files) < 1:
        print("No files with specified pattern found. Try another pattern.")
        return 0

    print("Found %s matched files:" % len(input_files))

    count = 0;
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

                count += 1
                print("%d) %s" % (count, temp_file_name))

                im = Image.open(in_file)
                width, height = im.size
                png_info = im.info
                if resize_arg:
                    if resize_arg.type == RESIZE_RATIO:
                        size_ratio = resize_arg.value
                        if size_ratio != 100:
                            size = (width * size_ratio / 100., height * size_ratio / 100.)
                            im.thumbnail(size, Image.ANTIALIAS)
                    elif resize_arg.type == RESIZE_WIDTH:
                        target_width = resize_arg.value
                        if width != target_width:
                            size = (target_width, 1.0 * height * target_width / width)
                            im.thumbnail(size, Image.ANTIALIAS)
                    elif resize_arg.type == RESIZE_HEIGHT:
                        target_height = resize_arg.value
                        if width != target_width:
                            size = (1.0 * width * target_height / height, target_height)
                            im.thumbnail(size, Image.ANTIALIAS)
                    else:
                        raise "Invalid ResizeArg type: %d" % resize_arg.type
                im.save(final_out, **png_info)
                print("Saved to %s" % final_out)
            else:
                print("The input file %s cannot be read!" % in_file)
        else:
            print("The path %s is not a file!" % in_file)

    return 0

def parse_input():
    parser = argparse.ArgumentParser(description='Process Images in batches.')

    # All the arguments in this group indicate size/dimension
    group = parser.add_mutually_exclusive_group()
    group.add_argument("-r", "--size-ratio", dest="size_ratio", type=int, help="Whether to resize, in %%", default=0)
    group.add_argument("--width", dest="width", type=int, help="Resize to specified width", default=0)
    group.add_argument("--height", dest="height", type=int, help="Resize to specified height", default=0)

    parser.add_argument("-d", "--dest-dir", dest="dest_dir", help="Destination directory to writen processed images")
    parser.add_argument("input_pattern", nargs="+", help="Look for files that match some pattern. E.g. *.png or pic*cool*")
    parser.add_argument("-o", "--output-format", dest="output_ext", help="Output format/extension to save all images. If empty, original format of images is preserved. Allowed output extensions: %s" % str(ALLOWED_FORMATS), default=None)
    parser.add_argument("-q", "--quiet", action="store_true", dest="accept_quietly", help="Convert files without confirmation")

    args = parser.parse_args()
    cwd = os.getcwd()

    # Mandate input pattern
    if not args.input_pattern:
        parser.print_help()
        return None

    # Verify output formats: Either None or ALLOWED_FORMATS
    if args.output_ext:
        args.output_ext = str(args.output_ext).lower()
        if args.output_ext not in ALLOWED_FORMATS:
            print("Output formats must be in %s" % str(ALLOWED_FORMATS))
            return None

    # If destination directory is missing, assign current working directory
    if not args.dest_dir:
        args.dest_dir = cwd

    # Verify existense of destination directory
    if not os.path.isdir(args.dest_dir):
        print('Invalid the DESTINATION directory!')
        return None

    # Verify that user has permission to write destination directory
    if not os.access(args.dest_dir, os.W_OK):
        print('You do not have permission to write to the DESTINATION directory!')
        return None

    if args.size_ratio > 0:
        args.resize_arg = ResizeArg(RESIZE_RATIO, args.size_ratio)

    if args.width > 0:
        args.resize_arg = ResizeArg(RESIZE_WIDTH, args.width)

    if args.height < 0:
        args.resize_arg = ResizeArg(RESIZE_HEIGHT, args.height)

    # Convert the destination directory to its full absolute path
    args.dest_dir = os.path.realpath(args.dest_dir)

    return args

def process_images(args):
    # If no conversion or resizing needed, just skipt
    if args.size_ratio == 100 and not args.output_ext:
        print("You can simply copy files over in this case!")
        return

    if args.output_ext:
        output_format = args.output_ext
    else:
        output_format = "Keep as is"
    # Note template to the user
    summary = """
    Please review before proceeding to batch coversion:
----------------------------------------------------------------
    The destination dir: %s
    The output format: %s
    The resize arg: %s
    """
    summary = summary % (args.dest_dir, output_format, args.resize_arg)
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
        batch_convert(
            input_pattern=args.input_pattern,
            dest_dir=args.dest_dir,
            resize_arg=args.resize_arg,
            output_ext=args.output_ext)
    else:
        print('Bye!')

def main():
    args = parse_input()
    if args:
        process_images(args)

if __name__ == "__main__":
    main()
