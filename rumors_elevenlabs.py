#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sun Nov 12 18:53:17 2023
@author: rafael
@description: Convierte texto a audio

pip install elevenlabs
"""
import sys, os, re, glob, time
#import request
#from dotenv import load_dotenv
from elevenlabs import generate, save, set_api_key
from elevenlabs.client import ElevenLabs
if sys.argv[0] == "./rumors_elevenlabs.py":
   #Si se ejecuta desde una terminal
   sys.path.append('..')
   import python.utilitats.colors as c
else:
   #Si se ejecuta desde un IDE que ya incluye la referencia al directorio utilitats
   import colors as c

sencer = True if (len(sys.argv) > 1 and sys.argv[1] == "sencer") else False

fragmentVeu = "rumors"
baseDir = os.getcwd()
baseArxiu = "rumors-Ernie" if sencer else "rumors-Ernie-escena-"
dirSortida = "sortides/rumors/mp3/"
baseArxiuWav = baseDir + "/" + dirSortida
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
               'Cassi': {'speed': 1.20, 'grave': 0.8, 'reduction': 1},
               'Güel':  {'speed': 1.20, 'grave': 2.0, 'reduction': 1},
               'Padni': {'speed': 1.20, 'grave': 1.3, 'reduction': 1}}
Narrador = {'speed': 1.30, 'grave': 1.2, 'reduction': 0.7}

def read_api_key():
	f = open("API_Key_ElevenLabs", "r")
	k = f.read()
	f.close()
   #set_api_key(k)
   return k


def elimina_fragments(escena):
   print(c.BG_CYN+"-----------\nFi de l\'escena "+escena+"\n"+c.C_NONE)
   os.chdir(baseArxiuWav)
   files = glob.glob("rumors_[0-9]*.mp3")
   for filename in files:
      os.remove(filename)
   os.chdir(baseDir)

def nom_arxiu(num):
   extra = "_" + f'{num:{"0"}{">"}{4}}' if sencer else ""
   return dirSortida + fragmentVeu + extra + ".mp3"

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
                                   text[:17]=="Situació Escènica" or text[:7]=="Comença" or text[:7]=="Escena " or
                                   text[:4]=="Teló") \
                                   else ini_color
   print(ini_color + text + c.C_NONE, end=ends)
   if ends == ": " and (text != "Erni" or sencer): return

   #load_dotenv()

   audio = generate(text = "",
                  voice = "Arnold",
                  model = "eleven_multilingual_v1"
                 )
   save(audio, dirSortida+fragmentVeu+".mp3")


   # Eliminar l'arxiu temporal
   if os.path.isfile(tmp3):
      os.remove(tmp3)
   if os.path.isfile(output_file):
      os.remove(twav)
   elif os.path.isfile(twav):
      os.rename(twav, output_file)

if __name__ == "__main__":

   client = ElevenLabs(
      api_key = ELEVENLABS_API_KEY
      #api_key = read_api_key()
   )
   #veus = {"Sarah","Laura","Charlie","George","Callum","Liam","Charlotte","Alice","Matilda","Will","Jessica","Eric","Chris","Brian","Daniel","Lily","Bill","Martin Osborne 5","Sara Martin 2","David Martin 2"}
   veus = client.voices.get_all()
	for veu in veus.voices: print(veu.name)

   patt_person = "^(\w*?\s?)(:\s?)(.*$)"
   patt_narrador = "([^\(]*)(\(.*?\))(.*)"

   for escena in escenes:
      arxiu = baseArxiu + escena
      ArxiuEntrada = "entrades/" + arxiu + ".txt"

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
