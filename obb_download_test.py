from gpapi.googleplay import GooglePlayAPI, RequestError

import sys

EMAIL = "dodo.godlike"
PASSWD = "inpobgakicfmnhwc"

testApps = ['com.cpuid.cpu_z']
server = GooglePlayAPI(debug=True)

# LOGIN

print('\nLogging in with email and password\n')
server.login(EMAIL, PASSWD, None, None)

download = server.download('com.haikugamesco.escapeasylum', 21, progress_bar=True)
with open(download['docId'] + '.apk', 'wb') as first:
    first.write(download['data'])
    print('\nDownload successful\n')

for obb in download['additionalData']:
    name = obb['type'] + '.' + str(obb['versionCode']) + '.' + download['docId'] + '.obb'
    with open(name, 'wb') as second:
        second.write(obb['data'])
        print('\nDownloaded additional data\n')
