# TMDB_CLI
 Command Line Interface for The Movie Database API written in Python 3.9. 

 # Configuration / API Authorisation
 Before using tmdb-cli run the following command with your API key from [The Movie Database](http://themoviedb.org). Ensure your use case does not violate their API terms of service.

	TMDB key "[your key]"

# usage

	usage: tmdb-cli.py [-h] [-j] [-k] [-m TMDB_ID | -tv TMDB_ID] [-id IMDB_ID]

	optional arguments:
	-h, --help            show this help message and exit
	-j, --json            return raw JSON output from the API
	-k, --key             add new API key for authorisation
	-m TMDB_ID, --movie TMDB_ID
							search for movie using themoviedb.org ID
	-tv TMDB_ID, --television TMDB_ID
							search for TV show using themoviedb.org ID
	-id IMDB_ID, --imdbid IMDB_ID
							converts IMDB ID to TMDB IDs