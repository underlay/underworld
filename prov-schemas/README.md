## provenance schema examples

Example schemas are organised into 'collection templates', here in labelled folders. These examples explore 2 possible collection templates for a recipe-scraping scenario.

Each collection is composed of a set of named graphs, which form the basis for assertions. The data-schema `data.toml` describes the how the contents of each graph is structured; the meta-schema `meta.toml` describes the structure of the provenance metadata associated with each graph.

### collection `individual_recipes/`

This scenario is a collection template where each named graph represents a single recipe. In this instance, the meta-schema captures information about the author and source of the recipe, while the data-schema captures details such as name and ingredients.

### collection `same_recipe/`

This scenario is for named graphs consisting of multiple versions of the same recipe (a recipe with the same name, by different authors, rather than three revisions of a recipe by one author): here, 3 different versions of _Okonomiyaki_. In this instance, the meta-schema describes *how* each of these graphs was generated, while the source and authorship information is stored in the data-schema.

### merging collections

Taking the `individual_recipes/` and `same_recipe/` templates as an example, how would the provevance file change if each of the `same_recipe/` graphs were separated into individual recipes?

Ordinarily, this transformation would be lossy, as the `individual_recipes` schema does not include a field for `source` and `author`. However, during the merge, the provenance structure of the graphs extracted from `same_recipes` is expanded, adding this information into the meta-schema.

If we relax the 'same-recipe' rule to allow recipes to be grouped by theme, merging `individual_recipes/` into `same_recipes` could produce a second named graph, where the individual recipes are grouped by their existing relationship.

If, instead the 'same-recipe' rule is enforced on merging the two collections (e.g. if the schema required each recipe to have the same name), merging `individual_recipes/` into `same_recipes` would produce a new named graph for each separate recipe in the collection (into which other recipes with the same name could be incorporated later).

Visually, this would look like:

![merging two schemas](./merging.png)
