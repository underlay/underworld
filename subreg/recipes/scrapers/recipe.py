class Recipe:
	def __init__(self, title, ingredients, directions, source="https://example.com", author="", cuisines=[]):
		self.title = title
		self.ingredients = ingredients
		self.directions = directions
		self.source = source
		self.author = author
		self.cuisines = cuisines