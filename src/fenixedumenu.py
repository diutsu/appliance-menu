#!/usr/bin/env python2                                                       
# -*- coding: utf-8 -*-
import curses
import interfaces
import fenixFrameworkProp
from  curses import panel,textpad

class Menu(object):                                                          

    def __init__(self, items, title, stdscreen, exit = True):                                    
        self.window = stdscreen.subwin(11,0)                                  
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
        self.top = curses.newwin(11,78,0,0)
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
        except :
            self.ip = False
        try:
            self.url = fenixFrameworkProp.getUrl()
        except : 
            self.url = False

        self.top.addstr(0,0,"                   XXXXXXX                                                    ")
        self.top.addstr(1,0,"                  + XXXXX +                                                   ")
        self.top.addstr(2,0,"                +++++ X +++++                                                 ")
        self.top.addstr(3,0,"               +++++++ +++++++                                                ")
        self.top.addstr(4,0,"              . +++++ . +++++ .            FenixEdu™                          ")
        self.top.addstr(5,0,"            ..... + ..... + .....          VM                                 ")
        self.top.addstr(6,0,"           ....... ....... .......                                            ")
        self.top.addstr(7,0,"            .....   .....   .....                                             ")
        self.top.addstr(8,0,"              .       .       .                                               ")
        if self.ip :
            if self.url and not self.url == "localhost":
                self.top.addstr(9,0,"Your url is http://"+self.url+"/")
            else : 
                self.top.addstr(9,0,"Your url is http://"+self.ip+"/")
            self.top.addstr(10,0,"Your IP is : " + self.ip)
        else : 
            self.top.addstr(10,0,"Check your network configurations")
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
                if (self.position == len(self.items)-1 and self.hasExit) or self.terminate:                       
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
        win.addstr(0,1,"  "+string)
        win.attroff(curses.A_REVERSE)
        
