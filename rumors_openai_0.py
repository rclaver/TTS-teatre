#!/usr/bin/python3
# -*- coding: UTF8 -*-
'''
@created: 13/09/2024
@description: reconocimiento base de las voces de openAI + elevenlabs
'''
from openai import OpenAI

PROJECT_ID=""
f = open("API_Key_ElevenLabs", "r")
eAK = f.read()
f.close()
f = open("API_Key_OpenAI", "r")
oAK = f.read()
f.close()
f = open("org_OpenAI", "r")
org = f.read()
f.close()
<<<<<<< HEAD

client = OpenAI(
   organization=org,
   project='$PROJECT_ID'
=======


client = OpenAI(
   organization=org,
   #project='$PROJECT_ID'
>>>>>>> 0cd8cc7fa6f588eef23da911c1c1e61f2f542b68
)
