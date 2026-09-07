Code structure : 
                  | APP (backend)
                      |__init__.py
                  |templates (frontend)
                      | index.html
                  | requirements.txt (packages)
                  | README.md

Config the app : 
1. Build Command : pip install -r requirements.txt
2. start command : gunicorn app:app
3. env variables : GEMINI_KEY, CLIENT_EMAIL
