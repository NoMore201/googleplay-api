from . import googleplay_pb2
from time import time
from os import path
from sys import version_info
from locale import getdefaultlocale
from re import match

VERSION = version_info[0]
if VERSION == 2:
    import ConfigParser
else:
    import configparser


DFE_TARGETS = "CAEScFfqlIEG6gUYogFWrAISK1WDAg+hAZoCDgIU1gYEOIACFkLMAeQBnASLATlASUuyAyqCAjY5igOMBQzfA/IClwFbApUC4ANbtgKVAS7OAX8YswHFBhgDwAOPAmGEBt4OfKkB5weSB5AFASkiN68akgMaxAMSAQEBA9kBO7UBFE1KVwIDBGs3go6BBgEBAgMECQgJAQIEAQMEAQMBBQEBBAUEFQYCBgUEAwMBDwIBAgOrARwBEwMEAg0mrwESfTEcAQEKG4EBMxghChMBDwYGASI3hAEODEwXCVh/EREZA4sBYwEdFAgIIwkQcGQRDzQ2fTC2AjfVAQIBAYoBGRg2FhYFBwEqNzACJShzFFblAo0CFxpFNBzaAd0DHjIRI4sBJZcBPdwBCQGhAUd2A7kBLBVPngEECHl0UEUMtQETigHMAgUFCc0BBUUlTywdHDgBiAJ+vgKhAU0uAcYCAWQ/5ALUAw1UwQHUBpIBCdQDhgL4AY4CBQICjARbGFBGWzA1CAEMOQH+BRAOCAZywAIDyQZ2MgM3BxsoAgUEBwcHFia3AgcGTBwHBYwBAlcBggFxSGgIrAEEBw4QEqUCASsWadsHCgUCBQMD7QICA3tXCUw7ugJZAwGyAUwpIwM5AwkDBQMJA5sBCw8BNxBVVBwVKhebARkBAwsQEAgEAhESAgQJEBCZATMdzgEBBwG8AQQYKSMUkAEDAwY/CTs4/wEaAUt1AwEDAQUBAgIEAwYEDx1dB2wGeBFgTQ"
GOOGLE_PUBKEY = "AAAAgMom/1a/v0lblO2Ubrt60J2gcuXSljGFQXgcyZWveWLEwo6prwgi3iJIZdodyhKZQrNWp5nKJ3srRXcUW+F1BD3baEVGcmEgqaLZUNBjm057pKRI16kB0YppeGx5qIQ5QjKzsR8ETQbKLNWgRY0QRNVz34kMJR3P/LgHax/6rmf5AAAAAwEAAQ=="
ACCOUNT = "HOSTED_OR_GOOGLE"

# parse phone config from the file 'device.properties'.
# if you want to add another phone, just create another section in
# the file. Some configurations for common phones can be found here:
# https://github.com/yeriomin/play-store-api/tree/master/src/main/resources
filepath = path.join(path.dirname(path.realpath(__file__)),
                     'device.properties')

if VERSION == 2:
    config = ConfigParser.ConfigParser()
else:
    config = configparser.ConfigParser()
config.read(filepath)


def getDevicesCodenames():
    """Returns a list containing devices codenames"""
    return config.sections()


def getDevicesReadableNames():
    """Returns codename and readable name for each device"""
    sections = getDevicesCodenames()
    output = []
    for s in sections:
        output.append({'codename': s,
                       'readableName': config[s]['userreadablename']})
    return output


class DeviceBuilder(object):

    def __init__(self, device):
        self.device = {}
        self.timezone = "Europe/Berlin"
        for (key, value) in config.items(device):
            self.device[key] = value

    def setLocale(self, locale):
        if locale is None:
            locale = getdefaultlocale()[0]

        # check if locale matches the structure of a common
        # value like "en_US"
        if match(r'[a-z]{2}\_[A-Z]{2}', locale) is None:
            locale = 'en_US'
        self.locale = locale

    def getUserAgent(self):
        return ("Android-Finsky/8.1.72.S-all [6] [PR] 165478484 ("
                "api=3"
                ",versionCode={versionCode}"
                ",sdk={sdk}"
                ",device={device}"
                ",hardware={hardware}"
                ",product={product}"
                "").format(versionCode=self.device['vending.version'],
                           sdk=self.device['build.version.sdk_int'],
                           device=self.device['build.device'],
                           hardware=self.device['build.hardware'],
                           product=self.device['build.product'])

    def getAuthParams(self, email, passwd):
        return {"Email": email,
                "EncryptedPasswd": passwd,
                "accountType": ACCOUNT,
                "has_permission": "1",
                "source": "android",
                "device_country": self.locale[0:2],
                "service": "androidmarket",
                "app": "com.android.vending",
                "lang": self.locale,
                "sdk_version": self.device['build.version.sdk_int']}

    def getLoginParams(self, email, encryptedPass):
        return {"Email": email,
                "EncryptedPasswd": encryptedPass,
                "service": "ac2dm",
                "add_account": "1",
                "accountType": ACCOUNT,
                "has_permission": "1",
                "app": "com.google.android.gsf",
                "source": "android",
                "device_country": self.locale[0:2],
                "lang": self.locale,
                "sdk_version": self.device['build.version.sdk_int']}

    def getAndroidCheckinRequest(self):
        request = googleplay_pb2.AndroidCheckinRequest()
        request.id = 0
        request.checkin.CopyFrom(self.getAndroidCheckin())
        request.locale = self.locale
        request.timeZone = self.timezone
        request.version = 3
        request.deviceConfiguration.CopyFrom(self.getDeviceConfig())
        request.fragment = 0
        return request

    def getDeviceConfig(self):
        libList = self.device['sharedlibraries'].split(",")
        featureList = self.device['features'].split(",")
        localeList = self.device['locales'].split(",")
        glList = self.device['gl.extensions'].split(",")
        platforms = self.device['platforms'].split(",")

        hasFiveWayNavigation = (self.device['hasfivewaynavigation'] == 'true')
        hasHardKeyboard = (self.device['hashardkeyboard'] == 'true')
        deviceConfig = googleplay_pb2.DeviceConfigurationProto()
        deviceConfig.touchScreen = int(self.device['touchscreen'])
        deviceConfig.keyboard = int(self.device['keyboard'])
        deviceConfig.navigation = int(self.device['navigation'])
        deviceConfig.screenLayout = int(self.device['screenlayout'])
        deviceConfig.hasHardKeyboard = hasHardKeyboard
        deviceConfig.hasFiveWayNavigation = hasFiveWayNavigation
        deviceConfig.screenDensity = int(self.device['screen.density'])
        deviceConfig.screenWidth = int(self.device['screen.width'])
        deviceConfig.screenHeight = int(self.device['screen.height'])
        deviceConfig.glEsVersion = int(self.device['gl.version'])
        for x in platforms:
            deviceConfig.nativePlatform.append(x)
        for x in libList:
            deviceConfig.systemSharedLibrary.append(x)
        for x in featureList:
            deviceConfig.systemAvailableFeature.append(x)
        for x in localeList:
            deviceConfig.systemSupportedLocale.append(x)
        for x in glList:
            deviceConfig.glExtension.append(x)
        return deviceConfig

    def getAndroidBuild(self):
        androidBuild = googleplay_pb2.AndroidBuildProto()
        androidBuild.id = self.device['build.fingerprint']
        androidBuild.product = self.device['build.hardware']
        androidBuild.carrier = self.device['build.brand']
        androidBuild.radio = self.device['build.radio']
        androidBuild.bootloader = self.device['build.bootloader']
        androidBuild.device = self.device['build.device']
        androidBuild.sdkVersion = int(self.device['build.version.sdk_int'])
        androidBuild.model = self.device['build.model']
        androidBuild.manufacturer = self.device['build.manufacturer']
        androidBuild.buildProduct = self.device['build.product']
        androidBuild.client = self.device['client']
        androidBuild.otaInstalled = False
        androidBuild.timestamp = int(time()/1000)
        androidBuild.googleServices = int(self.device['gsf.version'])
        return androidBuild

    def getAndroidCheckin(self):
        androidCheckin = googleplay_pb2.AndroidCheckinProto()
        androidCheckin.build.CopyFrom(self.getAndroidBuild())
        androidCheckin.lastCheckinMsec = 0
        androidCheckin.cellOperator = self.device['celloperator']
        androidCheckin.simOperator = self.device['simoperator']
        androidCheckin.roaming = self.device['roaming']
        androidCheckin.userNumber = 0
        return androidCheckin
