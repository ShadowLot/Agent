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

def is_email_command(text) : 
    text = text.lower()
    return any(k in text for k in KEYWORDS)

def extract_email(text) : 
    match = re.search(r"[\w.+-]+@[\w.-]+\.\w+", text)
    if match : 
        return match.group(0)

match = re.search(
    r"([\w.+-]+)\s+at\s+([\w.-]+)\s+dot\s+(\w+)",
    text.lower()
)

if match : 
    return f"{match.group(1)}@{match.group(2)}.{match.group(3)}"

if CLIENT_EMAIL and any (
    x in text.lower()
    for x in ("my client", "the client", "to client", "for my client")
):
    return CLIENT_EMAIL

return ""

def create_gmail_url(subject="", body="", recipient=""):
    params = urllib.parse.urlencode({
        "view" : "cm",
        "fs":"1",
        "to" : recipient,
        "su" : subject,
        "body" : body
    })
    return f"https://mail.google.com/mail/u/0/?{params}"
    

