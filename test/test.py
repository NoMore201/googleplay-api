from gpapi.googleplay import GooglePlayAPI, RequestError

import sys
import os

gsfId = int(os.environ["GPAPI_GSFID"])
authSubToken = os.environ["GPAPI_TOKEN"]

server = GooglePlayAPI("it_IT", "Europe/Rome")

# LOGIN
print("\nLogin with ac2dm token and gsfId saved\n")
server.login(None, None, gsfId, authSubToken)

# SEARCH
print("\nSearch suggestion for \"fir\"\n")
print(server.searchSuggest("fir"))

result = server.search("firefox")
for doc in result:
    if 'docid' in doc:
        print("doc: {}".format(doc["docid"]))
    for cluster in doc["child"]:
        print("\tcluster: {}".format(cluster["docid"]))
        for app in cluster["child"]:
            print("\t\tapp: {}".format(app["docid"]))


# HOME APPS
print("\nFetching apps from play store home\n")
result = server.home()
for cluster in result:
    print("cluster: {}".format(cluster.get("docid")))
    for app in cluster.get("child"):
        print("\tapp: {}".format(app.get("docid")))


# DOWNLOAD
docid = "org.mozilla.focus"
server.log(docid)
print("\nAttempting to download {}\n".format(docid))
fl = server.download(docid)
with open(docid + ".apk", "wb") as apk_file:
    for chunk in fl.get("file").get("data"):
        apk_file.write(chunk)
    print("\nDownload successful\n")

# BULK DETAILS
testApps = ["org.mozilla.focus", "com.non.existing.app"]
bulk = server.bulkDetails(testApps)

print("\nTesting behaviour for non-existing apps\n")
if bulk[1] is not None:
    print("bulkDetails should return empty dict for non-existing apps")
    sys.exit(1)

print("\nResult from bulkDetails for {}\n".format(testApps[0]))
print(bulk[0]["docid"])

# DETAILS
print("\nGetting details for %s\n" % testApps[0])
details = server.details(testApps[0])
print(details["title"])

# REVIEWS
print("\nGetting reviews for %s\n" % testApps[0])
revs = server.reviews(testApps[0])
for r in revs:
    print("UserId: {0} Vote: {1}".format(
        r["userProfile"]["personIdString"],
        str(r["starRating"])))

# BROWSE
print("\nBrowse play store categories\n")
browse = server.browse()
for c in browse.get("category"):
    print(c["name"])

sampleCat = browse["category"][0]["unknownCategoryContainer"]["categoryIdContainer"]["categoryId"]
print("\nBrowsing the {} category\n".format(sampleCat))
browseCat = server.home(cat=sampleCat)

for doc in browseCat:
    if 'docid' in doc:
        print("doc: {}".format(doc["docid"]))
    for child in doc["child"]:
        print("\tsubcat: {}".format(child["docid"]))
        for app in child["child"]:
            print("\t\tapp: {}".format(app["docid"]))

# LIST
cat = "MUSIC_AND_AUDIO"
print("\nList {} subcategories\n".format(cat))
catList = server.list(cat)
for c in catList:
    print(c)

limit = 4
print("\nList only {} apps from subcat {} for {} category\n".format(
    limit, catList[0], cat))
appList = server.list(cat, catList[0], 4, 1)
for app in appList:
    print(app["docid"])
