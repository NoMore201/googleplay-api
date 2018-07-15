from gpapi.googleplay import GooglePlayAPI

import argparse

ap = argparse.ArgumentParser(description='Test download of expansion files')
ap.add_argument('-e', '--email', dest='email', help='google username')
ap.add_argument('-p', '--password', dest='password', help='google password')

args = ap.parse_args()

server = GooglePlayAPI('it_IT', 'Europe/Rome')

# LOGIN

print('\nLogging in with email and password\n')
server.login(args.email, args.password, None, None)
docid = 'com.pixel.gun3d'

print('\nDownloading apk\n')
download = server.download(docid, expansion_files=True)
with open(download['docId'] + '.apk', 'wb') as first:
    for chunk in download.get('file').get('data'):
        first.write(chunk)

print('\nDownloading additional files\n')
for obb in download['additionalData']:
    name = obb['type'] + '.' + str(obb['versionCode']) + '.' + download['docId'] + '.obb'
    with open(name, 'wb') as second:
        for chunk in obb.get('file').get('data'):
            second.write(chunk)

print('\nDownload successful\n')
