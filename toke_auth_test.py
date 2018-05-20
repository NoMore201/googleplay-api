from gpapi.googleplay import GooglePlayAPI, RequestError
import sys
import argparse

ap = argparse.ArgumentParser(description='Token auth test')
ap.add_argument('-e', '--email', dest='email', help='google username')
ap.add_argument('-p', '--password', dest='password', help='google password')

args = ap.parse_args()

server = GooglePlayAPI('en_PK', 'Asia/Karachi')

# Password will be used only if cache info is invalid
server.do_login(args.email, args.password)

# Download a tiny file to test
packageId = 'com.evozi.deviceid'
fl = server.download(packageId)
with open(packageId + '.apk', 'wb') as apk_file:
	for chunk in fl.get('file').get('data'):
		apk_file.write(chunk)
	print('\nDownload successful\n')

