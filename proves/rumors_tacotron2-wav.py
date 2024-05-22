#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created 12/11/2023
@author: rafael
@description: Convierte texto a audio

$ pip install torch numpy scipy librosa unidecode inflect librosa
"""
import sys
if sys.argv[0] == "./rumors_tacotron2-wav.py":
   #Si se ejecuta desde una terminal
   sys.path.append('../..')
   import utilitats.colors as c
else:
   #Si se ejecuta desde un IDE que ya incluye la referencia al directorio utilitats
   import colors as c
import re, time
import tensorflow as tf
import numpy as np
import torch

ArxiuWav = None
ArxiuEntrada = "entrades/rumors-Ernie.txt"
DirSortida = "sortides/rumors/"
ArxiuVeu = "rumors"
Personatges = {'Erni':  {'pitch': 0.75, 'speed': 0.58, 'alt': 1700, 'baix': 1400},
               'Cuqui': {'pitch': 1.20, 'speed': 0.58, 'alt': 700, 'baix': 700},
               'Cris':  {'pitch': 1.15, 'speed': 0.57, 'alt': 900, 'baix': 850},
               'Ken':   {'pitch': 0.95, 'speed': 0.53, 'alt': 1000, 'baix': 900},
               'Cler':  {'pitch': 1.00, 'speed': 0.53, 'alt': 1100, 'baix': 1100},
               'Leni':  {'pitch': 0.85, 'speed': 0.58, 'alt': 1400, 'baix': 1000},
               'Glen':  {'pitch': 0.85, 'speed': 0.51, 'alt': 1200, 'baix': 1150},
               'Cassi': {'pitch': 0.95, 'speed': 0.51, 'alt': 1100, 'baix': 1050},
               'Güel':  {'pitch': 0.75, 'speed': 0.51, 'alt': 1100, 'baix': 1050},
               'Padni': {'pitch': 0.75, 'speed': 0.51, 'alt': 1100, 'baix': 1050}}
# parametres del to de veu. Frequencies entre 200Hz i 1050Hz
Narrador = {'pitch': 0.80, 'speed': 0.65, 'alt': 2000, 'baix': 1800}


def nom_arxiu(num):
    return DirSortida + ArxiuVeu + "_" + f'{num:{"0"}{">"}{4}}' + ".wav"

"""
@type text: string; text que es tracta
@type n: int; número seqüencial per a la generació del nom d'arxiu de sortida
@type to_veu: list; paràmetres de veu
@type ends: string; caracter de finalització de la funció print
"""
def fragmentos(text, n, to_veu, ends):
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

def text_to_sequence(input_text):
    filters='!"#$%&()*+,-./:;<=>?@[\\]^_`{|}~\t\n'
    output = input_text.split(filters)
    return output

def load_tacotron2_model():
    # Load the Tacotron2 model pre-trained on LJ Speech dataset and prepare it for inference
    tacotron2 = torch.hub.load('NVIDIA/DeepLearningExamples:torchhub', 'nvidia_tacotron2', model_math='fp16', map_location=torch.device('cpu'))
    #tacotron2 = tacotron2.to('cuda')
    tacotron2.eval()
    return tacotron2

def load_waveglow_model():
    # Load pretrained WaveGlow model
    waveglow = torch.hub.load('NVIDIA/DeepLearningExamples:torchhub', 'nvidia_waveglow', model_math='fp16', map_location=torch.device('cpu'))
    waveglow = waveglow.remove_weightnorm(waveglow)
    #waveglow = waveglow.to('cuda')
    waveglow.eval()
    return waveglow


def text_to_audio(text, tacotron2, waveglow, output_file, veu_params, ends):
    global ArxiuWav
    ini_color = c.CB_CYN if text in Personatges else c.C_NONE
    ini_color = c.CB_YLW if text == "Erni" else ini_color
    ini_color = c.BG_CYN + "\n" if (text[:6] == "Rumors" or text[:11] == "Acte Primer" or text[:10] == "Acte Segon" or
                                    text[:17] == "Situació Escènica" or text[:4] == "Teló") \
                                    else ini_color
    print(ini_color + text + c.C_NONE, end=ends)

    # obtenir els parametres
    pitch, speed, alt, baix = list(veu_params.values())

    # Dar formato al texto de entrada
    utils = torch.hub.load('NVIDIA/DeepLearningExamples:torchhub', 'nvidia_tts_utils')
    sequences, lengths = utils.prepare_input_sequence([text])

    # Run the chained models:
    with torch.no_grad():
        mel, _, _ = tacotron2.infer(sequences, lengths)
        audio = waveglow.infer(mel)
    audio_numpy = audio[0].data.cpu().numpy()
    rate = 22050

    # Guardar el audio resultante
    from scipy.io.wavfile import write
    write(output_file, rate, audio_numpy)

    ArxiuWav = audio if not ArxiuWav else ArxiuWav + audio


if __name__ == "__main__":
    # Cargar modelos preentrenados
    tacotron2_model = load_tacotron2_model()
    waveglow_model = load_waveglow_model()

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
                text_to_audio(text, tacotron2_model, waveglow_model, nom_arxiu(n), Narrador, ": ")
                to_veu = Personatges[text] if text in Personatges else Narrador
                # extraer, del texto ma(3), los comentarios del narrador
                mb = re.match(patt_narrador, ma.group(3))
                if mb:
                    if mb.group(1) and mb.group(2) and mb.group(3):
                        n += 1
                        text_to_audio(mb.group(1), tacotron2_model, waveglow_model, nom_arxiu(n), to_veu, " ")
                        n = fragmentos(mb.group(2), tacotron2_model, waveglow_model, n, Narrador, " ")
                        n = fragmentos(mb.group(3), tacotron2_model, waveglow_model, n, to_veu, "\n")
                    elif mb.group(1) and mb.group(2):
                        n += 1
                        text_to_audio(mb.group(1), tacotron2_model, waveglow_model, nom_arxiu(n), to_veu, " ")
                        n = fragmentos(mb.group(2), tacotron2_model, waveglow_model, n, Narrador, "\n")
                    elif mb.group(2) and mb.group(3):
                        n = fragmentos(mb.group(2), tacotron2_model, waveglow_model, n, Narrador, " ")
                        n = fragmentos(mb.group(3), tacotron2_model, waveglow_model, n, to_veu, "\n")
                else:
                    n = fragmentos(ma.group(3), tacotron2_model, waveglow_model, n, to_veu, "\n")
            else:
                n = fragmentos(sentencia, tacotron2_model, waveglow_model,n, Narrador, "\n")

    ArxiuWav.export(DirSortida + "rumors-tacotron2.wav", format="wav")  # , tags={'artist':'Ernie', 'album':'rumors'})
