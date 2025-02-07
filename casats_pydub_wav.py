#!/usr/bin/python3
# -*- coding: utf-8 -*-
"""
Creat: 16-01-2025
@author: rafael
@description: Convierte archivos de texto a audio

pip install gTTS
pip install pydub
pip install soundfile
pip install pyworld
pip install wave
"""
import os, re, glob, shutil
import sys
import soundfile as sf
import pyworld as pw
import wave
from gtts import gTTS
from pydub import AudioSegment

# paràmetres
#
is_linux = (os.name == 'posix')
terminal = (is_linux and sys.argv[0] == "./casats_pydub_wav.py") or (not is_linux and sys.argv[0] == "casats_pydub_wav.py")
if not terminal:
   #Si se ejecuta desde un IDE que ya incluye la referencia al directorio utilitats
   import colors as c
   escenes = input("indica les escenes:").split()
else:
   if is_linux:
      sys.path.append('../..')
      import python.utilitats.colors as c

   escenes = sys.argv[1] if len(sys.argv) > 1 else []
   if escenes:
      if escenes == "sencer":
         escenes = []
      elif escenes == "joan":
         escenes = ["102","104","202","204","205","207"]
         print(f"\n{c.CB_GRN}Es convertiran les escenes de'n Joan: {escenes}{c.C_NONE}", end='\n\n')
      else:
         escenes = escenes.split()
         print(c.CB_GRN+"\nEs convertiran les escenes indicades", escenes, c.C_NONE, end='\n\n')
   else:
      escenes = ["101","102","103","104","105","106","201","202","203","204","205","206","207"]
      print(c.CB_GRN+"\nEs convertiran (per defecte) aquestes escenes", escenes, c.C_NONE, end='\n\n')

sencer = not (escenes)
if sencer:
   print(f"\n{c.CB_GRN}Es convertirà l'arxiu sencer{c.C_NONE}", end='\n\n')

# variables locals
#
titol = "casats"
actor = "Joan"
baseDir = os.getcwd()
baseArxiu = "casats" if sencer else f"{titol}-escena-"
dirSortida = f"sortides/{titol}/wav/"
baseArxiuWav = baseDir + "/" + dirSortida
ArxiuWav = ""     #nom definitiu de l'arxiu wav corresponent a cada escena o al text sencer
tmp3 = dirSortida + "temp.mp3"
twav = dirSortida + "temp.wav"
silenci = "supplies/silenci2s.wav"

Personatges = {'Joan':   {'speed': 1.20, 'grave': 3.5, 'reduction': 0.6},
               'Gisela': {'speed': 1.30, 'grave': 0.9, 'reduction': 1.7},
               'Mar':    {'speed': 1.40, 'grave': 0.6, 'reduction': 1.4},
               'Emma':   {'speed': 1.40, 'grave': 0.7, 'reduction': 1.0},
               'Tina':   {'speed': 1.30, 'grave': 1.1, 'reduction': 1.0},
               'Justa':  {'speed': 1.40, 'grave': 1.8, 'reduction': 0.9},
               'Pompeu': {'speed': 1.30, 'grave': 2.6, 'reduction': 0.8},
               'Canut':  {'speed': 1.50, 'grave': 2.0, 'reduction': 0.8}}
Narrador = {'speed': 1.22, 'grave': 1.6, 'reduction': 1.7}
Narrador = "narrador"


def elimina_fragments(escena=None):
   if not escena: escena = " "
   t = c.BG_CYN+"Fi de l\'escena "+escena
   print("\n", f"{t:<60}", c.C_NONE, end='\n\n')
   os.chdir(baseArxiuWav)
   files = glob.glob("casats_[0-9]*.wav")
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
   return dirSortida + titol + "_" + f'{num:{"0"}{">"}{4}}' + ".wav"

def mostra_sentencia(text, ends):
   ini_color = c.CB_CYN if text in Personatges else c.C_NONE
   ini_color = c.CB_YLW if text == actor else ini_color
   text = f"{c.BG_CYN+text:<60}" if (text[:6] == "Casats" or
                                     text[:5] == "Acte " or
                                     text[:5] == " Part" or
                                     text[:6] == "Escena" or
                                     text[:4] == "Teló") \
                                 else ini_color+text
   print(text, c.C_NONE, end=ends)

'''
@type text: string; text que es vol convertir en veu
@type output_file: string; nom de l'arxiu de veu que es generarà
@type veu_params: llsta; llista de paràmetres de veu del personatge a tractar
@type ends: string; marca de final de la instrucció print
                    (": ") indica que el paràmetre text és el nom del personatge
'''
def text_to_audio(text, output_file, veu_params, ends):
   mostra_sentencia(text, ends)
   # Si ends == ": " significa que text és el nom del personatge, per tant, no es genera audio
   # Si veu_params == "narrador" no es genera audio
   if ends != ": ":
      if veu_params != "narrador":
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

         # va creant un arxiu únic afegint cada fragment
         concatena_wavs(output_file)

         # eliminar l'arxiu temporal
         if os.path.isfile(tmp3):
            os.remove(tmp3)
         if os.path.isfile(output_file) and os.path.isfile(twav):
            os.remove(twav)
         elif os.path.isfile(twav):
            os.rename(twav, output_file)
      else:
         #one_sec_segment = AudioSegment.silent(duration=2000, frame_rate=22000)
         #one_sec_segment.export(f"{silenci}.wav", format="wav")
         #one_sec_segment.export(f"{silenci}.mp3", format="mp3")
         #audio = AudioSegment.from_mp3(f"{silenci}.mp3")
         #audio.export(f"{silenci}.wav", format="wav")
         concatena_wavs(silenci)

"""
Parteix la sentència en fragments que puguin ser processats per gTTs
@type text: string; text que es tracta
@type n: int; número seqüencial per a la generació del nom d'arxiu de sortida
@type to_veu: list; paràmetres de veu
@type ends: string; caracter de finalització de la funció print
"""
def fragments(text, n, to_veu, ends):
   len_text = len(text)
   ini = 0
   while ini < len_text:
      longitud = 400
      if longitud < len_text:
         longitud = text[ini:].find(" ", longitud)
      if longitud == -1 or longitud > len_text:
         longitud = len_text
      n += 1
      text_to_audio(text[ini:ini+longitud], nom_arxiu(n), to_veu, ends)
      ini += longitud
   return n

'''
Lectura del text sencer o de l'escena seleccionada de l'obra
Partició del text en sentències (una sentència correspón a una línia del text)
Cada sentència pot pertanyer, bé al narrador, bé a un personatge
'''
def proces(escena=None):
   global ArxiuWav
   arxiu = baseArxiu + escena if escena else baseArxiu
   ArxiuWav = baseArxiuWav + arxiu + ".wav"
   if os.path.isfile(ArxiuWav): os.remove(ArxiuWav)
   arxiu = "entrades/" + arxiu + ".txt"

   with open(arxiu, 'r', encoding="utf-8") as f:
      sentencies = f.read().split('\n')

   n = 0
   for sentencia in sentencies:
      if sentencia:
         # extraer el personaje ma(1) y el texto ma(3)
         ma = re.match(patt_person, sentencia)
         if ma:
            personatge = ma.group(1)
            n = fragments(personatge, n, Narrador, ": ")
            to_veu = Personatges[personatge] if personatge in Personatges else Narrador
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

   elimina_fragments(escena)


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
