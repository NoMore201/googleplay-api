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

print('\nSearch suggestion for "fir"\n')
print(server.searchSuggest('fir'))

result = server.search('firefox', 34, None)
for cluster in result:
    print("cluster: {}".format(cluster.get('docid')))
    for app in cluster.get('child'):
        print("  app: {}".format(app.get('docid')))


# HOME APPS

print('\nFetching apps from play store home\n')
result = server.getHomeApps()
for cluster in result:
    print("cluster: {}".format(cluster.get('docid')))
    for app in cluster.get('child'):
        print("  app: {}".format(app.get('docid')))


# DOWNLOAD
docid = 'org.mozilla.focus'
server.log(docid)
print('\nAttempting to download {}\n'.format(docid))
fl = server.download(docid)
with open(docid + '.apk', 'wb') as apk_file:
    for chunk in fl.get('file').get('data'):
        apk_file.write(chunk)
    print('\nDownload successful\n')

# BULK DETAILS
testApps = ['org.mozilla.focus', 'com.non.existing.app']
bulk = server.bulkDetails(testApps)

print('\nTesting behaviour for non-existing apps\n')
if bulk[1] is not None:
    print('bulkDetails should return empty dict for non-existing apps')
    sys.exit(1)

print('\nResult from bulkDetails for {}\n'.format(testApps[0]))
print(bulk[0]['docid'])

# DETAILS
print('\nGetting details for %s\n' % testApps[0])
details = server.details(testApps[0])
print(details['title'])

# REVIEWS
print('\nGetting reviews for %s\n' % testApps[0])
revs = server.reviews(testApps[0])
for r in revs:
    print("UserId: {0} Vote: {1}".format(
        r['userProfile']['personIdString'],
        str(r['starRating'])))

# BROWSE

print('\nBrowse play store categories\n')
browse = server.browse()
for b in browse:
    print(b['name'])

sampleCat = browse[0]['unknownCategoryContainer']['categoryIdContainer']['categoryId']
print('\nBrowsing the {} category\n'.format(sampleCat))
browseCat = server.browse(sampleCat)

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
    print(app['docid'])
