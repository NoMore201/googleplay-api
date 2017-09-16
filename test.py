from googleplay import GooglePlayAPI

EMAIL = ""
PASSWD = ""
AC2DM = ""
GSFID = 0

server = GooglePlayAPI(True)
if AC2DM == "":
    server.login(EMAIL, PASSWD, None, None)
    print(server.search('firefox', 1, None).child[0])
    print(server.bulkDetails(['com.mozilla.firefox']))
    fl = server.download('com.cpuid.cpu_z', 23)
    with open('com.cpuid.cpu_z.apk', 'wb') as f:
        f.write(fl)
        f.close()
else:
    server.gsfId = GSFID
    server.login(EMAIL, PASSWD, AC2DM, GSFID)
    print(server.search('firefox', 1, None).child[0])
    print(server.bulkDetails(['com.mozilla.firefox']))
    fl = server.download('com.cpuid.cpu_z', 23)
    with open('com.cpuid.cpu_z.apk', 'wb') as f:
        f.write(fl)
        f.close()
