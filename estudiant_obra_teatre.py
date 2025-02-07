#!/usr/bin/python3
# -*- coding: utf-8 -*-
"""
Creat: 31-01-2025
@author: rafael claver
@description: Programa interactiu per estudiar i practicar un personatge d'una obra de teatre

pip install gTTS
pip install pydub
pip install soundfile
pip install playsound
pip install pyworld
pip install SpeechRecognition
"""
import sys, os, re
import difflib

import soundfile as sf
import pyworld as pw
from gtts import gTTS
from pydub import AudioSegment

import pyaudio
import wave
import playsound as plays
import speech_recognition as sr
from speech_recognition.recognizers import google
from pydub.playback import play

# ----------
# paràmetres
#
is_linux = (os.name == 'posix')
terminal = (is_linux and sys.argv[0] == "./estudiant_obra_teatre.py") or (not is_linux and sys.argv[0] == "estudiant_obra_teatre.py")
if not terminal:
   # si s'executa des d'un IDE que ja inclou la referència al directori utilitats
   import colors as c
   print(f"{c.CB_BLU}-----------------------------------\n Espai interactiu\n-----------------------------------{c.C_NONE}")
   escenes = input("Indica les escenes que vols processar: ").split()
else:
   if is_linux:
      sys.path.append('../..')
      import python.utilitats.colors as c
      print(f"{c.C_CYN}NOTA: es convenient redirigir la sortida d'errors: {c.C_YLW}{sys.argv[0]} 2>/dev/null{c.C_NONE}\n")

   escenes = sys.argv[1] if len(sys.argv) > 1 else []
   if escenes:
      if escenes == "sencer":
         escenes = []
      else:
         escenes = escenes.split()
         print(f"\n{c.CB_GRN}Es convertiran les escenes indicades: {escenes}{c.C_NONE}", end='\n\n')
   else:
      escenes = ["101","102","103","104","105","106","201","202","203","204","205","206","207"]
      print(f"\n{c.CB_GRN}Es convertiran (per defecte) les escenes: {escenes}{c.C_NONE}", end='\n\n')

sencer = not (escenes)
if sencer:
   print(f"\n{c.CB_GRN}Es convertirà l'arxiu sencer{c.C_NONE}", end='\n\n')

# -----------------
# variables globals
#
titol = "casats"
actor = "Joan"

base_arxiu_text = titol if sencer else f"{titol}-escena-"
dir_sortida = f"sortides/{titol}/estudi/"
tmp3 = dir_sortida + "temp.mp3"
twav = dir_sortida + "temp.wav"

seq_fragment = 0  #número seqüencial per a la generació del nom d'arxiu wav de sortida d'una sentència
seq_actor = 0     #número seqüencial per a la generació del nom d'arxiu wav temporal de la veu de l'actor
pendent_escolta = False  #indica si ha arribat el moment d'escoltar l'actor

Personatges = {'Joan':   {'speed': 1.18, 'grave': 3.2, 'reduction': 0.6},
               'Gisela': {'speed': 1.30, 'grave': 0.9, 'reduction': 1.0},
               'Mar':    {'speed': 1.40, 'grave': 0.7, 'reduction': 1.0},
               'Emma':   {'speed': 1.40, 'grave': 0.7, 'reduction': 1.0},
               'Tina':   {'speed': 1.25, 'grave': 1.1, 'reduction': 0.9},
               'Justa':  {'speed': 1.30, 'grave': 1.2, 'reduction': 0.8},
               'Pompeu': {'speed': 1.30, 'grave': 2.3, 'reduction': 0.7},
               'Canut':  {'speed': 1.40, 'grave': 2.1, 'reduction': 0.8}}
Narrador = {'speed': 1.40, 'grave': 1.8, 'reduction': 1.3}

# --------
# funcions
#
'''emite beep en Android '''
def beepAndroid():
   import androidhelper
   droid=androidhelper.Android()
   droid.generateDtmfTones('0',100)

'''emite beep '''
def beep():
   plays.playsound("supplies/beep.wav")

'''emite error '''
def beep_error():
   plays.playsound("supplies/laser.wav")

'''
Crea un nom per l'arxiu wav
'''
def GeneraNomArxiuWav(escena, es_actor=False):
   ret = dir_sortida + titol + escena
   if es_actor:
      ret += actor + f'{seq_actor:{"0"}{">"}{4}}' + ".wav"
   else:
      ret += f'{seq_fragment:{"0"}{">"}{4}}' + ".wav"
   return ret

'''
Mostra, a la terminal, el text que s'està processant.
Marca les escenes i realça el nom de l'actor
'''
def MostraSentencia(text, ends):
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
Compara 2 textos i indica el percentatge de semblances
'''
def ComparaSekuenciesDeText(text_1, text_2):
   # normalitza el text original
   replace = "[.,!¡¿?()]"
   while re.search(replace, text_1):
      for r in replace:
         text_1 = text_1.replace(r, " ")
   text_1 = re.sub("\s+", " ", text_1).lower()
   #print(f"text_1: {text_1}\ntext_2: {text_2}")
   '''
   a_text_1 = text_1.split()
   a_text_2 = text_2.split()
   encert =_compara_per_desplacament(a_txt1, a_txt2)
   max_error = _compara_per_posicio(a_text_1, a_text_2)
   '''
   encert = difflib.SequenceMatcher(None, text_1, text_2).ratio() * 100
   return encert

def _compara_per_desplacament(a_txt1, a_txt2):
   p1 = 0  #element actual de l'array 1
   p2 = 0  #element actual de l'array 2
   encert = 100
   error = 0
   for s1 in a_txt1:
      p2 = 0
      for s2 in a_txt2:
         p2 += 1
         if s1 == s2:
            error = 0
            p1 += 1
            a_txt1 = a_txt1[p1:]
            break
         else:
            encert -= 1
            if error >= 3:
               a_txt2 = a_txt2[p2:]
               p2 = 0
               break
   return encert

def _compara_per_posicio(txt1, txt2):
   i = 0
   error = 0
   for s1 in txt1:
      if s1 != txt2[i]:
         error = error + 1
      i = i+1

   return error
'''
Grava un text a un arxiu d'audio
@type text: string; text que es grava
@type file_name: string; nom del fitxer wav on es grava la veu
'''
def GravaAudio(text, file_name):
   fragment = 1024
   format = pyaudio.paInt16
   canals = 1     # channels, must be one for forced alignment toolkit to work
   taxa = 16000   # freqüència de mostreig (sample rate)
   temps = 5      # nombre de segons de temps per poder dir la frase

   #print(f"{c.CB_WHT}Llegeix en veu alta: {c.CB_YLW}{text}{c.C_NONE}", end=" ")
   beep()

   p = pyaudio.PyAudio()
   stream = p.open(format=format, channels=canals, rate=taxa, input=True, frames_per_buffer=fragment)

   frames = []
   for i in range(0, int(taxa / fragment * temps)):
      data = stream.read(fragment)
      frames.append(data)

   stream.stop_stream()
   stream.close()
   p.terminate()

   wf = wave.open(file_name, 'wb')
   wf.setnchannels(canals)
   wf.setsampwidth(p.get_sample_size(format))
   wf.setframerate(taxa)
   wf.writeframes(b''.join(frames))
   wf.close()

'''
Transforma un audio en text (utilitza speech_recognition)
@type audio: AudioSource; audio d'entrada que es vol convertir a text
@type r: Recognizer; instància de speech_recognition.Recognizer()
'''
def ReconeixementDeAudio(audio, r):
   text_reconegut = ""
   # Google Speech Recognition
   try:
      # for testing purposes, we're just using the default API key
      # to use another API key, use `r.recognize_google(audio, key="GOOGLE_SPEECH_RECOGNITION_API_KEY")`
      text_reconegut = r.recognize_google(audio, language="ca")
      print(f"{c.C_YLW}- {text_reconegut}{c.C_NONE}")
   except sr.UnknownValueError:
      print("Google Speech Recognition could not understand audio")
   except sr.RequestError as e:
      print("Could not request results from Google Speech Recognition service; {0}".format(e))

   return text_reconegut

'''
Genera un arxiu de text a partir d'un arxiu d'audio
@type warxiu: string; nom del fitxer wav del que es vol extraure el text
'''
def AudioToText(warxiu):
   r = sr.Recognizer()
   with sr.AudioFile(warxiu) as source:
      audio = r.record(source)  # read the entire audio file

   text_reconegut = ReconeixementDeAudio(audio, r)
   return text_reconegut

'''
Genera un arxiu de text a partir de la veu captada pel micròfon
@type text: string; text que es llegeiix davant del micròfon
'''
def EscoltaMicrofon(text):
   r = sr.Recognizer()
   print(text)
   beep()
   with sr.Microphone() as source:
      #r.adjust_for_ambient_noise(source)
      audio = r.listen(source)

   text_reconegut = ReconeixementDeAudio(audio, r)
   print(f"text_reconegut: {c.BG_YLW}{text_reconegut}{c.C_NONE}")
   return text_reconegut

'''
Grava en viu la veu de l'actor, genera el text corresponent i el compara amb el text que li correspon
@type text: string; text que es vol gravar
@type warxiu: string; nom del fitxer wav on es gravarà la veu
'''
def EscoltaActor(text, warxiu):
   global actor
   GravaAudio(text, warxiu)
   nou_text = AudioToText(warxiu)
   #nou_text = EscoltaMicrofon(text)
   encert = 0
   if nou_text:
      encert = ComparaSekuenciesDeText(text, nou_text)
   if encert < 90:
      beep_error()
      print(f"encert: {c.BG_YLW}{encert}{c.C_NONE}", " ")
      TextToAudio(text, f"{dir_sortida}repeticio.wav", Personatges[actor], "\n", True)

'''
Genera l'arxiu d'audio corresponent al text
@type text: string; text que es vol convertir en veu
@type output_file: string; nom de l'arxiu de veu que es generarà
@type veu_params: llsta; llista de paràmetres de veu del personatge a tractar
@type ends: string; marca de final de la instrucció print
                    (": ") indica que el paràmetre text és el nom del personatge
'''
def TextToAudio(text, output_file, veu_params, ends, reprodueix=False):
   MostraSentencia(text, ends)
   # Si ends == ": " significa que text és el nom del personatge, per tant, no es genera audio
   # Si veu_params == "narrador" no es genera audio
   if ends != ": " and veu_params != "narrador":
      # obtenir els parametres
      speed, grave, reduction = list(veu_params.values())

      # Generar un arxiu d'audio temporal amb gTTS
      tts = gTTS(text, lang='ca')
      tts.save(tmp3)

      # Convertir l'arxiu mp3 a wav
      audio = AudioSegment.from_mp3(tmp3)
      play(audio)
      if not reprodueix:
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

"""
Parteix la sentència en fragments que puguin ser processats per gTTs
@type text: string; text que es tracta
@type to_veu: list; paràmetres de veu
@type ends: string; caracter de finalització de la funció print
"""
def Fragments(text, escena, to_veu, ends):
   global seq_fragment, seq_actor, pendent_escolta
   long_text = len(text)
   ini = 0
   while ini < long_text:
      long_max = 600
      if long_max < long_text:
         long_max = text[ini:].find(" ", long_max)
      if long_max == -1 or long_max > long_text:
         long_max = long_text
      text = text[ini:ini+long_max]

      seq_fragment += 1
      if text == actor:
         pendent_escolta = True
         MostraSentencia(text, ends)
      elif pendent_escolta == True:
         pendent_escolta = False
         seq_actor += 1
         EscoltaActor(text, GeneraNomArxiuWav(escena,True))
         break
      else:
         TextToAudio(text, GeneraNomArxiuWav(escena), to_veu, ends)

      ini += long_max

'''
Lectura del text sencer o de l'escena seleccionada de l'obra
Partició del text en sentències (una sentència correspón a una línia del text)
Cada sentència pot pertanyer, bé al narrador, bé a un personatge
'''
def Proces(escena=None):
   arxiu = base_arxiu_text + escena if escena else base_arxiu_text
   arxiu = f"entrades/{arxiu}.txt"
   escena = f"_{escena}_" if escena else "_"

   with open(arxiu, 'r', encoding="utf-8") as f:
      sentencies = f.read().split('\n')

   for sentencia in sentencies:
      if sentencia:
         # extraure el personatje ma(1) i el text ma(3)
         ma = re.match(pattern_person, sentencia)
         if ma:
            personatje = ma.group(1)
            Fragments(personatje, escena, "narrador", ": ")
            to_veu = Personatges[personatje] if personatje in Personatges else "narrador"
            # extraure, del text ma(3), els comentaris del narrador
            mb = re.match(pattern_narrador, ma.group(3))
            if mb:
               if mb.group(1) and mb.group(2) and mb.group(3):
                  Fragments(mb.group(1), escena, to_veu, " ")
                  Fragments(mb.group(2), escena, "narrador", " ")
                  Fragments(mb.group(3), escena, to_veu, "\n")
               elif mb.group(1) and mb.group(2):
                  Fragments(mb.group(1), escena, to_veu, " ")
                  Fragments(mb.group(2), escena, "narrador", "\n")
               elif mb.group(2) and mb.group(3):
                  Fragments(mb.group(2), escena, "narrador", " ")
                  Fragments(mb.group(3), escena, to_veu, "\n")
            else:
               Fragments(ma.group(3), escena, to_veu, "\n")
         else:
            Fragments(sentencia, escena, "narrador", "\n")

# ---------
# principal
# ---------
if __name__ == "__main__":
   '''
   1. llegeix un arxiu de text i crea una llista de sentències: les frases del text
   2. cada frase es analitzada per separar els seus components: personatge, separador, text
   3. cada fragment obtingut en el pas anterior s'envia per fer-ne un pre-procés
      en el que s'identifica si la sentència corresón a una frase de l'actor seleccionat
   4.1 si la frase no és de l'actor seleccionat, es genera l'audio corresponent
   4.2 si la frase és de l'actor seleccionat, s'activa el micròfon per escoltar
   '''
   pattern_person = "^(\w*?\s?)(:\s?)(.*$)"
   pattern_narrador = "([^\(]*)(\(.*?\))(.*)"

   if sencer or not escenes:
      Proces()
   else:
      for escena in escenes:
         Proces(escena)
