#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
(SUMMARY)

GUI for NikCut program

:REQUIRES: ImageMagick installed
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

from pylab import *  # IMPORTS NumPy.*, SciPy.*, and matplotlib.*
import os  # os.walk(basedir) FOR GETTING DIR STRUCTURE
#from Tkinter import *
import Tkinter
import tkFileDialog # askopenfilename, asksaveasfilename, askdirectory
from tkSimpleDialog import askstring
from PIL import Image, ImageTk, ImageDraw, ImageChops
#import thread
import time
from collections import namedtuple
import pickle
from display_cv2 import DisplayImage



class NikCut_GUI(Tkinter.Tk):


    def load_settings(self, run_location ):
        try:
            with open( run_location + '\settings.ini', 'r' ) as rfile:
                self.settings = pickle.load(rfile)
            rfile.close()
            print 'Settings loaded'

        except IOError: # If file does not exist
            self.settings = dict( # DEFAULT SETTINGS
                                dir_work=os.getcwd(),
                                mode=0,
                                geometry='1900x1000+0+0',
                                maxWidth = 1900,
                                maxHeight = 1000,
                                tileborder = 1,
                                selectedImage = 0,
                                focalPixel = (0.5,0.5),
                                sobel = False,
                                recent_filenames = [],
                                scale = 1.0,
                                )
            with open( run_location + '\settings.ini', 'w' ) as wfile:
                pickle.dump(self.settings, wfile)
            wfile.close()
            print 'Restored default settings'


    def __init__(self, parent):
        Tkinter.Tk.__init__(self, parent)
        self.parent = parent

        self.initialize()

    def initialize(self):
        self.run_location = os.getcwd()
        self.load_settings( os.getcwd() )

        try:
            os.chdir( self.settings['dir_work'] )
        except WindowsError:
            self.set_work_dir()


        # CREATE THE MENU BAR
        self.create_menu()

        # LEFT HAND SIDE CONTROLS
#        self.create_left_controls()

        # MAIN SCREEN CANVAS BINDINGS
        self.create_image_canvas()

        # WINDOW PLACEMENT ON SCREEN
        try:
            self.geometry( self.settings['geometry'] ) # INITIAL POSITION OF TK WINDOW
        except KeyError:
            self.geometry( self.default_settings['geometry'] ) # INITIAL POSITION OF TK WINDOW

        self.update()
        self.canvas.bind('<Configure>', self.resize )

        # FINISHED GUI SETUP
        self.load_images()

        self.print_settings( 'Settings on initialization' )



    def create_menu(self):
        # MAIN MENU BAR
        menubar = Tkinter.Menu(self)

        # FILE MENU OPTIONS: LOAD, SAVE, EXIT...
        filemenu = Tkinter.Menu(menubar, tearoff=0)
        filemenu.add_command(label="Load image set", command=self.get_filenames)
        filemenu.add_separator()

        ALIGN_MODES = [
                "Align by pixel position",
                "Align by matching"
                ]

        self.rb = Tkinter.StringVar()
        self.rb.set(ALIGN_MODES[1]) # initialize

        for mode in ALIGN_MODES:
            filemenu.add_radiobutton(label=mode, variable=self.rb, value=mode,
                                     command=self.change_click_mode)





        filemenu.add_separator()
        filemenu.add_command(label="Exit", command=self.endsession)
        menubar.add_cascade(label="File", menu=filemenu)

        # HDR MENU OPTIONS
        hdrmenu = Tkinter.Menu(menubar, tearoff=0)
        #TODO: Add HDR options
        menubar.add_cascade(label="HDR", menu=hdrmenu)

        # SFM MENU OPTIONS
        sfmmenu = Tkinter.Menu(menubar, tearoff=0)
        #TODO: Add SFM options
        menubar.add_cascade(label="SFM", menu=sfmmenu)

        # HELP MENU OPTIONS: OPEN LADYBUG API HELP, OPEN WORKING DIRECTORY
        helpmenu = Tkinter.Menu(menubar, tearoff=0)
        helpmenu.add_command(label="About", command=hello)
        helpmenu.add_cascade(label="Open Working Directory", command=self.openWorkingDir)
        menubar.add_cascade(label="Help", menu=helpmenu)

        # SET AND SHOW MENU
        self.config(menu=menubar)



    def create_image_canvas(self):
        self.canvas = Tkinter.Canvas(self, width=self.settings['maxWidth'], height=self.settings['maxHeight'])
        self.canvas.bind("<ButtonPress-1>", self.grab_pt) # DETERMINE NEW POINT OR GRAB EXISTING
        self.canvas.bind("<ButtonRelease-1>", self.endMotion) # FINALIZE BUTTON ACTION
#        self.canvas.bind("<ButtonRelease-3>", self.drawOnCanvas)
        self.canvas.bind("<B1-Motion>", self.shiftImage)
        self.bind("<Key>", self.keypress)
        self.bind("<Delete>", self.deletekey)

        self.canvas.bind_all("<MouseWheel>", self.rollWheel)

        self.canvas.pack(side=Tkinter.RIGHT, expand=Tkinter.YES, fill=Tkinter.BOTH)


    def get_filenames(self):
        """Get a list of jpeg filenames from the user."""
        filenames = tkFileDialog.askopenfilename(multiple=True, filetypes=[("JPEG", ".jpg"),] )

        if filenames:
            if filenames[0] == "{":
                filenames = filenames[1:-1]
            filenames = filenames.split("} {")
            print filenames
            self.settings['filenames'] = filenames

            self.load_images()


    def load_images(self):
        """Load the images from the list of filenames."""
        if len(self.settings['filenames']) > 0:
            self.disp_images = []
            for filename in self.settings['filenames']:
                self.disp_images.append( DisplayImage( filename ) )


        self.show_images()


    def show_images(self):
        """Set up placement of images within the window space. Then crop and
        display the image tiles."""
        maxW = self.settings['maxWidth']
        maxH = self.settings['maxHeight']
        N = len(self.disp_images)

        self.canvas.create_rectangle( (0,0,maxW,maxH),
                                       fill='black'   )



        # Calculate best fit to show largest tiles
        tileW = maxW / N
        tilesPerRow = N
        tileRows = 1
        for i in r_[1:N][::-1]:
            testW = maxW / i
            testR = N / i + (1 if N%i > 0 else 0)
            if testR * testW < maxH and testW > tileW:
                tileW = testW
                tilesPerRow = i
                tileRows = testR
        for i in r_[1:N][::-1]:
            testR = N / i + (1 if N%i > 0 else 0)
            testW = maxH / testR
            if i * testW < maxW and testW > tileW:
                tileW = testW
                tilesPerRow = i
                tileRows = testR

        # Crop, anchor and display each image
        for i, each in enumerate( self.disp_images ):
            # Set the cropping for display
            each.set_box( (int(each.size[0] * self.settings['focalPixel'][0]) + self.settings['tileborder'],
                           int(each.size[1] * self.settings['focalPixel'][1]) + self.settings['tileborder'],
                           int(each.size[0] * self.settings['focalPixel'][0]) + tileW - self.settings['tileborder'],
                           int(each.size[1] * self.settings['focalPixel'][1]) + tileW - self.settings['tileborder']) )
            # Set the anchor position on display
            each.anchor = ((i % tilesPerRow) * tileW + self.settings['tileborder'],
                           tileW * (i / tilesPerRow) + self.settings['tileborder'])

            # Draw a yellow selection box around all selected tiles
            if i == self.settings['selectedImage']:
                self.canvas.create_rectangle( (each.anchor[0] - self.settings['tileborder'],
                                               each.anchor[1] - self.settings['tileborder'],
                                               each.anchor[0]+tileW - self.settings['tileborder'],
                                               each.anchor[1]+tileW - self.settings['tileborder'],  ),
                                               width=4, outline='yellow')

            self.image = each.image(sobel=self.settings['sobel'], scale=self.settings['scale'])
            self.canvas.create_image(each.anchor, image=self.image, anchor=Tkinter.NW, tags='image' )



    def change_mode(self):
        self.get_thumbs()
        self.refresh_display()

    def change_click_mode(self):
        print "i'm in!", self.rb.get()
#        if self.rb.get() == "Window Selection":
#            print "Window Selection"
#        if self.rb.get() == "Heading Selection":
#            print "Heading Selection"
#        if self.rb.get() == "Object Selection":
#            print "Object Selection"
#        if self.rb.get() == "Measure Distance":
#            print "Measure Distance"
#        if self.rb.get() == "Off":
#            print "Off"
#
#        self.refresh_display()

#    def change_view(self, event):
#        self.image_manager()
#        self.get_thumbs()
#        self.refresh_display()



    def resize(self, event):
        self.settings['maxWidth'] = event.width
        self.settings['maxHeight'] = event.height
        self.settings['geometry'] = str(event.width) + 'x' + str(event.height) + '+0+0'
        self.canvas.config(width = event.width, height = event.height)

        self.show_images()



    def grab_pt(self, event):
        if event.widget == self.canvas:
            # GET ASSOCIATED IMAGE
            self.b1press = (event.x, event.y)
            for imN, im in enumerate(self.disp_images):
                if im != None:
                    if im.point( self.b1press ):
                        break
            else:
                return # IF NO ASSOCIATED IMAGE IS FOUND

            self.settings['selectedImage'] = imN


            self.show_images()


    def shiftImage(self, event):
        if event.widget == self.canvas:
            imN = self.settings['selectedImage']
            self.inmotion = True
            im = self.disp_images[imN]

            dx, dy = self.b1press[0] - event.x, self.b1press[1] - event.y
            ox, oy = self.settings['focalPixel']

            self.settings['focalPixel'] = ox + dx / float(im.size[0]), \
                                          oy + dy / float(im.size[1])

            self.b1press = (event.x,event.y)

            self.show_images()



    def endMotion(self, event):
        self.inmotion = False


    def rollWheel(self, event):
#        print event.state
#        self.canvas.delete(Tkinter.ALL)

        # IF WHEEL TURNED, NOT HELD DOWN
        if event.state == 8 or event.state == 10: # 10 is with caps lock
            try:
                if event.delta > 0:
                    self.settings['scale'] += 0.1
                elif event.delta < 0:
                    self.settings['scale'] -= 0.1
            except Warning:
                return

        # IF WHEEL BUTTON DOWN AND TURNED
        if event.state == 520 or event.state == 522:
            pass

        self.show_images()



    def keypress(self, event):
        if event.char == 's':
            self.settings['sobel'] = (False if self.settings['sobel'] else True)

            self.show_images()

    def deletekey(self, event):



    def refresh_display(self):
        #print 'Refreshing'
        self.refreshImage()
        self.display_mask()
        self.get_drawing()
        self.refreshPolygon()
        self.refreshText()

    def display_mask(self):
        if self.rb.get() == "Window Selection":
            if not self.settings.get('subwindows'):
                w,h = self.disp_images[0].size
                self.settings['subwindows'] = \
                    [array([(0,int(h*.3)),(0,int(h*.6)),(w,int(h*.6)),(w,int(h*.3))])
                        for i in range(5)]

            mask = Image.new('RGBA', [int(each) for each in self.geometry().split('+')[0].split('x')])

            alpha = Image.new('L', mask.size, 100)
            draw_alpha = ImageDraw.Draw(alpha)
            for dimage in self.disp_images:
                if dimage == None:
                    break
                cam = dimage.ID % 10
                draw_alpha.polygon([dimage.to_disp_pt(xy) for xy in self.settings['subwindows'][cam]],
                                    fill=0)
            mask.putalpha( alpha )
            self.mask = ImageTk.PhotoImage( mask )
            self.canvas.create_image((0,0), image=self.mask, anchor=Tkinter.NW, tags='image' )
        elif self.rb.get() == "Heading Selection":
            mask = Image.new('RGBA', [int(each) for each in self.geometry().split('+')[0].split('x')])

            alpha = Image.new('L', mask.size, 100)
            draw_alpha = ImageDraw.Draw(alpha)
            for dimage in self.disp_images:
                if dimage == None:
                    break
                cam = dimage.ID % 10
                if self.settings.get('im_forward'):
                    fcam, xpos = self.settings.get('im_forward')
                    if cam == fcam:
                        draw_alpha.polygon([dimage.to_disp_pt((xpos-10,0)),
                                            dimage.to_disp_pt((xpos-10,dimage.size[1])),
                                            dimage.to_disp_pt((xpos+10,dimage.size[1])),
                                            dimage.to_disp_pt((xpos+10,0))],
                                            fill=0)
            mask.putalpha( alpha )
            self.mask = ImageTk.PhotoImage( mask )
            self.canvas.create_image((0,0), image=self.mask, anchor=Tkinter.NW, tags='image' )





    def refreshImage(self):

        mode = self.mode.get()
        self.canvas.delete('image')


        for dimage in self.disp_images[:nImage]:
            if dimage:
                imref = dimage.image()
                self.canvas.create_image(dimage.anchor, image=imref, anchor=Tkinter.NW, tags='image' )











    def get_thumbs(self):
        '''Get set of images from PGRstream based on GUI 'mode'.
        '''
        if self.disp_images[0] != None:
            self.old_image = self.disp_images[0].image(Tk=False)

        imlist = self.disp_images
        imlist[:] = [None for i in xrange(6)]
        try:
            test = self.settings['maxWidth']
            test = self.settings['maxHeight']
        except KeyError:
            self.settings['maxWidth'] = 1000
            self.settings['maxHeight'] = 800



        # 2 CAMERA MODE
        if self.mode.get() == '2 Cameras':
            for i in xrange(2):
                try:
                    imlist[i] = DisplayImage( self.PGRstream.image( (self.camera()+i)%5 ), self.frame()*10+(self.camera()+i)%5,
                                               fit=(self.settings['maxWidth']/2,self.settings['maxHeight'] ) )
                except AttributeError:
                    return False
            # SET POSITIONING OF VIEWS
            imlist[1].anchor = (imlist[0].box_span()[0], 0)
        # 3 CAMERA ROAD VIEW MODE
        if self.mode.get() == 'Road View':
            for i in xrange(3):
                try:
                    imlist[i] = DisplayImage( self.PGRstream.image( (self.camera()+i+4)%5 ),  self.frame()*10+(self.camera()+i+4)%5,
                                               fit=(self.settings['maxWidth'],self.settings['maxHeight']/3 ) )
                    size = imlist[i].size
                    imlist[i].set_box((0,int(size[1]*1/2),size[0],int(size[1]*3.2/4)))
                except AttributeError:
                    return False
            # SET POSITIONING OF VIEWS
            imlist[1].anchor = (0,imlist[0].box_span()[1])
            imlist[2].anchor = (0,imlist[0].box_span()[1]*2)
        # 3 CAMERA MODE
        if self.mode.get() == '3 Cameras':
            for i in xrange(3):
                try:
                    imlist[i] = DisplayImage( self.PGRstream.image( (self.camera()+i+4)%5 ),  self.frame()*10+(self.camera()+i+4)%5,
                                               fit=(self.settings['maxWidth']/3,self.settings['maxHeight'] ) )
                except AttributeError:
                    return False
            # SET POSITIONING OF VIEWS
            imlist[1].anchor = (imlist[0].box_span()[0], 0)
            imlist[2].anchor = (imlist[0].box_span()[0]*2, 0)
        # 1 CAMERA MODE
        if self.mode.get() == '1 CAMERA':
            pass
        # 1 CAMERA 2 TIMES MODE
        if self.mode.get() == '1 CAMERA 2 TIMES':
            pass
        # 2 STREAM MODE
        if self.mode.get() == '2 STREAM':
            pass



    def endsession(self):
        with open( self.run_location + '\settings.ini', 'w' ) as wfile:
            pickle.dump(self.settings, wfile)
        wfile.close()
        self.quit()
    #-----End of ladybug methods







    def sup(self, x):
        if isinstance(x,list):
            for i, each in enumerate(x):
                x[i] = each*1616./self.settings['imagesize'][1]
            return x
        return x*1616./self.settings['imagesize'][1]
    def sdown(self, x):
        if isinstance(x,list):
            for i, each in enumerate(x):
                x[i] = each*self.settings['imagesize'][1]/1616.
            return x
        return x*self.settings['imagesize'][1]/1616.



    def openWorkingDir(self):
        print 'Opening current working directory'
        os.startfile(os.getcwd())

    def set_work_dir(self):
        self.settings['dir_work'] = askdirectory(title='Choose a directory to store all session related files')





    def print_settings(self, string):
        print string + ':'
        for k in self.settings:
            print '\t', k, ':', self.settings[k]






def hello():
    print 'Please assign this option'





if __name__ == '__main__':
    app = NikCut_GUI(None)
    app.title('NikCut')
    app.mainloop()
