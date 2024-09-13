#!/usr/bin/python3
# -*- coding: UTF8 -*-
'''
@created: 12/09/2024
@description: reconocimiento base de las voces de elevenlabs
'''
import elevenlabs as e
from elevenlabs.client import ElevenLabs

AK = "sk_d5f6b46b457062243308bc8b37cd0f78a28d79f038247e96"
Personatges = {'Erni':  {'id':"JBFqnCBsd6RMkjVDRZzb", 'name':"George"},
               'Cuqui': {'id':"FGY2WhTYpPnrIDTdsKH5", 'name':"Laura"},
               'Cris':  {'id':"cgSgspJ2msm6clMCkdW9", 'name':"Jessica"},
               'Ken':   {'id':"IKne3meq5aSn9XLyUdCD", 'name':"Charlie"},
               'Cler':  {'id':"Ir1QNHvhaJXbAGhT50w3", 'name':"Sara Martin 2"},
               'Leni':  {'id':"TX3LPaxmHKxFdv7VOQHJ", 'name':"Liam"},
               'Glen':  {'id':"iP95p4xoKVk53GoZ742B", 'name':"Chris"},
               'Cassi': {'id':"XB0fDUnXU5powFXDhCwa", 'name':"Charlotte"},
               'Güel':  {'id':"y6WtESLj18d0diFRruBs", 'name':"David Martin 2"},
               'Padni': {'id':"pFZP5JQG7iQjIQuC4Bku", 'name':"Lily"}}
Narrador = {'id':"N2lVS1w4EtoT3dr4eOWO", 'name':"Callum"}
veus = [{'id':"EXAVITQu4vr4xnSDxMaL", 'name':"Sarah"},
		  {'id':"FGY2WhTYpPnrIDTdsKH5", 'name':"Laura"},
		  {'id':"IKne3meq5aSn9XLyUdCD", 'name':"Charlie"},
		  {'id':"JBFqnCBsd6RMkjVDRZzb", 'name':"George"},
		  {'id':"N2lVS1w4EtoT3dr4eOWO", 'name':"Callum"},
		  {'id':"TX3LPaxmHKxFdv7VOQHJ", 'name':"Liam"},
		  {'id':"XB0fDUnXU5powFXDhCwa", 'name':"Charlotte"},
		  {'id':"Xb7hH8MSUJpSbSDYk0k2", 'name':"Alice"},
		  {'id':"XrExE9yKIg1WjnnlVkGX", 'name':"Matilda"},
		  {'id':"bIHbv24MWmeRgasZH58o", 'name':"Will"},
		  {'id':"cgSgspJ2msm6clMCkdW9", 'name':"Jessica"},
		  {'id':"cjVigY5qzO86Huf0OWal", 'name':"Eric"},
		  {'id':"iP95p4xoKVk53GoZ742B", 'name':"Chris"},
		  {'id':"nPczCjzI2devNBz1zQrb", 'name':"Brian"},
		  {'id':"onwK4e9ZLuTAKqWW03F9", 'name':"Daniel"},
		  {'id':"pFZP5JQG7iQjIQuC4Bku", 'name':"Lily"},
		  {'id':"pqHfZKP75CvOlQylNhV4", 'name':"Bill"},
		  {'id':"D7dkYvH17OKLgp4SLulf", 'name':"Martin Osborne 5"},
		  {'id':"Ir1QNHvhaJXbAGhT50w3", 'name':"Sara Martin 2"},
		  {'id':"y6WtESLj18d0diFRruBs", 'name':"David Martin 2"}]

def nova_veu(voice_id):
	veu = e.Voice(
	  voice_id = voice_id,
	  settings = e.VoiceSettings(
			stability = 0.0,
			similarity_boost = 1.0,
			style = 1.0,
			use_speaker_boost = True
		)
	)
	return veu

def llistat_id_veus():
	voices = client.voices.get_all()
	for v in voices.voices:
		print(v.voice_id, v.name, v.settings)
def llistat_de_veus():
	voices = client.voices.get_all()
	for veus in voices.voices:
		print(veus.name)
		for veu in veus:
			print(veu)
		print()
def llistat_raw_veus():
	voices = client.voices.get_all()
	print(voices)

client = ElevenLabs(api_key = AK)

#llistat_raw_veus()
#llistat_id_veus()
#llistat_de_veus()
veu = nova_veu("pFZP5JQG7iQjIQuC4Bku")

audio = client.generate(
            text = "Cler, no obris fins que no hagi pujat. Si en Charly es desperta, potser acabaré sabent la història per la seva pròpia boca.",
            voice = veu,
            model = "eleven_multilingual_v2"
         )

e.play(audio)
