# Messages

An _Underlay message_ is an RDF dataset containing a signature, provenance, and zero or more named graphs called _assertions_.

- [Assertions](#assertions)
- [Provenance](#provenance)
- [Signatures](#signatures)
- [Examples](#examples)

A familiarity with [RDF](https://www.w3.org/TR/rdf11-primer/) and [JSON-LD](https://w3c.github.io/json-ld-syntax/) is assumed. Prefixes used here include:

```
rdf:  http://www.w3.org/1999/02/22-rdf-syntax-ns#
xsd:  http://www.w3.org/2001/XMLSchema#
sec:  https://w3id.org/security#
prov: http://www.w3.org/ns/prov#
```

## Assertions

Assertions are named graphs, and they must have blank graph names. The assertion graphs are the "payload" of a message that carry the object-level data the author intends to publish. As a result, the data in the assertions of a message is often expected to validate some schema associated with the domain or application that it came from.

Although named graphs appear to partition data between them, they're only used as a means of labelling subsets of data. Schema validation and other data operations are not done over individual named graphs, but over the union of all assertions (excluding the default graph of the dataset).

### Messages vs assertions

A single message should carry a _coherent unit of data_, such as a row in a database or a snapshot of state. Not all domains have clear divisions; applications are encouraged to use messages in whatever way feels most appropriate.

_Assertions label components of data according to their provenance._ They group the parts of the data that came from the same source, are attributed to the same entity, etc. In general, schemas and provenance do not always align, and so named graphs are used as an extra degree of freedom to capture the difference.

## Provenance

> Provenance is information about entities, activities, and people involved in producing a piece of data or thing, which can be used to form assessments about its quality, reliability or trustworthiness. - _[PROV-Overview](https://www.w3.org/TR/prov-overview/)_

The default graph of messages describes the provenance of the assertions using the [PROV-O Ontology](https://www.w3.org/TR/prov-o/), using each named graph's blank graph label to refer to each assertion. This promotes an interpretation of RDF dataset semantics where the graph name denotes the named graph, as described [here](https://www.w3.org/TR/rdf11-datasets/#the-graph-name-denotes-the-named-graph-or-the-graph) and as popularized by JSON-LD's representation of named graphs.

Every assertion must be the subject of at least one triple in the default graph whose predicate is one of `prov:wasDerivedFrom`, `prov:wasAttributedTo`, or `prov:wasGeneratedBy` (or a well-known subclass). Note that the range of these predicates are PROV Entities, so the objects of these "provenance entry point" triples cannot be RDF literals.

There is no upper limit to the contents of the default graph - it may describe the PROV Entities associated with an assertion using other ontologies as well - as long as it is in the service of describing the assertions, and not carrying asserted data itself.

Messages split data into assertions by their known provenance. An assertion should be a chunk of data whose provenance is described atomically, even if it means splitting up parts of a data structure between named graphs (querying, validation in ShEx, and other operations are all done over a merged graph). Depending on the granularity of the known provenance, there might be only one assertion, or there may be a separate assertion for each asserted triple.

Most messages have just one assertion.

### URIs for past assertions

The default graph of a message may also describe additional provenance of assertions in previous messages, or relate a new assertion to a past one. This is done with content-addressed URIs for datasets with the `ul:` URI scheme.

To get a dataset's canonical URI:

- Canonicalize the dataset using the [URDNA2015](https://json-ld.github.io/normalization/spec/) normalization algorithm
- Generate the base58btc CIDv1 of the canonicalized dataset as a raw IPLD block

```
% cat data.jsonld
{
	"@context": {
		"@vocab": "http://schema.org/",
		"prov": "http://www.w3.org/ns/prov#",
	},
	"prov:wasAttributedTo": { "name": "The Small Town Gazette" },
	"@graph": {
		"name": "Jane Doe",
		"jobTitle": "Professor",
		"knows": {
			"name": "John Doe",
			"jobTitle": "Firefighter"
		}
	}
}
% cat data.jsonld | jsonld normalize | ipfs add -Q --raw-leaves
zb2rhh7cNfeh64YM2CBcrt17H6fwku6DS6mpR9bZDUtPEZxzb
% ipfs cat zb2rhh7cNfeh64YM2CBcrt17H6fwku6DS6mpR9bZDUtPEZxzb
_:c14n0 <http://schema.org/jobTitle> "Professor" _:c14n3 .
_:c14n0 <http://schema.org/knows> _:c14n1 _:c14n3 .
_:c14n0 <http://schema.org/name> "Jane Doe" _:c14n3 .
_:c14n1 <http://schema.org/jobTitle> "Firefighter" _:c14n3 .
_:c14n1 <http://schema.org/name> "John Doe" _:c14n3 .
_:c14n2 <http://schema.org/name> "The Small Town Gazette" .
_:c14n3 <http://www.w3.org/ns/prov#wasAttributedTo> _:c14n2 .
```

The canonical URI for the dataset is `ul:zb2rhmHEgvSe6KUuZGnTzgdcswJ6YWnY1RDtJMeGsACquojrx`, and its single assertion has the canonical URI `ul:zb2rhmHEgvSe6KUuZGnTzgdcswJ6YWnY1RDtJMeGsACquojrx#_:c14n3`. More details and motivation for content-addressed URIs are described [here](https://kfg.mit.edu/pub/ic0grz58/).

If we wanted to refer to this assertion in a future message, we would use this URI as if it were a local blank graph name:

```json
{
	"@context": {
		"@vocab": "http://schema.org/",
		"prov": "http://www.w3.org/ns/prov#"
	},
	"prov:wasRevisionOf": {
		"@id": "ul:zb2rhmHEgvSe6KUuZGnTzgdcswJ6YWnY1RDtJMeGsACquojrx#_:c14n3"
	},
	"@graph": {
		"name": "Jane Doe",
		"jobTitle": "Professor",
		"knows": {
			"name": "John Doe",
			"jobTitle": "Lumberjack"
		}
	}
}
```

This forms the basic mechanism for retraction and revision.

## Signatures

The signature is the last part of a message to be assembled, and should be the first part of a message to be parsed.

Messages use the [`LinkedDataSignature2016`](https://web-payments.org/vocabs/security#LinkedDataSignature2015) signature for signing RDF datasets, which represents signatures as part of the dataset itself - that is, the signature is represented directly as RDF in the default graph, and only signs the "rest" of the dataset.

To sign a message, the unsigned dataset is first canonicalized using the [URDNA2015](https://json-ld.github.io/normalization/spec/) algorithm. Then the canonicalized string is signed with the [rsa-sha256 algorithm](http://www.w3.org/2000/09/xmldsig#rsa-sha256), using the key associated with a user's IPFS node, or a user's account with a registry, or similar.

The signature is encoded as base64 text in an `xsd:string` RDF literal, and added to the default graph as the object of a triple with predicate `sec:signatureValue` and a new blank node subject (called `_:sig` here).

The blank signature node is also the subject of three additional triples added to the default graph:

- `_:sig rdf:type sec:LinkedDataSignature2016`
- `_:sig dcterms:created <created>`, where `<created>` is an `xsd:dateTime` marking when the signature was generated
- `_:sig dcterms:creator <creator>`, where `<creator>` is a URI that can be dereferenced to retrieve the associated public key - For IPFS keys, use `dweb:/ipns/Qm...`, where `Qm...` is a base58 PeerId - Registries that control user's keys will have to implement their own standards around this

Despite the awkwardness of splicing signatures into the default graph, parsing and validating them is deterministic so long as the signature node label is unique, and no other set of four triples in the default graph match the same pattern.

### Identities vs keys

In general, tying user identity to individual keys is bad cryptographic practice. There is a new [Linked Data Signatures](https://w3c-dvcg.github.io/ld-signatures) spec under active development by the W3C Digital Verification Community Group that approaches signing with this in mind, with the goal of supporting "N entities with M keys" per user. `LinkedDataSignature2016` is a much simpler scheme that is adopted here for temporary use while these specs and tools stabilize.

## Examples

It's important to use the PROV vocabulary consistently, since it will be used to reason across domains.

The domain of `prov:wasAttributedTo` is `prov:Entity`, which means the object should usually be a blank node qualified with additional properties. Occasionally the object may be a content-addressed reference to a previous entity, and only on rarely should it be an external non-Underlay URI.

For example:

```json
{
	"@context": { ... },
	"prov:wasAttributedTo": "The New York Times",
	"@graph": { ... }
}
```

is **invalid**, since "The New York Times" is an RDF literal string, which cannot be a PROV Entity. The correct way to express "simple string" provenance like this would be to simply sketch out whatever properties of the entity are known, however sparse:

```json
{
	"@context": {
		"@vocab": "http://schema.org/",
		...
	},
	"prov:wasAttributedTo": {
		"name": "The New York Times"
	},
	"@graph": { ... }
}
```

---

The following is **not** recommended:

```json
{
	"@context": { ... },
	"prov:wasAttributedTo": { "@id": "https://nytimes.com" },
	"@graph": { ... }
}
```

This is because there's little-to-no agreement on how or whether to use HTTP URLs as RDF URIs, and it often leads to more harm than good. Do they refer to the webpage? The website as a whole? The entity behind the website? `http` or `https`? Trailing slash?? Fragments??? _The RDF data model successfully describes the world to an extent proportional to the consensus achieved by its users on the referents of its identifiers_, and carelessly guessing at URIs for entities dilutes the effective utility of everyone's data.

Instead, unless an explicit URI is publicly and visibly associated with an entity _with the express purpose of usage within RDF_, users should fall back to using blank nodes. No such explicit linked data URI is published by the New York Times, so a better provenance representation would be:

```json
{
	"@context": {
		"@vocab": "http://schem.org/",
		...
	},
	"prov:wasAttributedTo": {
		"url": "https://nytimes.com"
	},
	"@graph": { ... }
}
```
