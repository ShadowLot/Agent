import os 
import re 
import urllib.parse

CLIENT_EMAIL = os.getenv("CLIENT_EMAIL", "")

KEYWORDS = (
    "gmail", "email", "e-mail", "mail",
    "write an email", "send an email", "draft an email",
    "compose an email", "write mail", "send mail", "draft mail",
    "compose mail"
)

