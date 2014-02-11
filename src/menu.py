#!/usr/bin/env python2                                                       
# -*- coding: utf-8 -*-
import time
import curses                                                                
import interfaces
import re
import sys
import socket
import fcntl
import struct

from curses import panel,textpad
from subprocess import call
reload(sys)  # to enable `setdefaultencoding` again

sys.setdefaultencoding("UTF-8")

class Menu(object):                                                          

    def __init__(self, items, title, stdscreen, exit = True):                                    
        self.window = stdscreen.subwin(11,0)                                  
        self.window.keypad(1)                                                
        self.panel = panel.new_panel(self.window)                            
        self.panel.hide()                                                    
        panel.update_panels()                                                
        self.title = title
        self.position = 0                                                    
        self.items = items     
        self.hasExit = exit
        self.top = curses.newwin(0,0,0,0)
        self.topPanel = panel.new_panel(self.top)
        if exit : 
            self.items.append(('exit','exit'))                                   

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
        self.top.addstr(0,0,"                   XXXXXXX                                                    ")
        self.top.addstr(1,0,"                  + XXXXX +                                                   ")
        self.top.addstr(2,0,"                +++++ X +++++                                                 ")
        self.top.addstr(3,0,"               +++++++ +++++++                                                ")
        self.top.addstr(4,0,"              . +++++ . +++++ .            FenixEdu™                          ")
        self.top.addstr(5,0,"            ..... + ..... + .....          VM                                 ")
        self.top.addstr(6,0,"           ....... ....... .......                                            ")
        self.top.addstr(7,0,"            .....   .....   .....                                             ")
        self.top.addstr(8,0,"              .       .       .                                               ")
        self.top.addstr(9,0,"Your IP is : ")
        self.top.addstr(10,0,"Your IP is : " + get_ip_address("eth0"))
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
            self.setTitle(self.title,self.window)
            for index, item in enumerate(self.items):                        
                if index == self.position:                                   
                    mode = curses.A_REVERSE                                  
                else:                                                        
                    mode = curses.A_NORMAL                                   

                msg = '%s' % (item[0])                            
                self.window.addstr(1+index, 1, msg, mode)                    

            key = self.window.getch()                                        

            if key in [curses.KEY_ENTER, ord('\n')]:                         
                if self.position == len(self.items)-1 and self.hasExit :                       
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
        
class CursesIfaces():
    address = ""
    network = ""
    broadcast = ""
    gateway = ""
    netmask = ""
    menu = ""

    def setAddress(self) : 
        self.address = self.menu.getParam('IP Address')
        self.menu.items[0] = ("Address : " + self.address,self.menu.items[0][1])
        self.write()
    
    def setNetwork(self) : 
        self.network = self.menu.getParam('Network IP')
        self.menu.items[1] = ("Network  : " + self.network,self.menu.items[1][1])
        self.write()

    def setBroadcast(self) : 
        self.broadcast = self.menu.getParam('Broadcast IP')
        self.menu.items[2] = ("Broadcast  : " + self.broadcast,self.menu.items[2][1])
        self.write()

    def setGateway(self) : 
        self.gateway = self.menu.getParam('Gateway Mask')
        self.menu.items[3] = ("Gateway : " + self.gateway,self.menu.items[3][1])
        self.write()

    def setNetmask(self) : 
        self.netmask = self.menu.getParam('Netmask')
        self.menu.items[4] = ("Netmask : " + self.netmask,self.menu.items[4][1])
        self.write()

    def write(self) :
        settings = {}
        if(self.netmask!="") :
            settings["netmask"]=self.netmask
        if(self.gateway!="") :
            settings["gateway"]=self.gateway
        if(self.broadcast!="") :
            settings["broadcast"]=self.broadcast
        if(self.network!="") :
            settings["network"]=self.network
        if(self.address!="") :
            settings["address"]=self.address

        curses.endwin()
        interfaces.setStatic(settings)  

    def load(self):
        settings = interfaces.loadStaticSettings()
        self.address =  settings["address"] if "address" in settings.keys() else ""
        self.menu.items[0] = ("Address  : " + self.address,self.menu.items[0][1])
        self.network = settings["network"] if "network" in settings.keys() else ""
        self.menu.items[1] = ("Network  : " + self.network,self.menu.items[1][1])
        self.broadcast = settings["broadcast"] if "broadcast" in settings.keys() else ""
        self.menu.items[2] = ("Broadcast : " + self.broadcast,self.menu.items[2][1])
        self.gateway = settings["gateway"] if "gateway" in settings.keys() else ""
        self.menu.items[3] = ("Gateway  : " + self.gateway,self.menu.items[3][1])
        self.netmask = settings["netmask"] if "netmask" in settings.keys() else ""
        self.menu.items[4] = ("Netmask  : " + self.netmask,self.menu.items[4][1])
        self.menu.display()
            
    def reloadNetwork(self):
        self.menu.wait("Network restart","Please wait while network restarts")
        call(["/etc/init.d/network restart"])
        self.menu.delWait()
        curses.endwin()
        return

    def setDHCP(self) :
        interfaces.setDHCP()
        self.menu.confirm("Changed to DHCP","Restart network, to apply changes")
        
    def editInterfaces(self):
        curses.endwin()
    	call(["nano","/etc/network/interfaces"])
        self.menu.confirm("","Restart network, to apply changes")


class FenixFramework():
    host = ""
    name = ""
    port = ""
    user = ""
    passw = ""
    menu = ""

    def setHost(self) : 
        self.host = self.menu.getParam('Hostname')
        self.menu.items[0] = ("Hostname : " + self.host,self.menu.items[0][1])
        self.write()
    
    def setPort(self) : 
        self.port = self.menu.getParam('Database port')
        self.menu.items[1] = ("DB Port  : " + self.port,self.menu.items[1][1])
        self.write()

    def setDatabase(self) : 
        self.name = self.menu.getParam('Database name')
        self.menu.items[2] = ("DB Name  : " + self.name,self.menu.items[2][1])
        self.write()

    def setUser(self) : 
        self.user = self.menu.getParam('username')
        self.menu.items[3] = ("Username : " + self.user,self.menu.items[3][1])
        self.write()

    def setPass(self) : 
        self.passw = self.menu.getParam('Password')
        self.menu.items[4] = ("Password : " + self.passw,self.menu.items[4][1])
        self.write()

    def write(self):
        with open("/home/fenixuser/fenix-webapp/src/main/resources/fenix-framework.properties","w") as f:
            f.write("# Add additional backend-specific configurations in here\n\n")
            f.write("dbAlias=//"+self.host+":"+self.port+"/"+self.name+"\n")
            f.write("dbUsername="+self.user+"\n")
            f.write("dbPassword="+self.passw+"\n\n")
            f.write("updateRepositoryStructureIfNeeded = true\n\n")
            f.write("canCreateDomainMetaObjects=false\n")
            f.close()

    def load(self):
        with open("/home/fenixuser/fenix-webapp/src/main/resources/fenix-framework.properties","r") as f:
            for line in f :
                result = re.match("dbAlias=//(.*):([0-9]+)/(.*)",line)
                if result : 
                    self.host = result.group(1)
                    self.menu.items[0] = ("Hostname : " + self.host,self.menu.items[0][1])
                    self.port = result.group(2)
                    self.menu.items[1] = ("DB Port  : " + self.port,self.menu.items[1][1])
                    self.name = result.group(3)
                    self.menu.items[2] = ("DB Name  : " + self.name,self.menu.items[2][1])
                    continue
                result =  re.match("dbUsername=(.*)",line)
                if result : 
                    self.user = result.group(1)
                    self.menu.items[3] = ("Username : " + self.user,self.menu.items[3][1])
                    continue
                result = re.match("dbPassword=(.*)",line)
                if result : 
                    self.passw = result.group(1)
                    self.menu.items[4] = ("Password : " + self.passw,self.menu.items[4][1])
                    continue
            f.close()

class ApplianceMenu(object):                                                         
    top = ""

    def __init__(self, stdscreen):                                           
        self.screen = stdscreen                                              
        curses.curs_set(0)                                                   
        ff = FenixFramework()
        ci = CursesIfaces()
        networkMenu_items = [                                                    
                ('Use DHCP', ci.setDHCP),                                       
                ('Use Static IP', ci.load),
                ('Edit /etc/network/interfaces', ci.editInterfaces),
                ('Restart Network', ci.reloadNetwork) 
                ]                                                            
        networkMenu = Menu(networkMenu_items, "Network Settings", self.screen)                           
        
        ifacesMenu_items = [                                                    
                ('Address   : ', ci.setAddress),                                       
                ('Network   : ', ci.setNetwork),
                ('Broadcast : ', ci.setBroadcast),
                ('Gateway   : ', ci.setGateway),
                ('Netmask   : ', ci.setNetmask) 
                ]                                                            
        ifacesMenu = Menu(ifacesMenu_items, "Static eth0 Settings", self.screen)                           
        ci.menu = ifacesMenu
        
        databaseMenu_items = [
                #('Show Curent', ff.show),
                ('Hostname : ', ff.setHost),                                       
                ('DB Port  : ', ff.setPort),
                ('DB Name  : ', ff.setDatabase),
                ('Username : ', ff.setUser),                                      
                ('Password : ', ff.setPass)                                      
                ]                                                            
        databaseMenu = Menu(databaseMenu_items, "Database Settings", self.screen)                           
        ff.menu = databaseMenu
        ff.load()
        systemMenu_items = [                                                    
                ('Shutdown', shutdown),                                       
                ('Reboot', reboot)                                      
                ]                                                            
        systemMenu = Menu(systemMenu_items, "System", self.screen)                           

        main_menu_items = [                                                  
                ('Network', networkMenu.display),                                       
                ('Database Info', databaseMenu.display),   
                ('System', systemMenu.display)                                 
                ]                                                            
        main_menu = Menu(main_menu_items, "FenixEdu VM", self.screen, False)                       
        main_menu.display()                                                  

def get_ip_address(ifname):
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    return socket.inet_ntoa(fcntl.ioctl(
        s.fileno(),
        0x8915,  # SIOCGIFADDR
        struct.pack('256s', ifname[:15])
    )[20:24])

def reboot():
    curses.endwin()
    call(["reboot"])
    sys.exit()

def shutdown():
    curses.endwin()
    call(["shutdown","now","-hP"])
    sys.exit()
    
if __name__ == '__main__':                                                       
    curses.wrapper(ApplianceMenu)   
