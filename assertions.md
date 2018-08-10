# Assertions

Assertions in the Underlay are [JSON-LD documents](https://json-ld.org/spec/latest/json-ld/) that conform to a couple of Underlay-specific idioms. This document assumes a light familiarity with JSON-LD - skimming the [Basic Concepts](https://json-ld.org/spec/latest/json-ld/#basic-concepts) section of the spec should be enough context.

*Here is one sample assertion, for use as the simplest of templates*
```json
[
	{
		"@context": { "@vocab": "http://schema.org/" },
		"@id": "_:lebron",
		"@type": "Person",
		"name": "LeBron James",
		"birthDate": "1984-12-30"
	},
	{
		"@context": {
			"prov": "http://www.w3.org/ns/prov#",
			"schema": "http://schema.org/"
		},
		"@type": "prov:Entity",
		"prov:value": { "@id": "_:lebron" },
		"prov:wasAttributedTo": {
			"@type": ["prov:Organization", "schema:Organization"],
			"prov:atLocation": "http://www.espn.com/nba/player/_/id/1966/lebron-james",
			"schema:name": "ESPN",
			"schema:url": "http://www.espn.com/"
		}
	}
]
```


## JSON-LD format

JSON-LD documents encode graphs in one of three root forms:
1) An object as a top-level graph node, such as `{"@context": {...}, "name": "John Doe", ...}`
2) An array of top-level graphs, such as `[{"name": "John Doe", ...}, {"@context": {...}, "@graph": [...]}]`
3) An object `{"@context": {...}, "@graph": [...]}`, with no properties other than `@context` and `@graph`, where `@graph` is an array of graphs as in 2) but that all inherit the shared top-level `@context`

To simplify top-level parsing, we restrict assertions to be only the second format: an array of graphs, each of which may be of either the first or third format (but no nested arrays). This is necessary for including provenance, as described in the [provenance section](#prov-provenance).

## IPLD Links

[IPLD](https://github.com/ipld/ipld) is a data model for the decentralized web that promotes the use of "IPLD Links" that encode a self-describing hash of a piece of content as its unique, resolvable identifier. These self-describing hashes are [CIDs](https://github.com/ipld/cid) and are typically serialized as base58-encoded strings. 

An "IPLD Link" is a JSON object of the form `{"/": <base58-encoded-CID>}`, and links following this form can be traversed automatically in Unix-style paths by any IPLD resolver. This means that given an object `{"foo": 42}` with CID `<cid1>`, an object `{"bar": {"baz": {"/": <cid1>}}}` with CID `<cid2>`, the IPLD path `<cid1>/bar/baz/foo` would automatically resolve all the way to `42`. IPLD Links are great for hiding complexity that can be reached if necessary but doesn't need to be copied around all the time. If some giant object has an unwieldy amount of data, we can pass around these lightweight IPLD paths as pointers to its parts instead, confident that we could use IPLD to retrieve the real data at any time.

The JSON-LD spec requires applications to ignore foreign (unresolved non-IRI) properties in objects, which means that we can't just include a literal IPLD link object as a property's value. Instead, the JSON-LD spec promotes the use of [Index Maps](https://json-ld.org/spec/latest/json-ld/#index-maps) to encode foreign keys, which transform our IPLD Links into the form `{"@index": "/", "@value": <cid>}`. This is admittedly more clunky, but has huge advantages in not breaking compliance in existing JSON-LD processor implementations.

A pattern we're encouraging in Underlay assertions is substituting IPLD links instead of content "wherever appropriate". We expect some assertions to be enormous, and some provenance graphs to be duplicated. **We allow any part of an assertion to be replaced with an IPLD link, and encourage users to split up their assertions in whatever way makes the most sense for them.**

For example, we might want to link to every top-level graph element so that the resultant assertion is constant-size, lightweight, and more easily shareable.
```javascript
const content = {
	"@context": { "@vocab": "http://schema.org/" },
	name: "Joel Gustafson",
	email: "joelg@mit.edu",
	...
}
const cid = await ipfs.dag.put(content, {"format": "dag-cbor", hashAlg: "sha2-256"})
const dataLink = cid.toBaseEncodedString() // zBwWX9ecx5F4X54WAjmFL...
const provenance = {
	"@context": { "@vocab": "http://www.w3.org/ns/prov#" },
	"@type": "Entity",
	"value": {"@index": "/", "@value": dataLink},
	...
}
const cid2 = await ipfs.dag.put(provenance, {"format": "dag-cbor", hashAlg: "sha2-256"})
const provLink = cid2.toBaseEncodedString()
const assertion = [
	{"@index": "/", "@value": dataLink},
	{"@index": "/", "@value": provLink}
]
```

## PROV Provenance

The [PROV Ontology](https://www.w3.org/TR/2013/REC-prov-o-20130430/) is an ontology for recording provenance developed by the W3C Provenance Working Group. We're adopting PROV for assertions in the Underlay.

We also use JSON-LD to encode provenance, following the [PROV-DM](https://www.w3.org/TR/2013/REC-prov-dm-20130430/) namespace `http://www.w3.org/ns/prov#`. JSON-LD is not an officially specified serialization (the Provenance Working Group only describes an XML schema) but application of the namespace in JSON-LD is straightforward and often more intuitive than XML.

Recall from the [JSON-LD format paragraph](#json-ld-format) that every assertion is a top-level array of graphs. **In an assertion, each consecutive graph describes the provenance of its predecessor**. This means that the "content" of an assertion - any object-level facts about the world - must be contained in the first element of the array (either a case-1 node or a case-3 context+graph-array object). Then the second element is a PROV graph describing the provenance of the first. If this PROV graph has significant provenance itself (as in the case of PROV graphs generated by software agents that we wish to note), this provenance will be described in the third element, and so on.

Furthermore, **each PROV graph should at least contain one [Entity](https://www.w3.org/TR/2013/REC-prov-o-20130430/#Entity) node that links to the referent graph with the [value](https://www.w3.org/TR/2013/REC-prov-o-20130430/#value) property, either by `@id` or by IPLD Link.** This makes the link between the provenance and the object explicit; the layered consecutive-reference scheme is only a temporary idiom for easier parsing.

This means that knowledge without any provenance will still be wrapped in a single-element array, and that the vast majority of assertions will only have two elements in the top-level array. We'll likely relax this restriction in the longer term future (and just require every provenance graph to link to the referent `prov:Entity` with an IPLD Link under `prov:value`), but following this pattern will make parsing easier in the immediate future.

Assertions with layered provenance might look like this:
```javascript
const facts = { ...facts_about_the_world }
const cid = ipfs.dag.put(facts, {"format": "dag-cbor", hashAlg: "sha2-256"})
const link = cid.toBaseEncodedString()
const assertion = [
	{ "@index": "/", "@value": link },
	{
		"@context": { "@vocab": "http://www.w3.org/ns/prov#" },
		"@id": "_:provenance",
		"@type": "Entity",
		value: { "@index": "/", "@value": link },
		...provenance_of_those_facts
	},
	{
		"@context": { "@vocab": "http://www.w3.org/ns/prov#" },
		"@type": "Entity",
		value: { "@id": "_:provenance" },
		...provenance_of_provenance
	}
]
```

## Blank node IDs

We're discouraging the use of *significant* `@id`s in JSON-LD documents. Your `@id`s can still be IRIs so long as they're also duplicated in a named property (e.g. https://schema.org/identifier or ideally something more descriptive).

In general, treat `@id` *only as a way to link nodes together*, not as a property to store values in.

## Optional top-level signatures

We expect that most assertions will be uselessly untrustworthy without publicly verifiable signatures of their publishers (as distinct from their *source* - many Underlay nodes may publish an equivalent assertion citing the same sources). Accordingly, we anticipate to use the JSON-LD signatures specified in the [Security Vocabulary](https://web-payments.org/vocabs/security) drafted by the W3C Web Payments Community Group. These signatures are optional, but if you want to include one you should follow either `GraphSignature` or `LinkedDataSignature` for the best chances of staying future-compatible.

# FAQ

<dl>
	<dt>
		How big should be assertions be? 
		Should I put a big dataset into one assertion or make a separate assertion for every record?
	</dt>
	<dd>
		An assertion should be the most granular piece of data that you have specific provenance for. 
		If you have separate source for each record, they should each be assertions. 
		If you have a single source for the whole dataset, just cram it into one. 
		The IPLD link pattern lets us efficiently have arbitrarily large assertions, so in the whole-dataset case it'd be wise to split each record at the IPLD level and have the top-level, signed assertion just be an array of IPLD links.
	</dd>
	<dt>
		What's up with the whole layered provenance thing?
	</dt>
	<dd>
		<p>
			Assertions have to mean <em>something</em> - by signing and publishing one, there must be something that you are, in fact, asserting. But it's rarely object-level, world-relating knowledge, unless you're a primary source. You probably heard it from someone else, and even if you trust them, you should include that layer in your assertion. The layers exist so that assertion publishers can keep adding them until they reach a layer that they feel comfortable signing themselves - one that they are the primary source for.
		</p>
		<p>
			So I may not know what the population of Narnia is, and I may not even know that Dr. Suess claimed it was 122. But there is some articulable fact for which I <em>am</em> a primary source: that in the copy of Wired magazine dated 2012-12-12, an article credited to Dr. Suess listed Naria's population as 122. Each of these degrees of separation would be a separate graph involving (in order) Narnia, Dr. Suess, Wired, and (eventually and ultimately) <em>me</em>, the asserter. And when I've built a tower that reaches myself as a primary source, I sign and publish the whole stack. <strong>The signature of the assertion grounds the tower of provenance.</strong>
		</p>
	</dd>
</dl>
