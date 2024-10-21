#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sun Nov 12 18:53:17 2023
@author: rafael
@description: Convierte texto a audio

pip install gTTS
pip install pydub
pip install resemble
pip install ffprobe
sudo apt install ffmpeg
pip install ffmpeg
"""
import sys
if sys.argv[0] == "./rumors_pydub-mp3.py":
   #Si se ejecuta desde una terminal
   sys.path.append('../..')
   import utilitats.colors as c
else:
   #Si se ejecuta desde un IDE que ya incluye la referencia al directorio utilitats
   import colors as c
import os, re, glob, time
from gtts import gTTS
from pydub import AudioSegment
from resemble import Resemble

Resemble.api_key('YOUR_API_TOKEN')

ArxiuMp3 = None
ArxiuEntrada = "entrades/rumors-Ernie-escena-201.txt"
DirSortida = "sortides/rumors/mp3/"
tmp3 = DirSortida + "temp.mp3"
ArxiuVeu = "rumors"
Personatges = {'Erni':  {'pitch': 0.85, 'speed': 0.60, 'alt':1900, 'baix':1900},
               'Cuqui': {'pitch': 1.20, 'speed': 0.58, 'alt': 800, 'baix': 800},
               'Cris':  {'pitch': 1.15, 'speed': 0.57, 'alt': 900, 'baix': 850},
               'Ken':   {'pitch': 0.95, 'speed': 0.53, 'alt':1000, 'baix': 900},
               'Cler':  {'pitch': 1.00, 'speed': 0.53, 'alt':1100, 'baix':1100},
               'Leni':  {'pitch': 0.85, 'speed': 0.58, 'alt':1400, 'baix':1000},
               'Glen':  {'pitch': 0.85, 'speed': 0.51, 'alt':1200, 'baix':1150},
               'Cassi': {'pitch': 0.95, 'speed': 0.51, 'alt':1100, 'baix':1050},
               'Güel':  {'pitch': 0.75, 'speed': 0.51, 'alt':1100, 'baix':1050},
               'Padni': {'pitch': 0.75, 'speed': 0.51, 'alt':1100, 'baix':1050}}
# parametres del to de veu. Frequencies entre 200Hz i 1050Hz
Narrador = {'pitch':0.75, 'speed':0.58, 'alt': 1700, 'baix': 1400}

def createProject():
   Resemble.api_key('YOUR_API_TOKEN')
   name = 'Rumors'
   description = 'Rumors: grup de teatre de Vallgorguina'
   is_public = False
   is_collaborative = False
   is_archived = False
   response = Resemble.v2.projects.create(name, description, is_public, is_collaborative, is_archived)
   project = response['item']
   return project

def getProject(project_uuid):
   Resemble.api_key('YOUR_API_TOKEN')
   response = Resemble.v2.projects.get(project_uuid)
   project = response['item']
   return project

def getAllVoices():
   Resemble.api_key('YOUR_API_TOKEN')
   page = 1
   page_size = 10
   response = Resemble.v2.voices.all(page, page_size)
   voices = response['items']
   return voices

def getVoice(voice_uuid):
   Resemble.api_key('YOUR_API_TOKEN')
   response = Resemble.v2.voices.get(voice_uuid)
   voice = response['item']
   return voice

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

def nom_arxiu(num):
   return DirSortida + ArxiuVeu + "_" + f'{num:{"0"}{">"}{4}}' + ".mp3"


def text_to_audio(text, output_file, veu_params, ends):
   global ArxiuMp3
   ini_color = c.CB_CYN if text in Personatges else c.C_NONE
   ini_color = c.CB_YLW if text == "Erni" else ini_color
   ini_color = c.BG_CYN + "\n" if (text[:6] == "Rumors" or text[:11] == "Acte Primer" or text[:10] == "Acte Segon" or
                                   text[:17] == "Situació Escènica" or text[:7] == "Escena " or text[:4] == "Teló") \
                                   else ini_color
   print(ini_color+text+c.C_NONE, end=ends)

   #obtenir els parametres
   pitch, speed, alt, baix = list(veu_params.values())

   # Generar un arxiu d'audio temporal amb gTTS
   if text == "Erni":
      text = "ara parla l'"+text
   tts = gTTS(text, lang='ca')
   tts.save(tmp3)

   # Carregar l'arxiu d'audio i ajustar la frequencia (pitch)
   audio = AudioSegment.from_mp3(tmp3)
   try:
      metadata = {
            'sample_width': audio.sample_width,
            'frame_rate': int(audio.frame_rate * pitch),
            'frame_width': audio.frame_width,
            'channels': audio.channels
        }
      audio = audio._spawn(audio.raw_data, overrides=metadata)
      audio = audio.speedup(playback_speed=speed)
      audio = audio.high_pass_filter(cutoff=alt)
      audio = audio.low_pass_filter(cutoff=baix)
      # audio += AudioSegment.empty()

      # Guardar l'arxiu d'audio ajustat
      audio.export(output_file, format="mp3")
      ArxiuMp3 = audio if not ArxiuMp3 else ArxiuMp3 + audio

      # Reproduir l'audio
      #play(audio)
   except Exception as ex:
      print(c.C_BLU+"ERROR:", ex, c.C_NONE)

   # Eliminar l'arxiu temporal
   if os.path.isfile(output_file):
      os.remove(tmp3)
   elif os.path.isfile(tmp3):
      os.rename(tmp3, output_file)

def elimina_fragmentos():
   print(c.BG_CYN+"-----------\nFi del procès"+c.C_NONE);
   os.chdir(os.getcwd() + "/" + DirSortida)
   files = glob.glob("rumors_[0-9]*.mp3")
   for filename in files:
      os.remove(filename)


if __name__ == "__main__":
   patt_person = "^(\w*?\s?)(:\s?)(.*$)"
   patt_narrador = "([^\(]*)(\(.*?\))(.*)"
   sentencies = open(ArxiuEntrada, 'r', encoding="utf-8").read().split('\n')

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

   ArxiuMp3.export(DirSortida+ArxiuVeu+"_sencer.mp3", format="mp3")  #, tags={'artist':'Ernie', 'album':'Rumors'})
   
   elimina_fragmentos()
