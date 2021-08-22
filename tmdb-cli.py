#! python3

import sys
from pathlib import Path
import os
import json
import requests
import pyinputplus as pyip

CWD = Path('./')

if len(sys.argv) > 1:
	if sys.argv[1] == 'init':
		# While there's no valid API ask for a valid API:
		while True: 
			apiKeyInput = pyip.inputStr("Enter your API key from themoviedb.org:\n", )
			initFile = open('init', 'w')
			initFile.write(f"API_KEY='{apiKeyInput}'")


class API:
	def __init__(self) -> None:
		self.API_KEY = API_KEY
