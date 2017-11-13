#!/usr/bin/python3

# correctQCPdb.py
# by Corban Swain
# October 13, 2017

# Script to convert .pdb files output from QChem into the proper PDB
# format. This script shouldn't corrupt .pdb files that are already
# correctly formatted.

from re import compile, sub
from os import path, chdir, makedirs
from glob import glob
from sys import argv, flags

import sys
import getopt
import os

def correctPdbs(directory='.',replace=False,verbose=True,debug=False):

    # Always Show Verbose Output in debug Mode
    if debug: verbose = True

    # Check if Directory is real
    if not os.path.isdir(directory):
        print('ERROR! Not a real directory')
        return
    os.chdir(directory)
    
    # Check for .pdb files within directory
    pdbFileList = glob.glob('*.pdb')
    numFiles = len(pdbFileList)
    if numFiles == 0: 
        print('ERROR! No PDB Files in directory')
        return
        
    # Function to correct the PDB file text
    def fixText(text):
        
        # Regex string that selects for regions (1) directly following
        # a region that begins with ATOM followed by 26 characters,
        # (2) containing three numbers with a decimal point, (3)
        # preceeding a single letter.
        # 
        # The regex has named  groups for the x, y and z coordinates
        # and the trailing space following the coordinates. Use
        # https://regex101.com/ along with a pdb file's text to
        # visualize.
        regex = (r'(?<=ATOM.{26})\s*'
                 '(?P<x>-?\d+\.\d+)\s*'
                 '(?P<y>-?\d+\.\d+)\s*'
                 '(?P<z>-?\d+\.\d+)'
                 '(?P<tail>.*)(?=\w)')
        pattern = re.compile(regex)

        # Replacement function to be used with the re.sub method
        def fixNumberWidth(match):
            # pulling out the text from each group in the regex
            coordGroupKeys = ['x','y','z']
            tail = match.group('tail')
            coords = [float(match.group(key)) for key in coordGroupKeys]
            
            # formatting coordinates to have 3 decimal places and a
            # total length of 8 characters.
            newCoordStrs = ['{:8.3f}'.format(c) for c in coords]
            joinedCoords = ''.join(newCoordStrs)
            
            # calculating the change in length of the coordinate
            # region between the old version and the correctly
            # formated version
            deltaLen = len(match.group(0)) - (len(joinedCoords) + len(tail))
            
            # adding in extra spaces to maintain the position of the
            # element column
            returnStr = joinedCoords + tail + ' ' * deltaLen
            if debug: print(returnStr)
            return returnStr

        return pattern.sub(fixNumberWidth,text)

    if verbose:
        print(' Correcting PDB Files in `{}` '.\
              format(directory).center(70,'*'))

    # either place the correctd files in a new FixedPDBs/ directory or
    # overwrite the original files.
    if replace:
        fixedDir = '.'
    else:
        fixedDir = 'FixedPDBs'
        if not os.path.isdir(fixedDir):
            os.makedirs(fixedDir)
            
    # go through every .pdb file, read it in, and correct it
    for (i,fName) in enumerate(pdbFileList):
        if verbose: print(' Fixing {:3d}/{:3d}:  {:<35} '.\
                          format(i+1,numFiles,fName).center(70,'*'))
        with open(fName,'r') as f:
            original = f.read()

        fixedFName = os.path.join(fixedDir,fName)
        with open(fixedFName,'w') as f:
            f.write(fixText(original))
        if debug: print(' DONE. ')
 
def usage(name):
    sep = os.path.sep
    text = '''Usage: {0} [OPTION]... [PDB DIRECTORY]

Run a script to modify all .pdb files in the specified directory 
so that their x, y, and z coordinates are in the proper format.
This is to correct misformatted .pdb files output from QChem. 

If no directory is passed, the current directory will be used.

Corrected files will be placed in the directory .{1}FixedPDBs if 
the overwrite option is not specified.

Options:

--help, -h       display this help text
--overwrite, -o  overwrite existing .pdb files
--quiet, -q      prevent logs to the console
--debug, -d      print extra debug text to the console while running\n'''
    text = text.format(name,sep)
    return text
       
def main():
    n = len(sys.argv)
    # FIXME - allow arguments to control verbosity, debug, overwrite.
    if n == 1:
        correctPdbs()
    else n == 2:
        directory = sys.argv[-1]
        if os.path.isdir(directory):
            correctPdbs(sys.argv[1])
        else:
            raise NotADirectoryError(
                "Directory should be the last argument."
                "\t'{}' is not a drectory.".format(directory))
            sys.exit(2)
        overwrite = False
        verbose = True
        debug = False
        if sys.flags.debug:
            debug = True
        if sys.flags.quiet:
            verbose = False
        try:
            opts, args = getopt.getopt(sys.argv,
                                       'hoqd',
                                       ['help','overwrite',
                                        'quiet','debug'])
        except: getopt.GetoptError:
            print('Could not parse arguments.')
            sys.exit(2)
        for opt, arg in opts:
            if opt == 'h':
                print(usage(sys.argv[0]))
                sys.exit(0)
        

if __name__ == '__main__':
    main()
