from __future__ import absolute_import, print_function

from tweepy.streaming import StreamListener
from tweepy import OAuthHandler
from tweepy import Stream
import json
from bs4 import BeautifulSoup
import datetime
from pymongo import MongoClient

client = MongoClient()
db = client['twitter']
tweets = db['tweets']


consumer_key=""
consumer_secret=""
access_token=""
access_token_secret=""

class StdOutListener(StreamListener):

    def on_data(self, data):
        data = json.loads(data)
        sources = ['http://twitter.com/download/iphone',
                    'http://twitter.com/#!/download/ipad',
                    'http://twitter.com',
                    'http://twitter.com/download/android',
                    'http://www.twitter.com',
                    'https://mobile.twitter.com',
                    'https://about.twitter.com/products/tweetdeck']

        if 'limit' not in data.keys() and data['user']['lang'] == 'it': #Filtering Italian tweets, change the 'it', with what you need
            source_html = BeautifulSoup(data['source'], "lxml")
            source = source_html.find('a')['href']
            if source not in sources: #filtering the known providers
                print(source)
                elements = ['followers_count',
                'statuses_count',
                'profile_image_url_https',
                'geo_enabled',
                'screen_name',
                'following',
                'id_str',
                'location',
                'friends_count',
                'lang',
                'verified']
                post = { "date": datetime.datetime.utcnow()}
                for element in elements:
                    post[element] = data['user'][element]
                post_id = tweets.insert_one(post).inserted_id #Storing each elememt
                print(post_id)
        elif 'limit' in data.keys(): #avoid interruption during the scanning. If you have many spiders set a sleep time
            print(data)
        return True

    def on_error(self, status):
        print(status)

if __name__ == '__main__':
    l = StdOutListener()
    auth = OAuthHandler(consumer_key, consumer_secret)
    auth.set_access_token(access_token, access_token_secret)

    stream = Stream(auth, l)
    stream.filter(track=['hashtag'])
