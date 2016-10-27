import json
import random
import tweepy
import time
import datetime


from tweepy.streaming import StreamListener
from tweepy import OAuthHandler
from tweepy import Stream
import elasticsearch
import collections

import requests
from requests_aws4auth import AWS4Auth
from elasticsearch import Elasticsearch, RequestsHttpConnection

consumer_key="your twitter key"
consumer_secret="your twitter key"
access_token="your twitter key"
access_token_secret="your twitter key"

host = 'search-anirudh-kiran-twit-1-5zni7ksbpvchyaemgiwux3rzpi.us-west-2.es.amazonaws.com'
AWS_ACCESS_KEY = "your aws key"
AWS_SECRET_KEY = "your aws key"
REGION = "us-west-2"

awsauth = AWS4Auth(AWS_ACCESS_KEY, AWS_SECRET_KEY, REGION, 'es')

es = Elasticsearch(
    hosts=[{'host': host, 'port': 443}],
    http_auth=awsauth,
    use_ssl=True,
    verify_certs=True,
    connection_class=RequestsHttpConnection
)

search_key_array = ["TheWalkingDead", "Bentancur", "india", "DDoS", "apple", "dhoni", "chelsea", "facebook", "trump", "election", "hillary","RespectJustin","Drake","war","google"]
track_string = search_key_array[0]
for index in range(len(search_key_array)-1):
	track_string += ",%s" % search_key_array[index+1]


class StdOutListener(StreamListener):
	print ("class created")
	def on_data(self, data):
		if data is not None:
			dict = collections.OrderedDict()
			loc = collections.OrderedDict()
			tweet = json.loads(data)
			try:
				if tweet['id']:
					tweet_id = tweet['id']
				if tweet['text']:
					text= tweet['text']
				else :
					print("no text")
					return True
				if tweet['created_at']:
					dateTime = time.strftime('%Y-%m-%d %H:%M:%S', time.strptime(tweet['created_at'],'%a %b %d %H:%M:%S +0000 %Y'))
					date = str(datetime.datetime.strptime(dateTime, "%Y-%m-%d %H:%M:%S"))
				if tweet['user']:
					userName= str(tweet['user']['name'])
					userScreenName= str(tweet['user']['screen_name'])
				if tweet['coordinates']:
					coordinates = tweet['coordinates']['coordinates']
					longitude = coordinates[0]
					latitude = coordinates[1]
				elif tweet['place'] and tweet['place']['bounding_box'] and tweet['place']['bounding_box']['coordinates']:
					coordinates = tweet['place']['bounding_box']['coordinates'][0]
					longitude = (coordinates[0][0] + coordinates[2][0])/2
					latitude = (coordinates[0][1] + coordinates[2][1])/2
				else :
					print("no lat long")
					return True
				dict['text'] = text.replace("'","\'")
				dict['date'] = date
				dict['userName'] = userName
				dict['userScreenName'] = userScreenName
				dict['latitude'] = latitude
				dict['longitude'] = longitude
				dict['pin']={ 'location': str(latitude)+","+str(longitude)}
				search_key = []
				for key in search_key_array:
					if key.lower() in text.lower():
						search_key.append(key.lower())
				dict['search_key'] = search_key
				if (len(search_key)>0):
					print (search_key)
					jsonArray = json.dumps(dict)
					print(es.index(index='myposts2', doc_type='mytweets' ,id=tweet_id, body= jsonArray))

			except AttributeError as e:
				print ("Encountered a key AttributeError: "+str(e))
				return True		
			except KeyError as e:
				print ("Encountered a key error: "+str(e))
				return True	
			except Exception as e:
				print("err "+str(e))
				return True


		return True

	def on_error(self, status):
		print ("err: "+str(status))
		if status==420:
			return False
		return True


		
def main():
	listener = StdOutListener()
	auth = OAuthHandler(consumer_key, consumer_secret)
	auth.set_access_token(access_token, access_token_secret)
	stream = Stream(auth, listener)
	print("ready")
	try:
		mappings={"mappings": {"mytweets": {"properties": {"pin": {"properties": {"location": {"type": "geo_point"}}}}}}}
		print(es.indices.create(index='myposts2', body=json.dumps(mappings)))
	except Exception as e:
		print("err "+str(e))
	while 1==1:
		while True:
			try:
				stream.filter(track=search_key_array, locations=[-180,-90,180,90])
				print("done")
				break
			except tweepy.TweepError:
				print("tweepy error")
				print("error. sleeping in for :"+str(nsecs))
				nsecs=random.randint(60,63)
				time.sleep(nsecs)
		nmsecs=random.randint(60,63)
		print("error. sleeping out for :"+str(nmsecs))
		time.sleep(nmsecs)
			
if __name__ == '__main__':
	main()
