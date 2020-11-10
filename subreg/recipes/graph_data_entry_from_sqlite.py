from py2neo import Graph, Node, Relationship, NodeMatcher
import os
import sqlite3

uri = 'bolt://localhost:7687'
user = 'neo4j'
password = 'snacks'

dirname = os.path.dirname(__file__)
db_file = 'recipe.sqlite'

graph_db = Graph(uri, auth=(user, password))
matcher = NodeMatcher(graph_db)

conn = sqlite3.connect(os.path.join(dirname, db_file))
c = conn.cursor()
with conn:
	c.execute('SELECT * FROM "https://schema.org/Recipe"')
	rows = c.fetchall()
	for row in rows:
		tx = graph_db.begin()
		recipe = Node("Recipe", name=row[2], index=row[0])
		author = matcher.match("Author", name=row[1]).first()
		if author == None:
			author = Node("Author", name=row[1])
			tx.create(author)
		tx.create(recipe)
		relation = Relationship(recipe, "hasAuthor", author)
		tx.create(relation)
		tx.commit()
	print('added recipes and authors')

	c.execute('SELECT * FROM "https://schema.org/Ingredient"')
	rows = c.fetchall()
	for row in rows:
		tx = graph_db.begin()
		ingredient = Node("Ingredient", name=row[3], index=row[0])
		tx.create(ingredient)
		tx.commit()
	print('added ingredients')

	c.execute('SELECT * FROM "https://schema.org/Recipe/ingredient"')
	rows = c.fetchall()
	for index, row in enumerate(rows):
		tx = graph_db.begin()

		recipe = matcher.match("Recipe", index=row[1]).first()
		ingredient = matcher.match("Ingredient", index=row[2]).first()

		relation = Relationship(recipe, "hasIngredient", ingredient)
		tx.create(relation)
		tx.commit()