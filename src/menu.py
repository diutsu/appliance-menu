#!/usr/bin/env python2                                                       
# -*- coding: utf-8 -*-
import time
import curses                                                                
import fenixFrameworkProp
import sshManager
import interfaces
import fenixedumenu
import re
import sys
import locale
import urllib2 

from curses import panel,textpad
from subprocess import call,check_output
#reload(sys)
# to enable `setdefaultencoding` again

#sys.setdefaultencoding("UTF-8")

class ApplianceMenu(object):                                                         
    top = ""

    def __init__(self, stdscreen):                                           
        self.screen = stdscreen                                              
        curses.use_default_colors()
        for i in range(0, curses.COLORS):
            curses.init_pair(i + 1, i, -1)
        curses.curs_set(0)                                                   
        ff = fenixFrameworkProp.FenixFramework()
        if(not ff.isRunning()):
            ff.start()
        ci = interfaces.CursesIfaces()
        win = stdscreen.subwin(0,0)                                  
        win.addstr("Waiting for server to start, please be patient")
        win.refresh()          
        curses.doupdate()                                  
        blink = False
        blinkCount = 0
        while(not ff.isRunning() and blinkCount < 300) :
            if blink:
                blink = False
                win.addstr(1,0,". . .")
                win.refresh()          
                curses.doupdate()                                  
            else :
                blink = True
                win.addstr(1,0,"     ")
                win.refresh()          
                curses.doupdate()                                  
                time.sleep(1)
                blinkCount+=1

        networkMenu_items = [                                                    
                ('Use DHCP', ci.setDHCP),                                       
                ('Use Static IP', ci.load),
                ('Edit /etc/network/interfaces', ci.editInterfaces),
                ('Restart Network', ci.reloadNetwork) 
                ]                                                            
        networkMenu = fenixedumenu.Menu(networkMenu_items, "Network Settings", self.screen)                           

        ifacesMenu_items = [                                                    
                    ('Address   : ', ci.setAddress),                                       
                    ('Network   : ', ci.setNetwork),
                    ('Broadcast : ', ci.setBroadcast),
                    ('Gateway   : ', ci.setGateway),
                    ('Netmask   : ', ci.setNetmask) 
                    ]                                                            
        ifacesMenu = fenixedumenu.Menu(ifacesMenu_items, "Static eth0 Settings", self.screen)                           
        ci.menu = ifacesMenu

        databaseMenu_items = [
                ('DB Hostname : ', ff.setHost),                                       
                ('DB Port  : ', ff.setPort),
                ('DB Name  : ', ff.setDatabase),
                ('DB Username : ', ff.setUser),                                      
                ('DB Password : ', ff.setPass),                                      
                ]                                                            
        databaseMenu = fenixedumenu.Menu(databaseMenu_items, "Database Settings", self.screen)                           

        fenixMenu_items = [
                ('Database Settings', databaseMenu.display),
                ('Restart FenixEdu', ff.restart),                                      
                ('Destroy database', ff.destroy),
                ('FenixEdu Version : ',ff.setVersion),
                ]
        fenixMenu = fenixedumenu.Menu(fenixMenu_items, "Node Management", self.screen)                           

        ff.dbmenu = databaseMenu
        ff.menu = fenixMenu
        ff.load()
        ff.screen = self.screen

        ssh_calls = sshManager.SshCalls()
        sshMenu_items = [
            ("Stop SSH: ", ssh_calls.sshStop)
            ]
        sshMenu = fenixedumenu.Menu(sshMenu_items, "SSH Status", self.screen)
        ssh_calls.menu = sshMenu
        ssh_calls.sshStatus()

        systemMenu_items = [                                                    
                    ('Shutdown', shutdown),                                       
                    ('Reboot', reboot)                                      
                    ]                                                            
        systemMenu = fenixedumenu.Menu(systemMenu_items, "System", self.screen)                           

        main_menu_items = [                                                  
                    ('Node Management', fenixMenu.display),
                    ('SSH Server', sshMenu.display),
                    ('Network', networkMenu.display),                                       
                    ('System', systemMenu.display)                                 
                    ]                                                            
        main_menu = fenixedumenu.Menu(main_menu_items, "FenixEdu Node", self.screen, False)                       

        main_menu.display()                                                  


def reboot():
    curses.endwin()
    call(["reboot"])
    sys.exit()

def shutdown():
    curses.endwin()
    call(["shutdown","now","-hP"])
    sys.exit()

if __name__ == '__main__':                                                       
    locale.setlocale(locale.LC_ALL, '')
    curses.wrapper(ApplianceMenu)   


