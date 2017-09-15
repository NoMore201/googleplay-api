#!/usr/bin/python

import requests

from google.protobuf import descriptor
from google.protobuf.internal.containers import RepeatedCompositeFieldContainer
from google.protobuf import text_format
from google.protobuf.message import Message, DecodeError
from Crypto.Util import asn1
from Crypto.PublicKey import RSA
from Crypto.Hash import SHA
from Crypto.Cipher import PKCS1_OAEP

import googleplay_pb2
import config
import base64
import struct

ssl_verify = True


class LoginError(Exception):
    def __init__(self, value):
        self.value = value

    def __str__(self):
        return repr(self.value)


class RequestError(Exception):
    def __init__(self, value):
        self.value = value

    def __str__(self):
        return repr(self.value)


class GooglePlayAPI(object):
    """Google Play Unofficial API Class

    Usual APIs methods are login(), search(), details(), bulkDetails(),
    download(), browse(), reviews() and list().

    toStr() can be used to pretty print the result (protobuf object) of the
    previous methods.

    toDict() converts the result into a dict, for easier introspection."""

    SERVICE = "androidmarket"

    URL_LOGIN = "https://android.clients.google.com/auth"
    ACCOUNT_TYPE_HOSTED_OR_GOOGLE = "HOSTED_OR_GOOGLE"
    authSubToken = None

    def __init__(self, androidId=None, lang=None, debug=False):
        # you must use a device-associated androidId value
        self.preFetch = {}
        if androidId is None:
            androidId = config.ANDROID_ID
        if lang is None:
            lang = config.LANG
        self.androidId = androidId
        self.lang = lang
        self.debug = debug
        self.gsfId = None
        self.ac2dmToken = None
        self.authSubToken = None

    def encrypt_password(self, login, passwd):

        def readInt(byteArray, start):
            # [start:] remove elements before start
            # [0:4] select the first four elements from start
            return struct.unpack("!L", byteArray[start:][0:4])[0]


        def toBigInt(byteArray):
            array = byteArray[::-1] # reverse array
            out = 0
            for key, value in enumerate(array):
                decoded = struct.unpack("B", bytes([value]))[0]
                out = out | decoded << key*8
            return out

        binaryKey = base64.b64decode(config.GOOGLE_PUBKEY)
        i = readInt(binaryKey, 0)
        modulus = toBigInt(binaryKey[4:][0:i])
        j = readInt(binaryKey, i+4)
        exponent = toBigInt(binaryKey[i+8:][0:j])

        seq = asn1.DerSequence()
        seq.append(modulus)
        seq.append(exponent)

        publicKey = RSA.importKey(seq.encode())
        cipher = PKCS1_OAEP.new(publicKey)
        combined = login.encode() + b'\x00' + passwd.encode()
        encrypted = cipher.encrypt(combined)
        h = b'\x00' + SHA.new(binaryKey).digest()[0:4]
        return base64.urlsafe_b64encode(h + encrypted)


    def toDict(self, protoObj):
        """Converts the (protobuf) result from an API call into a dict, for
        easier introspection."""
        iterable = False
        if isinstance(protoObj, RepeatedCompositeFieldContainer):
            iterable = True
        else:
            protoObj = [protoObj]
        retlist = []

        for po in protoObj:
            msg = dict()
            for fielddesc, value in po.ListFields():
                # print value, type(value), getattr(value, "__iter__", False)
                if fielddesc.type == descriptor.FieldDescriptor.TYPE_GROUP or \
                        isinstance(value, RepeatedCompositeFieldContainer) or \
                        isinstance(value, Message):
                    msg[fielddesc.name] = self.toDict(value)
                else:
                    msg[fielddesc.name] = value
            retlist.append(msg)
        if not iterable:
            if len(retlist) > 0:
                return retlist[0]
            else:
                return None
        return retlist

    def toStr(self, protoObj):
        """Used for pretty printing a result from the API."""
        return text_format.MessageToString(protoObj)

    def _try_register_preFetch(self, protoObj):
        fields = [i.name for (i, _) in protoObj.ListFields()]
        if ("preFetch" in fields):
            for p in protoObj.preFetch:
                self.preFetch[p.url] = p.response

    def setAuthSubToken(self, authSubToken):
        self.authSubToken = authSubToken

        # put your auth token in config.py to avoid multiple login requests
        if self.debug:
            print("authSubToken: " + authSubToken)

    def setAc2dmToken(self, ac2dmToken):
        self.ac2dmToken = ac2dmToken

        # put your auth token in config.py to avoid multiple login requests
        if self.debug:
            print("ac2dmToken: " + ac2dmToken)

    def getDefaultHeaders(self):
        """Return the default set of request parameters, which
        can later be updated, based on the request type"""

        headers = {
            "Accept-Language": "en-US",
            "X-DFE-Encoded-Targets":
                "CAEScFfqlIEG6gUYogFWrAISK1WDAg+hAZoCDgIU1gYEOIACFkLMAeQBnASLATlASUuyAyqCAjY5igOMBQzfA/IClwFbApUC4ANbtgKVAS7OAX8YswHFBhgDwAOPAmGEBt4OfKkB5weSB5AFASkiN68akgMaxAMSAQEBA9kBO7UBFE1KVwIDBGs3go6BBgEBAgMECQgJAQIEAQMEAQMBBQEBBAUEFQYCBgUEAwMBDwIBAgOrARwBEwMEAg0mrwESfTEcAQEKG4EBMxghChMBDwYGASI3hAEODEwXCVh/EREZA4sBYwEdFAgIIwkQcGQRDzQ2fTC2AjfVAQIBAYoBGRg2FhYFBwEqNzACJShzFFblAo0CFxpFNBzaAd0DHjIRI4sBJZcBPdwBCQGhAUd2A7kBLBVPngEECHl0UEUMtQETigHMAgUFCc0BBUUlTywdHDgBiAJ+vgKhAU0uAcYCAWQ/"
                "5ALUAw1UwQHUBpIBCdQDhgL4AY4CBQICjARbGFBGWzA1CAEMOQH+BRAOCAZywAIDyQZ2MgM3BxsoAgUEBwcHFia3AgcGTBwHBYwBAlcBggFxSGgIrAEEBw4QEqUCASsWadsHCgUCBQMD7QICA3tXCUw7ugJZAwGyAUwpIwM5AwkDBQMJA5sBCw8BNxBVVBwVKhebARkBAwsQEAgEAhESAgQJEBCZATMdzgEBBwG8AQQYKSMUkAEDAwY/CTs4/wEaAUt1AwEDAQUBAgIEAwYEDx1dB2wGeBFgTQ",
            "User-Agent": "Android-Finsky/7.1.15 (api=3,versionCode=80798000,sdk=25,device=A0001,hardware=bacon,product=bacon)",
        }
        if self.gsfId is not None:
            headers["X-DFE-Device-Id"] = "{0:x}".format(self.gsfId)
        if self.authSubToken is not None:
            headers["Authorization"] = "GoogleLogin auth=%s" % self.authSubToken
        return headers

    def checkin(self, email):
        headers = self.getDefaultHeaders()
        headers["Content-Type"] = "application/x-protobuffer"
        url = "https://android.clients.google.com/checkin"

        request = googleplay_pb2.AndroidCheckinRequest()
        request.id = 0
        request.checkin.CopyFrom(config.androidCheckin)
        request.locale = self.lang
        request.timeZone = 'America/New_York'
        request.version = 3
        request.deviceConfiguration.CopyFrom(config.deviceConfig)
        request.fragment = 0

        stringRequest = request.SerializeToString()
        res = requests.post(url, data=stringRequest,
                                 headers=headers, verify=ssl_verify)
        response = googleplay_pb2.AndroidCheckinResponse()
        response.ParseFromString(res.content)

        securityToken = "{0:x}".format(response.securityToken)
        gsfId = "{0:x}".format(response.androidId)
        print("String representation of androidId: %s" % gsfId)

        # checkin again to upload gfsid
        request2 = googleplay_pb2.AndroidCheckinRequest()
        request2.CopyFrom(request)
        request2.id = response.androidId
        request2.securityToken = response.securityToken
        request2.accountCookie.append("[" + email + "]")
        request2.accountCookie.append(self.ac2dmToken)
        stringRequest = request2.SerializeToString()
        res2 = requests.post(url, data=stringRequest,
                             headers=headers, verify=ssl_verify)

        return response.androidId

    def uploadDeviceConfig(self):
        upload = googleplay_pb2.UploadDeviceConfigRequest()
        upload.deviceConfiguration.CopyFrom(config.deviceConfig)
        headers = self.getDefaultHeaders()
        headers["X-DFE-Enabled-Experiments"] = "cl:billing.select_add_instrument_by_default"
        headers["X-DFE-Unsupported-Experiments"] = "nocache:billing.use_charging_poller,market_emails,buyer_currency,prod_baseline,checkin.set_asset_paid_app_field,shekel_test,content_ratings,buyer_currency_in_app,nocache:encrypted_apk,recent_changes"
        headers["X-DFE-Client-Id"] = "am-android-google"
        headers["X-DFE-SmallestScreenWidthDp"] = "320"
        headers["X-DFE-Filter-Level"] = "3"
        url = "https://android.clients.google.com/fdfe/uploadDeviceConfig"
        stringRequest = upload.SerializeToString()
        res = requests.post(url, data=stringRequest,
                            headers=headers, verify=ssl_verify)
        response = googleplay_pb2.ResponseWrapper.FromString(res.content)
        print(res.text)


    def login(self, email=None, password=None, authSubToken=None):
        """Login to your Google Account. You must provide either:
        - an email and password
        - a valid Google authSubToken"""
        if (authSubToken is not None):
            self.setAuthSubToken(authSubToken)
            # check if token is valid with a simple search
            self.search('firefox', 1, None)
        else:
            if (email is None or password is None):
                raise Exception("You should provide at least " +
                                "authSubToken or (email and password)")

            encryptedPass = self.encrypt_password(email, password).decode('utf-8')
            # AC2DM token
            params = {
                "Email": email,
                "EncryptedPasswd": encryptedPass,
                "service": "ac2dm",
                "add_account": "1",
                "accountType": self.ACCOUNT_TYPE_HOSTED_OR_GOOGLE,
                "has_permission": "1",
                "app": "com.google.android.gsf",
                "source": "android",
                "device_country": "en",
                "lang": self.lang,
                "sdk_version": "25",
                "client_sig": "38918a453d07199354f8b19af05ec6562ced5788"
            }
            response = requests.post(self.URL_LOGIN, data=params, verify=ssl_verify)
            data = response.text.split()
            print(response.text)
            params = {}
            for d in data:
                if "=" not in d:
                    continue
                k, v = d.split("=")[0:2]
                params[k.strip().lower()] = v.strip()
            if "auth" in params:
                self.setAc2dmToken(params["auth"])
            elif "error" in params:
                raise LoginError("server says: " + params["error"])
            else:
                raise LoginError("Auth token not found.")

            self.gsfId = self.checkin(email)
            self.getAuthSubToken(email, encryptedPass)
            self.uploadDeviceConfig()

    def getAuthSubToken(self, email, passwd):
        params = {
            "Email": email,
            "EncryptedPasswd": passwd,
            "accountType": self.ACCOUNT_TYPE_HOSTED_OR_GOOGLE,
            "has_permission": "1",
            "source": "android",
            "device_country": "en",
            "service": "androidmarket",
            "app": "com.android.vending",
            "lang": self.lang,
            "sdk_version": "25",
            "client_sig": "38918a453d07199354f8b19af05ec6562ced5788"
        }
        response = requests.post(self.URL_LOGIN, data=params, verify=ssl_verify)
        data = response.text.split()
        print(response.text)
        params = {}
        for d in data:
            if "=" not in d:
                continue
            k, v = d.split("=")[0:2]
            params[k.strip().lower()] = v.strip()
        if "auth" in params:
            self.setAuthSubToken(params["auth"])
        elif "error" in params:
            raise LoginError("server says: " + params["error"])
        else:
            raise LoginError("Auth token not found.")

    def executeRequestApi2(self, path, datapost=None,
                           post_content_type="application/x-www-form-urlencoded; charset=UTF-8"):
        if (datapost is None and path in self.preFetch):
            data = self.preFetch[path]
        else:
            headers = self.getDefaultHeaders()

            if datapost is not None:
                headers["Content-Type"] = post_content_type

            url = "https://android.clients.google.com/fdfe/%s" % path
            if datapost is not None:
                response = requests.post(url, data=str(datapost),
                                         headers=headers, verify=ssl_verify)
            else:
                response = requests.get(url, headers=headers,
                                        verify=ssl_verify)
            data = response.content
            print(data)

        message = googleplay_pb2.ResponseWrapper.FromString(data)
        self._try_register_preFetch(message)

        return message

    def search(self, query, nb_results, offset=None):
        """Search for apps."""
        path = "search?c=3&q=%s" % requests.utils.quote(query)

        if (offset is not None):
            path += "&o=%d" % int(offset)

        message = self.executeRequestApi2(path)
        response = message.payload.searchResponse
        if len(response.doc) == 0:
            raise DecodeError
        remaining = int(nb_results) - len(response.doc[0].child)
        messagenext = message
        allmessages = message
        while remaining > 0:
            pathnext = response.doc[0].containerMetadata.nextPageUrl
            messagenext = self.executeRequestApi2(pathnext)
            remaining -= len(response.doc[0].child)
            allmessages.MergeFrom(messagenext)
        return allmessages.payload.searchResponse

    def details(self, packageName):
        """Get app details from a package name.
        packageName is the app unique ID (usually starting with 'com.')."""
        path = "details?doc=%s" % requests.utils.quote(packageName)
        message = self.executeRequestApi2(path)
        return message.payload.detailsResponse

    def bulkDetails(self, packageNames):
        """Get several apps details from a list of package names.

        This is much more efficient than calling N times details() since it
        requires only one request.

        packageNames is a list of app ID (usually starting with 'com.')."""
        path = "bulkDetails"
        req = googleplay_pb2.BulkDetailsRequest()
        req.docid.extend(packageNames)
        data = req.SerializeToString()
        message = self.executeRequestApi2(path,
                                          data.decode("utf-8"),
                                          "application/x-protobuf")
        return message.payload.bulkDetailsResponse

    def browse(self, cat=None, ctr=None):
        """Browse categories.
        cat (category ID) and ctr (subcategory ID) are used as filters."""
        path = "browse?c=3"
        if cat is not None:
            path += "&cat=%s" % requests.utils.quote(cat)
        if ctr is not None:
            path += "&ctr=%s" % requests.utils.quote(ctr)
        message = self.executeRequestApi2(path)
        return message.payload.browseResponse

    def list(self, cat, ctr=None, nb_results=None, offset=None):
        """List apps.

        If ctr (subcategory ID) is None, returns a list of valid subcategories.

        If ctr is provided, list apps within this subcategory."""
        path = "list?c=3&cat=%s" % requests.utils.quote(cat)
        if ctr is not None:
            path += "&ctr=%s" % requests.utils.quote(ctr)
        if nb_results is not None:
            path += "&n=%s" % requests.utils.quote(nb_results)
        if offset is not None:
            path += "&o=%s" % requests.utils.quote(offset)
        message = self.executeRequestApi2(path)
        return message.payload.listResponse

    def reviews(self, packageName, filterByDevice=False, sort=2,
                nb_results=None, offset=None):
        """Browse reviews.
        packageName is the app unique ID.
        If filterByDevice is True, return only reviews for your device."""
        path = "rev?doc=%s&sort=%d" % (requests.utils.quote(packageName), sort)
        if (nb_results is not None):
            path += "&n=%d" % int(nb_results)
        if (offset is not None):
            path += "&o=%d" % int(offset)
        if(filterByDevice):
            path += "&dfil=1"
        message = self.executeRequestApi2(path)
        return message.payload.reviewResponse

    def download(self, packageName, versionCode,
                 offerType=1, progress_bar=False):
        """Download an app and return its raw data (APK file).

        packageName is the app unique ID (usually starting with 'com.').

        versionCode can be grabbed by using the details() method on the given
        app."""
        path = "purchase"
        data = "ot=%d&doc=%s&vc=%d" % (offerType, packageName, versionCode)
        message = self.executeRequestApi2(path, data)
        response = message.payload.buyResponse.purchaseStatusResponse
        if len(response.appDeliveryData.downloadAuthCookie) == 0:
            raise DecodeError
        url = response.appDeliveryData.downloadUrl
        cookie = response.appDeliveryData.downloadAuthCookie[0]

        cookies = {
            str(cookie.name): str(cookie.value)
        }

        headers = {
            "User-Agent": "AndroidDownloadManager/4.4.3 (Linux; U; " +
                          "Android 4.4.3; Nexus S Build/JRO03E)",
            "Accept-Encoding": "",
        }

        if not progress_bar:
            response = requests.get(url, headers=headers,
                                    cookies=cookies, verify=ssl_verify)
            return response.content
        # If progress_bar is asked
        from clint.textui import progress
        response_content = str()
        response = requests.get(url,
                                headers=headers,
                                cookies=cookies,
                                verify=ssl_verify,
                                stream=True)
        total_length = int(response.headers.get('content-length'))
        for chunk in progress.bar(response.iter_content(chunk_size=1024),
                                  expected_size=(total_length/1024) + 1):
            if chunk:
                response_content += chunk
        return response_content
