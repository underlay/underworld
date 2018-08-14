# Assertions

Assertions in the Underlay are [JSON-LD documents](https://json-ld.org/spec/latest/json-ld/) that conform to a couple of Underlay-specific conventions. This document assumes a light familiarity with JSON-LD - skimming the [Basic Concepts](https://json-ld.org/spec/latest/json-ld/#basic-concepts) section of the spec should be enough @context.

_Here is a sample assertion, for use as the simplest of templates_

```json
{
  "@context": {
    "schema": "http://schema.org/",
    "prov": "http://www.w3.org/ns/prov#"
  },
  "@type": "prov:Entity",
  "@graph": {
    "@type": "schema:Person",
    "schema:name": "LeBron James",
    "schema:birthDate": "1984-12-30"
  },
  "prov:wasAttributedTo": {
    "@type": ["prov:Organization", "schema:Organization"],
    "@id": "_:espn",
    "schema:name": "ESPN",
    "schema:url": "http://www.espn.com/"
  },
  "prov:qualifiedAttribution": {
    "@type": "prov:Attribution",
    "prov:atLocation": "http://www.espn.com/nba/player/_/id/1966/lebron-james",
    "prov:agent": { "@id": "_:espn" }
  }
}
```

## IPLD Links

[IPLD](https://github.com/ipld/ipld) is a data model for the decentralized web that uses "IPLD Links" encoding a self-describing hash of a piece of content as its unique, resolvable identifier. These content identifiers are called [CIDs](https://github.com/ipld/cid) and are typically serialized as base58-encoded strings.

An "IPLD Link" is a JSON object of the form `{"/": <base58-encoded-CID>}`, and links following this form can be traversed automatically in Unix-style paths by any IPLD resolver. This means that given an object `{"foo": 42}` with CID `<cid1>`, and another object `{"bar": {"baz": {"/": <cid1>}}}` with CID `<cid2>`, the IPLD path `<cid1>/bar/baz/foo` would automatically resolve all the way to `42`. IPLD Links are great for hiding complexity that can be reached if necessary but doesn't need to be copied around all the time. Instead we can pass around these lightweight IPLD paths as pointers instead, confident that we could use IPLD to retrieve the real data at any time (so long as somebody on the network is keeping track of it).

The JSON-LD spec requires applications to ignore foreign (unresolved non-IRI) properties in objects, which means we can't just include a literal IPLD link object as a property's value. Instead, the JSON-LD spec promotes the use of [Index Maps](https://json-ld.org/spec/latest/json-ld/#index-maps) for foreign keys, which transform our IPLD Links into `{"@index": "/", "@value": <cid>}`. This is more clunky, but doesn't break compatibility with existing JSON-LD processor implementations. It _does_ break the default JSON IPLD resolver, but IPLD was designed from the beginning to be easily extensible to new formats, so we've written a [js-ipld-jsonld resolver](https://github.com/underlay/js-ipld-jsonld) that works with the index-map link format during path resolution.

A pattern we encourage in Underlay assertions is splitting files "wherever appropriate" and substituting IPLD Links for references. We expect some assertions to be enormous, and some provenance graphs to be duplicated. We allow any [node object](https://json-ld.org/spec/latest/json-ld/#node-objects), [graph object](https://json-ld.org/spec/latest/json-ld/#graph-objects), or [value object](https://json-ld.org/spec/latest/json-ld/#value-objects) in an assertion to be replaced with an IPLD link to the (respective) object's content, and encourage users to split up their assertions in whatever way makes the most sense for them.

For example, in an assertion containing a list of large, homogenous records, we might want to split each record so that the assertion is a (much smaller) list of links to each record. Or if we expect to re-use a provenance graph, we might split it off for deduplication:

```javascript
const context = {
  "@vocab": "http://schema.org/",
  prov: "http://www.w3.org/ns/prov#",
}

const provenance = {
  "@context": context,
  "@type": ["prov:Entity", "Book"],
  name: "the phone book",
  ...lots_of_provenance_data,
}

const options = { format: "jsonld", hashAlg: "sha2-256" }
const cid = await ipfs.dag.put(provenance, options)

const assertion = {
  "@context": context,
  "@graph": {
    name: "Joel Gustafson",
    telephone: "(000) 111-2222",
  },
  "prov:wasAttributedTo": {
    "@index": "/",
    "@value": cid.toBaseEncodedString(), // zBwWX9ecx5F4X54WAjmFL...
  },
}
```

## PROV Provenance

The [PROV Ontology](https://www.w3.org/TR/2013/REC-prov-o-20130430/) is an ontology for recording provenance developed by the W3C Provenance Working Group. We're adopting PROV for assertions in the Underlay. We include provenance inline, as object properties, using the [PROV-DM](https://www.w3.org/TR/2013/REC-prov-dm-20130430/) namespace `http://www.w3.org/ns/prov#` (prefixed in this document with `prov`).

```json
{
  "@type": ["schema:ScholarlyArticle", "prov:Entity"],
  "schema:headline": "The chromatic number of the plane is at least 5",
  "schema:url": "https://arxiv.org/pdf/1804.02385.pdf",
  "prov:wasAttributedTo": {
    "@type": ["schema:Person", "prov:Agent"],
    "schema:name": "Aubrey D. N. J. de Grey"
  }
}
```

### Shadowing existing properties

Often the terms in the PROV ontology will overlap with existing properties of various schemas. In the previous example, we might (and should!) have wanted to also use the `schema:author` property. This is straightforward; JSON-LD admits multiple types and has several easy ways to reference the same node from two locations:

```json
[
  {
    "@type": ["schema:ScholarlyArticle", "prov:Entity"],
    "schema:headline": "The chromatic number of the plane is at least 5",
    "schema:url": "https://arxiv.org/pdf/1804.02385.pdf",
    "schema:author": { "@id": "_:author" },
    "prov:wasAttributedTo": { "@id": "_:author" }
  },
  {
    "@type": ["prov:Agent", "schema:Person"],
    "@id": "_:author",
    "schema:name": "Aubrey D. N. J. de Grey"
  }
]
```

### Provenance of assertions themselves

One source of particular confusion (at least for this author) is the interplay between the provenance of real-world objects and the provenance of assertions as digital objects themselves. Suppose that you find an image on Wikipedia and you want to describe its provenance:

```json
{
  "@type": ["schema:ImageObject", "prov:Entity"],
  "schema:url": "https://commons.wikimedia.org/wiki/File:8-cell.gif",
  "schema:contentUrl": "https://upload.wikimedia.org/wikipedia/commons/d/d7/8-cell.gif",
  "prov:wasAttributedTo": {
    "@type": ["schema:Person", "prov:Agent"],
    "schema:name": "Dr. Suess",
    "schema:description": "world famous tesseract photographer"
  }
}
```

... Easy enough. But suppose that you didn't really know this for yourself: your friend Bob told you the image's `contentUrl` and photographer. This is definitely relevant information, but doesn't describe the provenance of the image (the image already exists, it couldn't care less about Bob): **it describes the provenance of the digital object that describes the image**. We use [JSON-LD Named Graphs](https://json-ld.org/spec/latest/json-ld/#named-graphs) to do this sort of referencing: wrapping your data in a `@graph` node lets you describe properties of your data-as-a-digital-collection, such as its provenance.

```json
{
  "@type": "prov:Entity",
  "@graph": {
    "@type": ["schema:ImageObject", "prov:Entity"],
    "schema:contentUrl": "https://upload.wikimedia.org/wikipedia/commons/d/d7/8-cell.gif",
    "prov:wasAttributedTo": {
      "@type": ["schema:Person", "prov:Agent"],
      "schema:name": "Joel Gustafson"
    }
  },
  "prov:wasAttributedTo": {
    "@type": ["schema:Person", "prov:Agent"],
    "schema:name": "Bob"
  }
}
```

The nesting here can get annoying, so make sure you're familiar with [graph containers](https://json-ld.org/spec/latest/json-ld/#graph-containers) so that you don't have to write out `@graph` every time.

### Collections

[PROV Collections](https://www.w3.org/TR/2013/REC-prov-o-20130430/#Collection) let us describe the collective provenance of groups of items, even if they also have additional, individual provenance.

## Blank node IDs

In general, treat `@id` _as a way to link nodes together_, not as a property to store values in.

We discourage the use of _significant_ `@id`s in JSON-LD documents: that is, if your `@id`s are IRIs or contain data that is used outside the context of the document, that data should also be duplicated in a named property (e.g. http://schema.org/identifier or something more descriptive).

## Optional top-level signatures

We expect that most assertions will be untrustworthy without publicly verifiable signatures of their publishers (as distinct from their _source_ - many Underlay nodes may publish an equivalent assertion citing the same sources). We anticipate using JSON-LD signatures specified in the [Security Vocabulary](https://web-payments.org/vocabs/security) from the W3C Web Payments Community Group. These signatures are optional, but if you want to include one you should follow either `GraphSignature` or `LinkedDataSignature` for the best chances of staying future-compatible.
