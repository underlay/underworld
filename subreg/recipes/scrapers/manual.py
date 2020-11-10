from bs4 import BeautifulSoup
from scrapers.recipe import Recipe
import requests
import re
from recipe_scrapers import scrape_me


with open("sources/borschts.txt", "r") as pr:
	global urls
	urls = pr.readlines()
	urls = [i.replace("\n", "") for i in urls] 

def scrape():
	global urls
	recipes = []

	for url in urls:
		recipe_id = 0
		page = requests.get(url)

		soup = BeautifulSoup(page.content, 'html.parser')

		title = soup.find('h1', {'class': re.compile(r'name|title|heading(?!.*(site|website))')})

		# look for a div where the classname contains ingredients and get the list from there
		ingredient_container = soup.find('div', {'class': re.compile(r'(?<!direction.)ingredient(?!.*(direction|instruction|steps))')})
		ingredients = ingredient_container.find_all('li')

		for index, ingredient in enumerate(ingredients):
			ingredient_name = ingredient.find('span', {'class': re.compile(r'name|Name|ingredient(?!.*(unit|amount))')})
			if ingredient_name:
				ingredient = ingredient_name
			ingredient = ingredient.text.strip()
			ingredients[index] = re.sub(r'\s+', ' ', ingredient)

		#look for a div where the classname contains ingredients and get the list from there
		direction_container = soup.find('div', {'class': re.compile(r'(?<!ingredient.)direction|instruction|steps(?!.*(ingredient|description))')})
		directions = direction_container.find_all('li')

		for direction in directions:
			direction = direction.text.strip()
			direction = re.sub(r'\s+', ' ', direction)


		if title:
			print('RECIPE:', title.text.strip())
			title = title.text.strip()
		else:
			title = None

		recipe = Recipe(title, ingredients, directions, url)
		recipes.append(recipe)
		print('this recipe has', len(ingredients), 'ingredients, and', len(directions), 'steps')

	return recipes