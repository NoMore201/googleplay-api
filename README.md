# Google play python API [![Build Status](https://travis-ci.org/NoMore201/googleplay-api.svg?branch=master)](https://travis-ci.org/NoMore201/googleplay-api)

This project contains an unofficial API for google play interactions. The code mainly comes from
[GooglePlayAPI project](https://github.com/egirault/googleplay-api/) which is not
maintained anymore. The code was updated with some important changes:

* ac2dm authentication with checkin and device info upload
* updated search and download calls
* select the device you want to fake from a list of pre-defined values (check `device.properties`)
(defaults to a OnePlus One)

# Usage
Check `test.py` for a simple example.

An important note about login function:
```
def login(self, email=None, password=None, gsfId=None, authSubToken=None)
```
for first time logins, you should only provide email and password.
The module will take care of initalizing the api,upload device information 
to the google account you supplied, and retrieving 
a Google Service Framework ID (which, from now on, will be the android ID of a device).

For the next logins you **should** save the gsfId and the authSubToken, and provide them as parameters to the login function. If you login again with email and password only, this is the equivalent of re-initalizing your android device with a google account.

# Documentation

For some documentation about the google play API check out the relative folder.
