#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created 12/11/2023
@author: rafael
@description: Convierte texto a audio

$ pip install tensorflow tensorflow_addons unidecode librosa
"""
import sys
if sys.argv[0] == "./convertir-texto-a-audio-5.py":
   #Si se ejecuta desde una terminal
   sys.path.append('../..')
   import utilitats.colors as c
else:
   #Si se ejecuta desde un IDE que ya incluye la referencia al directorio utilitats
   import colors as c
import re
import tensorflow as tf
import numpy as np
from tacotron2 import Tacotron2
from waveglow import WaveGlow
# import text.text_to_sequence

ArxiuMp3 = None
ArxiuEntrada = "entrades/pop-rapid-3-dani.txt"
DirSortida = "sortides/veu/"
ArxiuVeu = "popRapid-3"
Personatges = {'Dani': {'pitch': 0.75, 'speed': 0.58, 'alt': 1700, 'baix': 1400},
               'Gina': {'pitch': 1.20, 'speed': 0.58, 'alt': 700, 'baix': 700},
               'Laia': {'pitch': 1.15, 'speed': 0.57, 'alt': 900, 'baix': 850},
               'Toni': {'pitch': 0.95, 'speed': 0.53, 'alt': 1000, 'baix': 900},
               'Albert': {'pitch': 1.00, 'speed': 0.53, 'alt': 1100, 'baix': 1100},
               'Fede': {'pitch': 0.85, 'speed': 0.58, 'alt': 1400, 'baix': 1000},
               'Oscar': {'pitch': 0.85, 'speed': 0.51, 'alt': 1200, 'baix': 1150},
               'amic': {'pitch': 0.95, 'speed': 0.51, 'alt': 1100, 'baix': 1050}}
# parametres del to de veu. Frequencies entre 200Hz i 1050Hz
Narrador = {'pitch': 0.80, 'speed': 0.65, 'alt': 2000, 'baix': 1800}


def nom_arxiu(num):
    return DirSortida + ArxiuVeu + "_" + f'{num:{"0"}{">"}{3}}' + ".wav"

def text_to_sequence(input_text):
    filters='!"#$%&()*+,-./:;<=>?@[\\]^_`{|}~\t\n'
    output = input_text.split(filters)
    return output

def load_tacotron2_model():
    # Cargar el modelo Tacotron 2 preentrenado
    tacotron2 = Tacotron2()
    tacotron2.load_weights('tacotron2_weights.h5')  # Asegúrate de proporcionar el archivo correcto
    return tacotron2

def load_waveglow_model():
    # Cargar el modelo WaveGlow preentrenado
    waveglow = WaveGlow()
    waveglow.load_weights('waveglow_weights.h5')  # Asegúrate de proporcionar el archivo correcto
    return waveglow

def generate_audio(text, tacotron2, waveglow):
    # Convertir texto a secuencia numérica utilizando la función text_to_sequence
    input_seq = np.array([text_to_sequence(text)])

    # Generar espectrograma mel con Tacotron 2
    mel_outputs, mel_outputs_postnet, alignments = tacotron2.inference(input_seq)

    # Generar audio con WaveGlow
    audio = waveglow.inference(mel_outputs_postnet)

    return audio


def text_to_audio(text, tacotron2, waveglow, output_file, veu_params, ends):
    global ArxiuMp3
    ini_color = c.CB_CYN if text in Personatges else c.C_NONE
    ini_color = c.CB_YLW if text == "Dani" else ini_color
    ini_color = c.BG_CYN + "\n" if text[:6] == "Escena" or text[:9] == "Pop ràpid" else ini_color
    print(ini_color + text + c.C_NONE, end=ends)

    # obtenir els parametres
    pitch, speed, alt, baix = list(veu_params.values())

    # Convertir texto a secuencia numérica utilizando la función text_to_sequence
    input_seq = np.array([text_to_sequence(text)])

    # Generar espectrograma mel con Tacotron 2
    mel_outputs, mel_outputs_postnet, alignments = tacotron2.inference(input_seq)

    # Generar audio con WaveGlow
    audio = waveglow.inference(mel_outputs_postnet)

    # Guardar el audio resultante
    tf.audio.write_audio(output_file, audio, 22050)

    ArxiuMp3 = audio if not ArxiuMp3 else ArxiuMp3 + audio


# if __name__ == "__main__":
#    # Cargar modelos preentrenados
#    tacotron2_model = load_tacotron2_model()
#    waveglow_model = load_waveglow_model()

#     # Texto para la síntesis de voz
#     texto = "Hola, esto es un ejemplo de síntesis de voz con Tacotron 2 y WaveGlow."

#     # Generar audio
#     audio_resultante = generate_audio(texto, tacotron2_model, waveglow_model)

#     # Guardar el audio resultante
#     tf.audio.write_audio('audio_resultante.wav', audio_resultante, 22050)

if __name__ == "__main__":
    # Cargar modelos preentrenados
    tacotron2_model = load_tacotron2_model()
    waveglow_model = load_waveglow_model()

    patt_person = "^(\w*?\s?\d*)(:\s?)(.*$)"
    patt_narrador = "([^\(]*)(\(.*?\))(.*)"
    sentencies = open(ArxiuEntrada, 'r', encoding="utf-8").read().split('\n')

    # ArxiuMp3 = None
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

    ArxiuMp3.export(DirSortida + "pop-rapid_3.mp3", format="mp3")  # , tags={'artist':'Dani', 'album':'pop rapid 3'})
