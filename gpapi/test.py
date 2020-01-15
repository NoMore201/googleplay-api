import googleplay

gp = googleplay.GooglePlayAPI("en_GB", "CEST")
gp.login(email="matyas.kiss90@gmail.com", password="wdfrg789?")

print(gp.browse())

browse = gp.browse()
for b in browse:
    print(b['name'])

print('\nBrowsing the %s category\n' % browse[0]['catId'])
browseCat = gp.browse(browse[0]['catId'])
for b in browseCat:
    print('%s subcategory with %d apps' % (b['title'], len(b['apps'])))

asd = gp.list("ART_AND_DESIGN","apps_topselling_free")
for x in asd:
    print(x['docId'])

print("xxxxxxxxxxx")

asd = gp.list("ART_AND_DESIGN","apps_topselling_free",offset = 15)
for x in asd:
    print(x['docId'])