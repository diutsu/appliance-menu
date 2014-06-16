#!/usr/bin/env python2                                                       
# -*- coding: utf-8 -*-
import curses
import interfaces
import fenixFrameworkProp
from  curses import panel,textpad

class Menu(object):                                                          

    def __init__(self, items, title, stdscreen, exit = True):                                    
        height, width = stdscreen.getmaxyx()
        self.horizCenter = width/2
        self.window = stdscreen.subwin(18,0)                                  
        self.window.keypad(1)                                                
        self.panel = panel.new_panel(self.window)                            
        self.panel.hide()                                                    
        panel.update_panels()                                                
        self.titlestr = title
        self.position = 0                                                    
        self.items = items     
        self.hasExit = exit
        self.top = curses.newwin(0,0,0,0)
        self.topPanel = panel.new_panel(self.top)
        self.terminate = False
        if exit : 
            self.items.append(('Back','exit'))                                   

    def navigate(self, n):                                                   
        self.position += n                                                   
        if self.position < 0:                                                
            self.position = 0                                                
        elif self.position >= len(self.items):                               
            self.position = len(self.items)-1                                

    def displayTop(self) :
        self.top = curses.newwin(16,78,0,0)
        self.topPanel = panel.new_panel(self.top)
        self.updateTop()
        self.topPanel.top()
        self.topPanel.show()
        self.top.refresh()
        panel.update_panels()
        curses.doupdate()

    def updateTop(self) :
        try :
            self.ip = interfaces.get_ip_address("eth0")
            self.mac = interfaces.get_mac_address("eth0")
        except :
            self.ip = False
            self.mac = "0"
        try:
            self.url = fenixFrameworkProp.getUrl()
        except : 
            self.url = False
        blueColor = curses.color_pair(7)
        redColor = curses.color_pair(2)
        greenColor = curses.color_pair(3)
        strCenter = (len("FenixEdu")+22)/2
        self.top.addstr(1,self.horizCenter/2+15-strCenter,"         XXXXXXX         ",blueColor)
        self.top.addstr(2,self.horizCenter/2+15-strCenter,"        + XXXXX +        ",blueColor)
        self.top.addstr(3,self.horizCenter/2+15-strCenter,"      +++++ X +++++      ",blueColor)
        self.top.addstr(4,self.horizCenter/2+15-strCenter,"     +++++++ +++++++     ",blueColor)
        self.top.addstr(5,self.horizCenter/2+15-strCenter,"    . +++++ . +++++ .    ",blueColor)
        self.top.addstr(5,self.horizCenter/2+15-strCenter+30,"FenixEdu")
        self.top.addstr(6,self.horizCenter/2+15-strCenter,"  ..... + ..... + .....  ",blueColor)
        self.top.addstr(6,self.horizCenter/2+15-strCenter+30,"Node    ")
        self.top.addstr(7,self.horizCenter/2+15-strCenter," ....... ....... ....... ",blueColor)
        self.top.addstr(8,self.horizCenter/2+15-strCenter,"  .....   .....   .....  ",blueColor)
        self.top.addstr(9,self.horizCenter/2+15-strCenter,"    .       .       .    ",blueColor)
        if self.ip :
            dspStr = "IP address : " + self.ip
            self.top.addstr(11,1+self.horizCenter-len(dspStr)/2,dspStr)
            
            dspStr = "MAC address : " + self.mac
            self.top.addstr(12,self.horizCenter-len(dspStr)/2,dspStr)

            dspStr = "To finish configuring this node go to:"
            self.top.addstr(14,self.horizCenter-len(dspStr)/2,dspStr)
           
            if self.url and not self.url == "localhost":
                dpsStr = "http://"+self.url+"/"
                self.top.addstr(15,self.horizCenter-len(dspStr)/2,dspStr,greenColor)
            else : 
                dspStr = "http://"+self.ip+"/"
                self.top.addstr(15,self.horizCenter-len(dspStr)/2,dspStr,greenColor)
        else : 
            dspStr ="Please check your network configurations"
            self.top.addstr(12,self.horizCenter-len(dspStr)/2,dspStr,redColor)
            
            dspStr = "Could not determine your IP address"
            self.top.addstr(13,self.horizCenter-len(dspStr)/2,dspStr,redColor)
        self.top.refresh()

    def display(self):                                                       
        self.panel.top()                                                     
        self.panel.show()                                                    
        self.window.clear()                                                  
        self.displayTop()
        while True:                                                          
            self.window.refresh()                                            
            self.top.refresh()
            curses.doupdate()                                                
            self.setTitle(self.titlestr,self.window)
            for index, item in enumerate(self.items):                        
                if index == self.position:                                   
                    mode = curses.A_REVERSE                                  
                else:                                                        
                    mode = curses.A_NORMAL                                   

                msg = '%s' % (item[0])                            
                self.window.addstr(1+index, 1, msg, mode)                    

            key = self.window.getch()                                        
            
            if key in [curses.KEY_ENTER, ord('\n')]:                         
                if (self.position == len(self.items)-1 and self.hasExit) :                       
                    break                                                    
                else:                                                        
                    self.items[self.position][1]()

            elif key == curses.KEY_UP:                                       
                self.navigate(-1)                                            

            elif key == curses.KEY_DOWN:                                     
                self.navigate(1)                                             

        self.window.clear()                                                  
        self.panel.hide()                                                    
        panel.update_panels()                                                
        curses.doupdate()

    def removeOptions(self) :
        self.items = [('Back','exit')]
        self.panel.show()
        self.window.clear()

    def getParam(self, prompt_string):
        prompt = curses.newwin(3,43,5,0)
        prompt.border(0)
        self.setTitle("New Value for : " + prompt_string,prompt)
        prompt.addstr(1, 1, ">")
        prompt.refresh()
        inwin = curses.newwin(1,40,6,2)
        curses.doupdate()
        tb=curses.textpad.Textbox(inwin)
        inp = tb.edit()
        inp = inp[:-1]
        del tb
        inwin.erase()
        prompt.erase()
        inwin.refresh()
        prompt.refresh()
        del inwin
        del prompt
        self.panel.top()
        self.panel.show()
        self.panel.window().touchwin()
        self.panel.window().clear()
        self.panel.window().refresh()
        self.updateTop()
        curses.doupdate()
        return inp
    
    def wait(self, title, text):
        self.wait = curses.newwin(3,43,5,0)
        self.wait.border(0)
        self.setTitle(title,self.wait)
        self.wait.addstr(1, 1, text)
        self.wait.refresh()
        curses.doupdate()
        return 
    
    def confirm(self, title, text):
        self.wait = curses.newwin(3,43,5,0)
        self.wait.border(0)
        self.setTitle(title,self.wait)
        self.wait.addstr(1, 1, text)
        self.wait.refresh()
        curses.doupdate()
        self.wait.getch()
        self.wait.erase()
        self.wait.refresh()
        del self.wait
        self.updateTop()
        curses.doupdate()
        return 

    def delWait(self) :
        self.wait.erase()
        self.wait.refresh()
        self.updateTop()
        curses.doupdate()
        del self.wait

    def setTitle(self,string,win) :
        win.attron(curses.A_REVERSE)
        win.addstr(0,1," "+string)
        win.attroff(curses.A_REVERSE)
        
