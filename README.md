# Google play python3 API

This project contains an unofficial API for google play interactions. The code mainly comes from
[GooglePlayAPI project](https://github.com/egirault/googleplay-api/) which was written for python2 and it's not
maintained anymore. The code was ported to python3 with some minor additions and updates, mainly for python3 compatibility.

All credit goes to the original author [egirault](https://github.com/egirault).

This project is released under the BSD license.

# API reversing

Here are some example request reversed from LineageOS 14.1 (Android 7.1) with lastest play services (as of 06/09/2017):

### Search

**URL:** GET https://android.clients.google.com/fdfe/search?c=4&q=zodiac
```
X-Ad-Id: <hidden>
X-DFE-Device-Id: <hidden>
X-DFE-Content-Filters:
X-DFE-Network-Type: 4
X-DFE-Request-Params: timeoutMs=4000
X-DFE-Cookie: <hidden>
X-DFE-Encoded-Targets:        CAESqQGzlYEGDsgF3gTRAkIC2AMCFJIHgAIWjgi1AVhAmQGOA4ICb+kKmAHgAQyGAS9o8gLzAe0BFvsLuAMBAsADjwLDFYUBNS2lCJYStgEBfgegAm2xAgEoAQYo4wvDAtAFqwIB+APWArYDwgHhBf0BjAICU+MGmgGRAZsC0AFM/gXlASshzgFSAuUBAq8BGAEGAaMBS2IBqQWIA4UBAWNKNkqhA4ICaWGIA7QDGv4EEwIOzgE7tQGgAQhaAgMEazeA088CgruxAwEBAwIECQgIAQECCAMBAQIBAQECAgIGAQYUCgEHAgMDBAIQAQEBygEBEwMEAg3nAX0KJQIWBQIBCht1DDMXASEKFA8GByI3hAEODBZNCVMFfxERGAEDDX4EXx4UECMLDnBkBA0PaqMBwAKEAQSEAQIBAXwOGRg2FQEYAQsBKGUCAiUocxQnoQUGERoONxgcaY0BtAFZ0AEeJws0Ji9b1AFldwkBCt4BdgN9LQwDLGSeAQSBAXRQH3KIAYoBzAIFBQnNAQVFoAE5OI0CGmA1Ls4BDXKqAQEgiwOSAagCJpcDYa0ChAZ24wX4AV2hAQEPBgEBAocEBHOWAQZVbQFFAdwFMg57swGSAQOGBisYoQEHMAEhAQcCIAgSHQemAzgBGkaEAQH7AUB1pwEZIgKjAiwWD7wLAwKAASKHATvJAcoBtgEBDQMniAMe2wFSqASDBKoBEykEiwGyAzoQJ3RXRDgVowEBjQH1ARoLmQFFDAsIL1sBaRq5AQ4RX3wLuAEhBgIUAb4DFG8TIa4BjgFFBgQCAQECWUKdAmIVBAEUxwESASQLWgoeJQICBf8EwgEGIxUyEscBaAUhRxABAVnLATFOSpIBFtMBngEHHgg7ZOgBBlOOAqQB0QGSAQvPAXoBIk1dB0oEAQQ6BQcEAgVnDSYIMB0VCwIBed8BLW4DARUFBgcGnwE9KDY+DAJfO2cRFFUNKgMKQz8jB8oCAgddDAI/VjZuBAz5AgIGBxQFEQRYJkwDDBQYJFUqU2McAwYYRP8BDAELBQcEkwECfxEHHx5PBSoCCwkLDwcUBgQKChYEWgrTAhY
User-Agent: Android-Finsky/8.1.72.S-all%20%5B6%5D%20%5BPR%5D%20165478484 (api=3,versionCode=80817206,sdk=25,device=A0001,hardware=bacon,product=bacon,platformVersionRelease=7.1.2,model=A0001,buildId=NJH47F,isWideScreen=0,supportedAbis=armeabi-v7a;armeabi)
X-DFE-Client-Id: am-android-oneplus
X-Limit-Ad-Tracking-Enabled:  false
Authorization: GoogleLogin auth=<hidden>
Accept-Language: en-US
If-None-Match: 1903308838
Host: android.clients.google.com
Connection: Keep-Alive
Accept-Encoding: gzip
```

### Details (single)

**URL:** GET https://android.clients.google.com/fdfe/details?doc=com.google.android.apps.photos

```
X-Ad-Id: <hidden>
X-DFE-Device-Id: <hidden>
X-DFE-Content-Filters:
X-DFE-Network-Type: 4
X-DFE-Request-Params: timeoutMs=4000
X-DFE-Cookie: <hidden>
X-DFE-Encoded-Targets: CAESqQGzlYEGDsgF3gTRAkIC2AMCFJIHgAIWjgi1AVhAmQGOA4ICb+kKmAHgAQyGAS9o8gLzAe0BFvsLuAMBAsADjwLDFYUBNS2lCJYStgEBfgegAm2xAgEoAQYo4wvDAtAFqwIB+APWArYDwgHhBf0BjAICU+MGmgGRAZsC0AFM/gXlASshzgFSAuUBAq8BGAEGAaMBS2IBqQWIA4UBAWNKNkqhA4ICaWGIA7QDGv4EEwIOzgE7tQGgAQhaAgMEazeA088CgruxAwEBAwIECQgIAQECCAMBAQIBAQECAgIGAQYUCgEHAgMDBAIQAQEBygEBEwMEAg3nAX0KJQIWBQIBCht1DDMXASEKFA8GByI3hAEODBZNCVMFfxERGAEDDX4EXx4UECMLDnBkBA0PaqMBwAKEAQSEAQIBAXwOGRg2FQEYAQsBKGUCAiUocxQnoQUGERoONxgcaY0BtAFZ0AEeJws0Ji9b1AFldwkBCt4BdgN9LQwDLGSeAQSBAXRQH3KIAYoBzAIFBQnNAQVFoAE5OI0CGmA1Ls4BDXKqAQEgiwOSAagCJpcDYa0ChAZ24wX4AV2hAQEPBgEBAocEBHOWAQZVbQFFAdwFMg57swGSAQOGBisYoQEHMAEhAQcCIAgSHQemAzgBGkaEAQH7AUB1pwEZIgKjAiwWD7wLAwKAASKHATvJAcoBtgEBDQMniAMe2wFSqASDBKoBEykEiwGyAzoQJ3RXRDgVowEBjQH1ARoLmQFFDAsIL1sBaRq5AQ4RX3wLuAEhBgIUAb4DFG8TIa4BjgFFBgQCAQECWUKdAmIVBAEUxwESASQLWgoeJQICBf8EwgEGIxUyEscBaAUhRxABAVnLATFOSpIBFtMBngEHHgg7ZOgBBlOOAqQB0QGSAQvPAXoBIk1dB0oEAQQ6BQcEAgVnDSYIMB0VCwIBed8BLW4DARUFBgcGnwE9KDY+DAJfO2cRFFUNKgMKQz8jB8oCAgddDAI/VjZuBAz5AgIGBxQFEQRYJkwDDBQYJFUqU2McAwYYRP8BDAELBQcEkwECfxEHHx5PBSoCCwkLDwcUBgQKChYEWgrTAhY
User-Agent: Android-Finsky/8.1.72.S-all%20%5B6%5D%20%5BPR%5D%20165478484 (api=3,versionCode=80817206,sdk=25,device=A0001,hardware=bacon,product=bacon,platformVersionRelease=7.1.2,model=A0001,buildId=NJH47F,isWideScreen=0,supportedAbis=armeabi-v7a;armeabi)
X-DFE-Client-Id: am-android-oneplus
X-Limit-Ad-Tracking-Enabled: false
Authorization: GoogleLogin auth=<hidden>
Accept-Language: en-US
Host: android.clients.google.com
Connection: Keep-Alive
Accept-Encoding: gzip
```

### BulkDetails

**URL:** POST https://android.clients.google.com/fdfe/bulkDetails?au=1

```
X-DFE-Device-Id: <hidden>
X-DFE-Content-Filters:
X-DFE-Network-Type: 4
X-DFE-Request-Params: timeoutMs=30000
X-DFE-Cookie: <hidden>
X-DFE-Encoded-Targets: CAESqQGzlYEGDsgF3gTRAkIC2AMCFJIHgAIWjgi1AVhAmQGOA4ICb+kKmAHgAQyGAS9o8gLzAe0BFvsLuAMBAsADjwLDFYUBNS2lCJYStgEBfgegAm2xAgEoAQYo4wvDAtAFqwIB+APWArYDwgHhBf0BjAICU+MGmgGRAZsC0AFM/gXlASshzgFSAuUBAq8BGAEGAaMBS2IBqQWIA4UBAWNKNkqhA4ICaWGIA7QDGv4EEwIOzgE7tQGgAQhaAgMEazeA088CgruxAwEBAwIECQgIAQECCAMBAQIBAQECAgIGAQYUCgEHAgMDBAIQAQEBygEBEwMEAg3nAX0KJQIWBQIBCht1DDMXASEKFA8GByI3hAEODBZNCVMFfxERGAEDDX4EXx4UECMLDnBkBA0PaqMBwAKEAQSEAQIBAXwOGRg2FQEYAQsBKGUCAiUocxQnoQUGERoONxgcaY0BtAFZ0AEeJws0Ji9b1AFldwkBCt4BdgN9LQwDLGSeAQSBAXRQH3KIAYoBzAIFBQnNAQVFoAE5OI0CGmA1Ls4BDXKqAQEgiwOSAagCJpcDYa0ChAZ24wX4AV2hAQEPBgEBAocEBHOWAQZVbQFFAdwFMg57swGSAQOGBisYoQEHMAEhAQcCIAgSHQemAzgBGkaEAQH7AUB1pwEZIgKjAiwWD7wLAwKAASKHATvJAcoBtgEBDQMniAMe2wFSqASDBKoBEykEiwGyAzoQJ3RXRDgVowEBjQH1ARoLmQFFDAsIL1sBaRq5AQ4RX3wLuAEhBgIUAb4DFG8TIa4BjgFFBgQCAQECWUKdAmIVBAEUxwESASQLWgoeJQICBf8EwgEGIxUyEscBaAUhRxABAVnLATFOSpIBFtMBngEHHgg7ZOgBBlOOAqQB0QGSAQvPAXoBIk1dB0oEAQQ6BQcEAgVnDSYIMB0VCwIBed8BLW4DARUFBgcGnwE9KDY+DAJfO2cRFFUNKgMKQz8jB8oCAgddDAI/VjZuBAz5AgIGBxQFEQRYJkwDDBQYJFUqU2McAwYYRP8BDAELBQcEkwECfxEHHx5PBSoCCwkLDwcUBgQKChYEWgrTAhY
User-Agent: Android-Finsky/8.1.72.S-all%20%5B6%5D%20%5BPR%5D%20165478484 (api=3,versionCode=80817206,sdk=25,device=A0001,hardware=bacon,product=bacon,platformVersionRelease=7.1.2,model=A0001,buildId=NJH47F,isWideScreen=0,supportedAbis=armeabi-v7a;armeabi)
X-DFE-Client-Id: am-android-oneplus
Authorization: GoogleLogin auth=<hidden>
Accept-Language: en-US
Content-Type: application/x-protobuf
Content-Length: 345
Host: android.clients.google.com
Connection: Keep-Alive
Accept-Encoding: gzip
```

### Download (with DownloadManager)

**URL:** GET https://android.clients.google.com/market/download/Download?packageName=com.blizzard.bma&versionCode=37&ssl=1&token=AOTCm0RaA2KnsS7TNkToZHQ-HFvfoFcKVl8cEtfceae9R_D1AM7NUnBmYUQ94qbR7KE_WzE-ujoJ7zjyBPjxFXTycEPO2D3PEcEeEKRnRkT-lQnWBX0zBTVyxl3cl_SHNrsD4mU89DOlhd7MxFyjHXYy8Z0sjCEKoEkxN_sEI1Yc76cRvpfhhsD6Hp41B9qizcCWpYF40XXRVbbO75zsAA7Bx4tdyR-7xG5Fu8tVcTU1m9Apj3QyFrQYDmVCz642avKBW2FaZGup8Eg4ixX3LPGnV2t7sL2-kjFrKsnSg8pZ9McN9bqAwNi2jzuotwsrGPsB_YHeiC-mad44p4h7HrDrDojnclKVAGzvt2dVSpV83w&cf=2&did=0&cpn=mizUmddBG6L0EGEh

```
User-Agent: AndroidDownloadManager/7.1.2 (Linux; U; Android 7.1.2; A0001 Build/NJH47F)
Accept-Encoding: identity
Connection: close
Host: android.clients.google.com
```
