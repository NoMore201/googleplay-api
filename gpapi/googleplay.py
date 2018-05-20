#!/usr/bin/python


from Crypto.Util import asn1
from Crypto.PublicKey import RSA
from Crypto.Hash import SHA
from Crypto.Cipher import PKCS1_OAEP

import requests
from base64 import b64decode, urlsafe_b64encode
from itertools import chain
import time
import os
import pickle

from . import googleplay_pb2, config, utils

ssl_verify = True

BASE = "https://android.clients.google.com/"
FDFE = BASE + "fdfe/"
UPLOADURL = FDFE + "uploadDeviceConfig"
SEARCHURL = FDFE + "search"
CHECKINURL = BASE + "checkin"
AUTHURL = BASE + "auth"
LOGURL = FDFE + "log"
TOCURL = FDFE + "toc"
CACHEDIR = ".gpapicache/"


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
    download(), browse(), reviews() and list()."""

    def __init__(self, locale, timezone, device_codename='bacon',
                 proxies_config=None):
        self.authSubToken = None
        self.cachefile = CACHEDIR + device_codename + '.txt'
        self.gsfId = None
        self.device_config_token = None
        self.proxies_config = proxies_config
        self.deviceBuilder = config.DeviceBuilder(device_codename)
        self.set_locale(locale)
        self.set_timezone(timezone)

    def set_locale(self, locale):
        self.deviceBuilder.set_locale(locale)

    def set_timezone(self, timezone):
        self.deviceBuilder.set_timezone(timezone)

    def encrypt_password(self, login, passwd):
        """Encrypt the password using the google publickey, using
        the RSA encryption algorithm"""

        binaryKey = b64decode(config.GOOGLE_PUBKEY)
        i = utils.readInt(binaryKey, 0)
        modulus = utils.toBigInt(binaryKey[4:][0:i])
        j = utils.readInt(binaryKey, i+4)
        exponent = utils.toBigInt(binaryKey[i+8:][0:j])

        seq = asn1.DerSequence()
        seq.append(modulus)
        seq.append(exponent)

        publicKey = RSA.importKey(seq.encode())
        cipher = PKCS1_OAEP.new(publicKey)
        combined = login.encode() + b'\x00' + passwd.encode()
        encrypted = cipher.encrypt(combined)
        h = b'\x00' + SHA.new(binaryKey).digest()[0:4]
        return urlsafe_b64encode(h + encrypted)

    def setAuthSubToken(self, authSubToken):
        self.authSubToken = authSubToken

    def getDefaultHeaders(self):
        """Return the default set of request headers, which
        can later be expanded, based on the request type"""

        headers = {"Accept-Language": self.deviceBuilder.locale.replace('_', '-'),
                   "X-DFE-Encoded-Targets": config.DFE_TARGETS,
                   "User-Agent": self.deviceBuilder.getUserAgent(),
                   "X-DFE-Client-Id": "am-android-google",
                   "X-DFE-MCCMNC": self.deviceBuilder.device.get('celloperator'),
                   "X-DFE-Network-Type": "4",
                   "X-DFE-Content-Filters": "",
                   "X-DFE-Request-Params": "timeoutMs=4000"}
        if self.gsfId is not None:
            headers["X-DFE-Device-Id"] = "{0:x}".format(self.gsfId)
        if self.authSubToken is not None:
            headers["Authorization"] = "GoogleLogin auth=%s" % self.authSubToken
        if self.device_config_token is not None:
            headers["X-DFE-Device-Config-Token"] = self.device_config_token
        return headers

    def checkin(self, email, ac2dmToken):
        headers = self.getDefaultHeaders()
        headers["Content-Type"] = "application/x-protobuffer"

        request = self.deviceBuilder.getAndroidCheckinRequest()

        stringRequest = request.SerializeToString()
        res = requests.post(CHECKINURL, data=stringRequest,
                            headers=headers, verify=ssl_verify,
                            proxies=self.proxies_config)
        response = googleplay_pb2.AndroidCheckinResponse()
        response.ParseFromString(res.content)

        # checkin again to upload gfsid
        request2 = googleplay_pb2.AndroidCheckinRequest()
        request2.CopyFrom(request)
        request2.id = response.androidId
        request2.securityToken = response.securityToken
        request2.accountCookie.append("[" + email + "]")
        request2.accountCookie.append(ac2dmToken)
        stringRequest = request2.SerializeToString()
        requests.post(CHECKINURL, data=stringRequest,
                      headers=headers, verify=ssl_verify,
                      proxies=self.proxies_config)

        return response.androidId

    def uploadDeviceConfig(self):
        """Upload the device configuration of the fake device
        selected in the __init__ methodi to the google account."""

        upload = googleplay_pb2.UploadDeviceConfigRequest()
        upload.deviceConfiguration.CopyFrom(self.deviceBuilder.getDeviceConfig())
        headers = self.getDefaultHeaders()
        headers["X-DFE-Enabled-Experiments"] = "cl:billing.select_add_instrument_by_default"
        headers["X-DFE-Unsupported-Experiments"] = "nocache:billing.use_charging_poller,market_emails,buyer_currency,prod_baseline,checkin.set_asset_paid_app_field,shekel_test,content_ratings,buyer_currency_in_app,nocache:encrypted_apk,recent_changes"
        headers["X-DFE-SmallestScreenWidthDp"] = "320"
        headers["X-DFE-Filter-Level"] = "3"
        stringRequest = upload.SerializeToString()
        response = requests.post(UPLOADURL, data=stringRequest,
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

    def login(self, email=None, password=None, gsfId=None, authSubToken=None):
        """Login to your Google Account.
        For first time login you should provide:
            * email
            * password
        For the following logins you need to provide:
            * gsfId
            * authSubToken"""
        if email is not None and password is not None:
            # First time setup, where we obtain an ac2dm token and
            # upload device information

            encryptedPass = self.encrypt_password(email, password).decode('utf-8')
            # AC2DM token
            params = self.deviceBuilder.getLoginParams(email, encryptedPass)
            params['service'] = 'ac2dm'
            params['add_account'] = '1'
            params['callerPkg'] = 'com.google.android.gms'
            headers = self.deviceBuilder.getAuthHeaders(self.gsfId)
            headers['app'] = 'com.google.android.gsm'
            response = requests.post(AUTHURL, data=params, verify=ssl_verify,
                                     proxies=self.proxies_config)
            data = response.text.split()
            params = {}
            for d in data:
                if "=" not in d:
                    continue
                k, v = d.split("=", 1)
                params[k.strip().lower()] = v.strip()
            if "auth" in params:
                ac2dmToken = params["auth"]
            elif "error" in params:
                if "NeedsBrowser" in params["error"]:
                    raise LoginError("Security check is needed, try to visit "
                                     "https://accounts.google.com/b/0/DisplayUnlockCaptcha "
                                     "to unlock, or setup an app-specific password")
                raise LoginError("server says: " + params["error"])
            else:
                raise LoginError("Auth token not found.")

            self.gsfId = self.checkin(email, ac2dmToken)
            self.getAuthSubToken(email, encryptedPass)
            self.uploadDeviceConfig()
        elif gsfId is not None and authSubToken is not None:
            # no need to initialize API
            self.gsfId = gsfId
            self.setAuthSubToken(authSubToken)
            # check if token is valid with a simple search
            self.search('firefox', 1, None)
        else:
            raise LoginError('Either (email,pass) or (gsfId, authSubToken) is needed')

    def getAuthSubToken(self, email, passwd):
        requestParams = self.deviceBuilder.getLoginParams(email, passwd)
        requestParams['service'] = 'androidmarket'
        requestParams['app'] = 'com.android.vending'
        headers = self.deviceBuilder.getAuthHeaders(self.gsfId)
        headers['app'] = 'com.android.vending'
        response = requests.post(AUTHURL,
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
        if "token" in params:
            master_token = params["token"]
            second_round_token = self.getSecondRoundToken(master_token, requestParams)
            self.setAuthSubToken(second_round_token)
        elif "error" in params:
            raise LoginError("server says: " + params["error"])
        else:
            raise LoginError("auth token not found.")

    def getSecondRoundToken(self, first_token, params):
        if self.gsfId is not None:
            params['androidId'] = "{0:x}".format(self.gsfId)
        params['Token'] = first_token
        params['check_email'] = '1'
        params['token_request_options'] = 'CAA4AQ=='
        params['system_partition'] = '1'
        params['_opt_is_called_from_account_manager'] = '1'
        params.pop('Email')
        params.pop('EncryptedPasswd')
        headers = self.deviceBuilder.getAuthHeaders(self.gsfId)
        headers['app'] = 'com.android.vending'
        response = requests.post(AUTHURL,
                                 data=params,
                                 headers=headers,
                                 verify=ssl_verify,
                                 proxies=self.proxies_config)
        data = response.text.split()
        params = {}
        for d in data:
            if "=" not in d:
                continue
            k, v = d.split("=", 1)
            params[k.strip().lower()] = v.strip()
        if "auth" in params:
            return params["auth"]
        elif "error" in params:
            raise LoginError("server says: " + params["error"])
        else:
            raise LoginError("Auth token not found.")

    def executeRequestApi2(self, path, post_data=None, content_type=None, params=None):
        if self.authSubToken is None:
            raise Exception("You need to login before executing any request")
        headers = self.getDefaultHeaders()

        if content_type is None:
            content_type = "application/x-www-form-urlencoded; charset=UTF-8"
        headers["Content-Type"] = content_type
        url = FDFE + path
        if post_data is not None:
            response = requests.post(url,
                                     data=str(post_data),
                                     headers=headers,
                                     params=params,
                                     verify=ssl_verify,
                                     timeout=60,
                                     proxies=self.proxies_config)
        else:
            response = requests.get(url,
                                    headers=headers,
                                    params=params,
                                    verify=ssl_verify,
                                    timeout=60,
                                    proxies=self.proxies_config)

        message = googleplay_pb2.ResponseWrapper.FromString(response.content)
        if message.commands.displayErrorMessage != "":
            raise RequestError(message.commands.displayErrorMessage)

        return message

    def searchSuggest(self, query):
        params = {"c": "3",
                  "q": requests.utils.quote(query),
                  "ssis": "120",
                  "sst": "2"}
        data = self.executeRequestApi2("searchSuggest", params=params)
        response = data.payload.searchSuggestResponse
        return [{"type": e.type,
                 "suggestedQuery": e.suggestedQuery,
                 "title": e.title} for e in response.entry]

    def search(self, query, nb_result, offset=None):
        """ Search the play store for an app.

        nb_result is the maximum number of result to be returned.

        offset is used to take result starting from an index.
        """
        if self.authSubToken is None:
            raise Exception("You need to login before executing any request")

        remaining = nb_result
        output = []

        nextPath = "search?c=3&q=%s" % requests.utils.quote(query)
        if (offset is not None):
            nextPath += "&o=%d" % int(offset)
        while remaining > 0 and nextPath is not None:
            currentPath = nextPath
            data = self.executeRequestApi2(currentPath)
            if utils.hasPrefetch(data):
                response = data.preFetch[0].response
            else:
                response = data
            if utils.hasSearchResponse(response.payload):
                # we still need to fetch the first page, so go to
                # next loop iteration without decrementing counter
                nextPath = response.payload.searchResponse.nextPageUrl
                continue
            if utils.hasListResponse(response.payload):
                cluster = response.payload.listResponse.cluster
                if len(cluster) == 0:
                    # strange behaviour, probably due to expired token
                    raise LoginError('Unexpected behaviour, probably expired '
                                     'token')
                cluster = cluster[0]
                if len(cluster.doc) == 0:
                    break
                if cluster.doc[0].containerMetadata.nextPageUrl != "":
                    nextPath = cluster.doc[0].containerMetadata.nextPageUrl
                else:
                    nextPath = None
                apps = list(chain.from_iterable([doc.child for doc in cluster.doc]))
                output += list(map(utils.fromDocToDictionary, apps))
                remaining -= len(apps)

        if len(output) > nb_result:
            output = output[:nb_result]

        return output

    def details(self, packageName):
        """Get app details from a package name.

        packageName is the app unique ID (usually starting with 'com.')."""
        path = "details?doc=%s" % requests.utils.quote(packageName)
        data = self.executeRequestApi2(path)
        return utils.fromDocToDictionary(data.payload.detailsResponse.docV2)

    def bulkDetails(self, packageNames):
        """Get several apps details from a list of package names.

        This is much more efficient than calling N times details() since it
        requires only one request. If an item is not found it returns an empty object
        instead of throwing a RequestError('Item not found') like the details() function

        Args:
            packageNames (list): a list of app IDs (usually starting with 'com.').

        Returns:
            a list of dictionaries containing docv2 data, or None
            if the app doesn't exist"""

        path = "bulkDetails"
        params = {'au': '1'}
        req = googleplay_pb2.BulkDetailsRequest()
        req.docid.extend(packageNames)
        data = req.SerializeToString()
        message = self.executeRequestApi2(path,
                                          post_data=data.decode("utf-8"),
                                          content_type="application/x-protobuf",
                                          params=params)
        response = message.payload.bulkDetailsResponse
        return [None if not utils.hasDoc(entry) else
                utils.fromDocToDictionary(entry.doc)
                for entry in response.entry]

    def getHomeApps(self):
        path = "homeV2?c=3&nocache_isui=true"
        data = self.executeRequestApi2(path)
        output = []
        cluster = data.preFetch[0].response.payload.listResponse.cluster[0]
        for doc in cluster.doc:
            output.append({"categoryId": doc.docid,
                           "categoryStr": doc.title,
                           "apps": [utils.fromDocToDictionary(c) for c in doc.child]})
        return output

    def browse(self, cat=None, subCat=None):
        """Browse categories. If neither cat nor subcat are specified,
        return a list of categories, otherwise it return a list of apps
        using cat (category ID) and subCat (subcategory ID) as filters."""
        path = "browse?c=3"
        if cat is not None:
            path += "&cat=%s" % requests.utils.quote(cat)
        if subCat is not None:
            path += "&ctr=%s" % requests.utils.quote(subCat)
        data = self.executeRequestApi2(path)

        if cat is None and subCat is None:
            # result contains all categories available
            return [{'name': c.name,
                     'dataUrl': c.dataUrl,
                     'catId': c.unknownCategoryContainer.categoryIdContainer.categoryId}
                    for c in data.payload.browseResponse.category]

        output = []
        clusters = []

        if utils.hasPrefetch(data):
            clusters = chain.from_iterable([pf.response.payload.listResponse.cluster
                                            for pf in data.preFetch])

        # result contains apps of a specific category
        # organized by sections
        for cluster in clusters:
            for doc in cluster.doc:
                apps = [a for a in doc.child]
                apps = list(map(utils.fromDocToDictionary,
                                apps))
                section = {'title': doc.title,
                           'docid': doc.docid,
                           'apps': apps}
                output.append(section)
        return output

    def list(self, cat, ctr=None, nb_results=None, offset=None):
        """List apps for a specfic category *cat*.

        If ctr (subcategory ID) is None, returns a list of valid subcategories.

        If ctr is provided, list apps within this subcategory."""
        path = "list?c=3&cat=%s" % requests.utils.quote(cat)
        if ctr is not None:
            path += "&ctr=%s" % requests.utils.quote(ctr)
        if nb_results is not None:
            path += "&n=%s" % requests.utils.quote(nb_results)
        if offset is not None:
            path += "&o=%s" % requests.utils.quote(offset)
        data = self.executeRequestApi2(path)
        if ctr is None:
            # list subcategories
            clusters = chain.from_iterable([pf.response.payload.listResponse.cluster
                                            for pf in data.preFetch])
            docs = chain.from_iterable([c.doc for c in clusters])
            return [d.docid for d in docs]
        else:
            # list apps for specific subcat
            docs = chain.from_iterable([c.doc for c in
                                        data.payload.listResponse.cluster])
            childs = chain.from_iterable([d.child for d in docs])
            return [utils.fromDocToDictionary(c)
                    for c in childs]

    def reviews(self, packageName, filterByDevice=False, sort=2,
                nb_results=None, offset=None):
        """Browse reviews for an application

        Args:
            packageName (str): app unique ID.
            filterByDevice (bool): filter results for current device
            sort (int): sorting criteria (values are unknown)
            nb_results (int): max number of reviews to return
            offset (int): return reviews starting from an offset value

        Returns:
            dict object containing all the protobuf data returned from
            the api
        """
        path = "rev?doc=%s&sort=%d" % (requests.utils.quote(packageName), sort)
        if (nb_results is not None):
            path += "&n=%d" % int(nb_results)
        if (offset is not None):
            path += "&o=%d" % int(offset)
        if(filterByDevice):
            path += "&dfil=1"
        data = self.executeRequestApi2(path)
        output = []
        for rev in data.payload.reviewResponse.getResponse.review:
            author = {'personIdString': rev.author2.personIdString,
                      'personId': rev.author2.personId,
                      'name': rev.author2.name,
                      'profilePicUrl': rev.author2.urls.url,
                      'googlePlusUrl': rev.author2.googlePlusUrl}
            review = {'documentVersion': rev.documentVersion,
                      'timestampMsec': rev.timestampMsec,
                      'starRating': rev.starRating,
                      'comment': rev.comment,
                      'commentId': rev.commentId,
                      'author': author}
            output.append(review)
        return output

    def _deliver_data(self, url, cookies):
        headers = self.getDefaultHeaders()
        response = requests.get(url, headers=headers,
                                cookies=cookies, verify=ssl_verify,
                                stream=True, timeout=60,
                                proxies=self.proxies_config)
        total_size = response.headers.get('content-length')
        chunk_size = 32 * (1 << 10)
        return {'data': response.iter_content(chunk_size=chunk_size),
                'total_size': total_size,
                'chunk_size': chunk_size}

    def delivery(self, packageName, versionCode=None, offerType=1,
                 downloadToken=None, expansion_files=False):
        """Download an already purchased app.

        Args:
            packageName (str): app unique ID (usually starting with 'com.')
            versionCode (int): version to download
            offerType (int): different type of downloads (mostly unused for apks)
            downloadToken (str): download token returned by 'purchase' API
            progress_bar (bool): wether or not to print a progress bar to stdout

        Returns:
            Dictionary containing apk data and a list of expansion files. As stated
            in android documentation, there can be at most 2 expansion files, one with
            main content, and one for patching the main content. Their names should
            follow this format:

            [main|patch].<expansion-version>.<package-name>.obb

            Data to build this name string is provided in the dict object. For more
            info check https://developer.android.com/google/play/expansion-files.html
        """

        if versionCode is None:
            # pick up latest version
            versionCode = self.details(packageName).get('versionCode')

        path = "delivery"
        params = {'ot': str(offerType),
                  'doc': packageName,
                  'vc': str(versionCode)}
        headers = self.getDefaultHeaders()
        if downloadToken is not None:
            params['dtok'] = downloadToken
        url = "https://android.clients.google.com/fdfe/%s" % path
        response = requests.get(url, headers=headers,
                                params=params, verify=ssl_verify,
                                timeout=60,
                                proxies=self.proxies_config)
        response = googleplay_pb2.ResponseWrapper.FromString(response.content)
        if response.commands.displayErrorMessage != "":
            raise RequestError(response.commands.displayErrorMessage)
        elif response.payload.deliveryResponse.appDeliveryData.downloadUrl == "":
            raise RequestError('App not purchased')
        else:
            result = {}
            result['docId'] = packageName
            result['additionalData'] = []
            downloadUrl = response.payload.deliveryResponse.appDeliveryData.downloadUrl
            cookie = response.payload.deliveryResponse.appDeliveryData.downloadAuthCookie[0]
            cookies = {
                str(cookie.name): str(cookie.value)
            }
            result['file'] = self._deliver_data(downloadUrl, cookies)
            if not expansion_files:
                return result
            for obb in response.payload.deliveryResponse.appDeliveryData.additionalFile:
                a = {}
                # fileType == 0 -> main
                # fileType == 1 -> patch
                if obb.fileType == 0:
                    obbType = 'main'
                else:
                    obbType = 'patch'
                a['type'] = obbType
                a['versionCode'] = obb.versionCode
                a['file'] = self._deliver_data(obb.downloadUrl, None)
                result['additionalData'].append(a)
            return result

    def download(self, packageName, versionCode=None, offerType=1, expansion_files=False):
        """Download an app and return its raw data (APK file). Free apps need
        to be "purchased" first, in order to retrieve the download cookie.
        If you want to download an already purchased app, use *delivery* method.

        Args:
            packageName (str): app unique ID (usually starting with 'com.')
            versionCode (int): version to download
            offerType (int): different type of downloads (mostly unused for apks)
            downloadToken (str): download token returned by 'purchase' API
            progress_bar (bool): wether or not to print a progress bar to stdout

        Returns
            Dictionary containing apk data and optional expansion files
            (see *delivery*)
        """

        if self.authSubToken is None:
            raise Exception("You need to login before executing any request")

        if versionCode is None:
            # pick up latest version
            versionCode = self.details(packageName).get('versionCode')

        path = "purchase"
        headers = self.getDefaultHeaders()
        params = {'ot': str(offerType),
                  'doc': packageName,
                  'vc': str(versionCode)}
        url = FDFE + path
        self.log(packageName)
        response = requests.post(url, headers=headers,
                                 params=params, verify=ssl_verify,
                                 timeout=60,
                                 proxies=self.proxies_config)

        response = googleplay_pb2.ResponseWrapper.FromString(response.content)
        if response.commands.displayErrorMessage != "":
            raise RequestError(response.commands.displayErrorMessage)
        else:
            dlToken = response.payload.buyResponse.downloadToken
            return self.delivery(packageName, versionCode, offerType, dlToken,
                                 expansion_files=expansion_files)

    def log(self, docid):
        log_request = googleplay_pb2.LogRequest()
        log_request.downloadConfirmationQuery = "confirmFreeDownload?doc=" + docid
        timestamp = int(time.strftime('%H%M%S'))
        log_request.timestamp = timestamp

        string_request = log_request.SerializeToString()
        response = requests.post(LOGURL,
                                 data=string_request,
                                 headers=self.getDefaultHeaders(),
                                 verify=ssl_verify,
                                 timeout=60,
                                 proxies=self.proxies_config)
        response = googleplay_pb2.ResponseWrapper.FromString(response.content)
        if response.commands.displayErrorMessage != "":
            raise RequestError(response.commands.displayErrorMessage)

    @staticmethod
    def getDevicesCodenames():
        return config.getDevicesCodenames()

    @staticmethod
    def getDevicesReadableNames():
        return config.getDevicesReadableNames()

    def write_cache(self, gsfId, token):
        if not os.path.exists(CACHEDIR):
            os.makedirs(os.path.dirname(CACHEDIR))
        info = {'gsfId': gsfId, 'token': token}
        pickle.dump(info, open(self.cachefile, "wb"))

    def read_cache(self):
        try:
            with open(self.cachefile, "rb") as f:
                info = pickle.load(f)
        except:
            info = None
        return info

    def refresh_cache(self, email, password):
        self.login(email, password, None, None)
        self.write_cache(self.gsfId, self.authSubToken)
        return self

    def do_login(self, email, password):
        cacheinfo = self.read_cache()
        if cacheinfo:
            # Sign in using cached info
            try:
                self.login(None, None, cacheinfo['gsfId'], cacheinfo['token'])
            except:
                self.refresh_cache(email, password)
        else:
            # Re-authenticate using email and pass and save info to cache
            self.refresh_cache(email, password)
        return self