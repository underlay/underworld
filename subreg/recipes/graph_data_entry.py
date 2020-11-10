#scrape a bunch of recipes
import re
import json
import toml
from py2neo import Graph, Node, Relationship, NodeMatcher
import os
import requests

uri = 'bolt://localhost:7687'
user = 'neo4j'
password = 'snacks'

# incorporating different scraping modules
# change the import statement to change the scraper
# e.g. import scrapers.nyt as mod
# e.g. import scrapers.manual as mod
import scrapers.py_scraper as mod
import cleaning

with open("corpuses/meats.txt", "r") as am:
	global meats
	meats = am.readlines()
	meats = [i.replace("\n", "") for i in meats] 

def match_label(ingredient, title):
	matches = requests.get('http://www.ebi.ac.uk/ols/api/search?q=(%s)&ontology=foodon' % ingredient)
	resJSON = matches.json()
	if len(resJSON['response']['docs']) > 0:
		match = resJSON['response']['docs'][0]
		print(ingredient, 'matched with:', match['label'])
		return match
	else:
		return None

def insert_data(recipe):
	global meats
	recipe_id = 0
	#add recipe, author and source to the graph
	tx = graph_db.begin()
	recipeNode = matcher.match("http://schema.org/Recipe", wasDerivedFromURL=recipe.source).first()
	if recipeNode == None:
		recipeNode = Node("http://schema.org/Recipe", name=recipe.title, wasDerivedFromURL=recipe.source)
		print('source is', recipe.source)

	author = matcher.match("http://schema.org/Author", name=recipe.author).first()
	if author == None:
		author = Node("http://schema.org/Author", name=recipe.author)
		tx.create(author)

	rootURL = re.match(r'http?s:\/\/([a-z]+\.){1,}[a-z]+', recipe.source)[0]
	print(rootURL)

	source = matcher.match("http://schema.org/Webpage", url=rootURL).first()
	if source == None:
		source = Node("http://schema.org/Webpage", url=rootURL)
		tx.create(source)

	tx.create(recipeNode)
	auth_relation = Relationship(recipeNode, "hasAuthor", author)
	source_relation = Relationship(recipeNode, "hasSource", source)
	tx.create(auth_relation)
	tx.create(source_relation)
	tx.commit()


	for ingredient in recipe.ingredients:
		tx = graph_db.begin()
		ingredient = cleaning.clean_ingredient(ingredient)
		matched_ingredient = match_label(ingredient, recipe.title)

		if matched_ingredient:
			ingredient = matcher.match("http://schema.org/Ingredient", name=matched_ingredient["label"]).first()
			if ingredient == None:
				meat = False
				for word in meats:
					if word in matched_ingredient["label"].lower(): meat = True
				ingredient = Node("http://schema.org/Ingredient", name=matched_ingredient["label"], containsMeat=meat)
				tx.create(ingredient)
			relation = Relationship(recipeNode, "hasIngredient", ingredient)
			tx.create(relation)
		tx.commit()

	for cuisine in recipe.cuisines:
		tx = graph_db.begin()

		cuisineNode = matcher.match("http://schema.org/Cuisine", name=cuisine).first()
		if cuisineNode == None:
			cuisineNode = Node("http://schema.org/Cuisine", name=cuisine)
			tx.create(cuisineNode)
		relation = Relationship(recipeNode, "hasAssociatedCuisine", cuisineNode)
		tx.create(relation)
		tx.commit()

if __name__ == "__main__":


	graph_db = Graph(uri, auth=(user, password))
	graph_db.delete_all()
	matcher = NodeMatcher(graph_db)

	recipes = mod.scrape()

	for index, recipe in enumerate(recipes):
		print('recipe number', index)
		insert_data(recipe)

