#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
(SUMMARY)

(DESCRIPTION)

:REQUIRES: ...
:PRECONDITION: ...
:POSTCONDITION: ...

:AUTHOR: Ripley6811
:ORGANIZATION: National Cheng Kung University, Department of Earth Sciences
:CONTACT: python@boun.cr
:SINCE: Sun Jan 20 11:12:17 2013
:VERSION: 0.1
:STATUS: Nascent
:TODO: ...
"""
#===============================================================================
# PROGRAM METADATA
#===============================================================================
__author__ = 'Ripley6811'
__contact__ = 'python@boun.cr'
__copyright__ = ''
__license__ = ''
__date__ = 'Sun Jan 20 11:12:17 2013'
__version__ = '0.1'

#===============================================================================
# IMPORT STATEMENTS
#===============================================================================
from numpy import *  # IMPORTS ndarray(), arange(), zeros(), ones()
set_printoptions(precision=5)
set_printoptions(suppress=True)
#from visual import *  # IMPORTS NumPy.*, SciPy.*, and Visual objects (sphere, box, etc.)
import matplotlib.pyplot as plt  # plt.plot(x,y)  plt.show()
#from pylab import *  # IMPORTS NumPy.*, SciPy.*, and matplotlib.*
#import os  # os.walk(basedir) FOR GETTING DIR STRUCTURE
#import pickle  # pickle.load(fromfile)  pickle.dump(data, tofile)
from tkFileDialog import askopenfilename, askopenfile
#from collections import namedtuple
#from ctypes import *
#import glob
#import random
import cv2
from display import DisplayImage
import pexif
from PIL import Image
from PIL.ExifTags import TAGS
from scipy import misc


#===============================================================================
# METHODS
#===============================================================================
testim = r"C:\SkyDrive\Photos dated\2013 01 (Jan)\2013-01-05 11.09.42.jpg"
rawim = r"C:\My Box Files\My Pictures\NEF RAW\2013-01-08 09.42.49-1.nef"




#===============================================================================
# MAIN METHOD AND TESTING AREA
#===============================================================================
def main():
    """Description of main()"""
#    with askopenfile('r') as rawfile:
#        print rawfile

    im = cv2.imread(testim)
    mm = fromfile(rawim)
    print type(mm), mm.shape
#    cv2.namedWindow("hi")
#    cv2.imshow("hi", im)
#    plt.imshow(im)
#    plt.show()
    im1 = Image.open(testim)
    print type(im)
    print im1

    print im.size
#    im0 = DisplayImage( ID=testim, image=im )

    info = im1._getexif()
    for tag in info:
#       try:
            print repr(TAGS.get(tag)),
            if repr(TAGS.get(tag)) != repr('ComponentsConfiguration'):
                print 'inner'
                print info.get(tag)
#       except KeyError:
#           print "error", tag

    print "DONE---------------------------------------------------------------"

if __name__ == '__main__':
    main()



#===============================================================================
# QUICK REFERENCE
#===============================================================================
'''
>>PLOTTING

    plt.axis('equal')
    plt.gca().invert_yaxis()
    plt.show()

>>VISUAL PYTHON

    scene = display.get_selected()
    scene.exit = False

>>MATRIX CREATION
    xg, yg = numpy.meshgrid( arange(0,2*pi,.2),arange(0,2*pi,.2) )  # CREATE A PAIR OF 2D ARRAYS

>>BASIC FILE METHODS###
    filename = tkFileDialog.askopenfilename  # GET THE FILENAME STRING FOR SELECTED FILE
    with tkFileDialog.askopenfile('r') as rawfile:  # BEST FILE CHOOSER GUI I KNOW OF
    with open(filename, 'r+') as rawfile:  # BEST WAY TO OPEN A FILE, ENSURES CLOSURE
        for line in rawfile:
            data.append(float(line))
    numpy.loadtxt() # HAVEN'T TRIED THIS YET

>>INDEXING
    mask = where( logical_and(t>10, t10 & t<12 RETURN 1.0, OTHERWISE 0.0 ) )

>>SPYDER Note markers
    #XXX: !
    #TODO: ?
    #FIXME: ?
    #HINT: !
    #TIP: !

>>SPHINX markup
.. warning:: ...

.. note:: ...

.. todo:: ...

'''
