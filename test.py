from gpapi.googleplay import GooglePlayAPI, RequestError

import sys
import argparse

ap = argparse.ArgumentParser(description='Test download of expansion files')
ap.add_argument('-e', '--email', dest='email', help='google username')
ap.add_argument('-p', '--password', dest='password', help='google password')

args = ap.parse_args()

server = GooglePlayAPI('it_IT', 'Europe/Rome')

# LOGIN

print('\nLogging in with email and password\n')
server.login(args.email, args.password, None, None)
gsfId = server.gsfId
authSubToken = server.authSubToken

print('\nNow trying secondary login with ac2dm token and gsfId saved\n')
server = GooglePlayAPI('it_IT', 'Europe/Rome')
server.login(None, None, gsfId, authSubToken)

# SEARCH

apps = server.search('telegram', 34, None)

print('\nSearch suggestion for "fir"\n')
print(server.searchSuggest('fir'))

print('nb_result: 34')
print('number of results: %d' % len(apps))

print('\nFound those apps:\n')
for a in apps:
    print(a['docId'])

# HOME APPS

print('\nFetching apps from play store home\n')
home = server.getHomeApps()

for cat in home:
    print("cat {0} with {1} apps".format(cat.get('categoryId'),
                                         str(len(cat.get('apps')))))

# DOWNLOAD
docid = apps[0]['docId']
print('\nTelegram docid is: %s\n' % docid)
print('\nAttempting to download %s\n' % docid)
fl = server.download(docid)
with open(docid + '.apk', 'wb') as apk_file:
    for chunk in fl.get('file').get('data'):
        apk_file.write(chunk)
    print('\nDownload successful\n')

# DOWNLOAD APP NOT PURCHASED
# Attempting to download Nova Launcher Prime
# it should throw an error 'App Not Purchased'

print('\nAttempting to download "com.teslacoilsw.launcher.prime"\n')
errorThrown = False
try:
    app = server.search('nova launcher prime', 3, None)
    app = filter(lambda x: x['docId'] == 'com.teslacoilsw.launcher.prime', app)
    app = list(app)[0]
    fl = server.delivery(app['docId'], app['versionCode'])
except RequestError as e:
    errorThrown = True
    print(e)

if not errorThrown:
    print('Download of previous app should have failed')
    sys.exit(1)


# BULK DETAILS
testApps = ['org.mozilla.focus', 'com.non.existing.app']
bulk = server.bulkDetails(testApps)

print('\nTesting behaviour for non-existing apps\n')
if bulk[1] is not None:
    print('bulkDetails should return None for non-existing apps')
    sys.exit(1)

print('\nResult from bulkDetails for %s\n' % testApps[0])
print(bulk[0])

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
    print('%s subcategory with %d apps' % (b['title'], len(b['apps'])))

# LIST

cat = 'MUSIC_AND_AUDIO'
print('\nList %s subcategories\n' % cat)
catList = server.list(cat)
for c in catList:
    print(c)

print('\nList %s apps for %s category\n' % (catList[0], cat))
appList = server.list(cat, catList[0])
for app in appList:
    print(app['docId'])
