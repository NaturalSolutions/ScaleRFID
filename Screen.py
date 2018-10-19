#!/usr/bin/env python3

import os
import epd2in9
# import epdif
# import PIL
from PIL import Image, ImageDraw, ImageFont
from settings import ASSETS  # , logger


icon_details = {
    0: u'\u26A0',  # error
    1: u'\u261B',  # notice
    3: u'\u2460',  # petit 1
    4: u'\u2461',  # petit 2
    5: u'\u2462',  # petit 3
    6: u'\u2463',  # petit 4
    7: u'\u27A0'   # action
}
# errorArray = [PREPARATION_NOT_FOUND,
#                 PREPARATION_OUTDATED,
#                 BIRD_CHIP_NOT_FOUND,
#                 RFID_READER_NOT_FOUND,
#                 BIRD_ALREADY_WEIGHTED,
#                 EXCEL_FILE_CORRUPTED
#                 ]

epd = epd2in9.EPD()
epd.init(epd.lut_partial_update)


def reset():
    epd.reset()


def blank():
    # cree une image de 296*128 avec des couleurs RGB
    temp = Image.new('RGB', (296, 128), color='white')
    temp.save('temp.jpg')
    # on peut creer une variable pour stocker le nom du fichier
    image = Image.open('temp.jpg')
    epd.set_frame_memory(image, 0, 0)
    epd.display_frame()
    epd.set_frame_memory(image, 0, 0)
    epd.display_frame()


def getPoliceSize(strToParse):
    if(len(strToParse) < 16):
        return 30
    elif(len(strToParse) < 28):
        return 20
    else:
        return 15


def error(error, label=None):
    print(error)
    temp = Image.new('RGB', (296, 128), color='white')
    draw = ImageDraw.Draw(temp)
    offset = 0
    font_size = getPoliceSize(error)
    # permet de choisir la olice et sa aille
    font = ImageFont.truetype(
        os.path.join(ASSETS, 'DejaVuSans.ttf'), 30)
    # permet de choisir la olice et sa aille
    font_calculated = ImageFont.truetype(
        os.path.join(ASSETS, 'DejaVuSans.ttf'), font_size)
    if label is not None:
        # permet d'ecrire du texte
        draw.text((00, 00), text=label, fill=100, font=font)
        offset = 30

    # permet d'ecrire du texte
    draw.text((00, offset), text=error, fill=100, font=font_calculated)
    temp = temp.rotate(270)
    temp.save('temp.jpg')
    image = Image.open('temp.jpg')
    epd.set_frame_memory(image, 0, 0)
    epd.display_frame()
    epd.set_frame_memory(image, 0, 0)
    epd.display_frame()


def msg(str_msg, label=None, icon=None):
    print(str_msg)
    temp = Image.new('RGB', (296, 128), color='white')
    draw = ImageDraw.Draw(temp)
    offset = 0
    font_size = getPoliceSize(str_msg)
    # permet de choisir la olice et sa aille
    font = ImageFont.truetype(
        os.path.join(ASSETS, 'DejaVuSans.ttf'), 30)
    # permet de choisir la olice et sa aille
    font_calculated = ImageFont.truetype(
        os.path.join(ASSETS, 'DejaVuSans.ttf'), font_size)
    if label is not None:
        if(icon is not None):
            override_label = icon_details[icon] + label
        else:
            override_label = label
        # permet d'ecrire du texte
        draw.text((00, 00), text=override_label, fill=100, font=font)
        offset = 30

    # permet d'ecrire du texte
    draw.text((00, offset), text=str_msg, fill=100, font=font_calculated)
    temp = temp.rotate(270)
    temp.save('temp.jpg')
    image = Image.open('temp.jpg')
    epd.set_frame_memory(image, 0, 0)
    epd.display_frame()
    epd.set_frame_memory(image, 0, 0)
    epd.display_frame()


def msg_multi_lines(lines, label=None, icon=None):
    temp = Image.new('RGB', (296, 128), color='white')
    draw = ImageDraw.Draw(temp)
    offset = 0
    offset_cpt = 0
    font_size_force = None
    # font_size = getPoliceSize(str_msg)
    # permet de choisir la olice et sa aille
    font = ImageFont.truetype(
        os.path.join(ASSETS, 'DejaVuSans.ttf'), 30)
    # permet de choisir la olice et sa aille  # noqa: E501
    # font_calculated = ImageFont.truetype(
    #     os.path.join(ASSETS, 'DejaVuSans.ttf'), font_size)
    if label is not None:
        if(icon is not None):
            override_label = icon_details[icon] + label
        else:
            override_label = label
        # permet d'ecrire du texte
        draw.text((00, 00), text=override_label, fill=100, font=font)
        offset = 30
        offset_cpt = 30
    if(len(lines) > 3):
        # draw.text((00,offset), text = ' ', fill = 100, font = font) #permet d'ecrire du texte  # noqa: E501
        offset_cpt = 20
        font_size_force = 20
    for str_line in lines:
        font_size = (font_size_force
                     if font_size_force is not None
                     else getPoliceSize(str_line))
        print('boulasse   z    ' + str(font_size))
        # permet de choisir la olice et sa aille
        font_calculated = ImageFont.truetype(
            os.path.join(ASSETS, 'DejaVuSans.ttf'), font_size)
        # permet d'ecrire du texte
        draw.text((00, offset), text=str_line, fill=100, font=font_calculated)
        offset += offset_cpt
    temp = temp.rotate(270)
    temp.save('temp.jpg')
    image = Image.open('temp.jpg')
    epd.set_frame_memory(image, 0, 0)
    epd.display_frame()
    epd.set_frame_memory(image, 0, 0)
    epd.display_frame()


def bird_it_old(ring, position, weight, state):
    foo = Image.new('RGB', (296128), color='white')
    draw1 = ImageDraw.Draw(foo)
    font1 = ImageFont.truetype(
        os.path.join(ASSETS, 'DejaVuSans.ttf'), 26)
    font2 = ImageFont.truetype(
        os.path.join(ASSETS, 'DejaVuSans-Bold.ttf'), 20)
    draw1.text((00, 00), ' ' + ring, fill=0, font=font1)
    draw1.text((00, 25), ' ' + position, fill=0, font=font1)
    draw1.text((00, 50), ' ' + weight + 'g', fill=0, font=font1)
    draw1.text((00, 75), ' ' + state, fill=0, font=font2)
    foo = foo.rotate(270)
    foo.save('1.jpg')
    image = Image.open('1.jpg')
    epd.set_frame_memory(image, 0, 0)
    epd.display_frame()
    epd.set_frame_memory(image, 0, 0)
    epd.display_frame()


def bird_it(ring, position, weight, days, new_weight=None, new_state=None):
    foo = Image.new('RGB', (296, 128), color='white')
    draw1 = ImageDraw.Draw(foo)
    font1 = ImageFont.truetype(
        os.path.join(ASSETS, 'DejaVuSans.ttf'), 18)
    font2 = ImageFont.truetype(
        os.path.join(ASSETS, 'DejaVuSans-Bold.ttf'), 20)
    font3 = ImageFont.truetype(
        os.path.join(ASSETS, 'DejaVuSans-Bold.ttf'), 24)
    draw1.text((00, 00), ring, fill=0, font=font3)
    draw1.text((00, 30), position, fill=0, font=font2)
    if(weight not in {None, ''}):
        # draw1.text((180,02),'Last : ' + weight + 'g', fill = 0, font = font1)
        draw1.text((180, 2), 'Last : ' + weight + 'g', fill=0, font=font1)
        draw1.text((180, 32), 'Days : ' + days, fill=0, font=font1)

    if(new_weight is not None):
        draw1.text((00, 60), new_weight + 'g', fill=0, font=font3)
        draw1.text((00, 90), new_state, fill=0, font=font2)
    # weight_line = 'Last weight : ' + str(weight) + 'g'
    # # font_size = getPoliceSize(weight_line)
    # permet de choisir la olice et sa aille  # noqa: E501
    # font_calculated = ImageFont.truetype(
    #     os.path.join(ASSETS, 'DejaVuSans.ttf'), 20)
    # draw1.text((00,50), weight_line, fill = 0, font = font_calculated)
    # days_line = 'Days since last weight : ' + str(days)
    # # font_size = getPoliceSize(days_line)
    # permet de choisir la olice et sa aille  # noqa: E501
    # font_calculated = ImageFont.truetype(
    #     os.path.join(ASSETS, 'DejaVuSans.ttf'), 18)
    # draw1.text((00, 75), 'Days since last weight : ' + str(days),
    #            fill = 0, font = font_calculated)
    foo = foo.rotate(270)
    foo.save('1.jpg')
    image = Image.open('1.jpg')
    epd.set_frame_memory(image, 0, 0)
    epd.display_frame()
    epd.set_frame_memory(image, 0, 0)
    epd.display_frame()

##############################################################################


def numberBird(data):
    temp = Image.new('RGB', (296, 128), color='white')
    draw = ImageDraw.Draw(temp)
    font = ImageFont.truetype(
        os.path.join(ASSETS, 'DejaVuSans.ttf'), 30)
    draw.text((00, 00), text=data, fill=100, font=font)
    temp = temp.rotate(270)
    temp.save('temp.jpg')
    image = Image.open('temp.jpg')
    epd.set_frame_memory(image, 0, 0)
    epd.display_frame()
    epd.set_frame_memory(image, 0, 0)
    epd.display_frame()


def positionBird(data):
    temp = Image.new('RGB', (296, 128), color='white')
    draw = ImageDraw.Draw(temp)
    font = ImageFont.truetype(
        os.path.join(ASSETS, 'DejaVuSans.ttf'), 30)
    draw.text((00, 25), text=data, fill=100, font=font)
    temp = temp.rotate(270)
    temp.save('temp.jpg')
    image = Image.open('temp.jpg')
    epd.set_frame_memory(image, 0, 0)
    epd.display_frame()
    epd.set_frame_memory(image, 0, 0)
    epd.display_frame()


def weightBird(data):
    temp = Image.new('RGB', (296, 128), color='white')
    draw = ImageDraw.Draw(temp)
    font = ImageFont.truetype(
        os.path.join(ASSETS, 'DejaVuSans.ttf'), 30)
    draw.text((00, 50), text=data, fill=100, font=font)
    temp = temp.rotate(270)
    temp.save('temp.jpg')
    image = Image.open('temp.jpg')
    epd.set_frame_memory(image, 0, 0)
    epd.display_frame()
    epd.set_frame_memory(image, 0, 0)
    epd.display_frame()


def resultWetghing(data):
    temp = Image.new('RGB', (296, 128), color='white')
    draw = ImageDraw.Draw(temp)
    font = ImageFont.truetype(
        os.path.join(ASSETS, 'DejaVuSans.ttf'), 30)
    draw.text((00, 75), text=data, fill=100, font=font)
    temp = temp.rotate(270)
    temp.save('temp.jpg')
    image = Image.open('temp.jpg')
    epd.set_frame_memory(image, 0, 0)
    epd.display_frame()
    epd.set_frame_memory(image, 0, 0)
    epd.display_frame()
