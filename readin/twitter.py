# -*- coding: utf-8 -*-
import json
import pandas as pd
import tweepy


N_TWEETS_PER_REQUEST = 200
N_TWEETS_REMAINING = 80000


def from_twitter(profile,
                 access_token=None,
                 access_token_secret=None,
                 consumer_key=None,
                 consumer_secret=None,
                 as_file=None,
                 ):
    """
    A convenience function to directly download the timeline of a Twitter
    profile. It does the following steps:

    - register credentials.
    - download the timelines of a list of profiles.
    - return the timelines as a :code:`pandas.DataFrame`.
    - optional: save the timelines to disk.

    Args:
        profiles: scalar or list of one/multiple Twitter screen names.
        access_token: the access token as provided by Twitter.
        access_token_secret: the access token as provided by Twitter.
        consumer_key: the consumer key as provided by Twitter.
        consumer_secret:the consumer secret as provided by Twitter.
        as_file: boolean.

    """

    api = provide_credentials(consumer_key=consumer_key,
                              consumer_secret=consumer_secret,
                              access_token=access_token,
                              access_token_secret=access_token_secret)
    if not api.verify_credentials():
        print("Credentials are invalid.")
        return None

    timeline = crawl(api,
                     profile,
                     n_tweets_per_request=N_TWEETS_PER_REQUEST,
                     n_tweets_remaining=N_TWEETS_REMAINING,
                     )

    if as_file:
        timeline.to_csv(f'{profile}.csv', index=False)

    return timeline


def provide_credentials(consumer_key=None, consumer_secret=None,
                        access_token=None, access_token_secret=None):
    oauth = tweepy.OAuthHandler(consumer_key, consumer_secret)
    oauth.set_access_token(access_token, access_token_secret)
    api = tweepy.API(oauth)
    return api


def crawl(api, profile, n_tweets_per_request=None, n_tweets_remaining=None):

    # Twitter allows a maximum of 200, see https://developer.twitter.com/en
    # /docs/tweets/timelines/api-reference/get-statuses-user_timeline.html

    id_oldest_tweet = None
    timeline = pd.DataFrame()

    while True:
        new_timeline = fetch_timeline(
            api, profile, include_rts=True, max_id=id_oldest_tweet,
            n_tweets_per_request=n_tweets_per_request,
            n_tweets_remaining=n_tweets_remaining)
        if len(new_timeline) == 1:
            break
        if len(new_timeline) == 0:
            break

        new_timeline = load_as_df(new_timeline)
        if timeline.empty:
            timeline = load_as_df(new_timeline)
        else:
            timeline = timeline.append(new_timeline,
                                       ignore_index=True,
                                       sort=True)

        id_oldest_tweet = get_id_oldest_tweet(timeline)

    timeline = remove_duplicates(timeline)
    return timeline


def get_id_oldest_tweet(timeline):
    idx = timeline.index[timeline['created_at']
                         == timeline['created_at'].min()]
    idx = idx.tolist()[0]
    id_oldest_tweet = timeline.loc[idx, 'id']
    return id_oldest_tweet


def remove_duplicates(timeline):
    """
    Removes duplicates that occur during the crawl process. Currently, this is
    when the profile.timeline() method is called with a max_id. Twitter
    includes the Twitter with this ID in the response too, even though it is
    already there in the response of the previous call.
    """
    timeline.drop_duplicates(subset='created_at', inplace=True)
    return timeline


def fetch_timeline(api,
                   profile,
                   include_rts=None,
                   max_id=None,
                   n_tweets_per_request=None,
                   n_tweets_remaining=None,
                   ):
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
    timeline = api.user_timeline(profile,
                                 count=n_tweets_per_request,
                                 include_rts=True,
                                 max_id=max_id)
    timeline = timeline[:n_tweets_remaining]
    timeline = [preserve_json(k) for k in timeline]
    return timeline


def preserve_json(tweet):
    tweet = tweet._json
    tweet['entities'] = json.dumps(tweet['entities'])
    tweet['user'] = json.dumps(tweet['user'])
    return tweet


def load_as_df(timeline):
    """
    Turns a Twitter timeline into a DataFrame, and converts all columns to the
    required datatype.

    Args:
        timeline: A list with Tweets as json objects.
    """

    timeline = pd.DataFrame(timeline)
    timeline['created_at'] = pd.to_datetime(timeline['created_at'])
    return timeline
