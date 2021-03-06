#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Display image management class.

This class stores a full-size image and display position. It allows extraction
of a thumbnail of any size, converting points from display location to image
location. Went from PIL to trying OpenCV, but I get images displayed faster
in Tkinter with PIL.


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
from PIL import Image, ImageDraw, ImageTk, ExifTags, ImageFilter
from numpy import *  # IMPORTS ndarray(), arange(), zeros(), ones()
import cv2
import os


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
        self.im = Image.open(filename) # <type 'numpy.ndarray'>
#        print os.getcwd()
#        print filename, self.im
#        y,x,b =
        self.size = self.im.size
        self.scale = scale
        self.fit = fit # SET THE RETURN SCALING BY THE AREA IT MUST FIT INSIDE
        self.anchor = anchor # WHERE TOPLEFT OF IMAGE WILL BE PLACED IN DISPLAY AREA
        self.cropbox = (0, 0, self.size[0], self.size[1])

        self.fit_scale() # OVERRIDES SCALE PARAMETER IF FIT IS SET

        self.thumbnail = None
        self.focus = (self.size[0]/2,self.size[1]/2)

        self.exif = dict()
        info = self.im._getexif()
        for tag in info:
            self.exif[ExifTags.TAGS.get(tag)] = info.get(tag)



    def set_box(self, box, pixel):
        '''Set the display region of image.

        Arg is a 4-tuple defining the left, upper, right, and lower pixel
        coordinate. Same as in the crop method of PIL Image class.
        '''
        newbox = list(box)
        print box
        boxW = box[2] - box[0]
        if box[0] < 0:
            newbox[0] -= box[0]
            newbox[2] -= box[0]
        if box[1] < 0:
            newbox[1] -= box[1]
            newbox[3] -= box[1]
        if box[2] > self.size[0] - boxW:
            newbox[0] -= box[2] - self.size[0] - boxW
            newbox[2] -= box[2] - self.size[0] - boxW
        if box[3] > self.size[1] - boxW:
            newbox[1] -= box[3] - self.size[1] - boxW
            newbox[3] -= box[3] - self.size[1] - boxW

        self.cropbox = newbox
        self.fit_scale()



    def move_box(self, dx, dy):
        a,b,c,d = self.cropbox
        self.cropbox = (a+dx,b+dy,c+dx,d+dy)



    def set_fit(self, dxdy, zoom=False):
        '''Set desired size in pixels of final return image.

        :PARAMETERS:
            *dxdy* --- A tuple giving the desired width and height.

        '''
        assert dxdy[0] > 0 and dxdy[1] > 0
        self.fit = tuple(dxdy)
        if zoom:
            self.fit = 10000,dxdy[1]
        self.fit_scale()



    def fit_scale(self):
        if self.fit[0] > 0 and self.fit[1] > 0:
            cropsize = (self.cropbox[2] - self.cropbox[0], self.cropbox[3] - self.cropbox[1])
            self.scale = min(self.fit[0] / float(cropsize[0]), self.fit[1] / float(cropsize[1]))


    def set_thumbnail(self, tsize, zoom=False):
        self.thumbnail = self.im.copy()
        if zoom:
            scale = max(tsize[0]/float(self.size[0]),tsize[1]/float(self.size[1]))
            self.thumbnail = self.im.resize( tuple( int(x * scale) for x in self.size) )
            yoffset = (self.thumbnail.size[0] - tsize[0]) / 2
            xoffset = (self.thumbnail.size[1] - tsize[1]) / 2
            self.thumbnail = self.thumbnail.crop( (yoffset,
                                                   xoffset,
                                                   self.thumbnail.size[0]-yoffset,
                                                   self.thumbnail.size[1]-xoffset ) )
            self.thumbnail = ImageTk.PhotoImage( self.thumbnail )
        else:
            scale = min(tsize[0]/float(self.size[0]),tsize[1]/float(self.size[1]))

            self.thumbnail = self.im.resize( tuple( int(x * scale) for x in self.size) )
            self.thumbnail = ImageTk.PhotoImage( self.thumbnail )
        self.scale = scale


    def get_exif(self):
        exifsubset = []

        model = self.exif.get('Model')
        if model:
            exifsubset.append( 'Model: ' + model )
        extime = self.exif.get('ExposureTime')
        if extime:
            exifsubset.append( 'Exposure: ' + str( extime[0]/float(extime[1])) + '(1/'+str(extime[1]/extime[0]) + ')' )
        aperture = self.exif.get('FNumber')
        if aperture:
            exifsubset.append( 'Aperture: f/' + str( aperture[0]/float(aperture[1]) ) )
        flen = self.exif.get('FocalLength')
        if flen:
            exifsubset.append( 'FocalLength: ' + str( flen[0]/float(flen[1]))  + 'mm' )
        iso = self.exif.get('ISOSpeedRatings')
        if iso:
            exifsubset.append( 'ISO speed: ' + str( iso ) )

        return exifsubset



    def get_histogram(self):
        return self.im.histogram()


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



    def image(self, Tk=True, sobel=False):
        '''Retrieve a copy of the cropped and resized portion of this image.

        Default is to return a Tkinter compatible image.

        @kwarg Tk: True for Tkinter image, False for PIL
        '''
        self.imcopy = self.im.copy()
        if self.scale != 1.0:
            self.imcopy = cv2.resize(self.im, (0,0), fx=self.scale, fy=self.scale)
        x0,y0,x1,y1 = self.cropbox
        dx = (x1-x0)/2
        dy = (y1-y0)/2
        fx, fy = self.focus
        print 'crop', fy-dy,fy+dy,fx-dx,fx+dx
        self.imcopy = self.imcopy[fy-dy:fy+dy,fx-dx:fx+dx]
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



