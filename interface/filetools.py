'''
File management tools
'''
from glob import glob
import os

__all__ = ['most_recent_file', 'file_increment']

def most_recent_file(path):
    # Returns the most recent file in the path
    path = os.path.expanduser(path)
    dated_files = [(os.path.getmtime(file),file) for file in glob(path + '/*')]
    return sorted(dated_files)[-1][1]

def file_increment(path):
    # Adds a number to the filename in case it already exists
    name, ext = os.path.splitext(path)
    if os.path.exists(name+ext):
        i = 2
        while os.path.exists(name + str(i) + ext):
            i += 1
        return name + str(i) + ext
    else:
        return path

