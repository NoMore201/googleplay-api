#!/usr/bin/python

from datetime import datetime
import random

import requests

from . import googleplay_pb2, config

ssl_verify = True

BASE = "https://android.clients.google.com/"
FDFE = BASE + "fdfe/"
CHECKIN_URL = BASE + "checkin"
AUTH_URL = BASE + "auth"

UPLOAD_URL = FDFE + "uploadDeviceConfig"
OAUTH_SERVICE = "oauth2:https://www.googleapis.com/auth/googleplay"

CONTENT_TYPE_PROTO = "application/x-protobuf"


class LoginError(Exception):
    def __init__(self, value):
        self.value = value

    def __str__(self):
        return repr(self.value)

class TokenExpiredError(Exception):
    def __init__(self, value):
        self.value = value

    def __str__(self):
        return repr(self.value)


class RequestError(Exception):
    def __init__(self, value):
        self.value = value

    def __str__(self):
        return repr(self.value)

class SecurityCheckError(Exception):
    def __init__(self, value):
        self.value = value

    def __str__(self):
        return repr(self.value)


class GooglePlayAPI(object):
    """Google Play Unofficial API Class

    Usual APIs methods are login(), checkin(), getSubAuthToken()."""

    def __init__(self, locale="en_US", timezone="UTC", custom_device=None, device_codename=None,
                 proxies_config=None):
        self.authSubToken = None
        self.gsfId = None
        self.device_config_token = None
        self.deviceCheckinConsistencyToken = None
        self.dfeCookie = None
        self.masterToken = None
        self.proxies_config = proxies_config
        if custom_device is not None:
            self.deviceBuilder = config.DeviceBuilder(custom_device, True)
            device_codename = custom_device["Build.DEVICE"]
        else:
            device_codename = random.choice(config.getDevicesCodenames()).strip()
            self.deviceBuilder = config.DeviceBuilder(device_codename, False)
        self.device_name = device_codename
        self.setLocale(locale)
        self.setTimezone(timezone)

    def setLocale(self, locale):
        self.deviceBuilder.setLocale(locale)

    def getDeviceInfo(self):
        return self.deviceBuilder.getDeviceInfo()

    def setTimezone(self, timezone):
        self.deviceBuilder.setTimezone(timezone)

    def setAuthSubToken(self, authSubToken):
        self.authSubToken = authSubToken

    def getHeaders(self, upload_fields=False):
        """Return the default set of request headers, which
        can later be expanded, based on the request type"""

        if upload_fields:
            headers = self.deviceBuilder.getDeviceUploadHeaders()
        else:
            headers = self.deviceBuilder.getBaseHeaders()
        if self.gsfId is not None:
            headers["X-DFE-Device-Id"] = "{0:x}".format(self.gsfId)
        if self.authSubToken is not None:
            headers["Authorization"] = "Bearer %s" % self.authSubToken
        if self.device_config_token is not None:
            headers["X-DFE-Device-Config-Token"] = self.device_config_token
        if self.deviceCheckinConsistencyToken is not None:
            headers["X-DFE-Device-Checkin-Consistency-Token"] = self.deviceCheckinConsistencyToken
        if self.dfeCookie is not None:
            headers["X-DFE-Cookie"] = self.dfeCookie
        return headers

    def checkin(self, email, ac2dmToken):
        headers = self.getHeaders()
        headers["Content-Type"] = CONTENT_TYPE_PROTO

        request = self.deviceBuilder.getAndroidCheckinRequest()

        stringRequest = request.SerializeToString()
        res = requests.post(CHECKIN_URL, data=stringRequest,
                            headers=headers, verify=ssl_verify,
                            proxies=self.proxies_config)
        response = googleplay_pb2.AndroidCheckinResponse()
        response.ParseFromString(res.content)
        self.deviceCheckinConsistencyToken = response.deviceCheckinConsistencyToken

        # checkin again to upload gfsid
        request.id = response.androidId
        request.securityToken = response.securityToken
        request.accountCookie.append("[" + email + "]")
        request.accountCookie.append(ac2dmToken)
        stringRequest = request.SerializeToString()
        requests.post(CHECKIN_URL,
                      data=stringRequest,
                      headers=headers,
                      verify=ssl_verify,
                      proxies=self.proxies_config)

        return response.androidId

    def uploadDeviceConfig(self):
        """Upload the device configuration of the fake device
        selected in the __init__ methodi to the google account."""

        upload = googleplay_pb2.UploadDeviceConfigRequest()
        upload.deviceConfiguration.CopyFrom(self.deviceBuilder.getDeviceConfig())
        headers = self.getHeaders(upload_fields=True)
        stringRequest = upload.SerializeToString()
        response = requests.post(UPLOAD_URL, data=stringRequest,
                                 headers=headers,
                                 verify=ssl_verify,
                                 timeout=60,
                                 proxies=self.proxies_config)
        response = googleplay_pb2.ResponseWrapper.FromString(response.content)
        try:
            if response.payload.HasField('uploadDeviceConfigResponse'):
                self.device_config_token = response.payload.uploadDeviceConfigResponse
                self.device_config_token = self.device_config_token.uploadDeviceConfigToken
        except ValueError:
            pass

    def login(self, email=None, ac2dmToken=None):
        """Login to your Google Account.
        For first time login you should provide:
            * email
            * password
        For the following logins you need to provide:
            * gsfId
            * authSubToken"""

        self.ac2dmToken = ac2dmToken

        if email is not None:
            self.getAuthSubToken(email, ac2dmToken)
            self.gsfId = self.checkin(email, ac2dmToken)
            self.uploadDeviceConfig()
        else:
            raise LoginError('(email,aasToken) is needed!!')

    def getAuthSubToken(self, email, ac2dmToken):
        requestParams = self.deviceBuilder.getLoginParams(email)
        requestParams["app"] = "com.android.vending"
        requestParams["callerPkg"] = "com.google.android.gms"
        requestParams["Token"] = ac2dmToken
        requestParams["oauth2_foreground"] = "1"
        requestParams["token_request_options"] = "CAA4AVAB"
        requestParams["check_email"] = "1"
        requestParams["system_partition"] = "1"
        requestParams["service"] = "oauth2:https://www.googleapis.com/auth/googleplay"

        headers = self.deviceBuilder.getAuthHeaders(self.gsfId)
        headers["app"] = "com.google.android.gms"
        response = requests.post(AUTH_URL,
                                 data=requestParams,
                                 verify=ssl_verify,
                                 headers=headers,
                                 proxies=self.proxies_config)
        data = response.text.split()
        params = {}
        for d in data:
            if "=" not in d:
                continue
            k, v = d.split("=", 1)
            params[k.strip().lower()] = v.strip()
        if "auth" in params:
            self.setAuthSubToken(params["auth"])
        elif "error" in params:
            raise TokenExpiredError("server says: " + params["error"])
        else:
            raise LoginError("Auth token not found.")

