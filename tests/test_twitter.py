#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
MODULE DOCUMENTATION
"""

import os
import unittest

import tweepy

from .context import readin
from .context import twitter


def get_credentials():
    creds = {
        'access_token': os.environ.get('TWITTER_ACCESS_TOKEN', ''),
        'access_token_secret': os.environ.get('TWITTER_ACCESS_TOKEN_SECRET',
                                              ''),
        'consumer_key': os.environ.get('TWITTER_CONSUMER_KEY', ''),
        'consumer_secret': os.environ.get('TWITTER_CONSUMER_SECRET', ''),
    }
    if any([True for val in creds.values() if val == '']):
        creds = None
    return creds


@unittest.skipIf(not get_credentials(), "Credentials not in env variables.")
class TwitterTestSuite(unittest.TestCase):

    def setUp(self):

        self.creds = get_credentials()

    def test_timeline_crawl(self):
        """
        This is an end-to-end test that will only work when Twitter credentials
        are provided.
        """

        df = readin.from_twitter('stefan_gindl', **self.creds)
        assert df.shape == (92, 26)

    def test_authenticate(self):
        """
        Tests if the OAuth dance is done correctly.
        """

        api = twitter.authenticate(**self.creds)
        assert isinstance(api.verify_credentials(), tweepy.models.User)
