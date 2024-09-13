#!/usr/bin/python3
# -*- coding: UTF8 -*-
'''
@created: 13/09/2024
@description: reconocimiento base de las voces de openAI + elevenlabs
'''
from openai import OpenAI

OPENAI_API_KEY = "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"
ELEVENLABS_API_KEY = "sk_d5f6b46b457062243308bc8b37cd0f78a28d79f038247e96"

client = OpenAI(
  organization='org-KdOHXYUXcATh2AV92A7O1SKc',
  project='$PROJECT_ID',
)
