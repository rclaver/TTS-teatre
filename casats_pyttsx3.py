#!/usr/bin/python3
# -*- coding: utf-8 -*-
"""
Creat: 22-01-2025
@author: rafael
@description: Convierte archivos de texto a audio

pip install pyttsx3
"""
import sys, os, re
import pyttsx3

# paràmetres
#
is_linux = (os.name == 'posix')
terminal = (is_linux and sys.argv[0] == "./casats_pyttsx3.py") or (not is_linux and sys.argv[0] == "casats_pyttsx3.py")

if not terminal:
   #Si se ejecuta desde un IDE que ya incluye la referencia al directorio utilitats
   import colors as c
   escenes = input("indica les escenes:").lower().split()
else:
   if is_linux:
      sys.path.append('../..')
      import python.utilitats.colors as c

   escenes = sys.argv[1].lower() if len(sys.argv) > 1 else []
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

sencer = (escenes)
if sencer:
   print(c.CB_GRN+"\nEs convertirà l'arxiu sencer" + c.C_NONE, end='\n\n')

# variables locals
#
titol = "casats"
actor = "Joan"
baseDir = os.getcwd()
baseArxiu = titol if sencer else f"{titol}-escena-"
dirSortida = f"sortides/{titol}/mp3/"
baseArxiuWav = baseDir + "/" + dirSortida
ArxiuWav = ""

Personatges = {'Joan':   {'rate': 150, 'volume': 0.6, 'voz': 'Aragonese'},
               'Gisela': {'rate': 150, 'volume': 1.0, 'voz': 'Catalan'},
               'Mar':    {'rate': 150, 'volume': 1.0, 'voz': 'Guarani'},
               'Emma':   {'rate': 150, 'volume': 1.0, 'voz': 'Catalan'},
               'Tina':   {'rate': 150, 'volume': 0.9, 'voz': 'Italian'},
               'Justa':  {'rate': 150, 'volume': 1.0, 'voz': 'Esperanto'},
               'Pompeu': {'rate': 150, 'volume': 0.9, 'voz': 'Catalan'},
               'Canut':  {'rate': 150, 'volume': 0.8, 'voz': 'Spanish (Spain)'}}
Narrador = {'rate': 150, 'volume': 0.7, 'voz': 'Catalan'}

# Initialize the engine
engine = pyttsx3.init()

def list_voices():
   voices = engine.getProperty('voices')
   for voice in voices:
       # to get the info. about various voices in our PC
       print("Voice:")
       print("\tID: %s" %voice.id)
       print("\tName: %s" %voice.name)
       print("\tAge: %s" %voice.age)
       print("\tGender: %s" %voice.gender)
       print("\tLanguages Known: %s" %voice.languages)

def elimina_fragments(escena=""):
   t = c.BG_CYN+"Fi de l\'escena "+escena
   print("\n", f"{t:<60}", c.C_NONE, end='\n\n')
   os.chdir(baseArxiuWav)
   files = glob.glob(f"{titol}_[0-9]*.mp3")
   for filename in files:
      os.remove(filename)
   os.chdir(baseDir)

def nom_arxiu(num):
   return dirSortida + titol + "_" + f'{num:{"0"}{">"}{4}}' + ".mp3"

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

def fragments(text, n, veu, ends):
   mostra_sentencia(text, ends)
   n += 1
   arxiu_mp3 = nom_arxiu(n)

   rate, volume, voz = list(veu.values())

   # Sets speed percent
   engine.setProperty('rate', rate)
   # Set volume 0-1
   engine.setProperty('volume', volume)
   #cambio de voz
   engine.setProperty('voice', voz)

   # Queue the entered text
   # There will be a pause between each one like a pause in a sentence
   engine.say(text)

   engine.save_to_file(text, arxiu_mp3)

   # Empties the say() queue
   # Program will not continue until all speech is done talking
   engine.runAndWait()
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
      if n > 0 and n % 300 == 0:
         time.sleep(2)
      if sentencia:
         # extraer el personaje ma(1) y el texto ma(3)
         ma = re.match(pattern_person, sentencia)
         if ma:
            text = ma.group(1)
            n = fragments(text, n, Narrador, ": ")
            veu = Personatges[text] if text in Personatges else Narrador
            # extraer, del texto ma(3), los comentarios del narrador
            mb = re.match(pattern_narrador, ma.group(3))
            if mb:
               if mb.group(1) and mb.group(2) and mb.group(3):
                  n = fragments(mb.group(1), n, veu, " ")
                  n = fragments(mb.group(2), n, Narrador, " ")
                  n = fragments(mb.group(3), n, veu, "\n")
               elif mb.group(1) and mb.group(2):
                  n = fragments(mb.group(1), n, veu, " ")
                  n = fragments(mb.group(2), n, Narrador, "\n")
               elif mb.group(2) and mb.group(3):
                  n = fragments(mb.group(2), n, Narrador, " ")
                  n = fragments(mb.group(3), n, veu, "\n")
            else:
               n = fragments(ma.group(3), n, veu, "\n")
         else:
            n = fragments(sentencia, n, Narrador, "\n")

   elimina_fragments(escena)

# ---------
# principal
# ---------
if __name__ == "__main__":
   pattern_person = r"^(\w*?\s?)(:\s?)(.*$)"
   pattern_narrador = r"([^\(]*)(\(.*?\))(.*)"

   #list_voices()

   if sencer or not escenes:
      proces()
   else:
      for escena in escenes:
         proces(escena)
