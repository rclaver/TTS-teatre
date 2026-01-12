#!/usr/bin/python3
# -*- coding: utf-8 -*-
"""
Creat: 08-01-2025
@author: rafael
@description: Convierte texto a audio

pip install --no-cache-dir torch
pip install --no-cache-dir TTS
"""
import warnings
warnings.filterwarnings("ignore", message="pkg_resources is deprecated")

import sys, os, re, glob, time, shutil
import torch
from TTS.api import TTS
import wave

# paràmetres
#
is_linux = (os.name == 'posix')
terminal = (sys.argv[0] == "teràpies_coqui_tts.py")
if not terminal:
   #Si se ejecuta desde un IDE que ya incluye la referencia al directorio utilitats
   import colors as c
   actor = input("indica l'actor:").lower()
else:
   if is_linux:
      sys.path.append('../..')
      import python.utilitats.colors as c
   actor = sys.argv[1].lower() if len(sys.argv) > 1 else ""

if actor == "":
   actor = "teo"
print(f"\n{c.CB_GRN}Es convertiran les escenes de: {actor}{c.C_NONE}", end='\n\n')

sencer = (len(sys.argv) > 1 and sys.argv[1] == "sencer")
if sencer:
   actor = "sencer"
   print(c.CB_GRN+"\nEs convertirà l'arxiu sencer" + c.C_NONE, end='\n\n')

# Get device
device = "cuda" if torch.cuda.is_available() else "cpu"
tts = TTS("tts_models/ca/custom/vits", progress_bar=False).to(device)

# variables locals
#
titol = "teràpies"
baseDir = os.getcwd()
dir_dades = f"entrades/{titol}"
base_arxiu_text = titol
dir_sortida = f"sortides/{titol}/wav_tts/"
ruta_arxiu_wav = baseDir + "/" + dir_sortida
arxiu_wav = ""

Personatges={'Teo':  '02689',
             'Oscar':'01591',
             'Andy': '02452',
             'Pruden': 'mar',
             'Stef':  '00762',
             'Berta':  'ona'}
Narrador='narrador'


def elimina_fragments(escena):
   print(c.BG_CYN+"Fi de l\'escena "+escena+c.C_NONE, end='\n\n')
   os.chdir(ruta_arxiu_wav)
   files = glob.glob(f"{titol}_[0-9]*.wav")
   for filename in files:
      os.remove(filename)
   os.chdir(baseDir)

def nom_arxiu(num):
   return dir_sortida + titol + "_" + f'{num:{"0"}{">"}{4}}' + ".wav"

def concatena_wavs(wfile):
   if os.path.isfile(arxiu_wav):
      infiles = [arxiu_wav, wfile]

      data = []
      for infile in infiles:
         w = wave.open(infile, 'rb')
         # params: nchannels, sampwidth, framerate, nframes, comptype, compname
         data.append([w.getparams(), w.readframes(w.getnframes())])
         w.close()

      output = wave.open(arxiu_wav, 'wb')
      output.setparams(data[0][0])
      for i in range(len(data)):
         output.writeframes(data[i][1])
      output.close()
   else:
      shutil.copyfile(wfile, arxiu_wav)

def mostra_sentencia(text, ends):
   ini_color = c.CB_CYN if text in Personatges else c.C_NONE
   ini_color = c.CB_YLW if text == "Teo" else ini_color
   ini_color = c.BG_CYN + "\n" if (text[:8] == "teràpies" or
                                   text[:5] == "Acte " or
                                   text[:7] == "Escena " or
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
      if id_veu != "narrador" or actor == "sencer":
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

'''
Lectura del text sencer o de l'escena seleccionada de l'obra
Partició del text en sentències (una sentència correspón a una línia del text)
Cada sentència pot pertanyer, bé al narrador, bé a un personatge
'''
def proces(escena=None):
   global arxiu_wav
   arxiu = escena if escena else base_arxiu_text
   arxiu_wav = ruta_arxiu_wav + arxiu + ".wav"
   if os.path.isfile(arxiu_wav): os.remove(arxiu_wav)
   arxiu = f"{dir_dades}/{arxiu}.txt"

   with open(arxiu, 'r', encoding="utf-8") as f:
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
   # grupo captura parentesis "(\(.*?\))"
   # grupo no captura parentesis "(?:\(.*?\))"
   # grupo con nombre no captura parentesis "(?'parentesi'\(.*?\))"

   if actor == "sencer":
      proces()
   else:
      escenes = glob.glob(f"{dir_dades}/{base_arxiu_text}-{actor}-*")
      escenes.sort()
      for escena in escenes:
         es = re.match(f"^{dir_dades}/({base_arxiu_text}-{actor}-[0-9]+).*", escena)
         proces(es.group(1))
