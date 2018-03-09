import os
import unittest

from gpapi.googleplay import GooglePlayAPI

class TestGooglePlay(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        cls.EMAIL = os.environ['EMAIL']
        cls.PASSWORD = os.environ['PASSWORD']
        cls.GSFID = int(os.environ['GSFID'], 16)
        # Next, get AUTHSUBTOKEN. These expire, so it must be regenerated each
        # time the tests are run.
        api = GooglePlayAPI(locale='en_US', timezone='EST')
        c_password = api.encrypt_password(
            cls.EMAIL, cls.PASSWORD).decode('utf-8')
        api.getAuthSubToken(cls.EMAIL, c_password)
        cls.AUTHSUBTOKEN = api.authSubToken

    def setUp(self):
        # Create a fresh instance of GooglePlayAPI for each test
        self.API = GooglePlayAPI(locale='en_US', timezone='EST')
        self.API.login(gsfId=self.GSFID, authSubToken=self.AUTHSUBTOKEN)

    def test_search(self):
        # Search for 'firefox', requesting just 1 result
        results = self.API.search('firefox', 1)
        self.assertTrue(len(results), 1)
        result = results[0]
        # Check that the legit Firefox app was found
        self.assertEqual(result['docId'], 'org.mozilla.firefox')
        # TODO Add assertions for each of the attributes which the rest of our
        # code depends on. For now, I think this is the only attribute we
        # depend on.
        self.assertIn('versionCode', result)
