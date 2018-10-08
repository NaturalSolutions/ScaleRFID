#!/usr/bin/python 
# -*- coding:utf-8 -*-


import epd2in9
import epdif
import PIL


# errorArray = [PREPARATION_NOT_FOUND,
#                 PREPARATION_OUTDATED,
#                 BIRD_CHIP_NOT_FOUND,
#                 RFID_READER_NOT_FOUND,
#                 BIRD_ALREADY_WEIGHTED,
#                 EXCEL_FILE_CORRUPTED
#                 ]

epd = epd2in9.EPD()



def blank():
    temp = PIL.Image.new('RGB', (296,128), color = "white") #cree une image de 296*128 avec des couleurs RGB 
    temp.save('temp.jpg')
    image = PIL.Image.open('temp.jpg') #on peut creer une variable pour stocker le nom du fichier
    epd.set_frame_memory(image, 0, 0)
    epd.display_frame()
    epd.set_frame_memory(image, 0, 0)
    epd.display_frame() 


def error(error):
    print(error)
    temp = PIL.Image.new('RGB', (296,128), color = "white")
    draw = PIL.ImageDraw.Draw(temp)
    font = PIL.ImageFont.truetype("/home/pi/Desktop/ProjetRFID_Rework/DejaVuSans.ttf",30) #permet de choisir la olice et sa aille
    draw.text((00,00), text = error, fill = 100, font = font) #permet d'ecrire du texte
    temp = temp.rotate(270)
    temp.save('temp.jpg')
    image = PIL.Image.open('temp.jpg')
    epd.set_frame_memory(image, 0, 0)
    epd.display_frame()
    epd.set_frame_memory(image, 0, 0)
    epd.display_frame() 

################################################################################################

def numberBird(data):
    temp = PIL.Image.new('RGB', (296,128), color = "white")
    draw = PIL.ImageDraw.Draw(temp)
    font = PIL.ImageFont.truetype("/home/pi/Desktop/ProjetRFID_Rework/DejaVuSans.ttf",30)
    draw.text((00,00), text = data, fill = 100, font = font)
    temp = temp.rotate(270)
    temp.save('temp.jpg')
    image = PIL.Image.open('temp.jpg')
    epd.set_frame_memory(image, 0, 0)
    epd.display_frame()
    epd.set_frame_memory(image, 0, 0)
    epd.display_frame()  


def positionBird(data):
    temp = PIL.Image.new('RGB', (296,128), color = "white")
    draw = PIL.ImageDraw.Draw(temp)
    font = PIL.ImageFont.truetype("/home/pi/Desktop/ProjetRFID_Rework/DejaVuSans.ttf",30)
    draw.text((00,25), text = data, fill = 100, font = font)
    temp = temp.rotate(270)
    temp.save('temp.jpg')
    image = PIL.Image.open('temp.jpg')
    epd.set_frame_memory(image, 0, 0)
    epd.display_frame()
    epd.set_frame_memory(image, 0, 0)
    epd.display_frame()  
    
def weightBird(data):
    temp = PIL.Image.new('RGB', (296,128), color = "white")
    draw = PIL.ImageDraw.Draw(temp)
    font = PIL.ImageFont.truetype("/home/pi/Desktop/ProjetRFID_Rework/DejaVuSans.ttf",30)
    draw.text((00,50), text = data, fill = 100, font = font)
    temp = temp.rotate(270)
    temp.save('temp.jpg')
    image = PIL.Image.open('temp.jpg')
    epd.set_frame_memory(image, 0, 0)
    epd.display_frame()
    epd.set_frame_memory(image, 0, 0)
    epd.display_frame()    

def resultWetghing(data):
    temp = PIL.Image.new('RGB', (296,128), color = "white")
    draw = PIL.ImageDraw.Draw(temp)
    font = PIL.ImageFont.truetype("/home/pi/Desktop/ProjetRFID_Rework/DejaVuSans.ttf",30)
    draw.text((00,75), text = data, fill = 100, font = font)
    temp = temp.rotate(270)
    temp.save('temp.jpg')
    image = PIL.Image.open('temp.jpg')
    epd.set_frame_memory(image, 0, 0)
    epd.display_frame()
    epd.set_frame_memory(image, 0, 0)
    epd.display_frame()       


