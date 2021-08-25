# TMDB_CLI
 Command Line Interface for [The Movie Database API](https://developers.themoviedb.org/3/) written using Python 3.9.6. 

# Configuration / API Authorisation
 Before using tmdb-cli run the following command with your API key from [The Movie Database](http://themoviedb.org). Ensure your use case does not violate their API terms of service.

	TMDB --key

# usage

	usage: tmdb-cli.py [-h] [-j] [-k] [-m TMDB_ID] [-tv TMDB_ID] [-imdb] [-idconvert IMDB_ID]

	optional arguments:
	-h, --help            show this help message and exit
	-j, --json            return raw JSON output from the API
	-k, --key             add new API key for authorisation
	-m TMDB_ID, --movie TMDB_ID
							search for movie using themoviedb.org ID
	-tv TMDB_ID, --television TMDB_ID
							search for TV show using themoviedb.org ID
	-imdb, --imdbid       pass an IMDB ID instead of a themoviedb.org ID
	-idconvert IMDB_ID, --imdbidconvert IMDB_ID
							returns a TMDB ID when passed an IMDB ID


# Use Cases: 

## Convert IMDB IDs to TMDB IDs

Useful for migrating away from webscraping IMDB pages towards the robust [TMDB API](https://developers.themoviedb.org/3/). 

**CLI INPUT:**
	
	python3 tmdb-cli.py -idconvert tt6856396

**OUTPUT:**

	676691


## Retrieve JSON data about movies and TV shows easily!

Save all the movie data your heart desires, just pass the ``-j`` flag!

**CLI INPUT:** 
	
	python3 tmdb-cli.py -j -imdb -m tt6856396
	
**OUTPUT:**
	
	{"adult":false,"backdrop_path":"/kSu2HaqBJSaIN6sUd0RciwNzTSe.jpg","belongs_to_collection":null,"budget":0,"genres":[{"id":18,"name":"Drama"}],"homepage":"http://norrismovingpictures.com/thecrossroadsofhunterwilde/","id":676691,"imdb_id":"tt6856396","original_language":"en","original_title":"The Crossroads of Hunter Wilde","overview":"Hunter Wilde is the leader of a group of Christian survivalists who are trying to live as normal as possible two years after an EMP attack and knocking all the power down. In a world of chaos living day to day has become more treacherous. But that is nothing compared to when the gates of hell are opened up and demons are commissioned to seek and destroy the remaining believers on earth. Their targets are set on Hunter. If they can break him the whole town of Crossroads will follow.","popularity":59.015,"poster_path":"/ykwUc1b7bkKcpxT7MTxrv5s4JOv.jpg","production_companies":[{"id":129665,"logo_path":null,"name":"Norris Moving Pictures","origin_country":""}],"production_countries":[{"iso_3166_1":"US","name":"United States of America"}],"release_date":"2019-09-30","revenue":0,"runtime":87,"spoken_languages":[{"english_name":"Portuguese","iso_639_1":"pt","name":"Português"},{"english_name":"English","iso_639_1":"en","name":"English"}],"status":"Released","tagline":"A battle as old as time itself... Being fought at the end of days","title":"The Crossroads of Hunter Wilde","video":false,"vote_average":8.0,"vote_count":8}