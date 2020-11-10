#scrape a bunch of recipes
import re
import json
import toml
import sqlite3
import os
import requests

# incorporating different scraping modules
# change the import statement to change the scraper
# e.g. import scrapers.nyt as mod
# e.g. import scrapers.manual as mod
import scrapers.nyt as mod
import cleaning

dirname = os.path.dirname(__file__)
db_file = 'recipe.sqlite'

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
	recipe_id = 0
	#add recipe info to db
	try:
		conn = sqlite3.connect(os.path.join(dirname, db_file))
		c = conn.cursor()
		with conn:
			c.execute("INSERT INTO 'https://schema.org/Recipe' ('https://schema.org/Recipe/name', 'https://schema.org/Recipe/author', 'https://schema.org/Recipe/source') VALUES (?, ?, ?)", (recipe.title, recipe.author, recipe.source))
			recipe_id = c.lastrowid
	except sqlite3.Error as e:
		print(e)


	for ingredient in recipe.ingredients:
		ingredient = cleaning.clean_ingredient(ingredient)
		matched_ingredient = match_label(ingredient, recipe.title)

		if matched_ingredient:
			try:
				conn = sqlite3.connect(os.path.join(dirname, db_file))
				c = conn.cursor()
				description = None
				row_id = 0

				if 'description' in matched_ingredient:
					description = matched_ingredient['description'][0]

				with conn:
					##insert the ingredients
					row = c.execute('''
						SELECT * FROM "https://schema.org/Ingredient"
						WHERE "https://schema.org/Ingredient/name" = ?''', (matched_ingredient['label'],))
					row = row.fetchone()

					if row is None:
						c.execute('''
							INSERT INTO "https://schema.org/Ingredient" ("https://schema.org/Ingredient/description", "https://schema.org/Ingredient/id", "https://schema.org/Ingredient/name") 
							VALUES (?,?,?)''', (description , matched_ingredient['iri'] , matched_ingredient['label'] ))
						row_id = c.lastrowid
						conn.commit()
					else:
						row_id = row[0]

					##now, add to the ingredient list
					c.execute('''
						INSERT INTO "https://schema.org/Recipe/Ingredient" ("http://underlay.org/ns/source", "http://underlay.org/ns/target") 
						VALUES (?,?)''', (recipe_id, row_id))

			except sqlite3.Error as e:
				print('sqlite', e)
			finally:
				if conn:
					conn.close()

if __name__ == "__main__":

	#init db w foreign key constraints
	try:
		conn = sqlite3.connect(os.path.join(dirname, db_file))
		c = conn.cursor()
		with conn:
			c.execute('''CREATE TABLE IF NOT EXISTS "https://schema.org/Recipe" ( id INTEGER PRIMARY KEY, "https://schema.org/Recipe/author" text not null, "https://schema.org/Recipe/name" text not null, "https://schema.org/Recipe/source" text not null )''')
			c.execute('''CREATE TABLE IF NOT EXISTS "https://schema.org/Ingredient" ( id INTEGER PRIMARY KEY, "https://schema.org/Ingredient/description" text, "https://schema.org/Ingredient/id" text not null, "https://schema.org/Ingredient/name" text not null )''')
			c.execute('''CREATE TABLE IF NOT EXISTS "https://schema.org/Recipe/Ingredient" ( id INTEGER PRIMARY KEY, "http://underlay.org/ns/source" integer not null references "https://schema.org/Recipe", "http://underlay.org/ns/target" integer not null references "https://schema.org/Ingredient" )''')
			c.execute("PRAGMA foreign_keys = ON;")
	except sqlite3.Error as e:
		print(e)

	recipes = mod.scrape()

	#each recipe gets directions and ingredients
	# recipes = ws.scrape()

	for index, recipe in enumerate(recipes):
		print('recipe number', index)
		insert_data(recipe)

