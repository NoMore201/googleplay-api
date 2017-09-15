from googleplay import GooglePlayAPI

server = GooglePlayAPI(None, None, True)
server.login("", "", None)
server.search("firefox", 1, None)
