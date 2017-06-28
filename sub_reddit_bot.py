import praw 
import json
import requests
import tweepy
import time
import datetime


subreddit = 'your subreddit'
tag_string = "#whatever tags you want"
num_tweets_before_stopping = 30 #set same as get
tweet_delay = 15  #in minutes

#personalized access API for twitter
access_token = 'GET FROM TWITTER API'
access_token_secret = 'GET FROM TWITTER API'
consumer_key = 'GET FROM TWITTER API'
consumer_secret = 'GET FROM TWITTER API'

#google API key for shorten function 
google_api_key = "GET FROM google API"

def strip_title(title, tag_length):
	#makes title shorter with ... if it is too long for tweet
	char_remain = 140 - tag_length - 26 #24 for link and 2 for spaces 
	if len(title) <= char_remain:
		return title
	elif len(title) >= 3:
		print("Making the post '" + title + "' smaller.")
		return title[:char_remain-3] + "..."
	else: 
		return ""
		
def shorten(url):
	try:
		#uses goog.le API to make links shorter so more char's can be used in the tweet #24 chars
		googl_url = "https://www.googleapis.com/urlshortener/v1/url?key=" + google_api_key
		payload = {"longUrl": url}
		headers = {'content-type': 'application/json'}
		r = requests.post(googl_url, data=json.dumps(payload), headers=headers)
		url = json.loads(r.text)['id']
		print("[bot] Generating short link using goo.gl")
	except:
		print("[bot] unverified google api key, defaulting to twitter's t.co shortner")
	return url

def add_id_to_file(id):
  #adds the post ID to the text file
	with open('posted_posts.txt', 'a') as file:
		file.write(str(id) + "\n")
	file.close()		
	
def duplicate_check(post_id):
  #checks to see if the post id already exists in the text file
	found = 0
	with open('posted_posts.txt', 'r') as file:
		for line in file.read().splitlines():
			if post_id == line:
				found = 1
	file.close()			
	return found
	
def create_tweet(subreddit):
	print('[bot] setting up connection with Reddit')
	#connect to reddit using praw
	r = praw.Reddit(client_id='YOUR REDDDIT ID',
					 client_secret='YOUR REDDDIT ID',
					 user_agent='bot by /u/scarebaer')  	
	#create lists for relevant info, ids used for text for dupes
	post_titles = []
	post_urls = [] 
	post_ids = []
	print("Collecting new submissions from r/" + subreddit)
	for submission in r.subreddit(subreddit).new(limit=30):
		post_title = strip_title(submission.title, len(tag_string))
		post_url = submission.url
		post_id = submission.id
		
		post_titles.append(post_title)
		post_urls.append(post_url)
		post_ids.append(post_id)
		
		del post_title, post_url, post_id
	return post_titles, post_urls, post_ids

def tweeter(post_titles, post_urls, post_ids):	
	auth = tweepy.OAuthHandler(consumer_key, consumer_secret)
	auth.set_access_token(access_token, access_token_secret)
	api = tweepy.API(auth)
	index=0
	for post_title, post_url, post_id in zip(post_titles, post_urls, post_ids):
		found = duplicate_check(post_id)
		if found == 0:
			tweet_content = post_title + " " + shorten(post_url) + " " + tag_string
			print(tweet_content)
			try:
				api.update_status(tweet_content)
			except Exception as e:
				print("error triggered sending to twitter")
			add_id_to_file(post_id)
		else:
			print(post_id + " already found")
			index+=1 
			
def main():
	count = 0
	while count <= num_tweets_before_stopping:
		post_titles, post_urls, post_ids = create_tweet(subreddit)
		tweeter(post_titles, post_urls, post_ids)
		print("Waiting 15 minutes til next tweet: " + 'Timestamp: {:%Y-%m-%d %H:%M:%S}'.format(datetime.datetime.now()))
		time.sleep(tweet_delay*60)
		count+=1

if __name__ == '__main__':
	main()
