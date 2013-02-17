#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
(SUMMARY)

GUI for NikCut program

:REQUIRES: ImageMagick-6.8 installed
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
#import time
#from collections import namedtuple
import pickle
from display_cv2 import DisplayImage



class NikCut_GUI(Tkinter.Tk):


    def load_settings(self, run_location ):
        try:
            with open( run_location + '\settings.ini', 'r' ) as rfile:
                self.dat = pickle.load(rfile)
            rfile.close()
            print 'Settings loaded'

        except IOError: # If file does not exist
            self.dat = dict( # DEFAULT SETTINGS
                                dir_work=os.getcwd(),
                                curr_jpg_dir = u'C:/',
                                curr_nef_dir = u'C:/',
                                number_of_tiles = 3,
                                mode=0,
                                geometry='1900x1000+0+0',
                                maxWidth = 1900,
                                maxHeight = 1000,
                                tileborder = 1,
                                main_zoom = 0,
                                selectedImage = [0],
                                focalPixel = (0.5,0.5),
                                sobel = False,
                                filenames = [],
                                scale = 1.0,
                                )
            with open( run_location + '\settings.ini', 'w' ) as wfile:
                pickle.dump(self.dat, wfile)
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
            os.chdir( self.dat['dir_work'] )
        except WindowsError:
            self.set_work_dir()


        # CREATE THE MENU BAR
        self.create_menu()
        self.create_top_controls()

        # LEFT HAND SIDE CONTROLS
#        self.create_left_controls()

        # MAIN SCREEN CANVAS BINDINGS
        self.create_image_canvas()

        # WINDOW PLACEMENT ON SCREEN
        try:
            self.geometry( self.dat['geometry'] ) # INITIAL POSITION OF TK WINDOW
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


    def create_top_controls(self):
        '''Show the location of the working jpg and nef directories.

        Two text buttons that show and change the working directories.
        Program will search for NEF in both locations.
        One button for auto-move NEFs from JPG folder to NEF folder if found.
        or just put option in menu bar and set default for 'on'.
        '''

        address_bar = Tkinter.Frame(self)
        address_bar_jpg_line = Tkinter.Frame(address_bar)
        address_bar_nef_line = Tkinter.Frame(address_bar)

        self.jpg_dir = Tkinter.StringVar()
        self.jpg_dir.set(self.dat.get('curr_jpg_dir') )
        self.nef_dir = Tkinter.StringVar()
        self.nef_dir.set(self.dat.get('curr_nef_dir') )

        Tkinter.Label(address_bar_jpg_line, text='JPG Dir').pack(side=Tkinter.LEFT,padx=0,pady=0)
        jpg_dir = Tkinter.Button(address_bar_jpg_line,
                                 textvariable=self.jpg_dir,
                                 command=self.set_new_jpg_dir)
        jpg_dir.pack(side=Tkinter.LEFT,padx=0,pady=0, fill='x')

        Tkinter.Label(address_bar_nef_line, text='NEF Dir').pack(side=Tkinter.LEFT,padx=0,pady=0)
        nef_dir = Tkinter.Button(address_bar_nef_line,
                                 textvariable=self.nef_dir,
                                 command=self.set_new_nef_dir)
        nef_dir.pack(side=Tkinter.LEFT,padx=0,pady=0)

        address_bar_jpg_line.pack(side=Tkinter.LEFT)
        address_bar_nef_line.pack(side=Tkinter.LEFT)
        address_bar.pack(side=Tkinter.TOP)


#    def create_left_controls(self):
#        controls = Tkinter.Frame(self)
#
#
#        self.rb = Tkinter.StringVar()
#        self.rb.set("L") # initialize
#
#        for mode in MODES:
#            b = Tkinter.Radiobutton(controls, text=mode,
#                            variable=self.rb, value=mode, command=self.change_click_mode)
#            b.pack(anchor=Tkinter.W)
#            b.select()
#
#
#        Tkinter.Label(controls, text='Image Number').pack(side=Tkinter.TOP,padx=10,pady=10)
#        self.imNumStrVar = Tkinter.StringVar()
#        self.imNumStrVar.set(self.dat.get('imNumStrVar') )
#        imNumEntry = Tkinter.Entry(controls, textvariable=self.imNumStrVar, width=10)
#        imNumEntry.pack(side=Tkinter.TOP,padx=10,pady=10)
#        imNumEntry.bind('<Return>', self.change_view)
#
#        self.totalStrVar = Tkinter.StringVar()
#        self.totalStrVar.set(self.dat.get('totalStrVar') )
#        Tkinter.Label(controls, textvariable=self.totalStrVar).pack(side=Tkinter.TOP,padx=10,pady=10)
#
#        Tkinter.Label(controls, text='Camera Number').pack(side=Tkinter.TOP,padx=10,pady=10)
#        self.camNumStrVar = Tkinter.StringVar()
#        self.camNumStrVar.set(self.dat.get('camNumStrVar') )
#        camNumEntry = Tkinter.Entry(controls, textvariable=self.camNumStrVar, width=10)
#        camNumEntry.pack(side=Tkinter.TOP,padx=10,pady=10)
#        camNumEntry.bind('<Return>', self.change_view)
#
#        makePanButton = Tkinter.Button(controls, text='Save Panorama', command=self.save_panorama)
#        makePanButton.pack(side=Tkinter.TOP,padx=10,pady=10)
#
#        state = Tkinter.NORMAL if self.dat.get('panorama_forward') else Tkinter.DISABLED
#        state = Tkinter.NORMAL
#        self.estVidButton = Tkinter.Button(controls, text='Estimate video motion', command=self.estimate_motion, state=state)
#        self.estVidButton.pack(side=Tkinter.TOP,padx=10,pady=10)
#
#        self.forwardStrVar = Tkinter.StringVar()
#        cfor = str(self.dat.get('im_forward')) if self.dat.get('im_forward') else ''
#        pfor = str(self.dat.get('panorama_forward')) if self.dat.get('panorama_forward') else ''
#        self.forwardStrVar.set( cfor + ' ' + pfor )
#        Tkinter.Label(controls, textvariable=self.forwardStrVar).pack(side=Tkinter.TOP,padx=10,pady=10)
#
#        self.testButton = Tkinter.Button(controls, text='Test func', command=self.test)
#        self.testButton.pack(side=Tkinter.TOP,padx=10,pady=10)
#
#
#        controls.pack(side=Tkinter.LEFT)



    def create_image_canvas(self):
        self.canvas = Tkinter.Canvas(self, width=self.dat['maxWidth'], height=self.dat['maxHeight'], bg='black')
        self.canvas.bind("<ButtonPress-1>", self.grab_pt) # DETERMINE NEW POINT OR GRAB EXISTING
        self.canvas.bind("<ButtonRelease-1>", self.endMotion) # FINALIZE BUTTON ACTION
#        self.canvas.bind("<ButtonRelease-3>", self.drawOnCanvas)
        self.canvas.bind("<B1-Motion>", self.shiftImage)
        self.bind("<Key>", self.keypress)
        self.bind("<Delete>", self.deletekey)
        self.bind("<Escape>", self.endsession)
        self.bind("<Left>", self.prev_image)
        self.bind("<Right>", self.next_image)

        self.canvas.bind_all("<MouseWheel>", self.rollWheel)
        self.canvas.bind_all("<Up>", self.rollWheel)
        self.canvas.bind_all("<Down>", self.rollWheel)

        self.canvas.pack(side=Tkinter.RIGHT, expand=Tkinter.YES, fill=Tkinter.BOTH)



    def get_filenames(self, filename=''):
        """Get a list of jpeg filenames from the user."""
        if not filename:
            filename = tkFileDialog.askopenfilename( filetypes=[("JPEG", ".jpg"),] )
        if not filename.lower().endswith('jpg'):
            return False

        curr_path, curr_file = os.path.split(filename)

        self.jpg_list = []
        self.nef_list = []
        for each in os.listdir(curr_path):
            if each.lower().endswith('jpg'):
                self.jpg_list.append(each.lower())
            elif each.lower().endswith('nef'):
                self.nef_list.append(each.lower())

        self.jpg_list.sort()

        self.set_new_jpg_dir( curr_path )
        self.load_images(curr_file)



    def load_images(self, curr_file=''):
        """Load the images from the list of filenames."""
        if not curr_file:
            self.get_filenames()
            return

        curr_index = self.jpg_list.index( curr_file )
        self.disp_images = []

        if curr_index == 0:
            self.disp_images.append( None )
        else:
            self.disp_images.append( DisplayImage( self.jpg_dir.get() + '/' + self.jpg_list[curr_index-1] ) )

        self.disp_images.append( DisplayImage( self.jpg_dir.get() + '/' + self.jpg_list[curr_index] ) )

        if curr_index == len(self.jpg_list) - 1:
            self.disp_images.append( None )
        else:
            self.disp_images.append( DisplayImage( self.jpg_dir.get() + '/' + self.jpg_list[curr_index+1] ) )



        self.set_tile_positions()
        self.show_images()



    def set_tile_positions(self):
        """Sets up placement of images within the window space."""
        try:
            nTiles = self.dat['number_of_tiles']
        except:
            nTiles = self.dat['number_of_tiles'] = 3
        maxW = self.dat['maxWidth']
        tileW = maxW / nTiles
        tileH = self.dat['maxHeight']
        self.tileSize = tileW, tileH


#        N = len(self.disp_images)
#
#        self.tileW, tilesPerRow = self.calc_tile_fit()
        self.tiles = []
        for i in range(nTiles):
            self.tiles.append( (i * tileW, 0, i * tileW + tileW, tileH ) )
            if self.disp_images[i]:
                self.disp_images[i].set_thumbnail( (tileW-2,tileH-2), self.dat['main_zoom'] )




    def set_new_jpg_dir(self, new_dir=''):
        if not new_dir:
            new_dir = tkFileDialog.askdirectory(initialdir=self.jpg_dir.get())
        if new_dir:
            print repr(new_dir)
            self.jpg_dir.set(new_dir)
            self.dat['curr_jpg_dir'] = new_dir



    def set_new_nef_dir(self, new_dir=''):
        if not new_dir:
            new_dir = tkFileDialog.askdirectory(initialdir=self.nef_dir.get())
        if new_dir:
            print repr(new_dir)
            self.nef_dir.set(new_dir)
            self.dat['curr_nef_dir'] = new_dir






    def show_images(self):
        """Then crop and display the images in the tiles."""

        self.canvas.delete('text')
        self.canvas.delete('thumbnail')



        # Crop, anchor and display each image
        for tile, dimage in zip( self.tiles, self.disp_images ):
            if not dimage:
                continue

            tx,ty = tile[:2]
            self.canvas.create_image( (tx+1,ty+1), image=dimage.thumbnail, anchor=Tkinter.NW, tags='thumbnail')


            # Overlay info and icons
            head, tail = os.path.split( dimage.filename )
            self.canvas.create_rectangle( (tx+4, tile[3]-206, tx+204, tile[3]-4),
                                         fill="black")
            if (os.path.isfile( self.dat['curr_jpg_dir'] + '/' + tail[:-4] + '.nef' )
              or os.path.isfile( self.dat['curr_nef_dir'] + '/' + tail[:-4] + '.nef' ) ):
                self.canvas.create_text( (tx+5,tile[3]-190), text='NEF available', anchor=Tkinter.NW,
                                     fill='yellow', tags='text')
            else:
                self.canvas.create_text( (tx+5,tile[3]-190), text='NEF not found', anchor=Tkinter.NW,
                                     fill='grey', tags='text')
            self.canvas.create_text( (tx+5,tile[3]-205), text=tail, anchor=Tkinter.NW,
                                     fill='yellow', tags='text')
            self.canvas.create_text( (tx+5,tile[3]-175), text=str(int(dimage.scale*100))+'%', anchor=Tkinter.NW,
                                     fill='yellow', tags='text')
            for i, each in enumerate(dimage.get_exif()):
                self.canvas.create_text( (tx+5,tile[3]-150+i*15), text=each, anchor=Tkinter.NW,
                                     fill='yellow', tags='text')
            print dimage.get_histogram()



    def show_zoom(self):
            image = dimage.image(sobel=self.dat['sobel'])
            self.canvas.create_image( tile[:2], image=image, anchor=Tkinter.NW, tags='image' )




    def highlight_selected_tiles(self):
        self.canvas.delete('selected')

        for i, each in enumerate( self.disp_images ):

            # Draw a yellow selection box around all selected tiles
            if i in self.dat['selectedImage']:
                self.canvas.create_rectangle( (each.anchor[0] - self.dat['tileborder'],
                                               each.anchor[1] - self.dat['tileborder'],
                                               each.anchor[0]+self.tileW - self.dat['tileborder'],
                                               each.anchor[1]+self.tileW - self.dat['tileborder'],  ),
                                               width=4, outline='yellow', tags='selected')


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
        self.dat['maxWidth'] = event.width
        self.dat['maxHeight'] = event.height
        self.dat['geometry'] = str(event.width) + 'x' + str(event.height) + '+0+0'
        self.canvas.config(width = event.width, height = event.height)



        self.set_tile_positions()
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

            self.dat['selectedImage'] = [imN]


            self.show_images()


    def shiftImage(self, event):
        if event.widget == self.canvas:
            imN = self.dat['selectedImage']
            self.inmotion = True
            im = self.disp_images[imN[0]]

            dx, dy = self.b1press[0] - event.x, self.b1press[1] - event.y
            ox, oy = self.dat['focalPixel']

            x = ox + dx / float(im.size[0])
            y = oy + dy / float(im.size[1])

            print x, y
            if x < 0: x = 0
            if x > 1: x = 1
            if y < 0: y = 0
            if y > 1: y = 1

            self.dat['focalPixel'] = x,y


            self.b1press = (event.x,event.y)

            self.show_images()



    def endMotion(self, event):
        self.inmotion = False


    def rollWheel(self, event):
#        print event.state
#        self.canvas.delete(Tkinter.ALL)

        # IF WHEEL TURNED, NOT HELD DOWN
        if event.state == 8 or event.state == 10: # 10 is with caps lock

            # Switch main image size from full image fit to fitting the height of canvas
            try:
                if event.delta > 0:
                    self.prev_image(event)
                elif event.delta < 0:
                    self.next_image(event)
            except Warning:
                return

        # IF WHEEL BUTTON DOWN AND TURNED
        else:# event.state == 520 or event.state == 522:

            self.dat['main_zoom'] = (self.dat['main_zoom'] + 1) % 3

            self.set_tile_positions()
            self.show_images()



    def keypress(self, event):
        if event.char == 's':
            self.dat['sobel'] = (False if self.dat['sobel'] else True)

            self.show_images()

        if event.char == '1':
            self.dat['number_of_tiles'] = 1
            self.set_tile_positions()
            self.show_images()

        if event.char == '2':
            self.dat['number_of_tiles'] = 2
            self.set_tile_positions()
            self.show_images()

        if event.char == '3':
            self.dat['number_of_tiles'] = 3
            self.set_tile_positions()
            self.show_images()


    def next_image(self, event):
        try:
            head, tail = os.path.split( self.disp_images[2].filename )
        except:
            return


        i = self.jpg_list.index( tail )



        self.disp_images[0] = self.disp_images[1]
        self.disp_images[1] = self.disp_images[2]

        if i+1 < len(self.jpg_list):
            self.disp_images[2] = DisplayImage( self.jpg_dir.get() + '/' + self.jpg_list[i+1] )
        else:
            self.disp_images[2] = None



        self.set_tile_positions()
        self.show_images()



    def prev_image(self, event):
        try:
            head, tail = os.path.split( self.disp_images[0].filename )
        except:
            return


        i = self.jpg_list.index( tail )



        self.disp_images[2] = self.disp_images[1]
        self.disp_images[1] = self.disp_images[0]

        if i-1 >= 0:
            self.disp_images[0] = DisplayImage( self.jpg_dir.get() + '/' + self.jpg_list[i-1] )
        else:
            self.disp_images[0] = None



        self.set_tile_positions()
        self.show_images()



    def deletekey(self, event):
        if self.disp_images[1]:
            if self.dat['number_of_tiles'] == 3:
                head, tail = os.path.split( self.disp_images[1].filename )
            else:
                head, tail = os.path.split( self.disp_images[0].filename )



            print 'Deleting', head + '/' + tail
            os.remove( self.jpg_dir.get() + '/' + tail )

            # Find NEF in jpg or nef directory and delete it
            del_nef = self.jpg_dir.get() + '/' + tail[:-4] + '.nef'
            if os.path.isfile( del_nef ):
                print 'Deleting', del_nef
                os.remove( del_nef )

            del_nef = self.nef_dir.get() + '/' + tail[:-4] + '.nef'
            if os.path.isfile( del_nef ):
                print 'Deleting', del_nef
                os.remove( del_nef )

            i = self.jpg_list.index(tail)
            self.jpg_list.pop( i )
            if i < len(self.jpg_list):
                self.load_images( self.jpg_list[i] )
            else:
                self.load_images( self.jpg_list[i-1] )


    def refresh_display(self):
        #print 'Refreshing'
        self.refreshImage()
        self.display_mask()
        self.get_drawing()
        self.refreshPolygon()
        self.refreshText()

    def display_mask(self):
        if self.rb.get() == "Window Selection":
            if not self.dat.get('subwindows'):
                w,h = self.disp_images[0].size
                self.dat['subwindows'] = \
                    [array([(0,int(h*.3)),(0,int(h*.6)),(w,int(h*.6)),(w,int(h*.3))])
                        for i in range(5)]

            mask = Image.new('RGBA', [int(each) for each in self.geometry().split('+')[0].split('x')])

            alpha = Image.new('L', mask.size, 100)
            draw_alpha = ImageDraw.Draw(alpha)
            for dimage in self.disp_images:
                if dimage == None:
                    break
                cam = dimage.ID % 10
                draw_alpha.polygon([dimage.to_disp_pt(xy) for xy in self.dat['subwindows'][cam]],
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
                if self.dat.get('im_forward'):
                    fcam, xpos = self.dat.get('im_forward')
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
        self.canvas.delete('image')


        for dimage in self.disp_images[:nImage]:
            if dimage:
                imref = dimage.image()
                self.canvas.create_image(dimage.anchor, image=imref, anchor=Tkinter.NW, tags='image' )









    def endsession(self):
        with open( self.run_location + '\settings.ini', 'w' ) as wfile:
            pickle.dump(self.dat, wfile)
        wfile.close()
        self.quit()
    #-----End of ladybug methods







    def sup(self, x):
        if isinstance(x,list):
            for i, each in enumerate(x):
                x[i] = each*1616./self.dat['imagesize'][1]
            return x
        return x*1616./self.dat['imagesize'][1]
    def sdown(self, x):
        if isinstance(x,list):
            for i, each in enumerate(x):
                x[i] = each*self.dat['imagesize'][1]/1616.
            return x
        return x*self.dat['imagesize'][1]/1616.



    def openWorkingDir(self):
        print 'Opening current working directory'
        os.startfile(os.getcwd())

    def set_work_dir(self):
        self.dat['dir_work'] = askdirectory(title='Choose a directory to store all session related files')





    def print_settings(self, string):
        print string + ':'
        for k in self.dat:
            print '\t', k, ':', self.dat[k]






def hello():
    print 'Please assign this option'





if __name__ == '__main__':
    app = NikCut_GUI(None)
    app.title('NikCut')
    app.mainloop()
