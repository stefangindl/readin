Crawling stuff from Twitter
===========================

The function :code:`from_twitter()` downloads the timeline of a profile and
converts it to a :code:`pandas.DataFrame()`. The profile's screen name and
the app's Twitter credentials are passed into the function:

.. code-block:: python

   import readin
   
   creds = {
            'access_token': 'access_token',
            'access_token_secret': 'access_token_secret',
            'consumer_key': 'consumer_key',
            'consumer_secret': 'consumer_secret',
            }
   df = readin.from_twitter(
                            profile,
                            **creds,
                            as_file=True,
                            )

Setting :code:`as_file=True` spares you the hassle of calling 
:code:`df.to_csv('fname.csv')` another time and saves the
dataframe in :code:`f'{profile}.csv'`


API Documentation
-----------------

.. automodule:: readin.twitter
   :members: from_twitter
