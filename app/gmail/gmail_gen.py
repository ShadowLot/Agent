import os
import re
import json 
import time
import random
import urllib.request 
import urllib.error

API_KEY = os.getenv("GEMINI_API_KEY" , "")
MODEL - os.getenc("GEMINI_MODEL", "gemini-3.5-flash")

def generate_email_with_gemini(command):
  if not API_KEY : 
    raise RuntimeError("GEMINI_API_KEY is missing. ")

  
  prompt = f""" 
  You are a professional Gmail email writing assistant
  
  Convert the user's voice command into a professional email. 
  
  Rules : 
- Do not copy the command literally.
- Do not explain anything.
- Do not invent names, dates, prices, companies, attachments, or facts.
- Keep the email natural and concise.

Output exactly : 

Subject : <subject>

BODY:
<email body>

User command:
{command} """

url =(
  f"https://generativelivelanguage.googleapis.com/"
  f"v1beta/models/{Model}:generateContent" 
  )

payload = {
      "contents" : [{"parts" : [{prompt]}}],
      "generationConfig" : {
        "temperature" : 0.7, 
        "maxOutputTokens" : 1000 
      } 
}

  req = urllib.request.Request(
        url,
        data=json.dumps(payload).encode(),
        headers={
            "Content-Type": "application/json",
            "x-goog-api-key": API_KEY
        },
        method="POST"
    )
  
