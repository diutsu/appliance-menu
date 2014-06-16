#!/usr/bin/env python2                                                       
import urllib2
import os
import re
import curses 
import time
import fenixedumenu
from subprocess import call,check_output

directory= "/home/fenixedu/fenixedu-appliance-webapp/"
configFile= directory+"src/main/resources/configuration.properties"
propFile= directory+"src/main/resources/fenix-framework.properties"
pomFile= directory+"pom.xml"

class FenixFramework():
    host = ""
    name = ""
    port = ""
    user = ""
    passw = ""
    menu = ""
    dbmenu = ""
    screen = ""
    def setHost(self) : 
        self.host = self.dbmenu.getParam('Database hostname')
        self.dbmenu.items[0] = ("Hostname : " + self.host,self.dbmenu.items[0][1])
        self.writeDB()
    
    def setPort(self) : 
        self.port = self.dbmenu.getParam('Database port')
        self.dbmenu.items[1] = ("DB Port  : " + self.port,self.dbmenu.items[1][1])
        self.writeDB()

    def setDatabase(self) : 
        self.name = self.dbmenu.getParam('Database name')
        self.dbmenu.items[2] = ("DB Name  : " + self.name,self.dbmenu.items[2][1])
        self.writeDB()

    def setUser(self) : 
        self.user = self.dbmenu.getParam('Database username')
        self.dbmenu.items[3] = ("Username : " + self.user,self.dbmenu.items[3][1])
        self.writeDB()

    def setPass(self) : 
        self.passw = self.dbmenu.getParam('Database password')
        self.dbmenu.items[4] = ("Password : " + self.passw,self.dbmenu.items[4][1])
        self.writeDB()

    def setVersion(self) :
	self.version = self.menu.getParam('FenixEdu Version')
	self.menu.items[3] = ("FenixEdu Version : " + self.version,self.menu.items[3][1])
	self.writePOM()

    def writeDB(self):
        with open(propFile,"w") as f:
            f.write("# Add additional backend-specific configurations in here\n\n")
            f.write("dbAlias=//"+self.host+":"+self.port+"/"+self.name+"\n")
            f.write("dbUsername="+self.user+"\n")
            f.write("dbPassword="+self.passw+"\n\n")
            f.write("updateRepositoryStructureIfNeeded = true\n\n")
            f.write("canCreateDomainMetaObjects=false\n")
            f.close()
    
    def writePOM(self):
	os.rename(pomFile,pomFile+"~")
	
	groupMatch = False
	artifactMatch = False
	
	fwrite = open(pomFile,"w")		
        with open(pomFile+"~","r") as f:
            for line in f :
		line = re.sub(r"(.*version.pt.ist.fenix>).*(</version.pt.ist.fenix*)",r"\g<1>"+self.version+"\g<2>",line) 
		fwrite.write(line)
            f.close()
	fwrite.close()
     	os.remove(pomFile+"~")

    def load(self):
	self.loadDB()
	self.loadVersion()

    def loadVersion(self):
	groupMatch = False
	artifactMatch = False
		
        with open(pomFile,"r") as f:
            for line in f :
                versionMatch = re.match(".*version>(.*)</version.*",line) 
                if versionMatch :
                    self.version = versionMatch.group(1)
                    self.menu.items[3] = ("FenixEdu Version : " + self.version, self.menu.items[3][1])	
                    break
            f.close()

    def loadDB(self):
        with open(propFile,"r") as f:
            for line in f :
                result = re.match("dbAlias=//(.*):([0-9]+)/(.*)",line)
                if result : 
                    self.host = result.group(1)
                    self.dbmenu.items[0] = ("Hostname : " + self.host,self.dbmenu.items[0][1])
                    self.port = result.group(2)
                    self.dbmenu.items[1] = ("DB Port  : " + self.port,self.dbmenu.items[1][1])
                    self.name = result.group(3)
                    self.dbmenu.items[2] = ("DB Name  : " + self.name,self.dbmenu.items[2][1])
                    continue
                result =  re.match("dbUsername=(.*)",line)
                if result : 
                    self.user = result.group(1)
                    self.dbmenu.items[3] = ("Username : " + self.user,self.dbmenu.items[3][1])
                    continue
                result = re.match("dbPassword=(.*)",line)
                if result : 
                    self.passw = result.group(1)
                    self.dbmenu.items[4] = ("Password : " + self.passw,self.dbmenu.items[4][1])
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
        destroyDbMenu = fenixedumenu.Menu(destroyDbMenu_items, "Destroying the database is irreversible, do you want to proceed?", self.screen)                           
        destroyDbMenu.display()

    def destroyConfirmed(self) : 
        self.menu.wait("Server restart","Please wait while the server stops")
        if (self.isRunning()) :
    	    check_output("/etc/init.d/mvninit.sh stop",shell=True)
	while(self.isRunning()) :
		time.sleep(1)
        self.menu.delWait()
        self.menu.wait("Server restart","Please wait while we create a new database")
	call("mysql -u"+self.user+" -p"+self.passw+" -e 'drop database "+self.name+"; create database "+self.name+";'",shell=True)
        self.menu.delWait()
        self.menu.wait("Server restart","Please wait while we start the server again")
	self.start()
	while(not self.isRunning()) :
		time.sleep(1)
        self.menu.delWait()
	self.menu.terminate = True

def getUrl() :
    with open(configFile,'r') as file:
        for line in file.readlines():
            parts = line.split(" = ")
            if parts[0] == "http.host":
                return parts[1].rstrip()
                
