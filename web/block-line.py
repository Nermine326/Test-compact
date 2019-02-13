from Tkinter import *

class Test(Frame):
  

    def createWidgets(self):
        self.QUIT = Button(self, text='QUIT',
                                  background='red',
                                  foreground='white',
                                  height=3,
                                  command=self.quit)
        self.QUIT.pack(side=BOTTOM, fill=BOTH)
        self.EFFACER = Button(self,text='effacer' ,
                                   command=self.effacer)
        self.EFFACER.pack(side=RIGHT,padx=4, pady=4)

        self.canvasObject = Canvas(self, width="5i", height="5i")
        self.canvasObject.pack(side=LEFT)

    def mouseDown(self, event):
        global b1
        b1 = "up" 
        
        self.startx = self.canvasObject.canvasx(event.x)
        self.starty = self.canvasObject.canvasy(event.y)

    def mouseMotion(self, event):
        
        #
        x = self.canvasObject.canvasx(event.x)
        y = self.canvasObject.canvasy(event.y)
        if b1 == "up":
           global startx, starty
           if (self.startx != event.x)  and (self.starty != event.y):
            
               self.rubberbandBox = self.canvasObject.create_rectangle(self.startx, self.starty, x, y)
            
               self.update_idletasks()
          
               self.startx = event.x  
               self.starty = event.y
               
    def mouseUp(self, event):
          
             self.startx = None     
             self.starty = None

    def effacer(self):
            self.canvasObject.delete(ALL)
      

    def __init__(self, master=None):
        Frame.__init__(self, master)
        Pack.config(self)
        self.createWidgets()

       
        self.rubberbandBox = None

        # and the bindings that make it work..
        Widget.bind(self.canvasObject, "<Button-1>", self.mouseDown)
        Widget.bind(self.canvasObject, "<Button1-Motion>", self.mouseMotion)
        Widget.bind(self.canvasObject, "<Button1-ButtonRelease>", self.mouseUp)


test = Test()

test.mainloop()
