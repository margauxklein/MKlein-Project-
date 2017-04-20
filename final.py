import unittest
import itertools
import collections
import tweepy
import requests
import twitter_info # same deal as always...
import json
import sqlite3
import re

##### TWEEPY SETUP CODE:
# Authentication information should be in a twitter_info file...
consumer_key = twitter_info.consumer_key
consumer_secret = twitter_info.consumer_secret
access_token = twitter_info.access_token
access_token_secret = twitter_info.access_token_secret
auth = tweepy.OAuthHandler(consumer_key, consumer_secret)
auth.set_access_token(access_token, access_token_secret)

# Set up library to grab stuff from twitter with your authentication, and return it in a JSON format 
api = tweepy.API(auth, parser=tweepy.parsers.JSONParser())

##### END TWEEPY SETUP CODE

#Set up caching pattern, save data into cache file called SI206_project_final.json
CACHE_FNAME = "SI206_project_final.json"
# Put the rest of your caching setup here:
try:
	cache_file = open(CACHE_FNAME,'r')
	cache_contents = cache_file.read()
	cache_file.close()
	CACHE_DICTION = json.loads(cache_contents)
except:
	#if CACHE_DICTION IS EMPTY..
	CACHE_DICTION = {}

#write a function to get and cache twitter data, accepts a phrase as input
#Pick at least 3 movie search terms, put those strings into a list
#Movie_search_terms is a list of three movie names, + to represent where spaces would otherwise be in URL
movie_search_terms = ["The+Hunger+Games", "Mean+Girls", "Beauty+and+the+Beast"]
#Write and cache data from the OMDB API with a movie title search as input to the function:
def get_omdb_data(movie_title_search):
	base_url = "http://www.omdbapi.com/?"
	#if the movie title is in the cache file, will retrieve info from cache diction:
	if movie_title_search in CACHE_DICTION:
		info = CACHE_DICTION[movie_title_search]
	else:
	#if the movie title is not in the cache file, make a request to the API:
		info = requests.get(base_url + "t=" + movie_title_search).json()
		cache_file = open(CACHE_FNAME, 'w')
		cache_file.write(json.dumps(CACHE_DICTION))
		cache_file.close()
	return info
#Define a class movie
class Movie():
	#Write code to set up the initializing function of the Movie class, which accepts a dictionary that represents a movie (OMDB_dict). This class should have at least 3 instance variables
	def __init__(self, OMDB_dict):
		self.ID = OMDB_dict['imdbID']
		self.title = OMDB_dict['Title']
		self.director = OMDB_dict['Director']
		self.rating = OMDB_dict['imdbRating']
		self.actors = OMDB_dict['Actors'].split(',')
		self.languages = OMDB_dict['Language'].split(',')
		self.country = OMDB_dict['Country'].split(',')
		self.awards = OMDB_dict['Awards']
	#Write a method to return a string of the title and director of the movie in a formatted way
	def __str__(self):
		x = "Movie title: {} is directed by {}".format(self.title + self.director)

	#create a function that will search for the director name in the cache_diction. if it exists, retrieve that data. if the director's name is not in cache diction, make a request to the API
	def get_Tweets_user(self):
		unique_identifier = "twitter_{}".format(self.director) # seestring formatting chapter
		# see if that director name is in the cache diction!
		if unique_identifier in CACHE_DICTION: # if it is...
			public_tweets = CACHE_DICTION[unique_identifier] # grab the data from the cache!
		else:
			public_tweets = api.search(self.director) # get it from the internet
			# but also, save in the dictionary to cache it!
			CACHE_DICTION[unique_identifier] = public_tweets # add it to the dictionary -- new key-val pair
			# and then write the whole cache dictionary, now with new info added, to the file, so it'll be there even after your program closes!
			cache_file = open(CACHE_FNAME,'w') # open the cache file for writing
			cache_file.write(json.dumps(CACHE_DICTION)) # make the whole dictionary holding data and unique identifiers into a json-formatted string, and write that wholllle string to a file so you'll have it next time!
			cache_file.close()
		return public_tweets

#Create a class to handle the Twitter data:
class Tweet():
	#initializing function will accept Tweet_dict as input 
	def __init__(self, Tweet_dict):
		self.tweetText = Tweet_dict['text']
		self.tweetID = Tweet_dict['id_str']
		self.user = Tweet_dict['user']['id_str']
		self.num_favs = Tweet_dict['favorite_count']
		self.num_retweets = Tweet_dict['retweet_count']
	#use your function to access data about a Twitter user to get information about each of the Users in the "neighborhood", as it's called in social network studies -- every user who posted any of the tweets you retrieved and every user who is mentioned in them.
	def save_user_data(self):
		
		unique_identifier = "twitter_user{}".format(self.user) # seestring formatting chapter
		# see if that director name is in the cache diction!
		if unique_identifier in CACHE_DICTION: # if it is...
			user = CACHE_DICTION[unique_identifier] # grab the data from the cache!
		else:
			user = api.get_user(self.user) # get it from the internet
			# but also, save in the dictionary to cache it!
			CACHE_DICTION[unique_identifier] = user# add it to the dictionary -- new key-val pair
			# and then write the whole cache dictionary, now with new info added, to the file, so it'll be there even after your program closes!
			cache_file = open(CACHE_FNAME,'w') # open the cache file for writing
			cache_file.write(json.dumps(CACHE_DICTION)) # make the whole dictionary holding data and unique identifiers into a json-formatted string, and write that wholllle string to a file so you'll have it next time!
			cache_file.close()

		self.screen_name = user['screen_name']
		self.favorites = user['favourites_count']
		self.followers = user['followers_count']
		self.tweets = user['statuses_count']
		self.following = user['friends_count']
		self.location = user['location']

#Create a list of instances of the Movie class called list_of_movies
list_of_movies = []
#iterate through each movie in the list "movie_search_terms". for every movie in that list, call the get_omdb_data function on it
for x in movie_search_terms:
	movie_search = get_omdb_data(x)
	y = Movie(movie_search)
	list_of_movies.append(y)
	#print(y.get_Tweets_user()["statuses"][0])
tweet_list = []
for x in list_of_movies:
	for y in (x.get_Tweets_user()['statuses']):
		tweet_list.append(Tweet(y))
	x.list_of_tweets = tweet_list
	tweet_list = []
for x in list_of_movies:
	print(x.list_of_tweets)
	for y in x.list_of_tweets:
		y.save_user_data()
		print(y.screen_name)
#NEED INFORMATION ON USERS' NEIGHBORHOODS



## Task 2 - Creating database and loading data into database

# You will be creating a database file: finalproject.db
# Note that running the tests will actually create this file for you, but will not do anything else to it like create any tables; you should still start it in exactly the same way as if the tests did not do that! 
# The database file should have  3 tables, and each should have the following columns... 


conn = sqlite3.connect('finalproject.db')
cur = conn.cursor()

#Load data into your database
#Create a Tweets Table with tweet_id as primary key, and user_id, time_posted, tweet_text and retweets as other columns in this table:

cur.execute('DROP TABLE IF EXISTS Tweets')
table_spec = 'CREATE TABLE IF NOT EXISTS '
table_spec += 'Tweets(tweet_id TEXT PRIMARY KEY, '
table_spec += 'user_id TEXT, tweet_text TEXT, movie TEXT, retweets INTEGER, favorites INTEGER)'
cur.execute(table_spec)

#NEED INSERT STATEMENT ABOVE TO INSERT DATA INTO RESPECTIVE COLUMNS!!! 

#Create a Users Table (For Twitter Users), user_id as primary key, screen_name, num_favs and description as other columns of the table:
cur.execute('DROP TABLE IF EXISTS Users')
table_spec = 'CREATE TABLE IF NOT EXISTS '
table_spec += 'Users(user_id TEXT PRIMARY KEY, '
table_spec += 'screen_name TEXT, num_favs INTEGER, location TEXT)'
#NEED INSERT STATEMENT ABOVE TO INSERT DATA INTO RESPECTIVE COLUMNS!
cur.execute(table_spec)


#Create a Movies Table, movie_id as the primary key, movie_title, directors, IMDB_rating, run_time, num_languages, and first_actor as other columns of this table
cur.execute('DROP TABLE IF EXISTS Movies')
table_spec = 'CREATE TABLE IF NOT EXISTS '
table_spec += 'Movies(movie_id TEXT PRIMARY KEY,'
table_spec += 'movie_title TEXT, directors TEXT, IMDB_rating TEXT, country TEXT, num_languages INTEGER, first_actor TEXT)'
cur.execute(table_spec)

for each_movie in list_of_movies:
	movie_id = each_movie.ID
	movie_title = each_movie.title
	directors = each_movie.director
	IMDB_rating = each_movie.rating
	country = each_movie.country[0]
	num_languages = len(each_movie.languages)
	first_actor = each_movie.actors[0]
	statement = 'INSERT OR IGNORE INTO Movies Values (?, ?, ?, ?, ?, ?, ?)'
	cur.execute(statement, (movie_id, movie_title, directors, IMDB_rating, country, num_languages, first_actor))
	conn.commit()

	for each_tweet in each_movie.list_of_tweets:
		tweet_id = each_tweet.tweetID
		user_id = each_tweet.user
		tweet_text = each_tweet.tweetText
		movie = each_movie.ID
		retweets = each_tweet.num_retweets
		favorites = each_tweet.num_favs
		statement2 = 'INSERT OR IGNORE INTO Tweets Values (?, ?, ?, ?, ?, ?)'
		cur.execute(statement2, (tweet_id, user_id, tweet_text, movie, retweets, favorites))
		conn.commit()

		screen_name = each_tweet.screen_name
		num_favs = each_tweet.favorites
		location = each_tweet.location
		statement3 = 'INSERT OR IGNORE INTO Users Values (?, ?, ?, ?)'
		cur.execute(statement3, (user_id, screen_name, num_favs, location))
		conn.commit()


#Process the data and create an output file!
#Make queries to the database to grab intersections of data, and then use at least four of the processing mechanisms in the project requirements to find out something interesting or cool or weird about it. 
#MUST HAVE AT LEAST 3 QUERIES, resulting in information that would have been more difficult to combine without use of the database, and use the results of the queries to process your data
# Make a query to select all of the records in the Users database. Save the list of tuples in a variable called users_info.
query  = "SELECT * FROM Users"
users_info = cur.execute(query).fetchall()

# Make a query to select all of the tweets (full rows of tweet information) that have been retweeted more than 25 times. Save the result (a list of tuples, or an empty list) in a variable called more_than_25_rts.
query = "SELECT * FROM Tweets WHERE retweets > 25"
more_than_25_rts = cur.execute(query).fetchall()

# # Make a query to select all the descriptions (descriptions only) of the users who have favorited more than 25 tweets. Access all those strings, and save them in a variable called descriptions_fav_users, which should ultimately be a list of strings.
query = "SELECT location FROM Users WHERE num_favs > 0"
descriptions_fav_users = cur.execute(query).fetchall()
descriptions_fav_users = [tup[0] for tup in descriptions_fav_users]

# # USE AN INNER JOIN QUERY HERE:
# Make a query using an INNER JOIN to get a list of tuples with 2 elements in each tuple: the user screenname and the text of the tweet -- for each tweet that has been retweeted more than 50 times. Save the resulting list of tuples in a variable called joined_result.
query = 'SELECT screen_name, location FROM Users INNER JOIN Tweets ON Tweets.retweets WHERE retweets> 100'
joined_result = cur.execute(query).fetchall()

# #You must process the data you gather and store and extract from the database in at least four
query = "SELECT tweet_text from Tweets"
tweets = cur.execute(query).fetchall()
count_a = 0
unique_words = set()
for x in tweets:
	if 'a' in x[0]:
		count_a += 1
	match = re.findall(r'(\S+)', x[0])
	if match:
		for each in match:
			unique_words.add(each)

# ## Manipulating data with comprehensions & libraries

with open('project_output.txt', 'w') as outfile:
	output = """
		my output{}
"""
	for movie in cur.execute("SELECT movie_title, movie_id from Movies").fetchall():
		output += "unique_words in {}\n".format(movie[0])
		unique_words = set()
		for tweet in cur.execute("SELECT tweet_text from Tweets WHERE Tweets.movie = ?", (movie[1],)).fetchall():
			tweet_text = tweet[0]
			match = re.findall(r'(\S+)', tweet_text)
			if match:
				for each in match:
					unique_words.add(each)
		for word in unique_words:
			output += word + "\n"	



	
	outfile.write(output)




# # Write code to create a dictionary whose keys are Twitter screen names and whose associated values are lists of tweet texts that that user posted. You may need to make additional queries to your database! To do this, you can use, and must use at least one of: the DefaultDict container in the collections library, a dictionary comprehension, list comprehension(s). Y
# # You should save the final dictionary in a variable called twitter_info_diction.
# query = "SELECT description from USERS"
# description_text = cur.execute(query).fetchall()
# description_text2= []
# description_text2 = [y for x in description_text for y in x]
# twitter_info_diction = {}
# for x in screen_names:
# 	twitter_info_diction[x] = description_text2


# Write data to a text file - a summary stats page
#Create classes of test cases:
class CachingTests(unittest.TestCase):
	def test_cache_diction(self):
		self.assertEqual(type(CACHE_DICTION),type({}),"Testing whether you have a CACHE_DICTION dictionary")
	# def test_cache_file(self):
	# 	f = open("SI206_project_final.json","r")
	# 	s = f.read()
	# 	f.close()
	# 	self.assertEqual(type(s),type({}),"Doesn't look like you have a cache file with the right name / with content in it")	
# class TestCases(unittest.TestCase):
# 	#Create a test to ensure that list_of_tweets is a list
# 	def test_list_of_tweets(self):
# 		self.assertEqual(type(list_of_tweets), type([]))
# 	#Create a test to make sure that list_of_movies is a list
# 	def test_list_of_movies(self):
# 		self.assertEqual(type(test_list_of_movies), type([]))
# 	#create a test to make sure that the type of OMDB_dict is a dictionary
# 	def test_type_OMDB_dict(self):
# 		self.assertEqual(type(OMDB_dict), type({}))
class TestDatabases(unittest.TestCase):
	def testTweetclass(self):
		x = Tweet()
		self.assertEqual(type(x.tweetText), type("hi"))
	def testTweetclass2(self):
		a = Tweet()
		self.assertEqual(type(a.num_favs), type(1))
	def test_users_table(self):
		conn = sqlite3.connect('finalproject.db')
		cur = conn.cursor()
		cur.execute('SELECT * FROM Users');
		result = cur.fetchall()
		self.assertTrue(len(result)>=2,"Testing that there are at least 2 distinct users in the Users table")
		conn.close()
	def test_tweets_2(self):
		conn = sqlite3.connect('finalproject.db')
		cur = conn.cursor()
		cur.execute('SELECT * FROM Tweets');
		result = cur.fetchall()
		self.assertTrue(len(result[1])==6,"Testing that there are 6 columns in the Tweets table")
	def test_users(self):
		conn = sqlite3.connect('finalproject.db')
		cur = conn.cursor()
		cur.execute('SELECT * FROM Users');
		result = cur.fetchall()
		self.assertTrue(len(result[1])==4,"Testing that there are 4 columns in the Users table")
	def test_movies(self):
		conn = sqlite3.connect('finalproject.db')
		cur = conn.cursor()
		cur.execute('SELECT * FROM Movies');
		result = cur.fetchall()
		self.assertTrue(len(result[1])==7,"Testing that there are 7 columns in the Movies table")	
if __name__ == "__main__":
	unittest.main(verbosity=2)

#README DOC
#Finish output file using two more queries 
#Finish test cases ( 2 for each method ) and make sure all pass
