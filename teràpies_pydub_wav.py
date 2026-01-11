#!/usr/bin/python3
# -*- coding: utf-8 -*-
"""
Creat: 16-01-2025
@author: rafael
@description: Convierte archivos de texto a audio

pip install --no-cache-dir gTTS
pip install --no-cache-dir pydub
pip install --no-cache-dir soundfile
pip install --no-cache-dir pyworld
pip install --no-cache-dir wave
"""
import warnings
warnings.filterwarnings("ignore", message="pkg_resources is deprecated")

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
terminal = (sys.argv[0] == "teràpies_pydub_wav.py")
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

# variables locals
#
titol = "teràpies"
baseDir = os.getcwd()
dir_dades = f"entrades/{titol}"
base_arxiu_text = titol
dirSortida = f"sortides/{titol}/wav/"
baseArxiuWav = baseDir + "/" + dirSortida
ArxiuWav = ""     #nom definitiu de l'arxiu wav corresponent a cada escena o al text sencer
tmp3 = dirSortida + "temp.mp3"
twav = dirSortida + "temp.wav"
silenci = "supplies/silenci.wav"

Personatges = {'Teo':    {'speed': 1.20, 'grave': 3.6, 'reduction': 0.6},
               'Pruden': {'speed': 1.30, 'grave': 0.9, 'reduction': 1.7},
               'Stef':   {'speed': 1.40, 'grave': 0.6, 'reduction': 1.4},
               'Berta':  {'speed': 1.40, 'grave': 1.0, 'reduction': 0.9},
               'Oscar':  {'speed': 1.00, 'grave': 3.0, 'reduction': 0.8},
               'Andy':   {'speed': 1.50, 'grave': 2.8, 'reduction': 1.0}}
Narrador = {'speed': 1.22, 'grave': 1.6, 'reduction': 1.7}
Narrador = "narrador"


def elimina_fragments(escena=None):
   if not escena: escena = " "
   t = c.BG_CYN+"Fi de l\'escena "+escena
   print("\n", f"{t:<60}", c.C_NONE, end='\n\n')
   os.chdir(baseArxiuWav)
   files = glob.glob(f"{titol}_[0-9]*.wav")
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
   ini_color = c.CB_YLW if text == actor.capitalize() else ini_color
   text = f"{c.BG_CYN+text:<60}" if (text[:6] == "Teràpies" or
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
         #one_sec_segment = AudioSegment.silent(duration=1000, frame_rate=23000)
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
      longitud = 600
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
   arxiu = escena if escena else base_arxiu_text
   ArxiuWav = baseArxiuWav + arxiu + ".wav"
   if os.path.isfile(ArxiuWav): os.remove(ArxiuWav)
   arxiu = f"{dir_dades}/{arxiu}.txt"

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
