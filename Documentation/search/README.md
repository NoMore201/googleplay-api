# Search

## Request

    GET https://android.clients.google.com/fdfe/search?c=3&q=firefox HTTP/1.1

Required headers are marked with a '*'

    [ ] X-Ad-Id: 70417864-0f86-4451-b5aa-103de27a6af5
    [ ] X-DFE-Content-Filters:
    [ ] X-DFE-Network-Type: 4
    [*] X-DFE-Encoded-Targets: CAESqwGzlYEGDsgF3gTRAkIC2AMCFJIHgAIWjgi1AVhAmQGOA4ICb+kKmAHgAQyGAS9o8gLzAe0BFvsLuAMBAsADjwLDFYUBNS2lCJYStgEBfgegAm2xAgEoAQYo4wvDAtAFqwIB+APWArYDwgHhBf0BjAICU+MGmgGRAZsC0AFMmgPkAuUBKyHOAVIC5QECrwEYAQYBowFLYgGpBYgDhQEBY0o2SqEDggJpYYgDtAMa9gQTAg7OATu1AaABCFoCAwRrN4DTzwKCu7EDAQEDAgQJCAgBAQIIAwEBAgEBAQICAgYBBhQKAQcCAwMEAhABAQHKAQETAwQCDecBfQolAhYFAgEKG3UMMxcBIQoUDwYHIjeEAQ4MFk0JUwV/EREYAQMNfgRfHhQQIwsOcGQEDQ9qowHAAoQBBIQBAgEBfA4ZGDYVARgBCwEoZQICJShzFCehBQYRGg43GBxpjQG0AVnQAR4nCzQmL1vUAWV3CQEK3gF2A30tDAMsZJ4BBIEBdFAfcogBigHMAgUFCc0BBUWgATk4jQIaYDUuzgENcqoBASCLA5IBqAImlwNhrQKEBnbjBfgBXaEBAQ8GAQEChwQEc5YBBlVtAUUB3AUyDnuzAZIBA4YGKxihAQcwASEBBwIgCBIdB6YDOAEaRoQBAfsBQHWnARkiAqMCLBYPvAsDAoABIocBO8kBygG2AQENAyeIAx7bAVKoBIMEqgETKQSLAbIDOhAndFdEOBWjAQGNAfUBGguZAUUMCwgvWwFpGrkBDhEgP3wLuAEhBgIUAb4DFG8TIa4BjgFFBgQCAQECWUKdAmIVBAEUxwESASQLWgoeJQIChAXCAQYjFTISxwFoBSFHEAEBWcsBMU5KkgEW0wGeAQceCDtk6AEGU44CpAHRAZIBC88BegEiTV0HSgQBBLgBDSYIMB0VCwIBed8BLW4DATaWAT0odAwCXztnERRVDSoDCkM/IwfKAgIHXQwCP1Y2bgQM+QICBgcUBREEWCZMAwwUGCRVKlNjHAMGGET/AQwBCwUHBJMBAn8RBx8eTwUqAgsJCw8HFAYECgoWBFoK0wIWMwY
    [ ] X-DFE-Cookie: <hidden>
    [*] User-Agent: Android-Finsky/8.1.72.S-all [6] [PR] 165478484 (api=3,versionCode=80817206,sdk=25,device=A0001,hardware=bacon,product=bacon,platformVersionRelease=7.1.2,model=A0001,buildId=NJH47F,isWideScreen=0,supportedAbis=armeabi-v7a;armeabi)
    [ ] X-DFE-Client-Id: am-android-oneplus
    [ ] X-Limit-Ad-Tracking-Enabled: false
    [ ] X-DFE-MCCMNC: 22201
    [*] X-DFE-Device-Id: <hidden>
    [ ] X-DFE-Request-Params: timeoutMs=4000
    [*] Accept-Language: en-US
    [*] Authorization: GoogleLogin auth=<hidden>
    [*] Host: android.clients.google.com
    [ ] Connection: Keep-Alive
    [ ] Accept-Encoding: gzip

## Notes
Search results can be divided into two categories:

1. Search query is *specific*.
2. Search query is *general*.

In the **(1)** case, the result will contain 4 DocV1 objects

- **doc[0]** contains only one element, which is the specific app (e.g. firefox).
- **doc[1]** corresponds to the `You Might Also Like` section, and contains other less related apps.
- **doc[2]** corresponds to the `Similar Apps` section of the play store, with nearly 20 apps.
- **doc[3]** corresponds to the `More Result` section, with nearly 20 apps related to the search query.

You can verify this behaviour by yourself reading the `search-response-specific.txt`, where the query was `firefox`.

In the **(2)** case, the results contains only 1 DocV1 objects, with at most 21-22 apps. There is also a *containerMetadata* object with the URL for the next page of results.
