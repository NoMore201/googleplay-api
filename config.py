# separator used by search.py, categories.py, ...
SEPARATOR = ";"

LANG            = "en_US"
ANDROID_ID      = "320d104c4dc6eaa4"
GOOGLE_PUBKEY   = "AAAAgMom/1a/v0lblO2Ubrt60J2gcuXSljGFQXgcyZWveWLEwo6prwgi3iJIZdodyhKZQrNWp5nKJ3srRXcUW+F1BD3baEVGcmEgqaLZUNBjm057pKRI16kB0YppeGx5qIQ5QjKzsR8ETQbKLNWgRY0QRNVz34kMJR3P/LgHax/6rmf5AAAAAwEAAQ=="
GOOGLE_LOGIN    = "" 
GOOGLE_PASSWORD = ""
AUTH_TOKEN      = ""

# force the user to edit this file
if any([each == None for each in [ANDROID_ID, GOOGLE_LOGIN, GOOGLE_PASSWORD]]):
    raise Exception("config.py not updated")

