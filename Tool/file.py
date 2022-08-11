def removeComment():
    file = open("/Users/patch/Documents/project/patchclass/station2.json",'r')
    file2 = open("/Users/patch/Documents/project/patchclass/station3.json",'a')
    lines = file.readlines()
    for line in lines:
        if line.find('/*') == -1:
            file2.writelines([line])
    print('DONE')
    return
def check():
    file = open("/Users/patch/Documents/project/patchclass/station.json",'r')
    file2 = open("/Users/patch/Documents/project/patchclass/all.txt",'r')
    lines = file.readlines()
    db = []
    noshow = []

    name = ''
    for line in lines:
        if line.find('name') > -1:
            name = line[line.find('name')+9:len(line)-3]
            db.append(name)
    file.close()
    lines2 = file2.readlines()
    for line in lines2:
        has = 0
        for n in db:
            if line.find(n) > -1:
                has = 1
        if has == 0:
            print(line)
    file2.close()
    return


if __name__ == "__main__":
    #print str2md5('jieli360')
    #getDateNow('Asia/Shanghai')
    #getDateNow()
    #getDateNow('UTC')
    #getDateNow('America/Phoenix')
    #getDateNow('Europe/Berlin')
    #getDateNow('Asia/Hong_Kong')
    #getTimeZone('Beijing')
    removeComment()
    #check()
