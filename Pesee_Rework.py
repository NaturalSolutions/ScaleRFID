#!/usr/bin/env python3
# coding: utf-8

import sys
import re
import time
import datetime

import serial
# import sqlite3
import DB
# import RPi.GPIO as GPIO
import Export
import Screen

from settings import logger
import classState
import classGetch

# 'Intialisation des ecrans'
Screen.reset()

##############################################

# 'Demarrage du systeme'
Screen.demarrage_du_systeme()

# 'Variables'

# * means all if need specific format then *.db
# list_of_files = glob.glob('/home/pi/Share/Public/*.db')
# if len(list_of_files)== 0:
#       Screen.msg('Database not found', 'ERROR', True)
#       exit()
# latest_file = max(list_of_files, key=os.path.getctime)
# dbPath = latest_file
# TODO: dynamicfilename
# filename= 'WeightsFile_201801011.csv'
csvOutPath = '/home/pi/Share/Public/releve.csv'

Ink_Ring = ''
Ink_Position = ''
Ink_Weight = ''
Ink_Last_Weight = ''
Ink_State = ''
Ink_Day_Since = ''

Weight = ''


# dbExists = os.path.isfile(dbPath)
# if dbExists == False:
#       Screen.msg('Database not found', 'ERROR', True)
#
#       faa = Image.new('RGB', (296,128), color = 'white')
#       draw1 = ImageDraw.Draw(faa)
#       font1 = ImageFont.truetype(
#            os.path.join(ASSETS, 'DejaVuSans.ttf', 20)
#       draw1.text((00, 00), 'ERROR', fill=100, font=font1)
#       draw1.text((00, 30), 'Database Not Found', fill=100, font=font1)
#       faa = faa.rotate(270)
#       faa.save('1.jpg')
#       image = Image.open('1.jpg')
#       epd.set_frame_memory(image, 0, 0)
#       epd.display_frame()
#       epd.set_frame_memory(image, 0, 0)
#       epd.display_frame()
#       sys.exit()

# session = DB.createDB(dbPath)
dbinfos = DB.testSession()
# s = session
# if DB.testSession(s) == False:
#       exit()
s = dbinfos['session']
dbPath = dbinfos['file']
filename = dbinfos['export_file_name']

inkey = classGetch._Getch()

# date_access = DB.Log(Date = datetime.datetime.now())
# s.add(date_access)


# 'Fonctions'


def testIfEntryExists(testPresence):
    # Verification de la presence de l'outade dans la base de donnees
    # et si elle a deja ete pese, regarde environ 30000 outardes
    global languageChoice
    if testPresence is None:
        return {'isNew': False}
    elif testPresence.Weight is not None:
        return {'isNew': False}
    else:
        return {'isNew': True}


def testWeight(ref, WeightMes):
    # Test de la pesee pour voir si l'animal a un poids pathologique
    # ou impossible pour eviter d'enregistreer des valeurs incoherentes
    # et prevenir les maladies possibles de facon independante

    global languageChoice

    if WeightMes < ref.Weight_Min_Imp:
        return classState.State.rejeted
    elif WeightMes > ref.Weight_Max_Imp:
        return classState.State.rejeted
    elif WeightMes < ref.Weight_Min_Path and WeightMes > ref.Weight_Min_Imp:
        return classState.State.pendingLow
    elif WeightMes > ref.Weight_Max_Path and WeightMes < ref.Weight_Max_Imp:
        return classState.State.pendingHigh
    else:
        return classState.State.accepted


def recupUID(uid):
    uid = str(uid)
    start = '$A0112OKD'
    end = '#'
    logger.debug('luid . ' + uid)
    # try:
    uid = (uid.split(start))[1].split(end)[0]
    # except Exception:
    #     return None

    # if len(uid) >= 16:
    uid = uid[0:15]
    logger.debug(uid)

    return uid


def recupWeight(Weight):
    global languageChoice
    WeightStr = str(Weight)
    WeightDB = float(WeightStr)
    WeightStr = str(WeightDB)
    return WeightDB


# def ink(ring, position, weight, state):
#       foo = Image.new('RGB', (296,128), color = 'white')
#       draw1 = ImageDraw.Draw(foo)
#       font1 = ImageFont.truetype(os.path.join(ASSETS, 'DejaVuSans.ttf'),26)  # noqa: E501
#       font2 = ImageFont.truetype(os.path.join(ASSETS, 'DejaVuSans-Bold.ttf'), 20)  # noqa: E501
#       draw1.text((00,00), ' ' + ring, fill = 0, font = font1)
#       draw1.text((00,25), ' ' + position, fill = 0, font = font1)
#       draw1.text((00,50), ' ' + weight + 'g', fill = 0, font = font1)
#       draw1.text((00,75), ' ' + state , fill = 0, font = font2)
#       foo = foo.rotate(270)
#       foo.save('1.jpg')
#       image = Image.open('1.jpg')
#       epd.set_frame_memory(image, 0, 0)
#       epd.display_frame()
#       epd.set_frame_memory(image, 0, 0)
#       epd.display_frame()

# def reset():
#       faa = Image.new('RGB', (296,128), color = 'white')
#       draw1 = ImageDraw.Draw(faa)
#       font1 = ImageFont.truetype(os.path.join(ASSETS, 'DejaVuSans.ttf'),34)  # noqa: E501
#       draw1.text((00,00), 'READY', fill = 100, font = font1)
#       faa = faa.rotate(270)
#       faa.save('1.jpg')
#       image = Image.open('1.jpg')
#       epd.set_frame_memory(image, 0, 0)
#       epd.display_frame()
#       epd.set_frame_memory(image, 0, 0)
#       epd.display_frame()


# '''Verification date de la base de donnees'''

Ink_Ring = ''
Ink_Position = ''
Ink_Weight = ''
Ink_State = ''


def remarks():
    Screen.msg_multi_lines([
        '1 - No remark',
        '2 - Skinny',
        '3 - Fat',
        '4 - Other problem'
        ], 'ACTION', 7)
    flagVal = True
    p = inkey()

    while flagVal:
        if p in {'a', 'q'}:
            flagVal = False
            return ''
        elif p == 'b':
            flagVal = False
            return 'Skinny'
        elif p == 'c':
            flagVal = False
            return 'Fat'
        elif p == 'd':
            flagVal = False
            return 'Some problem have been noticed'


# Test des affichages a suppr 0 interets
# def screenmethis():
#     logger.debug('reset')
#     epd.clear_frame_memory(0xFF)
#     epd.display_frame()
#     time.sleep(2)
#     logger.debug('endreset')
#     logger.debug('grande taille : ' + str(len('Bird chip not in database')))
#     Screen.msg('Bird chip not in database', 'ERROR', True)
#     time.sleep(2)
#     Screen.msg('Bird chip not in database', 'ERROR', True)
#     time.sleep(2)
#     logger.debug(
#         'grande taille : ' + str(len('Bird position not in database')))
#     Screen.msg('Bird position not in database', 'ERROR', True)
#     time.sleep(2)
#     Screen.msg('Bird already weighted', 'ERROR', True)
#     time.sleep(2)
#     Screen.msg('Bird chip not in database', 'ERROR', True)
#     time.sleep(2)
#     exit()


def printkill():
    Screen.reset()
    Screen.msg_multi_lines([
        '1 - shutdown the SCALE',
        '2 - Cancel             '
        ], 'WARNING', 1)


# screenmethis()
# #FINB TEst affichage Normal
# #Tes affichage multi ligne full info outardes
def screen_my_bustard():
    Screen.msg('Bloupi machine plus plus', 'Boulp', 0)
    time.sleep(2)
    Screen.msg('Bloupi machine plus plus', 'Boulp', 1)

    # Screen.msg_multi_lines([
    #     'Boulp',
    #     'Bloupi machine plus plus',
    #     'Le bigorno des pres n est pas propre'
    #     ], 'Olala l\'erreur', True)
    exit()
# screen_my_bustard()


logger.debug('hard')
Screen.hard_reset()
logger.debug('endhard')
# screen_my_bustard()
# #Fin test multi ligne
try:
    serLec = serial.Serial('/dev/ttyUSB0', 9600, timeout=1)  # Lecteur
except serial.SerialException:
    Screen.msg('RFID Reader Disconnected', 'ERROR', True)
    sys.exit()

# Fermeture des ports pour les ouvrir seulement quand necessaire
# pour eviter le stack de donnees
serLec.close()


###############################################################################
def main():
    logger.debug('start weight')
    while True:
        Screen.reset()
        Screen.msg('Scan ready')
        Export.export(dbPath, filename)
        serLec.close()
        flagLec = True

        def get_bird(uid):
            try:
                strUid = recupUID(uid)
                # FIXME: define strUid set
                strUid = str(strUid).strip()
            except Exception as e:
                return {'error': 'exit', 'message': str(e)}

            # if strUid == None:
            #       Screen.msg('Please scan again','ERROR',True)
            #       sleep(1)
            #       break
            logger.debug('struid  = ' + strUid)

            # Recherche de l'individu dans la database
            # et recuperation de ses infos
            bird_data = s.query(DB.Session)\
                         .filter(DB.Session.ID_RFID == strUid)\
                         .first()
            return bird_data

        def on_detect_uid(uid):
            logger.debug('uid : ' + str(uid))
            Ink_Ring = ''
            Ink_Position = ''
            Ink_Weight = ''
            Ink_State = ''

            bird_data = get_bird(uid)

            if bird_data is None:
                e = 'Bird Chip Not In Database'
                Screen.msg(e, 'ERROR', 1)
                return {'action': 'exit_loop', 'message': e}

            logger.debug('bird_data', bird_data)

            try:
                # test en double
                Ink_Ring = str(bird_data.ID_Reneco)
            except AttributeError:
                Screen.msg('Bird Chip Not In Database', 'ERROR', 1)
                # break

            try:
                Ink_Position = str(bird_data.Position)
            except AttributeError:
                e = 'Bird Position Not In Database'
                Screen.msg(e, 'ERROR', 1)
                return {'action': 'exit_loop', 'message': str(e)}

            Ink_Day_Since = str(bird_data.Days_Since_Last_Weight)
            Ink_Last_Weight = str(bird_data.Last_Weight)
            logger.debug('Ink_Day_Since  ' + Ink_Day_Since)
            logger.debug('Ink_Last_Weight   ' + Ink_Last_Weight)

            try:
                Ink_Weight = str(bird_data.Weight)
                if Ink_Weight != 'None':
                    Screen.msg('Bird Already Weighed', 'NOTICE', 1)
                    return {'error'}
                if Ink_Weight == 'None':
                    Ink_Weight = ''
            except AttributeError:
                e = 'Bird Chip Not In Database'
                Screen.msg(e, 'ERROR', 1)
                return {'action': 'exit_loop', 'message': e}

            Screen.bird_it(
                Ink_Ring, Ink_Position, Ink_Last_Weight, Ink_Day_Since)
            result = testIfEntryExists(bird_data)

            logger.debug('result: %s', result)

            if (result['isNew']):
                flagBal = True
                Weight = ''
                # Boucle de lecture de la balance
                while flagBal:
                    time.sleep(1)
                    # try:
                    #     #   Weight = raw_input()
                    Weight = Ink_Last_Weight
                    # except EOFError:
                    #     pass
                    if Weight:
                        flagBal = False
                        strWeight = str(Weight)
                        logger.debug(strWeight)
                        # Conversion binaire to string pour pce
                        # On garde que le nombre int
                        intWeight = int(
                            re.findall(r'\d+', strWeight)[0])
                        strWeight = str(intWeight)

                        # Si on detecte un poids
                        if len(strWeight) >= 0:
                            WeightDB = recupWeight(strWeight)
                            valid = testWeight(bird_data, WeightDB)
                            Ink_Weight = strWeight
                            if (valid == classState.State.accepted):
                                Ink_State = 'OK'
                                Screen.bird_it(
                                    Ink_Ring, Ink_Position,
                                    Ink_Last_Weight, Ink_Day_Since,
                                    Ink_Weight, Ink_State)
                                time.sleep(2)
                                current_remark = remarks()
                                s.query(DB.Session)\
                                 .filter(
                                     DB.Session.ID_RFID == bird_data.ID_RFID  # noqa: E501
                                     )\
                                 .update({
                                     'Weight': WeightDB,
                                     'Date': datetime.datetime.now(),
                                     'Note': current_remark})
                                s.commit()
                            if (valid in {
                                    classState.State.pendingLow,
                                    classState.State.pendingHigh}):

                                if valid == classState.State.pendingLow:
                                    Ink_State = 'LOW WEIGHT'

                                if valid == classState.State.pendingHigh:
                                    Ink_State = 'HIGH WEIGHT'

                                Screen.bird_it(
                                    Ink_Ring, Ink_Position,
                                    Ink_Last_Weight, Ink_Day_Since,
                                    Ink_Weight, Ink_State)
                                time.sleep(2)
                                flagVal = True
                                Screen.msg_multi_lines([
                                    '1 - OK',
                                    '4 - Cancel'
                                    ], 'ACTION', 7)
                                p = inkey()
                                while flagVal:
                                    if p in {'a', 'q'}:
                                        flagVal = False
                                        Ink_State = 'OK'
                                        Screen.bird_it(
                                            Ink_Ring, Ink_Position,
                                            Ink_Last_Weight,
                                            Ink_Day_Since,
                                            Ink_Weight, Ink_State)
                                        time.sleep(2)
                                        current_remark = remarks()
                                        s.query(DB.Session)\
                                         .filter(
                                             DB.Session.ID_RFID == bird_data.ID_RFID  # noqa: E501
                                            )\
                                         .update({
                                             'Weight': WeightDB,
                                             'Date': datetime.datetime.now(),  # noqa: E501
                                             'Note': current_remark})
                                        s.commit()
                                    if p == 'd':
                                        flagVal = False
                                        Ink_State = 'WEIGHT CANCELLED'
                                        Screen.bird_it(
                                            Ink_Ring, Ink_Position,
                                            Ink_Last_Weight,
                                            Ink_Day_Since, Ink_Weight,
                                            Ink_State)
                            if (valid == classState.State.rejeted):
                                logger.debug('9.3')
                                Ink_State = 'IMPOSSIBLE WEIGHT'
                                Screen.bird_it(
                                    Ink_Ring, Ink_Position,
                                    Ink_Last_Weight, Ink_Day_Since,
                                    Ink_Weight, Ink_State)
            else:
                Screen.result_not_new()
                return {'action': 'exit_loop',
                        'message': 'result not new'}

        # Boucle de lecture du scanner
        while flagLec:
            serLec.open()
            uid = serLec.readline(100)
            serLec.close()
            # Si on detecte un uid
            if uid:
                flagLec = False
                serLec.close()
                result = on_detect_uid(uid)
                if result['action'] == 'exit_loop':
                    logger.debug(result)
                    break

            logger.debug('fin')
            Export.export(dbPath, filename)
            time.sleep(3)


if __name__ == '__main__':
    main()
    while True:
        try:
            main()
        except KeyboardInterrupt:
            sys.exit()
        except Exception:
            pass
