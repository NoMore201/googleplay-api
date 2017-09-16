from googleplay import GooglePlayAPI

EMAIL = ""
PASSWD = ""
AC2DM = ""
GSFID = 0

server = GooglePlayAPI(True)
if AC2DM == "":
    server.login(EMAIL, PASSWD, None, None)
    print(server.search('firefox', 1, None))
else:
    server.gsfId = GSFID
    server.login(EMAIL, PASSWD, AC2DM, GSFID)
    print(server.search('firefox', 1, None).doc[0].child[0])
    print(server.download('org.telegram.messenger', 10853))
