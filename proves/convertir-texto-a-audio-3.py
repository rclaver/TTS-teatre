#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sun Nov 12 18:53:17 2023
@author: rafael
@description: Convierte texto a audio
"""
import sys
if sys.argv[0] == "./convertir-texto-a-audio-3.py":
   #Si se ejecuta desde una terminal
   sys.path.append('../..')
   import utilitats.colors as c
else:
   #Si se ejecuta desde un IDE que ya incluye la referencia al directorio utilitats
   import colors as c
import os, re
from gtts import gTTS
from pydub import AudioSegment
import soundfile as sf
import pyworld as pw
# import pygame
# from pygame import mixer

ArxiuEntrada = "entrades/pop-rapid-3-dani.txt"
DirSortida = "sortides/veu/"
tmp3 = DirSortida + "temp.mp3"
twav = DirSortida + "temp.wav"
ArxiuVeu = "popRapid-3"
Personatges = {'Dani'  :{'speed':1.00, 'grave':2.0, 'reduction':1},
               'Gina'  :{'speed':1.02, 'grave':0.8, 'reduction':1},
               'Laia'  :{'speed':1.00, 'grave':1.0, 'reduction':1},
               'Toni'  :{'speed':1.00, 'grave':0.9, 'reduction':1},
               'Albert':{'speed':1.00, 'grave':1.5, 'reduction':1},
               'Fede'  :{'speed':1.00, 'grave':1.5, 'reduction':1},
               'Oscar' :{'speed':1.00, 'grave':1.5, 'reduction':1},
               'amic'  :{'speed':1.00, 'grave':1.5, 'reduction':1}}
Narrador = {'speed':1.20, 'grave':2.5, 'reduction':0.7}


def nom_arxiu(num):
   return DirSortida + ArxiuVeu + "_" + f'{num:{"0"}{">"}{3}}' + ".wav"


def text_to_audio(text, output_file, veu_params, ends):
   ini_color = c.CB_CYN if text in Personatges else c.C_NONE
   ini_color = c.CB_YLW if text == "Dani" else ini_color
   ini_color = c.BG_CYN+"\n" if text[:6] == "Escena" or text[:9] == "Pop ràpid" else ini_color
   print(ini_color+text+c.C_NONE, end=ends)

   #obtenir els parametres
   speed, grave, reduction = list(veu_params.values())

   # Generar un arxiu d'audio temporal amb gTTS
   tts = gTTS(text, lang='ca')
   tts.save(tmp3)

   # Convertir l'arxiu mp3 a wav
   audio = AudioSegment.from_mp3(tmp3)
   audio.export(twav, format="wav")

   # tractament de l'audio
   x, fs = sf.read(twav)
   f0, sp, ap = pw.wav2world(x, fs)
   yy = pw.synthesize(f0/grave, sp/reduction, ap, fs/speed, pw.default_frame_period)
   sf.write(output_file, yy, fs)

   # Eliminar l'arxiu temporal
   if os.path.isfile(tmp3):
      os.remove(tmp3)
   if os.path.isfile(output_file):
      os.remove(twav)
   elif os.path.isfile(twav):
      os.rename(twav, output_file)


if __name__ == "__main__":
   patt_person = "^(\w*?\s?\d*)(:\s?)(.*$)"
   patt_narrador = "([^\(]*)(\(.*?\))(.*)"
   sentencies = open(ArxiuEntrada, 'r', encoding="utf-8").read().split('\n')

   n = 0
   for sentencia in sentencies:
      if sentencia:
         n += 1
         # extraer el personaje ma(1) y el texto ma(3)
         ma = re.match(patt_person, sentencia)
         if ma:
            text = ma.group(1)
            text_to_audio(text, nom_arxiu(n), Narrador, ": ")
            to_veu = Personatges[text] if text in Personatges else Narrador
            # extraer, del texto ma(3), los comentarios del narrador
            mb = re.match(patt_narrador, ma.group(3))
            if mb and mb.group(1) and mb.group(2) and mb.group(3):
               n += 1
               text_to_audio(mb.group(1), nom_arxiu(n), to_veu, " ")
               n += 1
               text_to_audio(mb.group(2), nom_arxiu(n), Narrador, " ")
               n += 1
               text_to_audio(mb.group(3), nom_arxiu(n), to_veu, "\n")
            elif mb and mb.group(1) and mb.group(2):
               n += 1
               text_to_audio(mb.group(1), nom_arxiu(n), to_veu, " ")
               n += 1
               text_to_audio(mb.group(2), nom_arxiu(n), Narrador, "\n")
            elif mb and mb.group(2) and mb.group(3):
               n += 1
               text_to_audio(mb.group(2), nom_arxiu(n), Narrador, " ")
               n += 1
               text_to_audio(mb.group(3), nom_arxiu(n), to_veu, "\n")
            else:
               n += 1
               text_to_audio(ma.group(3), nom_arxiu(n), to_veu, "\n")

         else:
            text_to_audio(sentencia, nom_arxiu(n), Narrador, "\n")
