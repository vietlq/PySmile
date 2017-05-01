# PySmile - Simple Tool to Batch Convert Images

If you are an active blogger or creating lots marketing material, you probably use a huge number of images and photos to keep your audience engaged. If you share on Facebook and Twitter, you may want to have suitable thumbnails. It's a hell lot of work to have so many images and their derivatives. Some common tasks:

* Create a derivative image for Facebook post of size [281x394, 470x235, 470x246](https://blog.bufferapp.com/ideal-image-sizes-social-media-posts), ...
* Generate an image for Twitter post of size [600x335, 800x320](https://business.twitter.com/en/help/campaign-setup/advertiser-card-specifications.html), ...
* Create round, square thumbnails, ...
* Generate images for Facebook Open Graph and Twitter Card

Without simple and affective tools, you won't be able to accomplish those tasks efficiently. I create a too called [**PySmile**](https://github.com/vietlq/PySmile) that does automated conversion for you. The tool is a command line Python script and will add GUI soon.

## Features

* Easy to run with very few input arguments
* Supports multiple output formats: 'PNG', 'GIF', 'JPG', 'JPEG', 'BMP', 'PDF'
* Preserves transparency (PNG => PNG, PNG => GIF)
* Multiple options for resizing: By ratio, fixed width, fixed height
* Takes wildcards for input files
* Specify as many input files as you want
* Non-destructive conversion of transparent PNG to non-transparent PDF, JPEG, BMP, GIF

## Usage

### Convert `*.png` to `pdf`

```
./pysmile.py -i ~/Downloads/*.png -o pdf -d ExportFolder
```

### Resize to 50% and Keep Format

```
./pysmile.py -i ~/images/* -r 50 -d ExportFolder
```

### Resize to Fixed Width 200px and Keep Format

```
./pysmile.py -i ~/images/* --width 200 -d ExportFolder
```

### Resize `secret*.bmp` to Fixed Height 200px to JPEG

```
./pysmile.py -i ~/images/secret*.bmp -o jpeg --height 200 -d ExportFolder
```

### For Detailed Usage

```
usage: pysmile.py [-h] [-r SIZE_RATIO | --width WIDTH | --height HEIGHT]
                  [-d DEST_DIR] [-o OUTPUT_EXT] [-t] [-q]
                  input_pattern [input_pattern ...]

Process images in batches.

positional arguments:
  input_pattern         Look for files that match some pattern. E.g. *.png or
                        pic*cool*

optional arguments:
  -h, --help            show this help message and exit
  -r SIZE_RATIO, --size-ratio SIZE_RATIO
                        Whether to resize, in %
  --width WIDTH         Resize to specified width
  --height HEIGHT       Resize to specified height
  -d DEST_DIR, --dest-dir DEST_DIR
                        Destination directory to writen processed images
  -o OUTPUT_EXT, --output-format OUTPUT_EXT
                        Output format/extension to save all images. If empty,
                        original format of images is preserved. Allowed output
                        extensions: ('png', 'gif', 'jpg', 'jpeg', 'bmp',
                        'pdf')
  -t, --gif-transparency
                        Preserve transparency when converting to GIF. Note:
                        May yield lower quality output.
  -q, --quiet           Convert files without confirmation
```

## References

* [https://python-pillow.org/](https://python-pillow.org/)
* [http://stackoverflow.com/questions/1233772/pil-does-not-save-transparency](http://stackoverflow.com/questions/1233772/pil-does-not-save-transparency)
* [https://www.reddit.com/r/learnpython/comments/4g4dru/error_converting_images_to_pdf/](https://www.reddit.com/r/learnpython/comments/4g4dru/error_converting_images_to_pdf/)
* [http://stackoverflow.com/questions/9166400/convert-rgba-png-to-rgb-with-pil](http://stackoverflow.com/questions/9166400/convert-rgba-png-to-rgb-with-pil)
* [http://www.pythonclub.org/modules/pil/convert-png-gif](http://www.pythonclub.org/modules/pil/convert-png-gif)
* [http://stackoverflow.com/questions/1962795/how-to-get-alpha-value-of-a-png-image-with-pil](http://stackoverflow.com/questions/1962795/how-to-get-alpha-value-of-a-png-image-with-pil)
* [http://stackoverflow.com/questions/2336522/png-vs-gif-vs-jpeg-vs-svg-when-best-to-use](http://stackoverflow.com/questions/2336522/png-vs-gif-vs-jpeg-vs-svg-when-best-to-use)
* [http://stackoverflow.com/questions/5324647/how-to-merge-a-transparent-png-image-with-another-image-using-pil](http://stackoverflow.com/questions/5324647/how-to-merge-a-transparent-png-image-with-another-image-using-pil)
