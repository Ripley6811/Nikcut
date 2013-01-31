#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Display image management class (OpenCV version).

This class stores a full-size image and display position. It allows extraction
of a thumbnail of any size, converting points from display location to image
location. Previous version used PIL. This version will rely on OpenCV.


:REQUIRES: ...
:PRECONDITION: ...
:POSTCONDITION: ...

:AUTHOR: Ripley6811
:ORGANIZATION: National Cheng Kung University, Department of Earth Sciences
:CONTACT: python@boun.cr
:SINCE: Thu Jan 31 19:51:08 2013
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
__date__ = 'Thu Jan 31 19:51:08 2013'
__version__ = '0.1'

#===============================================================================
# IMPORT STATEMENTS
#===============================================================================
from PIL import Image, ImageDraw, ImageTk, ImageChops, ImageFilter
from numpy import *  # IMPORTS ndarray(), arange(), zeros(), ones()
import cv2


#===============================================================================
# DISPLAY_IMAGE CLASS
#===============================================================================
class DisplayImage:
    '''Structure for holding an image and info on how it is displayed on screen.
    '''
    def __init__(self, filename, ID=0, anchor=(0,0), scale=1.0, fit=(0,0)):
        '''Accepts PIL image. 'fit' overrides 'scale' if given as a parameter.
        '''
        self.ID = ID
        self.filename = filename
        self.im = cv2.imread(filename) # <type 'numpy.ndarray'>
        y,x,b = self.im.shape
        self.size = x,y
        self.scale = scale
        self.fit = fit # SET THE RETURN SCALING BY THE AREA IT MUST FIT INSIDE
        self.anchor = anchor # WHERE TOPLEFT OF IMAGE WILL BE PLACED IN DISPLAY AREA
        self.cropbox = (0, 0, x, y)

        self.fit_scale() # OVERRIDES SCALE PARAMETER IF FIT IS SET



    def set_box(self, box):
        '''Set the display region of image.

        Arg is a 4-tuple defining the left, upper, right, and lower pixel
        coordinate. Same as in the crop method of PIL Image class.
        '''
#        assert box[0] >=0 and box[1] >= 0
        assert box[2] <= self.size[0] and box[3] <= self.size[1]
        self.cropbox = box
        self.fit_scale()

    def move_box(self, dx, dy):
        a,b,c,d = self.cropbox
        self.cropbox = (a+dx,b+dy,c+dx,d+dy)



    def set_fit(self, dxdy):
        '''Set desired size in pixels of final return image.

        :PARAMETERS:
            *dxdy* --- A tuple giving the desired width and height.

        '''
        assert dxdy[0] > 0 and dxdy[1] > 0
        self.fit = tuple(dxdy)
        self.fit_scale()



    def fit_scale(self):
        if self.fit[0] > 0 and self.fit[1] > 0:
            cropsize = (self.cropbox[2] - self.cropbox[0], self.cropbox[3] - self.cropbox[1])
            self.scale = min(self.fit[0] / float(cropsize[0]), self.fit[1] / float(cropsize[1]))



    def point(self, xy):
        '''Translates the point on display window to pixel coordinate of whole
        image. Returns False if point is not within image.

        This method can be used to test if a clicked point was on this image.
        Can use this method to retrieve the image coordinate of a clicked point.
        '''
        axy = self.anchor
        cxy = (self.cropbox[0] * self.scale, self.cropbox[1] * self.scale)
        boxspan = self.box_span()
        for i in xrange(2):
            if xy[i] < self.anchor[i] or xy[i] > self.anchor[i] + boxspan[i]:
                return False
        # SUBTRACT ANCHOR COORD, REVERSE SCALING, AND ADD CROPPED DISTANCE BACK
        retval = ((xy[0] - axy[0] + cxy[0])/self.scale,
                  (xy[1] - axy[1] + cxy[1])/self.scale )
        return retval



    def box_span(self):
        return (int((self.cropbox[2] - self.cropbox[0])*self.scale),
                int((self.cropbox[3] - self.cropbox[1])*self.scale))



    def image(self, Tk=True, sobel=False, scale=1.0):
        '''Retrieve a copy of the cropped and resized portion of this image.

        Default is to return a Tkinter compatible image.

        @kwarg Tk: True for Tkinter image, False for PIL
        '''
        self.imcopy = self.im.copy()
        if scale != 1.0:
            self.imcopy = cv2.resize(self.im, (0,0), fx=scale, fy=scale)
        x0,y0,x1,y1 = self.cropbox
        self.imcopy = self.imcopy[y0:y1,x0:x1]
#        self.imcopy.thumbnail(tuple([int(each * self.scale) for each in self.size]))
        if sobel:
#            self.imcopy = self.imcopy.filter(ImageFilter.FIND_EDGES)
            self.imcopy = cv2.Sobel(self.imcopy, ddepth=-1, dx=1, dy=1, ksize=5)
        if Tk == True:
            self.imcopy = ImageTk.PhotoImage(Image.fromarray(self.imcopy[:,:,::-1]))
        return self.imcopy


    def to_disp_pt(self, pt):
        '''Scale down and offset image points for display. Image point -> Disp point.

        '''
        axy = self.anchor
        cxy = (self.cropbox[0], self.cropbox[1])
        return (pt[0]*self.scale - cxy[0]*self.scale + axy[0], pt[1]*self.scale - cxy[1]*self.scale + axy[1])


    def get_texture(self, poly, polydest):
        out_texture = self.im.copy()



        out_texture = perspective_transform(out_texture, poly+polydest )

        mask = Image.new('L', out_texture.size, color=0)
        draw = ImageDraw.Draw(mask)
        draw.polygon(polydest, fill=255)
        out_texture.putalpha(mask)


        out_texture = out_texture.crop(self.cropbox)
        out_texture.thumbnail(tuple([int(each * self.scale) for each in self.size]))

        out_texture = ImageTk.PhotoImage(out_texture)
        return out_texture
#        out_texture.show()



