from gpapi.googleplay import GooglePlayAPI

import argparse

ap = argparse.ArgumentParser(description='Test download of expansion files')
ap.add_argument('-e', '--email', dest='email', help='google username')
ap.add_argument('-p', '--password', dest='password', help='google password')

args = ap.parse_args()

server = GooglePlayAPI(debug=True)

# LOGIN

print('\nLogging in with email and password\n')
server.login(args.email, args.password, None, None)

download = server.download('com.mapswithme.maps.pro', 1754, progress_bar=True, expansion_files=True)
with open(download['docId'] + '.apk', 'wb') as first:
    first.write(download['data'])

for obb in download['additionalData']:
    name = obb['type'] + '.' + str(obb['versionCode']) + '.' + download['docId'] + '.obb'
    with open(name, 'wb') as second:
        second.write(obb['data'])

print('\nDownload successful\n')
