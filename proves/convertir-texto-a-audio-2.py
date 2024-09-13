#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sun Nov 12 18:53:17 2023
@author: rafael
@description: Convierte texto a audio
"""
import sys
if sys.argv[0] == "./convertir-texto-a-audio-2.py":
   #Si se ejecuta desde una terminal
   sys.path.append('../..')
   import utilitats.colors as c
else:
   #Si se ejecuta desde un IDE que ya incluye la referencia al directorio utilitats
   import colors as c
import re, time
import pyttsx3

ArxiuEntrada = "entrades/pop-rapid-3-dani.txt"
DirSortida = "sortides/veu/"
ArxiuVeu = "popRapid-3.2"
Personatges = {'Toni'  :{'sexe':0, 'velocitat':20, 'genere':2, 'edat':40},
               'Dani'  :{'sexe':1, 'velocitat':25, 'genere':1, 'edat':35},
               'Gina'  :{'sexe':0, 'velocitat':20, 'genere':2, 'edat':20},
               'Laia'  :{'sexe':0, 'velocitat':20, 'genere':2, 'edat':22},
               'Albert':{'sexe':1, 'velocitat':30, 'genere':1, 'edat':27},
               'Fede'  :{'sexe':1, 'velocitat':20, 'genere':1, 'edat':25},
               'Oscar' :{'sexe':1, 'velocitat':30, 'genere':1, 'edat':42},
               'amic'  :{'sexe':1, 'velocitat':30, 'genere':1, 'edat':38}}
# parametres del to de veu
# frequencies entre 200Hz i 1050Hz
Narrador = {'sexe':1, 'velocitat':15, 'genere':1, 'edat':50}


def nom_arxiu(num):
   return DirSortida + ArxiuVeu + "_" + f'{num:{"0"}{">"}{3}}' + ".mp3"

def speak(engine, text):
   engine.say(text)
   engine.runAndWait()
   #engine.stop()

def mostraVeus(engine):
   # Cerca de veus, catalan = 6
   nveu = 0
   voices = engine.getProperty('voices')
   for voice in voices:
      nveu += 1
      if voice.id == 'catalan':
         print("gender:", voice.gender, ". age:", voice.age, ". languages:", voice.languages)
         engine.setProperty('voice', voice.id)
         break
   # engine.setProperty('voice', voices[nveu].id)

def text_to_audio(text, output_file, veu_params, ends):
   ini_color = c.CB_CYN if text in Personatges else c.C_NONE
   ini_color = c.CB_YLW if text == "Dani" else ini_color
   ini_color = c.BG_CYN+"\n" if text[:6] == "Escena" or text[:9] == "Pop ràpid" else ini_color
   print(ini_color+text+c.C_NONE, end=ends)

   #obtenir els parametres
   sexe, velocitat, genere, edat = list(veu_params.values())

   try:
      engine = pyttsx3.init('espeak')   # 'espeak', 'dummy'
      # mostraVeus(engine)
      engine.setProperty('voice', 'catalan')
      veu = pyttsx3.voice.Voice('catalan', name='catalan', gender=genere, age=edat)

      # Velocitat
      rate = engine.getProperty('rate')
      # print(c.C_BLU+"new rate:", rate-velocitat, c.C_NONE)
      engine.setProperty('rate', rate - velocitat)

      # Changing volume
      volume = engine.getProperty('volume')
      # print(c.C_BLU+"new volume:", volume+0.25, c.C_NONE)
      engine.setProperty('volume', volume+0.25)

      engine.save_to_file(text, output_file)
      engine.runAndWait()
      time.sleep(0.2)
      n = 0
      while engine.isBusy() and n < 100000:
         n += 1
      engine.stop()

   except Exception as ex:
      print(c.C_BLU+"ERROR:", ex, c.C_NONE)


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
