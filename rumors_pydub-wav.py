#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sun Nov 12 18:53:17 2023
@author: rafael
@description: Convierte texto a audio

pip install gTTS
pip install pydub
pip install soundfile
pip install pyworld
pip install wave
"""
import os, re, glob, time, shutil
import sys
import soundfile as sf
import pyworld as pw
import wave
from gtts import gTTS
from pydub import AudioSegment
if sys.argv[0] == "./rumors_pydub-wav.py":
   #Si se ejecuta desde una terminal
   sys.path.append('..')
   import python.utilitats.colors as c
else:
   #Si se ejecuta desde un IDE que ya incluye la referencia al directorio utilitats
   import colors as c
# import pygame
# from pygame import mixer

sencer = True if (len(sys.argv) > 1 and sys.argv[1] == "sencer") else False

FragmentVeu = "rumors"
baseDir = os.getcwd()
baseArxiu = "rumors-Ernie" if sencer else "rumors-Ernie-escena-"
dirSortida = "sortides/rumors/wav/"
baseArxiuWav = baseDir + "/" + dirSortida
ArxiuWav = ""
tmp3 = dirSortida + "temp.mp3"
twav = dirSortida + "temp.wav"

if sencer:
   escenes = [""]
elif len(sys.argv) > 1 and sys.argv[1] != "":
   escenes = [sys.argv[1]]
else:
   escenes = ["106","107","108","109","111","112","201","202","203","204","205","207"]

Personatges = {'Erni':  {'speed': 1.20, 'grave': 2.4, 'reduction': 0.6},
               'Cuqui': {'speed': 1.20, 'grave': 0.8, 'reduction': 1},
               'Cris':  {'speed': 1.20, 'grave': 1.0, 'reduction': 1},
               'Ken':   {'speed': 1.30, 'grave': 1.9, 'reduction': 0.9},
               'Cler':  {'speed': 1.20, 'grave': 1.2, 'reduction': 1},
               'Leni':  {'speed': 1.60, 'grave': 2.0, 'reduction': 0.8},
               'Glen':  {'speed': 1.20, 'grave': 2.0, 'reduction': 0.8},
               'Keisi': {'speed': 1.20, 'grave': 0.8, 'reduction': 1},
               'Güel':  {'speed': 1.20, 'grave': 2.0, 'reduction': 1},
               'Padni': {'speed': 1.20, 'grave': 1.3, 'reduction': 1}}
Narrador = {'speed': 1.30, 'grave': 1.2, 'reduction': 0.7}

def elimina_fragments(escena):
   print(c.BG_CYN+"Fi de l\'escena "+escena+c.C_NONE+"\n")
   os.chdir(baseArxiuWav)
   files = glob.glob("rumors_[0-9]*.wav")
   for filename in files:
      os.remove(filename)
   os.chdir(baseDir)

def concatena_wavs(wfile):
   if os.path.isfile(ArxiuWav):
      infiles = [ArxiuWav, wfile]

      data = []
      for infile in infiles:
         w = wave.open(infile, 'rb')
         # params: nchannels, sampwidth, framerate, nframes, comptype, compname
         data.append([w.getparams(), w.readframes(w.getnframes())])
         w.close()

      output = wave.open(ArxiuWav, 'wb')
      output.setparams(data[0][0])
      for i in range(len(data)):
         output.writeframes(data[i][1])
      output.close()
   else:
      shutil.copyfile(wfile, ArxiuWav)

def nom_arxiu(num):
   return dirSortida + FragmentVeu + "_" + f'{num:{"0"}{">"}{4}}' + ".wav"

"""
@type text: string; text que es tracta
@type n: int; número seqüencial per a la generació del nom d'arxiu de sortida
@type to_veu: list; paràmetres de veu
@type ends: string; caracter de finalització de la funció print
"""
def fragments(text, n, to_veu, ends):
   len_text = len(text)
   ini = 0
   while ini < len_text:
      longitud = 180
      if longitud < len_text:
         longitud = text[ini:].find(" ", longitud)
      if longitud == -1 or longitud > len_text:
         longitud = len_text
      n += 1
      text_to_audio(text[ini:ini+longitud], nom_arxiu(n), to_veu, ends)
      ini += longitud
   return n

def text_to_audio(text, output_file, veu_params, ends):
   ini_color = c.CB_CYN if text in Personatges else c.C_NONE
   ini_color = c.CB_YLW if text == "Erni" else ini_color
   ini_color = c.BG_CYN + "\n" if (text[:6]=="Rumors" or text[:11]=="Acte Primer" or text[:10]=="Acte Segon" or
                                   text[:17]=="Situació Escènica" or text[:7]=="Comença" or text[:6]=="Escena" or
                                   text[:4]=="Teló") \
                                   else ini_color
   print(ini_color + text + c.C_NONE, end=ends)
   if ends == ": ": return
   #if ends == ": " and (text != "Erni" or sencer): return
   #if text == "Erni" and sencer: text = "parla l'"+text

   # obtenir els parametres
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

   concatena_wavs(output_file)   # va creando un archivo único añadiendo cada fragmento

   # Eliminar l'arxiu temporal
   if os.path.isfile(tmp3):
      os.remove(tmp3)
   if os.path.isfile(output_file):
      os.remove(twav)
   elif os.path.isfile(twav):
      os.rename(twav, output_file)

if __name__ == "__main__":
   patt_person = "^(\w*?\s?)(:\s?)(.*$)"
   patt_narrador = "([^\(]*)(\(.*?\))(.*)"

   for escena in escenes:
      arxiu = baseArxiu + escena
      ArxiuEntrada = "entrades/" + arxiu + ".txt"
      ArxiuWav = baseArxiuWav + arxiu + ".wav"

      if os.path.isfile(ArxiuWav): os.remove(ArxiuWav)

      with open(ArxiuEntrada, 'r', encoding="utf-8") as f:
         sentencies = f.read().split('\n')

      n = 0
      for sentencia in sentencies:
         if n > 0 and n % 300 == 0:
            time.sleep(2)
         if sentencia:
            # extraer el personaje ma(1) y el texto ma(3)
            ma = re.match(patt_person, sentencia)
            if ma:
               text = ma.group(1)
               n = fragments(text, n, Narrador, ": ")
               to_veu = Personatges[text] if text in Personatges else Narrador
               # extraer, del texto ma(3), los comentarios del narrador
               mb = re.match(patt_narrador, ma.group(3))
               if mb:
                  if mb.group(1) and mb.group(2) and mb.group(3):
                     n = fragments(mb.group(1), n, to_veu, " ")
                     n = fragments(mb.group(2), n, Narrador, " ")
                     n = fragments(mb.group(3), n, to_veu, "\n")
                  elif mb.group(1) and mb.group(2):
                     n = fragments(mb.group(1), n, to_veu, " ")
                     n = fragments(mb.group(2), n, Narrador, "\n")
                  elif mb.group(2) and mb.group(3):
                     n = fragments(mb.group(2), n, Narrador, " ")
                     n = fragments(mb.group(3), n, to_veu, "\n")
               else:
                  n = fragments(ma.group(3), n, to_veu, "\n")
            else:
               n = fragments(sentencia, n, Narrador, "\n")

      if not sencer: elimina_fragments(escena)
