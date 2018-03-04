#!/usr/bin/env python3
# -*- coding: utf8 -*-

#from gpiozero import LED
import RPi.GPIO as GPIO
import sys, MFRC522, MySQLdb, datetime
from time import sleep
from _thread import start_new_thread
from classes import Led, Servo, DataBase

if sys.version_info[0] == 2:  
    from Tkinter import *
else:
    from tkinter import *
from PIL import Image, ImageTk

GPIO.setmode(GPIO.BCM)


green = Led(17)
orange = Led(27)
red = Led(4)
servo = Servo(2)

continue_reading = True
top = None
window = None


db = DataBase()        
        
# --------------------------------------------------- #

class Fullscreen_Window(Tk):

    def __init__(self):
        Tk.__init__(self)
        self.attributes('-zoomed', True)  # This just maximizes it so we can see the window. It's nothing to do with fullscreen.
        self.frame = Frame(self)
        self.frame.pack()
        self.configure(background='#006080')

        # iset logo
        self.l = ImageTk.PhotoImage(Image.open("/var/www/flask/accessControl/static/imgs/logo.jpg"))
        self.logo = Label(self, image=self.l, background="#006080")
        self.logo.pack(side="top")
        #self.logo.place(x=8, y=12)

        # scan logo
        self.sl = ImageTk.PhotoImage(Image.open("/var/www/flask/accessControl/static/imgs/scan.png").resize((400, 300), Image.ANTIALIAS))
        self.scan_logo = Label(self, image=self.sl, background="#006080")
        self.scan_logo.pack()
        self.scan_logo.place(x=430, y=210)

        # developer text
        self.add = Label(self, text="developed by @medyas", font=('courier' , 16 ), background='#006080', anchor='center', height=2, width=33, fg="#4ddbff").pack(side="bottom")
        
        self.state = False
        self.toggle_fullscreen()
        self.bind("<F11>", self.toggle_fullscreen)
        self.bind("<Escape>", self.end_fullscreen)
        self.bind("<q>", self.exit)

    def exit(self, e):
        global db
        db.close()
        GPIO.cleanup() 
        self.destroy()
        
    def toggle_fullscreen(self, event=None):
        self.state = not self.state  # Just toggling the boolean
        self.attributes("-fullscreen", self.state)
        return "break"

    def end_fullscreen(self, event=None):
        self.state = False
        self.attributes("-fullscreen", False)
        return "break"

# --------------------------------------------------- #


class window(Toplevel):

    def __init__(self, root):
        Toplevel.__init__(self, root)
        self.title("Card UID")
        self.resizable(width=False, height=False)
        self.geometry('{}x{}+{}+{}'.format(650, 200, 50, 100))
        self.configure(background='#008080')
        self.overrideredirect(1)
        
        self.img = ImageTk.PhotoImage(Image.open("/var/www/flask/accessControl/static/imgs/user.png").resize((175, 175), Image.ANTIALIAS))
        self.image = Label(self, image=self.img, background="#008080")
        self.image.pack(side="left")
        self.image.place(x=8, y=12)

        # setting up the name
        self.n = StringVar()
        self.name = Label(self, textvariable=self.n, font=('arial', 12, 'bold', 'italic'), anchor='sw', padx=3, height=2, width=50, fg="#66ccff", background="#008080")
        self.name.pack()
        self.name.place(x=190, y=42)

        # setting up the address
        self.a = StringVar()
        self.add = Label(self, textvariable=self.a, font=('arial', 12 ), anchor='sw', background="#008080", height=2, width=50, fg="#b3e6ff", padx=3)
        self.add.pack()
        self.add.place(x=190, y=80)

        # setting up the id
        self.i = StringVar()
        self.uid = Label(self, textvariable=self.i, font=('arial', 12 ), anchor='sw', background="#008080", height=2, width=50, fg="white", padx=3)
        self.uid.pack()
        self.uid.place(x=190, y=115)

        # setting up the block message
        self.b = StringVar()
        self.block = Label(self, textvariable=self.b, font=('Times', 10, 'bold'), anchor='sw', background="#008080", height=2, width=150, fg="#660000", padx=3)
        self.block.pack()
        self.block.place(x=190, y=150)
        self.b.set("you dont have access to this facility!")

        # hide the window
        self.withdraw()
        
    def setData(self, name, address, uid, path, block):
        self.img= ImageTk.PhotoImage(Image.open(path).resize((175, 175), Image.ANTIALIAS))
        self.image.config(image=self.img)

        self.n.set("Name:\t"+name)
        self.a.set("Address: "+address)
        self.i.set("N."+str(uid))
        self.b.set(block)



# --------------------------------------------------- #


# Create an object of the class MFRC522
MIFAREReader = MFRC522.MFRC522()


# --------------------------------------------------- #

def readRFID():
    global top, db
    
    # This loop keeps checking for chips. If one is near it will get the UID and authenticate
    while continue_reading:
        orange.on()
        
        # Scan for cards    
        (status,TagType) = MIFAREReader.MFRC522_Request(MIFAREReader.PICC_REQIDL)

            
        # Get the UID of the card
        (status,uid) = MIFAREReader.MFRC522_Anticoll()

        # If we have the UID, continue
        if status == MIFAREReader.MI_OK:
            uid = str(uid[0])+str(uid[1])+str(uid[2])+str(uid[3])
            status, d = db.checkUID(uid)
            orange.off()
            block = ''
            if(status):
                data = d[0]
                name = str(data[1]+", "+data[2])
                status, start, end = db.check_block(data[0])
                if(status):
                    red.on()
                    block = "Your access has been block from: "+start+" To "+end
                    top.setData(name, data[3], data[0], data[5], block)
                    top.deiconify()
                    sleep(2)
                    top.withdraw()
                    red.off()
                else:
                    green.on()
                    block = ""
                    top.setData(name, data[3], data[0], data[5], block)
                    top.deiconify()
                    servo.setOpen()
                    db.setLogin(data[0])
                    sleep(2)
                    green.off()
                    top.withdraw()
                    servo.setClose()
            else:
                red.on()
                top.setData("Error, Couldn't find the scaned card", "Unknown", "Unknown", "/var/www/flask/accessControl/static/imgs/stop.png", block)
                top.deiconify()
                sleep(1)
                top.withdraw()
                red.off()


# --------------------------------------------------- #

if __name__ == '__main__':
    root = Fullscreen_Window()
    top = window(root)
    start_new_thread(readRFID,())
    root.mainloop()




