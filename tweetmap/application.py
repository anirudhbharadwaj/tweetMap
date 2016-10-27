from __future__ import print_function
from flask import Flask, redirect, url_for, request, render_template
import json
import os
from requests_aws4auth import AWS4Auth
from elasticsearch import Elasticsearch, RequestsHttpConnection

template_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'templates')
static_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'static')
application = Flask(__name__, template_folder=template_dir, static_folder=static_dir)

host = 'search-anirudh-kiran-twit-1-5zni7ksbpvchyaemgiwux3rzpi.us-west-2.es.amazonaws.com'
AWS_ACCESS_KEY = "your key"
AWS_SECRET_KEY = "your key"
REGION = "us-west-2"

awsauth = AWS4Auth(AWS_ACCESS_KEY, AWS_SECRET_KEY, REGION, 'es')

es = Elasticsearch(
    hosts=[{'host': host, 'port': 443}],
    http_auth=awsauth,
    use_ssl=True,
    verify_certs=True,
    connection_class=RequestsHttpConnection
)


@application.route ('/',methods = ['POST', 'GET'])
def processInput():
	if request.method == 'POST':
		searchKey = request.form['keyword']
		type_txt= request.form['happy']
		isnormal=request.form['isnormal']
		lat=""
		lng=""
		dist=request.form['distance']
		if(isnormal is "2"):
			lat=str(request.form['lat'])
			lng=str(request.form['lng'])
		print("success ", searchKey+" : "+type_txt)
		tweets = getMatchingTweets(searchKey,type_txt,isnormal,lat,lng,dist)
	else:
		tweets = ""	
	return render_template('tweetmap.html', tweets = tweets)
	

def getMatchingTweets(search_key,type_txt,isnormal,lat,lng,dist):
	listOfTweetsAsList = []
	dict = {}
	resultDict={}
	print("START")
	bodyOfRequest=""
	if(isnormal is "1"):
		bodyOfRequest = '{"fields" : ["latitude", "longitude","userName","text","date","userScreenName"],"query":{"term":{"search_key" : "'+search_key.lower()+'" }},"size":3000}'
	else:
		bodyOfRequest = '{"fields" : ["latitude", "longitude","userName","text","date","userScreenName"],"query":{"filtered": {"query": {"match_all": {}},"filter": {"and": [{"geo_distance" : {"distance" : "'+dist+'km","pin.location": ['+lng+','+lat+']} },{"term":{"search_key" : "'+search_key.lower()+'" }}] }}},"size":3000}'
	print ("BODY" + bodyOfRequest)
	res = es.search(index="myposts2", doc_type="mytweets", body = bodyOfRequest)
	print("%d documents found" % res['hits']['total'])
	resultDict['search_key'] = search_key
	resultDict['type_txt']=type_txt
	resultDict['dist']=dist
	resultDict['lat']=lat
	resultDict['lng']=lng
	resultDict['isnormal']=isnormal
	if res['hits']['total'] is 0:
		print ("SORRY, NO MATCHING TWEETS FOUND")
		message = "NO_TWEETS"
		resultDict['message'] = message
		resultDict['result'] = None
	else:
		print ("HORRAY!!, FOUND A FEW MATCHING TWEETS")
		resultDict['message'] = "SUCCESS"
		for doc in res['hits']['hits']:
			dict['latitude'] = doc['fields']['latitude']
			dict['longitude'] = doc['fields']['longitude']
			dict['name'] = doc['fields']['userName']
			dict['userScreenName'] = doc['fields']['userScreenName']
			dict['text'] = doc['fields']['text']
			dict['date'] = doc['fields']['date']
			jsonArray = json.dumps(dict)
			listOfTweetsAsList.append(jsonArray)
		resultDict['result']=listOfTweetsAsList
	dataToReturn = stringEscape(str(json.dumps(resultDict)))
	return dataToReturn

def stringEscape(myString):
	return myString.translate(myString.maketrans({"-":  r"\-", "]":  r"\]", "\\": r"\\", "^":  r"\^", "$":  r"\$", "*":  r"\*", ".":  r"\.", "'":  r"\'", '"':  r'\"'}))


if __name__ == '__main__':
	application.run(host='0.0.0.0',debug = True)