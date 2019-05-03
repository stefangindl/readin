# -*- coding: utf-8 -*-
import json

import pandas as pd
import tweepy


N_TWEETS_PER_REQUEST = 200


def from_twitter(profile, access_token=None, access_token_secret=None,
                 consumer_key=None, consumer_secret=None, as_file=None):
    """
    Downloads the timeline of a Twitter profile and turn it into a dataframe.

    Args:
        profiles: scalar or list of one/multiple Twitter screen names.
        access_token: the access token as provided by Twitter.
        access_token_secret: the access token as provided by Twitter.
        consumer_key: the consumer key as provided by Twitter.
        consumer_secret:the consumer secret as provided by Twitter.
        as_file: boolean.
    Returns:
        A dataframe, each row is a Tweet.

    """

    api = authenticate(
        consumer_key=consumer_key, consumer_secret=consumer_secret,
        access_token=access_token, access_token_secret=access_token_secret)
    if not api.verify_credentials():
        print("Credentials are invalid.")
        return None

    pages = fetch_timeline_pages(
        api, profile, n_tweets_per_request=N_TWEETS_PER_REQUEST)

    pages = [pd.DataFrame(page) for page in pages]
    df = pd.concat(pages)
    df['created_at'] = pd.to_datetime(df['created_at'])
    df.drop_duplicates(subset='created_at', inplace=True)

    if as_file:
        df.to_csv(f'{profile}.csv', index=False)

    return df


def authenticate(access_token=None, access_token_secret=None,
                 consumer_key=None, consumer_secret=None,):
    """
    Sends the credentials to the Twitter API and returns an API object upon
    success.

    Args:
        access_token: the access token as provided by Twitter.
        access_token_secret: the access token as provided by Twitter.
        consumer_key: the consumer key as provided by Twitter.
        consumer_secret:the consumer secret as provided by Twitter.
    """
    oauth = tweepy.OAuthHandler(consumer_key, consumer_secret)
    oauth.set_access_token(access_token, access_token_secret)
    api = tweepy.API(oauth)
    return api


def fetch_timeline_pages(api, profile, n_tweets_per_request=None):
    """
    Browses through the timeline of the profile and appends each returned
    page objects to a list, which is returned.

    Args: api: a
        profile: the Twitter profile's screen name as a string.
        n_tweets_per_request: number of Tweets Twitter will return per request.
    Returns:
        list: the returned timeline pages.
    """
    # Twitter allows a maximum of 200, see https://developer.twitter.com/en
    # /docs/tweets/timelines/api-reference/get-statuses-user_timeline.html

    id_oldest_tweet = None
    pages = []

    while True:
        page = fetch_timeline_page(
            api, profile, include_rts=True, max_id=id_oldest_tweet,
            n_tweets_per_request=n_tweets_per_request)
        if is_last_page(page):
            break
        id_oldest_tweet = page[-1]['id']
        pages.append(page)

    return pages


def fetch_timeline_page(api, profile, include_rts=None, max_id=None,
                        n_tweets_per_request=None):
    """
    Iterates over the timeline of a profile and returns the result as a list
    of .json

    Args:
        api: A Twitter API object with credentials confirmed and acces tokens
        set.
        profile: The account name as a string.

    Returns:
        list: A list of Tweets as json objects.
    """
    timeline = api.user_timeline(profile, count=n_tweets_per_request,
                                 include_rts=True, max_id=max_id)
    return [preserve_json(tweet) for tweet in timeline]


def preserve_json(tweet):
    tweet = tweet._json
    tweet['entities'] = json.dumps(tweet['entities'])
    tweet['user'] = json.dumps(tweet['user'])
    return tweet


def is_last_page(page):
    """
    The last page is either empty or only the one Tweet, the last Tweet of the
    previous page repeated.

    Args:
        page: a Twitter timeline page
    Returns:
        boolean: True if page is the last page.
    """
    return len(page) == 1 or len(page) == 0
