import re
import nltk
from nltk import word_tokenize, pos_tag
nltk.download('averaged_perceptron_tagger')
nltk.download('tagsets')
import spacy
nlp = spacy.load("en_core_web_sm")

with open("corpuses/amounts.txt", "r") as am:
	global amounts
	amounts = am.readlines()
	amounts = [i.replace("\n", "") for i in amounts] 

with open("corpuses/processes.txt", "r") as pr:
	global processes
	processes = pr.readlines()
	processes = [i.replace("\n", "") for i in processes] 


def clean_ingredient(ingredient):
	global amounts, processes
	print('cleaning', ingredient)

	ingredient = ingredient.lower()

	#array of words to remove
	remove = amounts + processes

	#get rid of digits and punctuation
	ingredient = re.sub(r'[^a-zA-Z\s]', '', ingredient)

	for word in remove:
		ingredient = re.sub(rf"(\s|^){word}(\s|$)", '', ingredient)

	frag = nlp(ingredient)
	[token.text for token in frag]

	ing = ''
	for token in frag:
		if token.tag_ in ['NNP', 'NNS', 'NN', 'JJ']:
			ing = ing + token.text + ' '

	print('cleaned', ing)
	return ing