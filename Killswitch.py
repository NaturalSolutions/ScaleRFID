import classGetch
import datetime
import Screen

validstamp = None
isFirst = True
inkey = classGetch._Getch()

def printkill():
    Screen.reset()
    Screen.msg_multi_lines(['1 - shutdown the SCALE', '2 - Cancel             '],'WARNING', 1)


def killemall(isfirst, cpt = 0):
    # inkey = classGetch._Getch()
    print('zoulch ' + str(isfirst))
    p = inkey()
    flagVal = True
    global validstamp
    if(isfirst):
        validstamp = datetime.datetime.now()
    else:
        compstamp = datetime.datetime.now()
        secstamp = (compstamp - validstamp)
        print('secstq;p '  + str(secstamp))
        if(secstamp > datetime.timedelta(seconds = 2)):
            print('breqk')
            cpt = 0
            validstamp = None
            killemall(True,0) 
            
    if(cpt < 4):
        while flagVal:
                if p == 'a'
                    print('ok = ' + str(cpt))
                    flagVal = False
                    validstamp = datetime.datetime.now()
                    killemall(False, cpt +1)  
                """A supprimer danger"""
                if p == 'c':
                    exit()              
                else:
                    validstamp = None
                    datetime.datetime.now()
                    killemall(True, 0)
    else:
        printkill()
        while flagVal:
                if p == 'd':
                    print('end == kill = ' + str(cpt))
                    flagVal = False
                    exit() 
                else:
                    validstamp = None
                    datetime.datetime.now()
                    killemall(True,0) 

def main():

    killemall(True)

main()