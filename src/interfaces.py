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



#st = { "address" : "1.1.1.1", "network":"1.0.0.0", "broadcast" : "0.1.1.1",
        #"gateway" : "1.0.1.0", "netmask":"1.0.0.1"}
#setStatic(st)
