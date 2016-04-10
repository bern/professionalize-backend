from flask import Flask
from flask import request
from alchemyapi import AlchemyAPI
from nltk.corpus import wordnet
from itertools import chain
import os

app = Flask(__name__)
app.debug = True
alchemyapi = AlchemyAPI()

#greetings = Set(['hello', 'hey', 'hi', 'dear', 'yo', 'to whom it may concern', 'sup'])

@app.route("/profesh", methods=['POST', 'GET'])
def api_test():
    if request.method == 'POST':
        return handlePost(request)
    else:
		return "ERROR: Couldn't understand your request."

def handlePost(request):
	content = request.get_json(silent=True)
	print content
	if content.has_key('inputText'):
		input_text = content.get('inputText')
		alchemy_response = alchemyapi.keywords("text", input_text, {'sentiment': 1})
		keywords = alchemy_response.get('keywords')

		return transformKeywords(keywords)
	else:
		return "ERROR: Couldn't find a text key."

def transformKeywords(keywords):
	for keyword in keywords:
		print 'Here\'s a keyword: ' + keyword.get('text')
		str_to_build = str()
		str_to_build += ('text: '      + keyword.get('text').encode('utf-8') + "\n")
		str_to_build += ('relevance: ' + keyword.get('relevance') + "\n")
		str_to_build += ('sentiment: ' + keyword.get('sentiment').get('type') + "\n")
		if keyword['sentiment']['type'] == "negative":
			word = str(keyword['text'])
			synonyms = wordnet.synsets(word)
			syns = set(chain.from_iterable([word.lemma_names() for word in synonyms]))
			print syns

	return str_to_build

if __name__ == "__main__":
        app.run()
