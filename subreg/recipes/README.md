## Food Schema Composer

This script takes the output of a recipe scraper, composes it into a schema using the [FoodON food ontology](https://github.com/FoodOntology/foodon) and inserts it into a sqlite database that satisfies the schema specified in [references/](https://github.com/FoodOntology/foodon). This can then be serialised into assertions using the [io-sqlite](https://github.com/underlay/io-sqlite) module. 

So long as the recipe scraper module is structured correctly (see instructions below), this script will run with any arbitrary scraper.

### Installation

This script needs Python 3.6+ to run. To install requirements and run script, do:

```
$ pip3 install requirements.txt
$ python3 data_entry.py
```

(or `pip` and `python` respectively if python3 is your default installation)

### Structure

* `data_entry.py` -- takes in an array of Recipe objects and outputs, matches ingredients to FoodON equivalents (this could be improved) and generates a database called `recipe.sqlite`
* `references/` -- holds the reference schema, which was used to generate the database template
* `scrapers/` -- holds the scraping modules and the template class for Recipes (`recipe.py`)

Existing scraping modules:

* `scrapers/py_scraper.py` -- uses the python module [recipe-scrapers](https://github.com/hhursev/recipe-scrapers), which can scrape a range of different recipe sites. A quick test on a random range of urls from smaller sites had about 50% success, much higher for larger sites (+ 100% success for each on their list). 
* `scrapers/manual.py` -- was the first attempt at a scraper using beautiful soup and regular expressions. Not very effective, but could be improved and might be able to get some sites where py_scraper doesn't work
* `scrapers/nyt.py` -- gets recipes from the scraped nyt archive -- you need a .zip of this from me for this to work, unzip in top level directory

To use a different scraper module, change line 13 of the file `data_entry.py` (by default it's set to `py_scraper`, which right now is set up to scrape okonomiyaki recipes):

```
import scrapers.{module-you-want} as mod
```

### Adding a scraper module

If you'd like to add a new scraping module, it can do whatever you like, so long as it exports a function called `scrape()` that `return`s an array of `Recipe` objects. (for reference `py_scraper.py` is probably the simplest version of this).

Modules need to have the following as an import statement:

```
from scrapers.recipe import Recipe
```

and need to create an array of recipe objects, where `title, ingredients, directions, url, author` are values that were scraped from the recipe. Note that url and author may be left blank

```
recipe = Recipe(title, ingredients, directions, url, author)
recipes.append(recipe)
```
and, finally, those objects should be returned from `scrape()`, where they will be used as the input to the data entry script

```
return recipes
```