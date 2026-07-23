'''
Parse arguments from the command line and return a movie
'''
from optparse import OptionParser
import os
import re
import yaml
import glob

__all__ = ['guess_fps_and_pixelsize']

def parse_filename(filename):
    '''
    Parse file or folder name to extract fps and pixel size.
    Ex: movie_12_fps_1.34_um.avi
    '''
    m = re.search('(\d+(\.\d+)?)[^\d]*fps.*?(\d+(\.\d+)?)[^\d]*um',filename)
    if m is None:
        return None, None
    else:
        fps, pixel_size = m.group(1), m.group(3)
    if fps is not None:
        fps = float(fps)
    if pixel_size is not None:
        pixel_size = float(pixel_size)
    return fps, pixel_size

def guess_fps_and_pixelsize(path=None):
    '''
    Look for FPS and pixel size in order in:
    - in the filename given as first argument
    - in the path
    - in a yaml file in the path or in its parents directory
    - the command line (arguments)
    '''
    fps, pixel_size = None, None

    ## Get command line arguments
    parser = OptionParser()
    parser.add_option('--fps', dest='fps', help='frame rate (Hz)', default=None)
    parser.add_option('--framerate', dest='fps', help='frame rate (Hz)', default=None)
    parser.add_option('--pixelsize', dest='pixel_size', help='pixel size (um)', default=None)
    parser.add_option('--pixel_size', dest='pixel_size', help='pixel size (um)', default=None)
    (options, args) = parser.parse_args()

    # First argument
    if len(args)>0:
        fps, pixel_size = parse_filename(args[0])

    # Path, if given
    if path is not None:
        fps_path, pixel_size_path = parse_filename(path)
        fps = fps or fps_path
        pixel_size = pixel_size or pixel_size_path

        # Look in a yaml file
        if (fps is None) or (pixel_size is None):
            if not os.path.isdir(path):
                path = os.path.dirname(path) # in the directory of the path
            description_files = glob.glob(os.path.join(path, '*.yaml'))
            # Parent directory
            path = os.path.dirname(path)
            description_files += glob.glob(os.path.join(path, '*.yaml'))
            for description_file in description_files:
                with open(description_file) as f:
                    d = yaml.safe_load(f)
                    try:
                        fps = fps or d.get('framerate') or d.get('fps')
                        if "scaled" in d:
                            pixel_size = 1 # It's already scaled
                        else:
                            pixel_size = pixel_size or d.get('pixel_size') or d.get('pixelsize') or d.get('pixel_width')
                    except:
                        pass

    # Arguments
    if options.fps is not None:
        fps = fps or float(options.fps)
    if options.pixel_size is not None:
        pixel_size = pixel_size or float(options.pixel_size)

    return fps, pixel_size

if __name__ == '__main__':
    print(guess_fps_and_pixelsize('movie_12_fps_1.34_um.avi'))
    print(guess_fps_and_pixelsize())
