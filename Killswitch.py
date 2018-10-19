#!venv/bin/python3

import logging
import classGetch
import datetime
import Screen
# import Pesee_Rework as pr


logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)
_consolelog = logging.StreamHandler()
_consolelog.setLevel(logging.DEBUG)
logger.addHandler(_consolelog)

validstamp = None
isFirst = True

inkey = classGetch._Getch()


def printkill():
    Screen.reset()
    Screen.msg_multi_lines([
        '1 - shutdown the SCALE',
        '2 - Cancel             '
        ], 'WARNING', 1)


def killemall(isfirst=False, cpt=0):
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
        print('secstq;p ' + str(secstamp))
        if(secstamp > datetime.timedelta(seconds=2)):
            print('breqk')
            cpt = 0
            validstamp = None
            killemall(True, 0)

    if(cpt < 4):
        while flagVal:
            if p == 'a' or p == 'q':
                print('ok = ' + str(cpt))
                flagVal = False
                validstamp = datetime.datetime.now()
                killemall(False, cpt + 1)
            # FIXME: A supprimer danger
            if p == 'c':
                logger.debug('shuting down...')
                exit()
            else:
                validstamp = None
                datetime.datetime.now()
                killemall(True, 0)
    else:
        printkill()
        while flagVal:
            print('loop')
            if p == 'd':
                print('end == kill = ' + str(cpt))
                flagVal = False
                print('shutdown')
                exit()

            else:
                validstamp = None
                datetime.datetime.now()
                killemall(True, 0)


def main():

    killemall(True)
    # pr.main()


if __name__ == '__main__':
    main()
# main()
