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
if sys.argv[0] == "./rumors_coqui_tts.py":
   #Si se ejecuta desde una terminal
   sys.path.append('../..')
   import python.utilitats.colors as c
else:
   #Si se ejecuta desde un IDE que ya incluye la referencia al directorio utilitats
   import colors as c

sencer = True if (len(sys.argv) > 1 and sys.argv[1] == "sencer") else False
if sencer:
   escenes = [""]
   print(c.BG_CYN+"Es convertirà l'arxiu sencer" + c.C_NONE)
elif len(sys.argv) > 1 and sys.argv[1] != "":
   escenes = [sys.argv[1]]
   print(c.BG_CYN+"Es convertiran les escenes indicades", escenes, c.C_NONE)
else:
   escenes = ["106","107","108","109","111","112","201","202","203","204","205","207"]
   print(c.BG_CYN+"Es convertiran (per defecte) aquestes escenes", escenes, c.C_NONE)

# Get device
device = "cuda" if torch.cuda.is_available() else "cpu"
tts = TTS("tts_models/ca/custom/vits", progress_bar=False, verbose=False).to(device)

# variables locals
#
FragmentVeu = "rumors"
baseDir = os.getcwd()
baseArxiu = "rumors-Ernie" if sencer else "rumors-Ernie-escena-"
dirSortida = "sortides/rumors/wav/"
baseArxiuWav = baseDir + "/" + dirSortida
ArxiuWav = ""

Personatges = {'Erni':  '02689',
               'Cuqui': '01591',
               'Cris':  '02452',
               'Ken':   '00762',
               'Cler':  'mar',
               'Leni':  'jan',
               'Glen':  'pau',
               'Keisi': 'ona',
               'Güel':  'pol',
               'Padni': '00983a845f95493fb27125b114c635f3b40060efaee167d32d8a3dd040c877713446c7bd3e6944641227bdb4165ecb8d684ec2ef66c817e65e77c52cc50e62ed'}
Narrador = 'pep'


def elimina_fragments(escena):
   print(c.BG_CYN+"Fi de l\'escena "+escena+c.C_NONE+"\n")
   os.chdir(baseArxiuWav)
   files = glob.glob("rumors_[0-9]*.wav")
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

def text_to_audio(text, output_file, id_veu, ends):
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


   # Run TTS
   #print("tts: ", tts)
   #print("tts.speakers: ", tts.speakers)
   # Text to speech list of amplitude values as output
   #wav = tts.tts(text, speaker=id_veu)
   # Text to speech to a file
   tts.tts_to_file(text, speaker=id_veu, file_path=output_file, verbose=False)

   concatena_wavs(output_file)   # va creando un archivo único añadiendo cada fragmento

"""
@type text: string; text que es tracta
@type n: int; número seqüencial per a la generació del nom d'arxiu de sortida
@type id_veu: string; id de veu
@type ends: string; caracter de finalització de la funció print
"""
def fragments(text, n, id_veu, ends):
   len_text = len(text)
   ini = 0
   while ini < len_text:
      longitud = 1800
      if longitud < len_text:
         longitud = text[ini:].find(" ", longitud)
      if longitud == -1 or longitud > len_text:
         longitud = len_text
      n += 1
      text_to_audio(text[ini:ini+longitud], nom_arxiu(n), id_veu, ends)
      ini += longitud
   return n


# ------------------------------
# principal
# ------------------------------
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
               id_veu = Personatges[text] if text in Personatges else Narrador
               # extraer, del texto ma(3), los comentarios del narrador
               mb = re.match(patt_narrador, ma.group(3))
               if mb:
                  if mb.group(1) and mb.group(2) and mb.group(3):
                     n = fragments(mb.group(1), n, id_veu, " ")
                     n = fragments(mb.group(2), n, Narrador, " ")
                     n = fragments(mb.group(3), n, id_veu, "\n")
                  elif mb.group(1) and mb.group(2):
                     n = fragments(mb.group(1), n, id_veu, " ")
                     n = fragments(mb.group(2), n, Narrador, "\n")
                  elif mb.group(2) and mb.group(3):
                     n = fragments(mb.group(2), n, Narrador, " ")
                     n = fragments(mb.group(3), n, id_veu, "\n")
               else:
                  n = fragments(ma.group(3), n, id_veu, "\n")
            else:
               n = fragments(sentencia, n, Narrador, "\n")

      if not sencer: elimina_fragments(escena)
