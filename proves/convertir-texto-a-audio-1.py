#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sun Nov 12 18:53:17 2023
@author: rafael
@description: Convierte texto a audio

bibliotecas requeridas:
pip install gTTS
pip install pydub
"""
import sys
if sys.argv[0] == "./convertir-texto-a-audio-1.py":
   #Si se ejecuta desde una terminal
   sys.path.append('../..')
   import utilitats.colors as c
else:
   #Si se ejecuta desde un IDE que ya incluye la referencia al directorio utilitats
   import colors as c
import os, re
from gtts import gTTS
from pydub import AudioSegment
#from pydub.playback import play

ArxiuMp3 = None
ArxiuEntrada = "entrades/pop-rapid-3-dani.txt"
DirSortida = "sortides/rumors/mp3/"
tmp3 = DirSortida + "temp.mp3"
ArxiuVeu = "popRapid-3"
Personatges = {'Dani'  :{'pitch':0.75, 'speed':0.58, 'alt':1700, 'baix':1400},
               'Gina'  :{'pitch':1.20, 'speed':0.58, 'alt':700, 'baix':700},
               'Laia'  :{'pitch':1.15, 'speed':0.57, 'alt':900, 'baix':850},
               'Toni'  :{'pitch':0.95, 'speed':0.53, 'alt':1000, 'baix':900},
               'Albert':{'pitch':1.00, 'speed':0.53, 'alt':1100, 'baix':1100},
               'Fede'  :{'pitch':0.85, 'speed':0.58, 'alt':1400, 'baix':1000},
               'Oscar' :{'pitch':0.85, 'speed':0.51, 'alt':1200, 'baix':1150},
               'amic'  :{'pitch':0.95, 'speed':0.51, 'alt':1100, 'baix':1050}}
# parametres del to de veu. Frequencies entre 200Hz i 1050Hz
Narrador = {'pitch':0.80, 'speed':0.65, 'alt':2000, 'baix':1800}


def nom_arxiu(num):
   return DirSortida + ArxiuVeu + "_" + f'{num:{"0"}{">"}{3}}' + ".mp3"


def text_to_audio(text, output_file, veu_params, ends):
   global ArxiuMp3
   ini_color = c.CB_CYN if text in Personatges else c.C_NONE
   ini_color = c.CB_YLW if text == "Dani" else ini_color
   ini_color = c.BG_CYN+"\n" if text[:6] == "Escena" or text[:9] == "Pop ràpid" else ini_color
   print(ini_color+text+c.C_NONE, end=ends)

   #obtenir els parametres
   pitch, speed, alt, baix = list(veu_params.values())

   # Generar un arxiu d'audio temporal amb gTTS
   tts = gTTS(text, tld='cat', lang='ca')
   tts.save(tmp3)

   # Carregar l'arxiu d'audio i ajustar la frequencia (pitch)
   audio = AudioSegment.from_mp3(tmp3)
   try:
      metadata = {
            'sample_width': audio.sample_width,
            'frame_rate': int(audio.frame_rate * pitch),
            'frame_width': audio.frame_width,
            'channels': audio.channels
        }
      audio = audio._spawn(audio.raw_data, overrides=metadata)
      audio = audio.speedup(playback_speed=speed)
      audio = audio.high_pass_filter(cutoff=alt)
      audio = audio.low_pass_filter(cutoff=baix)
      # audio += AudioSegment.empty()

      # Guardar l'arxiu d'audio ajustat
      audio.export(output_file, format="mp3")
      ArxiuMp3 = audio if not ArxiuMp3 else ArxiuMp3 + audio

      # Reproduir l'audio
      #play(audio)
   except Exception as ex:
      print(c.C_BLU+"ERROR:", ex, c.C_NONE)

   # Eliminar l'arxiu temporal
   if os.path.isfile(output_file):
      os.remove(tmp3)
   elif os.path.isfile(tmp3):
      os.rename(tmp3, output_file)


if __name__ == "__main__":
   patt_person = "^(\w*?\s?\d*)(:\s?)(.*$)"
   patt_narrador = "([^\(]*)(\(.*?\))(.*)"
   sentencies = open(ArxiuEntrada, 'r', encoding="utf-8").read().split('\n')

   # ArxiuMp3 = None
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

   ArxiuMp3.export(DirSortida+"pop-rapid_3.mp3", format="mp3")  #, tags={'artist':'Dani', 'album':'pop rapid 3'})
