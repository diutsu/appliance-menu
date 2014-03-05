#!/usr/bin/env python2                                                       
import urllib2
import re
import curses 
from subprocess import call,check_output

directory= "/home/fenixuser/fenix-webapp/"
configFile= directory+"src/main/resources/configuration.properties"
propFile= directory+"src/main/resources/fenix-framework.properties"

class FenixFramework():
    host = ""
    name = ""
    port = ""
    user = ""
    passw = ""
    menu = ""
    screen = ""
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
        with open(propFile,"w") as f:
            f.write("# Add additional backend-specific configurations in here\n\n")
            f.write("dbAlias=//"+self.host+":"+self.port+"/"+self.name+"\n")
            f.write("dbUsername="+self.user+"\n")
            f.write("dbPassword="+self.passw+"\n\n")
            f.write("updateRepositoryStructureIfNeeded = true\n\n")
            f.write("canCreateDomainMetaObjects=false\n")
            f.close()

    def load(self):
        with open(propFile,"r") as f:
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
   
    def restart(self) :
        self.menu.wait("Server restart","Please wait while the server restarts")
        if (self.isRunning()) :
    	    check_output("/etc/init.d/mvninit.sh stop",shell=True)
	while(self.isRunning()) :
		time.sleep(1)
	time.sleep(10)
	check_output("/etc/init.d/mvninit.sh start",shell=True)
	while( not self.isRunning()) :
		time.sleep(1)
        self.menu.delWait()
    
    def start(self) :
	curses.endwin()	
        print check_output("/etc/init.d/mvninit.sh force_start",shell=True)

    def isRunning(self) :
	try:
	    urllib2.urlopen('http://localhost/')
            return True
	except:
	    return False

    def destroy(self) :
        destroyDbMenu_items = [
                ('Ok, destroy it', self.destroyConfirmed),]                                                            
        destroyDbMenu = Menu(destroyDbMenu_items, "Destroying the database is irreversible, do you want to proceed?", self.screen)                           
        destroyDbMenu.display()

    def destroyConfirmed(self) : 
	self.stop()
	call("mysql -u"+self.user+" -p"+self.passw+" -e 'drop database "+self.name+"; create database "+self.name+";'",shell=True)
	self.start()

def getUrl() :
    with open(configFile,'r') as file:
        for line in file.readlines():
            parts = line.split(" = ")
            if parts[0] == "http.host":
                return parts[1].rstrip()
                
