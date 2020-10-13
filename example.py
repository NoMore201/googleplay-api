import json
from gpapi.googleplay import GooglePlayAPI

# Json login file should be structured like:
# {
#     "log_in_name": {
#         "deviceName": device_name:str,
#         "gsfId" : id_number:int,
#         "authSubToken" : token:str
#     },
# }

with open("login.json") as logins:
    device_log_ins = json.load(logins)
    current_log_in = device_log_ins['pixel_2'] # Change this to change device

server = GooglePlayAPI("en_US", "America/Toronto", current_log_in['deviceName'])

print("Logging in...")
server.login(
    gsfId=current_log_in['gsfId'],
    authSubToken=current_log_in['authSubToken']
)
print("Complete!")

# Replace these with your package and version code names
docid = "com.package.name"
versionCode = 1234

details = server.details(docid, versionCode)
title = details['title'].replace("\n", "-")

print(f"""App Details Below:

Name: {title}
Package: {details['docid']}
Version Code: {details['details']['appDetails']['versionCode']}
App Version: {details['details']['appDetails']['versionString']}
""")

print("Attempting to download {}".format(docid))
fl = server.download(docid, versionCode=versionCode)
with open(docid, "wb") as apk_file:
    for chunk in fl.get("file").get("data"):
        apk_file.write(chunk)
    print("Download successful")

print("Attempting to download {} splits".format(docid))
splits = fl.get('splits')
if splits:
    for split in splits:
        split_path = f"{docid}_{split['name']}.apk"
        with open(split_path, 'wb') as f:
            for chunk in split.get('file').get('data'):
                f.write(chunk)
    print("Download successful")
