import nltk
from pyhugeconnector.pyhugeconnector import thesaurus_entry
from flask import Flask
from flask import request
from alchemyapi import AlchemyAPI
app = Flask(__name__)
alchemyapi = AlchemyAPI()

#greetings = Set(['hello', 'hey', 'hi', 'dear', 'yo', 'to whom it may concern', 'sup'])

@app.route("/profesh", methods=['POST', 'GET'])
def api_test():
	if request.method == 'GET':
		return "Hit with a GET"
	if request.method == 'POST':
		content = request.get_json(silent=True)
		if content.has_key('analysisText'):
			analysisText = content.get('analysisText')
			str = "Received the following text: \n"+analysisText+"\n"
			
			response = alchemyapi.keywords("text", analysisText, {'sentiment': 1})
			
			for keyword in response['keywords']:
				str += ('text: ' + keyword['text'].encode('utf-8') + "\n")
        			str += ('relevance: ' + keyword['relevance'] + "\n")
        			str += ('sentiment: ' + keyword['sentiment']['type'] + "\n")
				if keyword['sentiment']['type'] == "negative":
					word = keyword['text']+""
					word = "beep"
					te = ['a'] #thesaurus_entry(word, 'API_KEY', 'n', 0, 'syn')
					if len(te) > 0:
						str += "Maybe "+te[0]+"?\n"
				#str += "\nAnalyzed sentiment is "+response["docSentiment"]["type"]
			return str
		else:
			return "ERROR: Couldn't find a text key."
	else:
		return "ERROR: Couldn't understand your request."

if __name__ == "__main__":
	app.run()
