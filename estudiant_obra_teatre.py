#!/usr/bin/python3
# -*- coding: utf-8 -*-
"""
Creat: 31-01-2025
@author: rafael claver
@description: Programa interactiu per estudiar i practicar un personatge d'una obra de teatre

pip install gTTS
pip install pydub
pip install soundfile
pip install pyworld
"""
import sys, os, re
import soundfile as sf
import pyworld as pw
from gtts import gTTS
from pydub import AudioSegment

# ----------
# paràmetres
#
is_linux = (os.name == 'posix')
terminal = (is_linux and sys.argv[0] == "./estudiant_obra_teatre.py") or (not is_linux and sys.argv[0] == "estudiant_obra_teatre.py")
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
      else:
         escenes = escenes.split()
         print(c.CB_GRN+"\nEs convertiran les escenes indicades", escenes, c.C_NONE, end='\n\n')
   else:
      escenes = ["101","102","103","104","105","106","201","202","203","204","205","206","207"]
      print(c.CB_GRN+"\nEs convertiran (per defecte) aquestes escenes", escenes, c.C_NONE, end='\n\n')

sencer = not (escenes)
if sencer:
   print(c.CB_GRN+"\nEs convertirà l'arxiu sencer" + c.C_NONE, end='\n\n')

# -----------------
# variables globals
#
titol = "casats"
actor = "Joan"
baseArxiuText = titol if sencer else f"{titol}-escena-"
dirSortida = f"sortides/{titol}/estudi/"
tmp3 = dirSortida + "temp.mp3"
twav = dirSortida + "temp.wav"

Personatges = {'Joan':   {'speed': 1.20, 'grave': 2.9, 'reduction': 0.6},
               'Gisela': {'speed': 1.20, 'grave': 0.9, 'reduction': 1.0},
               'Mar':    {'speed': 1.30, 'grave': 0.6, 'reduction': 1.0},
               'Emma':   {'speed': 1.30, 'grave': 0.7, 'reduction': 1.0},
               'Tina':   {'speed': 1.25, 'grave': 1.1, 'reduction': 0.9},
               'Justa':  {'speed': 1.30, 'grave': 1.2, 'reduction': 0.8},
               'Pompeu': {'speed': 1.30, 'grave': 2.6, 'reduction': 0.7},
               'Canut':  {'speed': 1.30, 'grave': 2.3, 'reduction': 0.8}}
Narrador = {'speed': 1.22, 'grave': 1.6, 'reduction': 1.7}

# --------
# funcions
#
'''
Crea el nom de l'arxiu wav
'''
def nom_arxiu_wav(escena, num):
   return dirSortida + titol + escena + f'{num:{"0"}{">"}{4}}' + ".wav"

'''
Mostra, a la terminal, el text que s'està processant.
Marca les escenes i realça el nom de l'actor
'''
def mostra_sentencia(text, ends):
   ini_color = c.CB_CYN if text in Personatges else c.C_NONE
   ini_color = c.CB_YLW if text==actor else ini_color
   text = f"{c.BG_CYN+text:<60}" if (text[:6] == "Casats" or
                                     text[:11] == "Acte Primer" or
                                     text[:10] == "Acte Segon" or
                                     text[:11] == "Acte Tercer" or
                                     text[:10] == "Acte Quart" or
                                     text[:12] == "Primera Part" or
                                     text[:11] == "Segona Part" or
                                     text[:6] == "Escena" or
                                     text[:4] == "Teló") \
                                 else ini_color+text
   print(text, c.C_NONE, end=ends)

'''
Genera l'arxiu d'audio corresponent al text
@type text: string; text que es vol convertir en veu
@type output_file: string; nom de l'arxiu de veu que es generarà
@type veu_params: llsta; llista de paràmetres de veu del personatge a tractar
@type ends: string; marca de final de la instrucció print
                    (": ") indica que el paràmetre text és el nom del personatge
'''
def text_to_audio(text, output_file, veu_params, ends):
   mostra_sentencia(text, ends)
   # Si ends == ": " significa que text és el nom del personatge, per tant, no es genera audio
   if ends != ": ":
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

      # elimina l'arxiu temporal
      if os.path.isfile(tmp3):
         os.remove(tmp3)
      if os.path.isfile(output_file):
         os.remove(twav)
      elif os.path.isfile(twav):
         os.rename(twav, output_file)

'''
Grava en viu la veu de l'actor, genera el text corresponent i el compara amb el text que li correspon
'''
def escolta_actor(text, warxiu):


"""
Parteix la sentència en fragments que puguin ser processats per gTTs
@type text: string; text que es tracta
@type n: int; número seqüencial per a la generació del nom d'arxiu de sortida
@type to_veu: list; paràmetres de veu
@type ends: string; caracter de finalització de la funció print
"""
def fragments(text, escena, n, to_veu, ends):
   ltext = len(text)
   ini = 0
   while ini < ltext:
      lmax = 600
      if lmax < ltext:
         lmax = text[ini:].find(" ", lmax)
      if lmax == -1 or lmax > ltext:
         lmax = ltext
      text = text[ini:ini+lmax]

      n += 1
      if text == actor:
         escoltaPendent = True
         mostra_sentencia(text, ends)
      elif escoltaPendent == True:
         escoltaPendent == False
         escolta_actor(text, nom_arxiu_wav(escena, n))
      else:
         text_to_audio(text, nom_arxiu_wav(escena, n), to_veu, ends)

      ini += lmax
   return n

'''
Lectura del text sencer o de l'escena seleccionada de l'obra
Partició del text en sentències (una sentència correspón a una línia del text)
Cada sentència pot pertanyer, bé al narrador, bé a un personatge
'''
def proces(escena=None):
   arxiu = baseArxiuText + escena if escena else baseArxiuText
   arxiu = f"entrades/{arxiu}.txt"
   escena = f"_{escena}_" if escena else "_"

   with open(arxiu, 'r', encoding="utf-8") as f:
      sentencies = f.read().split('\n')

   n = 0
   for sentencia in sentencies:
      if sentencia:
         # extraer el personaje ma(1) y el texto ma(3)
         ma = re.match(pattern_person, sentencia)
         if ma:
            text = ma.group(1)
            n = fragments(text, escena, n, Narrador, ": ")
            to_veu = Personatges[text] if text in Personatges else Narrador
            # extraure, del text ma(3), els comentaris del narrador
            mb = re.match(pattern_narrador, ma.group(3))
            if mb:
               if mb.group(1) and mb.group(2) and mb.group(3):
                  n = fragments(mb.group(1), escena, n, to_veu, " ")
                  n = fragments(mb.group(2), escena, n, Narrador, " ")
                  n = fragments(mb.group(3), escena, n, to_veu, "\n")
               elif mb.group(1) and mb.group(2):
                  n = fragments(mb.group(1), escena, n, to_veu, " ")
                  n = fragments(mb.group(2), escena, n, Narrador, "\n")
               elif mb.group(2) and mb.group(3):
                  n = fragments(mb.group(2), escena, n, Narrador, " ")
                  n = fragments(mb.group(3), escena, n, to_veu, "\n")
            else:
               n = fragments(ma.group(3), escena, n, to_veu, "\n")
         else:
            n = fragments(sentencia, escena, n, Narrador, "\n")

# ---------
# principal
# ---------
if __name__ == "__main__":
   pattern_person = "^(\w*?\s?)(:\s?)(.*$)"
   pattern_narrador = "([^\(]*)(\(.*?\))(.*)"

   if sencer or not escenes:
      proces()
   else:
      for escena in escenes:
         proces(escena)
