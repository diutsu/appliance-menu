import re
import os

def setStatic(settings) :
    fwrite = open('if~','w')
    with open('if','r') as fread:
        try:
            for line in fread :
                line_out = re.sub(r"(iface .*eth0 .*inet.*) dhcp",r"\g<1> static",line)
                if line != line_out :
                    fwrite.write(line_out)    
                    for key in settings.keys() :
                        line = "\t" + key + " " + settings[key] + "\n"
                        fwrite.write(line)
                    continue
                fwrite.write(line)
        finally:
            fread.close()
            fwrite.close()
            os.rename('if~','if')

def setDHCP():
    fwrite = open('if~','w')
    with open('if','r') as fread:
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
            os.rename('if~','if')

def loadStaticSettings():
    settings ={}
    matched = False
    with open('if','r') as fread:
        try:
            for line in fread :
                line_out = re.match(r"(iface .*eth0 .*inet.*) static",line)
                
                if matched : 
                    matched = False
                    m = re.search("address\s(.*)",line)
                    if m : 
                        settings["address"]=m.group(1)
                        searched = True

                    m = re.search("network\s(.*)", line)
                    if m : 
                        settings["network"]=m.group(1)
                        searched = True
                    
                    m = re.search("broadcast\s(.*)", line)
                    if m : 
                        settings["broadcast"]=m.group(1)
                        searched = True

                    m = re.search("gateway\s(.*)",line)
                    if m : 
                        settings["gateway"]=m.group(1)
                        searched = True

                    m = re.search("netmask\s(.*)",line)
                    if m : 
                        settings["netmask"]=m.group(1)
                        searched = True

                if line_out : 
                    matched = True
        finally:
            fread.close()
    return settings
