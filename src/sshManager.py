#!/usr/bin/env python2                                                       
import curses
import sys
from subprocess import call,check_output
class SshCalls():
    menu = ""
    def sshStatus(self) :
        output = check_output(["service","ssh","status"])
        if "running" in output :
            self.menu.titlestr = "SSH server is running"
            self.menu.items[0] = ('Stop SSH', self.sshStop)
        else :
            self.menu.items[0] = ('Start SSH', self.sshStart)
            self.menu.titlestr = "SSH server is stopped"
    def sshStop(self) :
	curses.endwin()
        check_output(["service","ssh","stop"])
	try: 
	    check_output("pkill sshd", shell=True)
	except: 
	    pass
        self.menu.items[0] = ('Start SSH', self.sshStart)
        self.menu.titlestr = "SSH server is stopped"
	sys.exit()
    def sshStart(self) :
        check_output(["service","ssh","start"])
        self.menu.items[0] = ('Stop SSH', self.sshStop)
        self.menu.titlestr = "SSH server is running"
	sys.exit()
