#!/usr/bin/env python2                                                       
import re
import os
import curses                                                                
import socket
import fcntl
import struct

from curses import panel,textpad
from subprocess import call,check_output

def get_ip_address(ifname):
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    return socket.inet_ntoa(fcntl.ioctl(
        s.fileno(),
        0x8915,  # SIOCGIFADDR
        struct.pack('256s', ifname[:15])
    )[20:24])

def setStatic(settings) :
    fwrite = open('if~','w')
    with open('/etc/network/interfaces','r') as fread:
        try:
            changed = False
            for line in fread :
                line_out = re.sub(r"(iface .*eth0 .*inet.*) dhcp",r"\g<1> static",line)
                m = re.match("iface .*eth0 .*inet.* static",line)
                if line != line_out or m :
                    changed = True
                    fwrite.write(line_out)    
                    print settings
                    for key in settings.keys() :
                        print key
                        fwrite.write("\t" + key + " " + settings[key] + "\n")
                    continue
                elif changed :
                    if not line.strip() :
                        changed = False
                    else : 
                        continue
                fwrite.write(line)
        finally:
            fread.close()
            fwrite.close()
            os.rename('if~','if')

def setDHCP():
    fwrite = open('if~','w')
    with open('/etc/network/interfaces','r') as fread:
        try:
            replaced = False
            for line in fread :
                line_out = re.sub(r"(iface .*eth0 .*inet.*) static",r"\g<1> dhcp",line)
                if line != line_out :
                    replaced = True
                    fwrite.write(line_out)
                    continue
                if replaced :
                    if ("address" in line or "network" in line or
                        "broadcast" in line or "gateway" in line or
                        "netmask" in line):
                        continue
                replaced = False
                fwrite.write(line)
        finally:
            fread.close()
            fwrite.close()
            os.rename('if~','/etc/network/interfaces')

def loadStaticSettings():
    settings ={}
    matched = False
    with open('/etc/network/interfaces','r') as fread:
        try:
            for line in fread :
                line_out = re.match(r"(iface .*eth0 .*inet.*) static",line)
                
                if matched : 
                    matched = False
                    m = re.search("address\s(.*)",line)
                    if m : 
                        settings["address"]=m.group(1)
                        matched = True

                    m = re.search("network\s(.*)", line)
                    if m : 
                        settings["network"]=m.group(1)
                        matched = True
                    
                    m = re.search("broadcast\s(.*)", line)
                    if m : 
                        settings["broadcast"]=m.group(1)
                        matched = True

                    m = re.search("gateway\s(.*)",line)
                    if m : 
                        settings["gateway"]=m.group(1)
                        matched = True

                    m = re.search("netmask\s(.*)",line)
                    if m : 
                        settings["netmask"]=m.group(1)
                        matched = True

                if line_out : 
                    matched = True
        finally:
            fread.close()
    return settings

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
        setStatic(settings)  

    def load(self):
        settings = loadStaticSettings()
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
        self.menu.confirm("Changed to DHCP","Restart network, to apply changes")
            
    def reloadNetwork(self):
        self.menu.wait("Network restart","Please wait while network restarts")
        check_output("service networking stop && service networking start",shell=True)
        self.menu.delWait()
        curses.endwin()
	return

    def setDHCP(self) :
        setDHCP()
        self.menu.confirm("Changed to DHCP","Restart network, to apply changes")
        
    def editInterfaces(self):
        curses.endwin()
        call(["nano","/etc/network/interfaces"])
        self.menu.confirm("","Restart network, to apply changes")
