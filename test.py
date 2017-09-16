from googleplay import GooglePlayAPI

EMAIL = ""
PASSWD = ""

testApps = ['com.cpuid.cpu_z']
server = GooglePlayAPI(True)

print('\nLogging in with email and password\n')
server.login(EMAIL, PASSWD, None, None)
ac2dmToken = server.ac2dmToken
gsfId = server.gsfId

print('\nNow trying secondary login with ac2dm token and gsfId saved\n')
server.login(EMAIL, PASSWD, ac2dmToken, gsfId)

app = server.search('telegram', 1, None).child[0]
docid = app.docid
version = app.details.appDetails.versionCode
print('\nFirefox docid is: %s\n' % docid)
print('\nAttempting to download %s\n' % docid)
fl = server.download(docid, version)
with open(docid + '.apk', 'wb') as f:
    f.write(fl)
    print('\nDownload successful\n')
    f.close()
print('\nGetting details for %s\n' % testApps[0])
bulk = server.bulkDetails(testApps)
print(bulk)
