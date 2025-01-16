#!/usr/bin/python3
# -*- coding: utf-8 -*-
"""
Creat: 08-01-2025
@author: rafael
@description: Convierte texto a audio

pip install TTS
"""
import os, re, glob, time, shutil
import sys

import torch
from TTS.api import TTS
import wave

# paràmetres
#
terminal = True if (sys.argv[0] == "./casats_coqui_tts.py") else False
if terminal:
   #Si se ejecuta desde una terminal
   sys.path.append('../..')
   import python.utilitats.colors as c
else:
   #Si se ejecuta desde un IDE que ya incluye la referencia al directorio utilitats
   import colors as c

if not terminal:
   escenes = input("indica les escenes:").split()
elif len(sys.argv) > 1 and sys.argv[1] != "":
   escenes = [sys.argv[1]]
   print(c.CB_YLW+"Es convertiran les escenes indicades", escenes, c.C_NONE)
else:
   escenes = ["101","102","103","201","202"]
   print(c.CB_YLW+"Es convertiran (per defecte) aquestes escenes", escenes, c.C_NONE)

sencer = True if (len(sys.argv) > 1 and sys.argv[1] == "sencer" or not escenes) else False
if sencer:
   escenes = []
   print(c.CB_YLW+"Es convertirà l'arxiu sencer" + c.C_NONE)

# Get device
device = "cuda" if torch.cuda.is_available() else "cpu"
tts = TTS("tts_models/ca/custom/vits", progress_bar=False, verbose=False).to(device)

# variables locals
#
FragmentVeu = "casats"
baseDir = os.getcwd()
baseArxiu = "casats" if sencer else "casats-escena-"
dirSortida = "sortides/casats/wav/"
rutaArxiuWav = baseDir + "/" + dirSortida
ArxiuWav = ""

Personatges={'Joan':  '02689',
             'Pompeu':'01591',
             'Canut': '02452',
             'Justa': 'mar',
             'Tina':  '00762',
             'Gisela':'jan',
             'Mar':   'pau',
             'Emma':  'ona'}
Narrador='pep'


def elimina_fragments(escena):
   print(c.BG_CYN+"Fi de l\'escena "+escena+c.C_NONE+"\n")
   os.chdir(rutaArxiuWav)
   files = glob.glob("casats_[0-9]*.wav")
   for filename in files:
      os.remove(filename)
   os.chdir(baseDir)

def nom_arxiu(num):
   return dirSortida + FragmentVeu + "_" + f'{num:{"0"}{">"}{4}}' + ".wav"

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

def mostra_sentencia(text, ends):
   ini_color = c.CB_CYN if text in Personatges else c.C_NONE
   ini_color = c.CB_YLW if text == "Joan" else ini_color
   ini_color = c.BG_CYN + "\n" if (text[:6] == "Casats" or
                                   text[:11] == "Acte Primer" or
                                   text[:10] == "Acte Segon" or
                                   text[:11] == "Acte Tercer" or
                                   text[:10] == "Acte Quart" or
                                   text[:12] == "Primera Part" or
                                   text[:11] == "Segona Part" or
                                   text[:6] == "Escena" or
                                   text[:4] == "Teló") \
                               else ini_color
   print(ini_color + text + c.C_NONE, end=ends)

"""
@type text: string; text que es tracta
@type n: int; número seqüencial per a la generació del nom d'arxiu de sortida
@type id_veu: string; id de la veu
@type ends: string; caracter de finalització de la funció print
"""
def fragment_text_to_audio(text, n, id_veu, ends):
   mostra_sentencia(text, ends)
   n += 1
   output_file = nom_arxiu(n)

   if ends != ": ":
      #if ends == ": " and (text != "Erni" or sencer): return
      #if text == "Erni" and sencer: text = "parla l'"+text

      # Run TTS
      #print("tts: ", tts)
      #print("tts.speakers: ", tts.speakers)
      # Text to speech list of amplitude values as output
      #wav = tts.tts(text, speaker=id_veu)

      # Text to speech to a file
      tts.tts_to_file(text, speaker=id_veu, file_path=output_file, verbose=False)
      concatena_wavs(output_file)   # va creando un archivo único añadiendo cada fragmento

   return n

def proces(escena=None):
   global ArxiuWav
   arxiu = baseArxiu + escena if escena else baseArxiu
   ArxiuWav = rutaArxiuWav + arxiu + ".wav"
   if os.path.isfile(ArxiuWav): os.remove(ArxiuWav)
   arxiu = "entrades/" + arxiu + ".txt"
   n = 0

   with open(arxiu, 'r', encoding="utf-8") as f:
      sentencies = f.read().split('\n')

   for sentencia in sentencies:
      if n > 0 and n % 300 == 0:
         time.sleep(2)
      if sentencia:
         # extraer el personaje ma(1) y el texto ma(3)
         ma = re.match(patt_person, sentencia)
         if ma:
            text = ma.group(1)
            n = fragment_text_to_audio(text, n, Narrador, ": ")
            id_veu = Personatges[text] if text in Personatges else Narrador
            # extraer, del texto ma(3), los comentarios del narrador
            mb = re.match(patt_narrador, ma.group(3))
            if mb:
               if mb.group(1) and mb.group(2) and mb.group(3):
                  n = fragment_text_to_audio(mb.group(1), n, id_veu, " ")
                  n = fragment_text_to_audio(mb.group(2), n, Narrador, " ")
                  n = fragment_text_to_audio(mb.group(3), n, id_veu, "\n")
               elif mb.group(1) and mb.group(2):
                  n = fragment_text_to_audio(mb.group(1), n, id_veu, " ")
                  n = fragment_text_to_audio(mb.group(2), n, Narrador, "\n")
               elif mb.group(2) and mb.group(3):
                  n = fragment_text_to_audio(mb.group(2), n, Narrador, " ")
                  n = fragment_text_to_audio(mb.group(3), n, id_veu, "\n")
            else:
               n = fragment_text_to_audio(ma.group(3), n, id_veu, "\n")
         else:
            n = fragment_text_to_audio(sentencia, n, Narrador, "\n")

   if not sencer and escena: elimina_fragments(escena)

# ---------
# principal
# ---------
if __name__ == "__main__":
   patt_person = "^(\w*?\s?)(:\s?)(.*$)"
   patt_narrador = "([^\(]*)(\(.*?\))(.*)"

   if sencer or not escenes:
      proces()
   else:
      for escena in escenes:
         proces(escena)
