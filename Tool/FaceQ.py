'''
Created on Sep 20, 2020

@author: patch
'''
import json

def openFace(filename):
    print filename
    cat = filename[filename.find('faceq-')+6:filename.find('.json')]
    print cat
    f = open(filename, 'r')
    #print f
    s = f.read()
    myjson = json.loads(s)
    
    for key in myjson.keys():
        paths = None
        frontPaths = None
        backPaths = None
        #print myjson[key]
        try: 
          paths = myjson[key]["frontSide"]["path"]
        except:
            err = 1
        try:
            backPaths = myjson[key]["frontSide"]["backPath"]
        except:
            err = 2 
        try:
            frontPaths = myjson[key]["frontSide"]["frontPath"]
        except:
                    print 'json load err'
                
        
        s = '<?xml version="1.0" standalone="no"?><svg width="1000" height="1000" version="1.1" xmlns="http://www.w3.org/2000/svg">'
        if cat == 'face':
            print 'is FACE----------------'
            s = s + '<style>path.faceColor{fill:rgb(250,200,154);}</style>'
        if cat.find('hair') > -1:
            cat = 'hair'
            print 'is HAIR----------------'
            s = s + '<style>path{fill:rgb(113,64,4);}</style>'
        try:
          if cat.find('hair') == -1:    
            for path in paths:
                s = s + '<' + path["type"]
                for style in path["style"]:
                    s = s + " " + style["attr"] + '=' + "\"" + str(style["val"]) + "\""
                s = s + " />"
        except Exception as e:
            print(e)
        try:
            for path in frontPaths:
                s = s + '<' + path["type"]
                for style in path["style"]:
                    s = s + " " + style["attr"] + '=' + "\"" + str(style["val"]) + "\""
                s = s + " />"
        except Exception as e:
            print(e)
        
        try:
            for path in backPaths:
                s = s + '<' + path["type"]
                for style in path["style"]:
                    s = s + " " + style["attr"] + '=' + "\"" + str(style["val"]) + "\""
                s = s + " />"
        except Exception as e:
            print(e)
            
        s = s + "</svg>"
        
        f2 = open('../static/svg/'+cat+'/'+key+'.svg','w')
        f2.write(s)
        
        #
    return

if __name__ == "__main__":
    print 'FaceQ'
    openFace('../static/faceq-hair.json')