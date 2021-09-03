#! python3

from pathlib import Path
import json
import requests
import pyinputplus as pyip
from colorama import Fore, Style
import argparse
import os
import time
from pygments import highlight
from pygments.formatters.terminal256 import Terminal256Formatter
from pygments.lexers.web import JsonLexer
from pygments.styles import get_style_by_name

# TMDB IDs: [tv, movie] (for testing purposes)
TMDB_IDs = ['113036', '676691']
# IMDB IDs: [tv, movie] (for testing purposes)
IMDB_IDs = ['tt3230854', 'tt0109045']

# CONSTANTS:
CWD = Path('./')
REQUEST_RATE_LIMIT_SECONDS = 1

# COLOR SHORTCUTS FOR TERM OUTPUT STYLING EG f"{GREEN} THIS IS GREEN {RS} THIS IS NOT GREEN"
RS = Style.RESET_ALL
RED = Fore.RED
YELLOW = Fore.YELLOW
BLUE = Fore.BLUE
GREEN = Fore.GREEN

# For taking filepaths as input and validating them
def dir_path(string):
	if os.path.isfile(string):
		return string
	else:
		raise NotADirectoryError(string)


# for printing readable JSON (coloured)
def prettyJson(json_string):
	json_string = json.loads(json_string)
	formatted_json = json.dumps(json_string, indent=4)
	if args.colour:
		colorful_json = highlight(formatted_json, JsonLexer(), Terminal256Formatter(style=get_style_by_name('monokai')))
		return colorful_json
	else:
		return str(formatted_json)


# Take the user arguments and flags
parser = argparse.ArgumentParser()
exclusiveArgs = parser.add_mutually_exclusive_group() # makes sure users don't pass -tv and -m for example
listInputArgs = parser.add_argument_group()
parser.add_argument(
	"-j", "--json", help="return raw JSON output from the API", action="store_true")
parser.add_argument(
	"-k", "--key", help="authenticate with your API key", action="store_true")
exclusiveArgs.add_argument(
	"-m", "--movie", help="search for movie using themoviedb.org ID", type=str, metavar='TMDB_ID')
exclusiveArgs.add_argument(
    "-tv", "--television", help="search for TV show using themoviedb.org ID", type=str, metavar='TMDB_ID')
listInputArgs.add_argument(
	"-l", "--list", help="use a list of line separated ID values as input (pass -c for JSON syntax highlighting and formatted output)", action="store_true")
listInputArgs.add_argument(
	"-c", "--colour", help="Colourful JSON output (don't use if output is being sent to a file)", action="store_true")
parser.add_argument(
	"-imdb", "--imdbid", help="pass an IMDB ID instead of a themoviedb.org ID", action="store_true")
exclusiveArgs.add_argument(
	"-idconvert", "--imdbidconvert", help="returns a TMDB ID when passed an IMDB ID", type=str, metavar="IMDB_ID")
args = parser.parse_args()


# Reads each line of file and returns a list
def read_file_lines(filePath):
	# Make sure the file exists
	dir_path(filePath)
	
	# Open the file and return each line in a list
	with open(filePath, 'r') as file:
		lines = file.readlines()
	return lines


# TMDB class containing API interactions
class TMDB:


	# Ask for API KEY
	def InitialiseKey():
		while True:
			apiKeyInput = pyip.inputStr("Enter your API key from themoviedb.org:\n", )
			if (requests.get(f'https://api.themoviedb.org/3/movie/{100}?api_key={apiKeyInput}&language=en-US').status_code == requests.codes.ok):
				print('Awesome, your key worked and has been saved. Run \'tmdb -h\' if you need help getting started.')
				break
		# Write the API key to 'init' file
		initFile = open('init.py', 'w')
		initFile.write(f"API_KEY='{apiKeyInput}'")
		initFile.close()

	# Get Movie Details, TODO: allow multiple arguments and return all output.
	def Movie(TMDB_ID: str, j=False) -> dict:
		url = f'https://api.themoviedb.org/3/movie/{TMDB_ID}?api_key={API_KEY}&language=en-US'
		response = requests.get(url)
		response.raise_for_status()
		# Return JSON if JSON parameter is passed
		if j == True:
			return response.text
		# Create Dictionary of Movie Data:
		movieDict = json.loads(response.text)
		# 	Genre Data:
		genresList = []
		for genre in movieDict["genres"]:
			genresList.append(genre["name"])
		# 	Title: 
		title = movieDict['title']
		# 	Ovierview / Description
		description = movieDict['overview']
		# Genres
		genres = ' | '.join(genresList[:])
		# 	Release Date
		release_date = movieDict['release_date']
		# 	Languages # TODO: fix languages to accept more than one input
		languages = movieDict['spoken_languages'][0]['english_name']
		# 	rating
		rating = movieDict['vote_average']
		# 	Trailer
		trailer = movieDict['video']
		# 	Runtime in minutes
		runtime = movieDict['runtime']
		returnDict = {  'title': title, 'description': description, 'genres': genres,
						'release_date': release_date, 'languages': languages, 'rating': rating, 
						'trailer': trailer, 'runtime': runtime
						}
		return returnDict

	# Returns a python dict of TV details, TODO: allow multiple arguments and return all output.
	def TV(TMDB_ID: str, j=False) -> dict:
		url = f'https://api.themoviedb.org/3/tv/{TMDB_ID}?api_key={API_KEY}&language=en-US'
		response = requests.get(url)
		response.raise_for_status()
		# Return JSON if JSON parameter is passed
		if j == True:
			return response.text
		# Create Dictionary of TV Data:
		tvDict = json.loads(response.text)
		# 	Genre Data:
		genresList = []
		for genre in tvDict["genres"]:
			genresList.append(genre["name"])
		# TODO: add all languages rather than the primary spoken
		# BUG: if there isn't an entry, it fails ungracefully
		title = tvDict['name']
		description = tvDict['overview']
		genres = ' | '.join(genresList[:])
		release_date = {tvDict['first_air_date']}
		languages = tvDict['spoken_languages'][0]['english_name']
		rating = tvDict['vote_average']
		runtime = tvDict['episode_run_time']
		seasoncount = tvDict['number_of_seasons']
		returnDict = {'title': title, 'description': description, 'genres': genres,
                    'release_date': release_date, 'languages': languages, 'rating': rating,
                    'runtime': runtime, 'seasons': seasoncount
                }
		return returnDict

	# Converts an IMDB ID to a TMDB ID, TODO: automatically convert IMDB IDs to TMDB
	def IMDB_CONVERTER(IMDB_ID) -> str:
		url = f'https://api.themoviedb.org/3/find/{IMDB_ID}?api_key={API_KEY}&language=en-US&external_source=imdb_id'
		response = requests.get(url)
		response.raise_for_status()
		findResponseDictionary = json.loads(response.text)
		if findResponseDictionary['movie_results'] != []:
			return findResponseDictionary['movie_results'][0]["id"]
		elif findResponseDictionary['tv_results'] != []:
			return findResponseDictionary['tv_results'][0]["id"]
	
	# TODO: Add search for movies / TV shows in an interactive menu using pyinputplus menus
	# TODO: Add justwatch providers search: https://developers.themoviedb.org/3/watch-providers/get-available-regions
		# localised to region 
			# eg translate country name to country code 
	# TODO: Add determine type (Movie or Tv show) function


if __name__ == "__main__":

	# Initialise API KEY:
	#		 run when 'key' is passed or there is no init file found
	if (args.key) or not Path.exists(Path('./init.py')):
		TMDB.InitialiseKey()
	else:
		from init import API_KEY

	# MOVIE OUTPUT [-m / --movie]
	if args.movie != None:
		if args.imdbid:
			args.movie = TMDB.IMDB_CONVERTER(args.movie)
		if args.list:
			id_list = read_file_lines(args.movie)
			for id in id_list:
				print(prettyJson(TMDB.movie(id, j=True)))
				time.sleep(REQUEST_RATE_LIMIT_SECONDS)
		if args.json:
			print(prettyJson(TMDB.Movie(args.movie, j=True)))
		else:
			# convert IMDB ID to TMDB ID if IMDB ID is given
			movieDict = TMDB.Movie(args.movie)
			print(f"{GREEN}TITLE:{RS}{YELLOW} {movieDict['title']} {RS}	{movieDict['runtime']}mins")
			print(f"{GREEN}GENRES:{RS} {movieDict['genres']}")
			print(f"{GREEN}RATING:{RS} {movieDict['rating']}/10 		{GREEN}RELEASED:{RS} {movieDict['release_date']}")
			print(f"{GREEN}DESCRIPTION:{RS} {movieDict['description']}")
			# appends link to trailer if available.
			if movieDict['trailer']: print(f'{GREEN}TRAILER:{RS} {movieDict["trailer"]}') 

	# TV OUTPUT [-tv / --television]
	if args.television != None:
		if args.imdbid:
			args.television = TMDB.IMDB_CONVERTER(args.television)
		
		if args.list:
			# reads each line of file and stores it in id_list
			id_list = read_file_lines(args.television)
			# for each line return the pretty json version of the file
			for id in id_list:
				print(prettyJson(TMDB.TV(id, j=True)))
				time.sleep(REQUEST_RATE_LIMIT_SECONDS)
		if args.json and not args.list:
			print(prettyJson(TMDB.TV(args.television, j=True)))
		elif args.list == None:
			tvDict = TMDB.TV(args.television)
			print(f"{GREEN}TITLE: {RS}{YELLOW} {tvDict['title']} {RS}")
			print(f"{GREEN}GENRES: {RS} {tvDict['genres']}")
			print(f"{GREEN}EPISODE LENGTH: {RS} {tvDict['runtime']}mins	{GREEN}SEASONS: {RS} {tvDict['seasons']}")
			print(f"{GREEN}RATING: {RS} {tvDict['rating']}/10 		{GREEN}RELEASED: {RS} {str(tvDict['release_date'])[2:-2]}")
			print(f"{GREEN}DESCRIPTION:{RS} {tvDict['description']}")

	# CONVERTS IMDB ID TO TMDB ID [-idconvert / --imdbidconvert]
	if args.imdbidconvert != None:
		print(TMDB.IMDB_CONVERTER(args.imdbidconvert))