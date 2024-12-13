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

if sys.argv[0] == "./text_a_veu_pydub.py":
   #Si se ejecuta desde una terminal
   sys.path.append('..')
   import python.utilitats.colors as c
else:
   #Si se ejecuta desde un IDE que ya incluye la referencia al directorio utilitats
   import colors as c

idioma = 'es'
FragmentVeu = "fragment_veu"
baseDir = os.getcwd() + "/"
dirSortida = "sortides/wav/"
baseArxiuWav = baseDir + dirSortida
baseArxiu = ""
ArxiuWav = ""
tmp3 = dirSortida + "temp.mp3"
twav = dirSortida + "temp.wav"

#Tratamiento de los argumentos de la línea de comandos
arg = sys.argv[1:]
if (not arg or arg[0]=="-h" or arg[0]=="-help"):
	print("Sintaxi:")
	print("\t<arxiu>: non de l'arxiu d'entrada que cal convertir a veu")
	exit()
else:
	baseArxiu = arg[0]
	ArxiuEntrada = "entrades/" + baseArxiu + ".txt"
	if not os.path.exists(baseDir + ArxiuEntrada):
		print("No s'ha trobat l'arxiu: " + baseDir + ArxiuEntrada)
		exit()

Personatges = {'Erni':  {'speed': 1.20, 'grave': 2.4, 'reduction': 0.6},
               'Cuqui': {'speed': 1.20, 'grave': 0.8, 'reduction': 1}}
Narrador = {'speed': 1.30, 'grave': 1.2, 'reduction': 0.7}

def elimina_fragments():
   os.chdir(baseArxiuWav)
   files = glob.glob("fragment_veu_[0-9]*.wav")
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
   ini_color = c.BG_CYN + "\n" if (text[:7]=="Comença" or text[:4]=="Teló") \
                                   else ini_color
   print(ini_color + text + c.C_NONE, end=ends)
   if ends == ": ": return

   # obtenir els parametres
   speed, grave, reduction = list(veu_params.values())

   # Generar un arxiu d'audio temporal amb gTTS
   tts = gTTS(text, lang=idioma)
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

   ArxiuWav = baseArxiuWav + baseArxiu + ".wav"

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

      elimina_fragments()
