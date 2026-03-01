#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sun Nov 12 18:53:17 2023
@author: rafael
@description: Convierte texto a audio

pip install --no-cache-dir pyttsx3
"""
import sys, os, glob, re, time, shutil
import pyttsx3
import wave
#import soundfile as sf
#import pyworld as pw
from pydub import AudioSegment

# paràmetres
terminal = (sys.argv[0] == "teràpies_pyttsx3.py")
if not terminal:
   #Si se ejecuta desde un IDE que ya incluye la referencia al directorio utilitats
   import colors as c
   actor = input("indica l'actor:").lower()
else:
   sys.path.append('../..')
   import python.utilitats.colors as c
   actor = sys.argv[1].lower() if len(sys.argv) > 1 else ""

if actor == "": actor = "teo"

# variables locals
titol = "teràpies"
baseDir = os.getcwd()
dir_dades = f"entrades/{titol}"
base_arxiu_text = titol
dir_sortida = f"sortides/{titol}/mp3_pyttsx3/"
base_arxiu_wav = baseDir + "/" + dir_sortida
arxiu_wav = ""
tmp3 = f"{dir_sortida}temp.mp3"
twav = f"{dir_sortida}temp.wav"

Personatges = {'Teo'   :{'sexe':0, 'velocitat':0, 'genere':1, 'edat':60},
               'Oscar' :{'sexe':0, 'velocitat':0, 'genere':1, 'edat':40},
               'Andy'  :{'sexe':0, 'velocitat':80, 'genere':1, 'edat':42},
               'Pruden':{'sexe':1, 'velocitat':10, 'genere':2, 'edat':20},
               'Stef'  :{'sexe':1, 'velocitat':100, 'genere':2, 'edat':22},
               'Berta' :{'sexe':1, 'velocitat':100, 'genere':2, 'edat':38}}
# parametres del to de veu
# frequencies entre 200Hz i 1050Hz
Narrador = {'sexe':2, 'velocitat':10, 'genere':2, 'edat':50}


def nom_arxiu(num):
   if not os.path.exists(dir_sortida):
      os.mkdir(dir_sortida)
   return dir_sortida + titol + "_" + f'{num:{"0"}{">"}{3}}' + ".mp3"

def speak(engine, text):
   engine.say(text)
   engine.runAndWait()
   #engine.stop()

def mostraVeus(engine):
   # Cerca de veus, catalan = 6
   nveu = 0
   voices = engine.getProperty('voices')
   for voice in voices:
      nveu += 1
      if voice.id == 'catalan':
         print("gender:", voice.gender, ". age:", voice.age, ". languages:", voice.languages)
         engine.setProperty('voice', voice.id)
         break
   # engine.setProperty('voice', voices[nveu].id)

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
   text = f"{c.BG_CYN+text:<60}" if (text[:6] == "Escena" or
                                     text[:4] == "Teló") \
                                 else ini_color+text
   print(text, c.C_NONE, end=ends)

def text_to_audio(text, output_file, veu_params, ends):
   mostra_sentencia(text, ends)

   if ends != ": ":
      #obtenir els parametres
      sexe, velocitat, genere, edat = list(veu_params.values())

      if sexe < 2:
         try:
            engine = pyttsx3.init('espeak')   # 'espeak', 'dummy'

            veus = engine.getProperty('voices')
            engine.setProperty('voices', veus[11].id) # "roa/ca" Catalan

            id_veu = engine.getProperty('voice')
            engine.setProperty('voice', id_veu)  #'roa/ca'

            '''# mostraVeus(engine)
            veu = pyttsx3.voice.Voice('catalan', name='Catalan', languages=['ca'], gender=genere, age=edat)
            veus = engine.getProperty('voices')
            for v in veus:
               print(f"veu:{v}")
               for l in v.languages:
                  print(f"- llengua:{l}")
            '''

            # Velocitat
            rate = engine.getProperty('rate')
            #print(c.C_MAG+"new rate:", rate-velocitat, c.C_NONE)
            engine.setProperty('rate', rate + velocitat)

            # Changing volume
            volume = engine.getProperty('volume')
            # print(c.C_MAG+"new volume:", volume+0.25, c.C_NONE)
            engine.setProperty('volume', volume+0.25)

            engine.save_to_file(text, output_file)
            engine.runAndWait()
            time.sleep(0.2)
            n = 0
            while engine.isBusy() and n < 100000: n += 1
            engine.stop()

            # Convertir l'arxiu mp3 a wav
            audio = AudioSegment.from_mp3(output_file)
            audio.export(twav, format="wav")
            concatena_wavs(twav)

            ''''# tractament de l'audio
            x, fs = sf.read(twav)
            f0, sp, ap = pw.wav2world(x, fs)
            yy = pw.synthesize(f0/grave, sp/reduction, ap, fs/speed, pw.default_frame_period)
            sf.write(output_file, yy, fs)

            # va creant un arxiu únic afegint cada fragment
            concatena_wavs(output_file)
            '''

            # eliminar l'arxiu temporal
            if os.path.isfile(tmp3):
               os.remove(tmp3)
            if os.path.isfile(output_file) and os.path.isfile(twav):
               os.remove(twav)
            elif os.path.isfile(twav):
               os.rename(twav, output_file)

         except Exception as ex:
            #print(c.CB_CYN+"ERROR:", ex, c.C_NONE)
            print(c.CB_CYN+"ERROR:", c.C_NONE)

def proces(escena=None):
   global arxiu_wav
   arxiu = escena if escena else base_arxiu_text
   arxiu_wav = base_arxiu_wav + arxiu + ".wav"
   if os.path.isfile(arxiu_wav): os.remove(arxiu_wav)
   arxiu = f"{dir_dades}/{arxiu}.txt"

   with open(arxiu, 'r', encoding="utf-8") as f:
      sentencies = f.read().split('\n')

   n = 0
   for sentencia in sentencies:
      if sentencia:
         n += 1
         # extraer el personaje ma(1) y el texto ma(3)
         ma = re.match(patt_person, sentencia)
         if ma:
            text = ma.group(1)
            text_to_audio(text, nom_arxiu(n), Narrador, ": ")
            to_veu = Personatges[text] if text in Personatges else Narrador
            # extraer, del texto ma(3), los comentarios del narrador
            mb = re.match(patt_narrador, ma.group(3))
            if mb and mb.group(1) and mb.group(2) and mb.group(3):
               n += 1
               text_to_audio(mb.group(1), nom_arxiu(n), to_veu, " ")
               n += 1
               text_to_audio(mb.group(2), nom_arxiu(n), Narrador, " ")
               n += 1
               text_to_audio(mb.group(3), nom_arxiu(n), to_veu, "\n")
            elif mb and mb.group(1) and mb.group(2):
               n += 1
               text_to_audio(mb.group(1), nom_arxiu(n), to_veu, " ")
               n += 1
               text_to_audio(mb.group(2), nom_arxiu(n), Narrador, "\n")
            elif mb and mb.group(2) and mb.group(3):
               n += 1
               text_to_audio(mb.group(2), nom_arxiu(n), Narrador, " ")
               n += 1
               text_to_audio(mb.group(3), nom_arxiu(n), to_veu, "\n")
            else:
               n += 1
               text_to_audio(ma.group(3), nom_arxiu(n), to_veu, "\n")

         else:
            text_to_audio(sentencia, nom_arxiu(n), Narrador, "\n")

if __name__ == "__main__":
   patt_person = "^(\w*?\s?\d*)(:\s?)(.*$)"
   patt_narrador = "([^\(]*)(\(.*?\))(.*)"

   if actor == "sencer":
      proces()
   else:
      escenes = glob.glob(f"{dir_dades}/{base_arxiu_text}-{actor}-*")
      escenes.sort()
      for escena in escenes:
         es = re.match(f"^{dir_dades}/({base_arxiu_text}-{actor}-[0-9]+).*", escena)
         proces(es.group(1))
