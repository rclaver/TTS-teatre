#!/usr/bin/python3
# -*- coding: UTF8 -*-
'''
@created: 12/09/2024
@description: reconocimiento base de las voces de elevenlabs
'''
import elevenlabs as e
from elevenlabs.client import ElevenLabs

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

f = open("API_Key_ElevenLabs", "r")
k = f.read()
f.close()
client = ElevenLabs(api_key = k)

#llistat_raw_veus()
#llistat_id_veus()
#llistat_de_veus()
veu = nova_veu("D7dkYvH17OKLgp4SLulf") #Martin Osborne 5
text = "Cler, no obris fins que no hagi pujat. Si en Charly es desperta, potser acabaré sabent la història per la seva pròpia boca."
text = "Muchos años después, frente al pelotón de fusilamiento, el coronel Aureliano Buendía había de recordar aquella tarde remota en que su padre lo llevó a conocer el hielo. Macondo era entonces una aldea de veinte casas de barro y cañabrava construidas a la orilla de un río de aguas diáfanas que se precipitaban por un lecho de piedras pulidas, blancas y enormes como huevos prehistóricos. El mundo era tan reciente, que muchas cosas carecían de nombre, y para mencionarlas había que señalarías con el dedo. Todos los años, por el mes de marzo, una familia de gitanos desarrapados plantaba su carpa cerca de la aldea, y con un grande alboroto de pitos y timbales daban a conocer los nuevos inventos. Primero llevaron el imán. Un gitano corpulento, de barba montaraz y manos de gorrión, que se presentó con el nombre de Melquiades, hizo una truculenta demostración pública de lo que él mismo llamaba la octava maravilla de los sabios alquimistas de Macedonia. Fue de casa en casa arrastrando dos lingotes metálicos, y todo el mundo se espantó al ver que los calderos, las pailas, las tenazas y los anafes se caían de su sitio, y las maderas crujían por la desesperación de los clavos y los tornillos tratando de desenclavarse, y aun los objetos perdidos desde hacía mucho tiempo aparecían por donde más se les había buscado, y se arrastraban en desbandada turbulenta detrás de los fierros mágicos de Melquíades."

audio = client.generate(
            text = text,
            voice = veu,
            model = "eleven_multilingual_v2"
         )

e.save(audio, "sortides/mp3/100ans_001.mp3")
