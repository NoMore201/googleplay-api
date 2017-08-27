# separator used by search.py, categories.py, ...
SEPARATOR = ";"

LANG            = "en_US"
ANDROID_ID      = "8AAF7D11483A175"
GOOGLE_LOGIN    = "" 
GOOGLE_PASSWORD = ""
AUTH_TOKEN      = ""

# force the user to edit this file
if any([each == None for each in [ANDROID_ID, GOOGLE_LOGIN, GOOGLE_PASSWORD]]):
    raise Exception("config.py not updated")

