  Code structure : 
  
                    | APP (backend)
                        |__init__.py
                        |gmail 
                          |gmail_gen.py
                          |gmail_write.py
                          |__init__.py
                        |youtube
                          |__init__.py
                          |player.py
                        |templates (frontend)
                          | index.html
                        | requirements.txt (packages)
                        | README.md
                        |wsgi.py

Config the app : 
1. Build Command : pip install -r requirements.txt
2. start command : gunicorn app:app
3. env variables : GEMINI_KEY, CLIENT_EMAIL
