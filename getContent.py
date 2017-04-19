import pymongoExample
import sys

filename =  "urls.txt"
fileout = open(filename,"w")
sys.stdout = fileout
try:
    with open("urls-raw.txt") as f:
        content = f.readlines()
    #print(content)
    for f in content:
        for e in f.split(' '):
            if(e.find("http:") != -1):
                print(e)
except:
    pass
fileout.close()