# TMDB_CLI
 Command Line Interface for The Movie Database API written in Python 3.9. 

 # Authorisation
 Before using tmdb-cli run the following command with your API key from (The Movie Database)[http://themoviedb.org]. Ensure your use case does not violate their API terms of service.

	TMDB init "[your key]"

# Flags

	-j					Get raw JSON, rather than the default readable output.
	-m [TMDB_ID] 		Access the movie API.
	-tv [TMDB_ID]		Access the TV shows API.
	-IMDB				Converts an IMDB ID to a TMDB ID.