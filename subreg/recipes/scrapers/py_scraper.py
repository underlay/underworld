from recipe_scrapers import scrape_me
from scrapers.recipe import Recipe


with open("sources/borschts.txt", "r") as pr:
	global urls
	urls = pr.readlines()
	urls = [i.replace("\n", "") for i in urls] 

def scrape():
	global urls
	recipes = []
	for url in urls:
		# Q: What if the recipe site I want to extract information from is not listed below?
		# A: You can give it a try with the wild_mode option! If there is Schema/Recipe available it will work just fine.
		try:
			scraper = scrape_me(url, wild_mode=True)
			if scraper:
				recipe = Recipe(scraper.title(), scraper.ingredients(), scraper.instructions(), url, scraper.author())
				recipes.append(recipe)
		except:
			print('no recipe schema for ', url)

	return recipes
