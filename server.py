from flask import Flask, request, jsonify
from alchemyapi import AlchemyAPI
from nltk.corpus import wordnet
from nltk import word_tokenize, pos_tag, sent_tokenize
from itertools import chain
import grammar_check
import random
import os
import re

app = Flask(__name__)
app.debug = True
alchemyapi = AlchemyAPI()
tool = grammar_check.LanguageTool('en-US')

@app.route("/profesh", methods=['POST', 'GET'])
def api_test():
    if request.method == 'POST':
        return handlePost(request)
    else:
		return 'ERROR: Couldn\'t understand your request.'

def handlePost(request):
	content = request.get_json(silent=True)
	print content
	if content.has_key('inputText'):
		# Do basic grammar correction.
		input_text = replaceContractions(content['inputText'])
		matches = tool.check(input_text)
		input_text = grammar_check.correct(input_text, matches)

		passive_sentences = classifySentences(input_text)

		alchemy_response = alchemyapi.keywords('text', input_text, {'sentiment': 1})
		keywords = alchemy_response['keywords']

		transformKeywords(keywords)
		return memeSwitch(input_text)
		# return jsonify(
		#	text=input_text,
		#	passive=passive_sentences
		# )
	else:
		return 'ERROR: Couldn\'t find a text key.'

def replaceContractions(input_text):
	output_text = input_text
	contraction_tuples = [
		('it will', 'it\'ll'),
		('cannot', 'can\'t'),
		('we are', 'we\'re'),
		('would not', 'wouldn\'t'),
		('could not', 'couldn\'t'),
		('should not', 'shouldn\'t'),
		('she will', 'she\'ll'),
		('he will', 'he\'ll'),
		('would have', 'would\'ve'),
		('should have', 'should\'ve'),
		('could have', 'could\'ve'),
		('you all', 'ya\'ll'),
		('I will', 'i\'ll'),
		('you will', 'you\'ll'),
		('you are', 'you\'re'),
		('is not', 'isn\'t'),
		('they are', 'they\'re'),
		('I am', 'i\'m'),
		('it is', 'it\'s'),
		('do not', 'don\'t'),
		('have not', 'haven\'t'),
		('will not', 'won\'t'),
		('how is', 'how\'s'),
		('are not', 'aren\'t'),
		('we will', 'we\'ll'),
		('I would', 'i\'d'),
		('he would', 'he\'d'),
		('she would', 'she\'d'),
		('they would', 'they\'d'),
		('had not', 'hadn\'t'),
	]
	# Lol actually edit this first
	for cont_tuple in contraction_tuples:
		output_text = re.sub(cont_tuple[1], cont_tuple[0], output_text)
		output_text = re.sub(
			cont_tuple[1][0:].capitalize() + cont_tuple[1][:0],
			cont_tuple[0][0:].capitalize() + cont_tuple[0][:0], output_text)
	return output_text

def classifySentences(input_text):
	sentences = sent_tokenize(input_text)
	return map(classifySentence, sentences)

def classifySentence(sentence):
	words = pos_tag(word_tokenize(sentence))
	print words
	for i in range(0, len(words) - 1):
		verb_correctly_follows = words[i + 1][1] in ['VBG', 'VBZ', 'VBD']
		if words[i][1] == 'VBN' and verb_correctly_follows:
			return sentence
		if verb_correctly_follows and words[i][1] == 'VBN':
			return sentence
	return ''

def transformKeywords(keywords):
	str_to_build = 'wow'
	for keyword in keywords:
		if keyword['sentiment']['type'] == 'negative':
			word = str(keyword['text'])
			synsets = wordnet.synsets(word)
			antonyms = []
			synonyms = []
			for syn in synsets:
				for l in syn.lemmas():
					synonyms.append(l.name())
					if l.antonyms():
						antonyms.append(l.antonyms()[0].name())

			print word + ': ' + str(antonyms)

	return str_to_build

def memeSwitch(input_text):
	sentences = sent_tokenize(input_text)
	return ' '.join(map(memeSentence, sentences))

def memeSentence(sentence):
	words = word_tokenize(sentence)
	memed = map(getLongestSynonym, words)
	memed_sent = (' '.join(memed[:len(memed) - 1]) + memed[len(memed) - 1])
	memed_sent = cleanupPunctuation(memed_sent).capitalize()
	return memed_sent

def getLongestSynonym(word):
	if len(word) <= 2:
		return word

	syns = wordnet.synsets(word)
 	synonyms = filter(
		filterPhrases,
		set(chain.from_iterable([word.lemma_names() for word in syns]))
	)

	if len(synonyms) is 0:
		return word
	else:
		return getRandomMax(synonyms)

def getRandomMax(synonyms):
	m = len(max(synonyms, key=len))
	index = random.choice([i for i, j in enumerate(synonyms) if len(j) == m or len(j) == (m - 1)])
	return synonyms[index]

def cleanupPunctuation(sentence):
	sentence = re.sub(' ,', ',', sentence)
	sentence = re.sub(' ;', ';', sentence)
	return sentence

def filterPhrases(synonym):
	return '_' not in synonym

if __name__ == '__main__':
	app.run()
