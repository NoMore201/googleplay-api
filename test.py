from gpapi.googleplay import GooglePlayAPI

import sys

EMAIL = "maracaiboez"
PASSWD = "fjgozwjmkwyvvutt"

testApps = ['com.cpuid.cpu_z']
server = GooglePlayAPI(debug=True)

# LOGIN

print('\nLogging in with email and password\n')
server.login(EMAIL, PASSWD, None, None)
gsfId = server.gsfId
authSubToken = server.authSubToken

print('\nNow trying secondary login with ac2dm token and gsfId saved\n')
server = GooglePlayAPI(debug=True)
server.login(None, None, gsfId, authSubToken)

# SEARCH

apps = server.search('telegram', 34, None)

print('nb_result: 34')
print('number of results: %d' % len(apps))


print('\nFound those apps:\n')
for a in apps:
    print(a['docId'])

# DOWNLOAD

docid = apps[0]['docId']
version = apps[0]['versionCode']
print('\nTelegram docid is: %s\n' % docid)
print('\nAttempting to download %s\n' % docid)
fl = server.download(docid, version)
with open(docid + '.apk', 'wb') as f:
    f.write(fl)
    print('\nDownload successful\n')
    f.close()

# BULK DETAILS

print('\nGetting details for %s\n' % testApps[0])
bulk = server.bulkDetails(testApps)
print(bulk)
print()

# BROWSE

browse = server.browse(cat='MUSIC_AND_AUDIO')
for key, value in browse.items():
    print('First app for category %s is %s' % (key, value[0]['docId']))
