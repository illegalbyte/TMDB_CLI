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
from pprint import pprint

# TMDB IDs: [tv, movie] (for testing purposes)
TMDB_IDs = ['113036', '676691']
# IMDB IDs: [tv, movie] (for testing purposes)
IMDB_IDs = ['tt3230854', 'tt0109045']
# JSON of TMDB / JUSTWATCH COUNTRY CODES:  [REQ = f"https://api.themoviedb.org/3/watch/providers/regions?api_key={API_KEY}&language=en-US"]
COUNTRY_CODES = json.loads('''{"results":[{"iso_3166_1":"AR","english_name":"Argentina","native_name":"Argentina"},
							{"iso_3166_1":"AT","english_name":"Austria","native_name":"Austria"},
							{"iso_3166_1":"AU","english_name":"Australia","native_name":"Australia"},
							{"iso_3166_1":"BE","english_name":"Belgium","native_name":"Belgium"},
							{"iso_3166_1":"BG","english_name":"Bulgaria","native_name":"Bulgaria"},
							{"iso_3166_1":"BR","english_name":"Brazil","native_name":"Brazil"},
							{"iso_3166_1":"CA","english_name":"Canada","native_name":"Canada"},
							{"iso_3166_1":"CH","english_name":"Switzerland","native_name":"Switzerland"},
							{"iso_3166_1":"CZ","english_name":"Czech Republic","native_name":"Czech Republic"},
							{"iso_3166_1":"DE","english_name":"Germany","native_name":"Germany"},
							{"iso_3166_1":"DK","english_name":"Denmark","native_name":"Denmark"},
							{"iso_3166_1":"EE","english_name":"Estonia","native_name":"Estonia"},
							{"iso_3166_1":"ES","english_name":"Spain","native_name":"Spain"},
							{"iso_3166_1":"FI","english_name":"Finland","native_name":"Finland"},
							{"iso_3166_1":"FR","english_name":"France","native_name":"France"},
							{"iso_3166_1":"GB","english_name":"United Kingdom","native_name":"United Kingdom"},
							{"iso_3166_1":"HU","english_name":"Hungary","native_name":"Hungary"},
							{"iso_3166_1":"ID","english_name":"Indonesia","native_name":"Indonesia"},
							{"iso_3166_1":"IE","english_name":"Ireland","native_name":"Ireland"},
							{"iso_3166_1":"IN","english_name":"India","native_name":"India"},
							{"iso_3166_1":"IT","english_name":"Italy","native_name":"Italy"},
							{"iso_3166_1":"JP","english_name":"Japan","native_name":"Japan"},
							{"iso_3166_1":"KR","english_name":"South Korea","native_name":"South Korea"},
							{"iso_3166_1":"LT","english_name":"Lithuania","native_name":"Lithuania"},
							{"iso_3166_1":"MX","english_name":"Mexico","native_name":"Mexico"},
							{"iso_3166_1":"NL","english_name":"Netherlands","native_name":"Netherlands"},
							{"iso_3166_1":"NO","english_name":"Norway","native_name":"Norway"},
							{"iso_3166_1":"NZ","english_name":"New Zealand","native_name":"New Zealand"},
							{"iso_3166_1":"PH","english_name":"Philippines","native_name":"Philippines"},
							{"iso_3166_1":"PL","english_name":"Poland","native_name":"Poland"},
							{"iso_3166_1":"PT","english_name":"Portugal","native_name":"Portugal"},
							{"iso_3166_1":"RU","english_name":"Russia","native_name":"Russia"},
							{"iso_3166_1":"SE","english_name":"Sweden","native_name":"Sweden"},
							{"iso_3166_1":"TR","english_name":"Turkey","native_name":"Turkey"},
							{"iso_3166_1":"US","english_name":"United States of America","native_name":"United States"},
							{"iso_3166_1":"ZA","english_name":"South Africa","native_name":"South Africa"}]}''')

# CONSTANTS:
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
justwatchArgs = parser.add_argument_group()
parser.add_argument(
	"-j", "--json", help="return raw JSON output from the API", action="store_true")
parser.add_argument(
	"-k", "--key", help="authenticate with your API key", action="store_true")
exclusiveArgs.add_argument(
	"-m", "--movie", help="search for movie using themoviedb.org ID", type=str, metavar='<TMDB_ID>')
exclusiveArgs.add_argument(
    "-tv", "--television", help="search for TV show using themoviedb.org ID", type=str, metavar='<TMDB_ID>')
listInputArgs.add_argument(
	"-l", "--list", help="use a list of line separated ID values as input (pass -c for JSON syntax highlighting and formatted output)", action="store_true")
listInputArgs.add_argument(
	"-c", "--colour", help="Colourful JSON output (don't use if output is being sent to a file)", action="store_true")
parser.add_argument(
	"-imdb", "--imdbid", help="pass an IMDB ID instead of a themoviedb.org ID", action="store_true")
exclusiveArgs.add_argument(
	"-idconvert", "--imdbidconvert", help="returns a TMDB ID when passed an IMDB ID", type=str, metavar="<IMDB_ID>")
justwatchArgs.add_argument(
	"-mw", "--moviewatch", help="Find which streaming platforms a movie is available (specify country using -loc)", type=str, metavar="<TMDB_ID>")
justwatchArgs.add_argument(
    "-tvw", "--tvwatch", help="Find which streaming platforms a TV show is available (specify country using -loc)", type=str, metavar="<TMDB_ID>")
justwatchArgs.add_argument(
	"-loc", "--locale", help="Specify which country's streaming services you want to search (default: 'Australia')", metavar="<COUNTRY>")
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
			apiKeyInput = pyip.inputStr("Enter your API key from themoviedb.org:n", )
			if (requests.get(f'https://api.themoviedb.org/3/movie/{100}?api_key={apiKeyInput}&language=en-US').status_code == requests.codes.ok):
				print('Awesome, your key worked and has been saved. Run \'tmdb -h\' if you need help getting started.')
				break
		# Write the API key to 'init' file
		initFile = open('init.py', 'w')
		initFile.write(f"API_KEY='{apiKeyInput}'")
		initFile.close()

	# Get Movie Details
	def Movie(TMDB_ID: str, j=False) -> dict:
		url = f'https://api.themoviedb.org/3/movie/{TMDB_ID}?api_key={API_KEY}&language=en-US'
		response = requests.get(url)
		response.raise_for_status()
		# Return JSON if JSON parameter is passed
		if j == True:
			return response.text
		# Create Dictionary of Movie Data:
		movieDict = json.loads(response.text)
		# Genre Data:
		genresList = []
		for genre in movieDict["genres"]:
			genresList.append(genre["name"])
		# Title: 
		title = movieDict['title']
		# Ovierview / Description
		description = movieDict['overview']
		# Genres
		genres = ' | '.join(genresList[:])
		# Release Date
		release_date = movieDict['release_date']
		# Languages
		languages = [] 
		for language in movieDict['spoken_languages']:
			languages.append(language['english_name'])
		# Rating
		rating = movieDict['vote_average']
		# Trailer
		trailer = movieDict['video']
		# Runtime in minutes
		runtime = movieDict['runtime']
		returnDict = {'title':title, 'description': description, 'genres': genres,
						'release_date': release_date, 'languages': languages, 'rating': rating, 
						'trailer':trailer, 'runtime':runtime}
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
		# BUG: if there isn't an entry, it fails ungracefully
		title = tvDict['name']
		description = tvDict['overview']
		genres = ' | '.join(genresList[:])
		release_date = {tvDict['first_air_date']}
		languages = []
		for language in tvDict['spoken_languages']:
			languages.append(language['english_name'])
		rating = tvDict['vote_average']
		runtime = tvDict['episode_run_time']
		seasoncount = tvDict['number_of_seasons']
		returnDict = {'title': title, 'description': description, 'genres': genres,
                    'release_date': release_date, 'languages': languages, 'rating': rating,
                    'runtime': runtime, 'seasons': seasoncount}
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
	
	def justwatch(TMDB_ID: str, movie=False, tv=False, country='AU') -> dict:
		if movie == True:
			url = f'https://api.themoviedb.org/3/movie/{TMDB_ID}/watch/providers?api_key={API_KEY}'
			response = requests.get(url)
			response.raise_for_status()
			providers_dict = json.loads(response.text)
			pprint(providers_dict)
		elif tv == True:
			url = f'https://api.themoviedb.org/3/tv/{TMDB_ID}/watch/providers?api_key={API_KEY}'
			response = requests.get(url)
			response.raise_for_status()
			providers_dict = json.loads(response.text)
			pprint(providers_dict)



if __name__ == "__main__":

	# Initialise API KEY: run when 'key' is passed or there is no init file found
	if (args.key) or not Path.exists(Path('./init.py')):
		TMDB.InitialiseKey()
	else:
		from init import API_KEY

	# MOVIE OUTPUT [Args: -m / --movie]
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
			print(f"{GREEN}TITLE:{RS}{YELLOW} {movieDict['title']} {RS}	{movieDict['runtime']} mins")
			print(f"{GREEN}GENRES:{RS} {movieDict['genres']}")
			print(f"{GREEN}RATING:{RS} {movieDict['rating']}/10 		{GREEN}RELEASED:{RS} {movieDict['release_date']}")
			print(f"{GREEN}DESCRIPTION:{RS} {movieDict['description']}")
			print(f"{GREEN}Spoken Language(s):{RS} {' | '.join(movieDict['languages'])}")

			# appends link to trailer if available.
			if movieDict['trailer']: print(f'{GREEN}TRAILER:{RS} {movieDict["trailer"]}') 

	# TV OUTPUT [Args: -tv / --television]
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
		else:
			tvDict = TMDB.TV(args.television)
			print(f"{GREEN}TITLE: {RS}{YELLOW} {tvDict['title']} {RS}")
			print(f"{GREEN}GENRES: {RS} {tvDict['genres']}")
			print(f"{GREEN}EPISODE LENGTH: {RS} {tvDict['runtime']}mins	{GREEN}SEASONS: {RS} {tvDict['seasons']}")
			print(f"{GREEN}RATING: {RS} {tvDict['rating']}/10 		{GREEN}RELEASED: {RS} {str(tvDict['release_date'])[2:-2]}")
			print(f"{GREEN}DESCRIPTION:{RS} {tvDict['description']}")
			print(f"{GREEN}Spoken Language(s):{RS} {' | '.join(tvDict['languages'])}")

	# CONVERTS IMDB ID TO TMDB ID [-idconvert / --imdbidconvert]
	if args.imdbidconvert != None:
		print(TMDB.IMDB_CONVERTER(args.imdbidconvert))

	# GETS THE AVAILABLE STREAMING SERVICES FOR A SPECIFIED COUNTRY: 
	if args.tvwatch or args.moviewatch:
		TMDB.justwatch(args.moviewatch,movie=True)
