from gpapi.googleplay import GooglePlayAPI, RequestError

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
fl = server.download(docid, version, progress_bar=True)
with open(docid + '.apk', 'wb') as f:
    f.write(fl)
    print('\nDownload successful\n')
    f.close()

# DOWNLOAD APP NOT PURCHASED
# Attempting to download Nova Launcher Prime
# it should throw an error 'App Not Purchased'

print('\nAttempting to download "com.teslacoilsw.launcher.prime"\n')
errorThrown = False
try:
    app = server.search('nova launcher prime', 3, None)
    app = filter(lambda x: x['docId'] == 'com.teslacoilsw.launcher.prime', app)
    app = list(app)[0]
    fl = server.delivery(app['docId'], app['versionCode'], progress_bar=True)
    with open(docid + '.apk', 'wb') as f:
        f.write(fl)
        print('\nDownload successful\n')
        f.close()
except RequestError as e:
    errorThrown = True
    print(e)

if not errorThrown:
    print('Download of previous app should have failed')
    sys.exit(1)


# BULK DETAILS

print('\nGetting bulkDetails for %s\n' % testApps[0])
bulk = server.bulkDetails(testApps)
print(bulk)

# DETAILS
print('\nGetting details for %s\n' % testApps[0])
details = server.details(testApps[0])
print(details)

# REVIEWS
print('\nGetting reviews for %s\n' % testApps[0])
revs = server.reviews(testApps[0])
for r in revs:
    print(r['comment'])

# BROWSE

print('\nBrowse play store categories\n')
browse = server.browse()
for b in browse:
    print(b['name'])

print('\nBrowsing the %s category\n' % browse[0]['catId'])
browseCat = server.browse(browse[0]['catId'])
for b in browseCat:
    print('%s subcategory with %d apps' % (b['title'],len(b['apps'])))

# LIST

cat = 'MUSIC_AND_AUDIO'
print('\nList %s subcategories\n' % cat)
catList = server.list(cat)
for c in catList:
    print(c)

print('\nList %s apps for %s category\n' % (catList[0],cat))
appList = server.list(cat, catList[0])
for app in appList:
    print(app['docId'])
