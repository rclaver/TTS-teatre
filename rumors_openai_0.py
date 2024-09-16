#!/usr/bin/python3
# -*- coding: UTF8 -*-
'''
@created: 13/09/2024
@description: reconocimiento base de las voces de openAI + elevenlabs
'''
from openai import OpenAI

f = open("API_Key_ElevenLabs", "r")
eAK = f.read()
f.close()
f = open("API_Key_OpenAI", "r")
oAK = f.read()
f.close()
f = open("org_OpenAI", "r")
org = f.read()
f.close()


client = OpenAI(
   organization=org,
   #project='$PROJECT_ID'
)
