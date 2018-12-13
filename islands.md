# Schema translations

_I'm going to use the words "schema" and "ontology" interchangeably and there's nothing you can do to stop me._

There's lots of structured data out in the wild, but it's only structured internally, relative to itself. For example, IMDB will let you download [CSVs of its archives](https://datasets.imdbws.com/), but they're in IMDB's own schema, with made-up IMDB names for all the columns. If you're consuming their data, you still need to read their [interface docs](https://www.imdb.com/interfaces/) and transform the data into an externally compatible format. Their data is only usable _intentionally_.

What we'd really love is for data to also be usable _incidentally_ - reachable, retrievable, and interpretable from outside worlds without any human in the loop. One way to achieve this is through standardization (getting IMDB to switch all their property names to fully-qualified URIs in some standardized movie-ish ontology), but a far more practical & scalable strategy is through self-description. To do this we need to formalize the _schema_ of a dataset as an object itself.

[RDFS](https://en.wikipedia.org/wiki/RDF_Schema) and [OWL](https://en.wikipedia.org/wiki/Web_Ontology_Language) implement one facet of this structured schema dream. They're both meta-ontologies that define vocabularies for structuring other schemas with types like `Class` and `Property`, and relations like subclass, domain, and range, so that given a schema and a record from a dataset, a computer could infer the record's shape and properties based of its type. [JSON Schema](https://json-schema.org/) fills the same role in a parallel, less-RDF-y world.

This is necessary, but only half of the puzzle: having assembled schemas into a   structured tangles of class hierarchies and type constraints, **we also need ways to relate different schemas to each other**. OWL hints at this with relations like `equivalentProperty` and `sameAs`, but stops there, which is unfortunate as true equality is so rarely found in the wild. One might have `firstName` and `lastName`, another might just have `name`. IMDB has a column for `isAdult` with the range `{0, 1}`, but schema.org has a property `isFamilyFriendly` with the range `{true, false}`.

This sort of light transformation consumes a lot of developer time nowadays (insert Googler joke about living only to transform protobufs) and it's a shame that we have to reimplement it so redundantly, let alone implement it at all. Couldn't there be a better world where data naturally attaches itself to some self-aware, self-transforming connected component? An archipelago of island ontologies traversable by property translations? OWL gave us intra-schema structure, now where's our inter-schema orientation?

This is the other half of the puzzle: self-describing transformations. We're after some static expression (one that could fit in e.g. some JSON value) that describes the mapping of `0 -> true` and `1 -> false` for the translation from `imdb:isAdult` to `schema:isFamilyFriendly` (and vice versa). And while we're at it, let's imagine chaining them together too: we don't need quadratic bridges between every pair of islands, we just need good route planning.

(Wait why? What do we get out of this again?)

IMDB is probably not going to switch their data format into some standard ontology like schema.org. They don't see any need to, and even if they did, there are countless domains for which there just aren't any standards at all. The advantages of building systems that parse these hypothetical "linked schemas" as first-class objects are that 1) we avoid fighting an uphill coordination battle between everyone talking about the same things and 2) that _anyone could write the schema object_. IMDB doesn't even need to know about it, just like Javascript libraries don't need to know about TypeScript for someone to write a good @types package for them. We can start keeping indices of linked API schemas! You could imagine querying the index for data without ever noticing which source (much less which format) your data came from! You might just be looking for the `schema:isFamilyFriendly` property of a movie that satisfies `{"name": "Vertigo"}`, without caring that IMDB called them `isAdult` and `primaryTitle` respectively, or even that the data was from IMDB (although your results will hopefully be accompanied by some rich provenance graph that references both IMDB and the schema translations involved).

If dragging computation into this scares you, it probably should (it certainly scares me). It's not immediately clear that there's actually a need for anything Turing-complete. Maybe a configuration language or something circuit-y could express enough real-world transformations to make data generally usable. 

There's mild prior art from the XML-verse in [XSLT](https://en.wikipedia.org/wiki/XSLT), a Turing-complete "language for transforming XML documents into other XML documents" while itself expressed in... XML! An analogous language for transforming JSON values that either fits well into a string or other JSON values would unlock all the slick inductive translations we were giddy about a minute ago.

(Why not JavaScript?)

Even if we sacrifice ourselves to Turing-completeness, it'd be really really really nice to have a restricted langauge that literally only transforms JSON values. It'd inevitably be more concise. It wouldn't be a gaping security liability. It'd have less surface area. Passing JavaScript code around as string is a nightmare waiting to happen.

Viable Options
1. JavaScript
2. [jq](https://github.com/stedolan/jq)
3. [jmespath](http://jmespath.org/)
4. some binary-packed base64-encoded WASM thing
5. some other thing
