# Links

> Notes from Joel on linking documents

JSON-LD Documents need to be able to link to each other. Right now this is only possible implicitly when two documents use the same IRIs to identify their nodes. Ideally this would always happen with perfect 1-1-1 correspondence of JSON-LD node objects, IRIs, and real-world objects, but in practice it's often impossible to distinguish a deliberate reference from a coincidencal collision.

In general, relying so heavily on absolute IRIs places an enormous burden on both content publishers and consumers to coordinate namespaces/schemas/ontologies (not to mention the inevitable fuzziness of intra-schema ambiguities). _It shouldn't be that hard to publish linked data_, and one way to do that is to let the data be truly linked: direct, unambigious, immutable references to existing documents.

(This also reflects a deeper principle: edges are more important than nodes. Meaning emerges from relative connections, not from absolute identifiers. Encouraging documents to reference each other directly feels like a better long-term strategy than curating collections of identifiers; this should be spun out in a standalone "Identifiers considered harmful" argument.)

But okay, how do we do it?

## v0.1

The original purpose for the JSON-LD IPLD format was to traverse circular property-paths.

```json
{
  "@context": { "@vocab": "http://schema.org/" },
  "@id": "_:john",
  "name": "John Doe",
  "spouse": {
    "@id": "_:jane",
    "name": "Jane Doe",
    "spouse": { "@id": "_:john" }
  }
}
```

| Path                       | Value    |
| -------------------------- | -------- |
| /name                      | John Doe |
| /spouse/name               | Jane Doe |
| /spouse/spouse/name        | John Doe |
| /spouse/spouse/spouse/name | Jane Doe |

In this world, IPLD links were easy to include as [index maps](https://json-ld.org/spec/latest/json-ld/#index-maps) like `{"@index": "/", "@value": "Qm..."}` or even literal IPLD link objects like `{"/": "Qm..."}` with the right context container. Then we can run examples like this:

```javascript
const options = {format: "jsonld", hashAlg: "sha2-256"}

const city = {
  "@context": { "@vocab": "http://schema.org/" },
  "@type": "City",
  "name": "Duluth",
  "url": "http://www.duluthmn.gov/",
}

const cityCid = await ipfs.dag.put(city, options)

const person = {
  "@context": {
    "@vocab": "http://schema.org/",
    "birthPlace": { "@container": "@index" },
  },
  "@type": "Person",
  "name": "Joel Gustafson",
  "birthPlace": { "/": cityCid.toBaseEncodedString()},
}

const personCid = await ipfs.dag.put(jsonld, options)

const {value} = await ipfs.dag.get(personCid, "birthPlace/name")
// "Duluth"
```

I implemented and published this approach in [versions `0.1.*`](https://github.com/underlay/js-ipld-jsonld/tree/f625327cbc406d0cad2d471d93ceca97d76d4e42), but usage was very limited and filesystem-style paths were not a good conceptual fit for JSON-LD. Since JSON-LD supports multiple, unsorted values of differening schemas, a user would have to know a document's structure so precisely that they'd be better off just using ordinary JSON paths and `dag-cbor` to link within documents.

A separate concern was that in JSON-LD, [value objects](https://json-ld.org/spec/latest/json-ld/#value-objects) can't have additional keys beyond `@index` and optionally `@type` or `@language`. So the use case of "appending" properties to someone else's node isn't actually possible - you could only ever use others' nodes as values on your own properties, and even then you'd have to know exactly where to find them in the document.

## Maybe a query syntax?

I also explored a query syntax for terse selectors that could fit inside path elements, like `/{"name": "John Doe"}/spouse`. This was not a great idea, and an abuse of path elements. We want a solution with good conceptual hygiene!

## JSON-LD Frames?

The Linking Data in JSON Community Group published a [report](https://json-ld.org/spec/latest/json-ld-framing/) on "JSON-LD Framing", a heavy-duty solution for forcing foreign JSON-LD into a specific tree layout (or "frame"). Frames are themselves JSON-LD, and scale well with the complexity of the selection: framing a single node by `@id` is just `{ "@id": <id> }`. Including properties and subproperties add only marginal overhead.

The homoiconism of JSON-LD frames is really appealing, but it's hard to know exactly what to do with it. There are certainly some crazy ideas available:
- IPLD path elements are themselves hashes of JSON-LD frames! `<document-cid>/<frame-cid>`
- Bring back URL fragments! `<document-cid>#<frame-cid>` or `<document-cid>/#<frame-cid>`

But instead I'm leaning toward something that uses CIDs of root documents as `@index` values directly, where the `@graph` object is interpreted to be a JSON-LD Frame. So an object `{ "@index": "Qm..." }` refers to the entire default graph of the target document, while

```json
{
  "@context": { "@vocab": "http://schema.org/" },
  "@index": "Qm...",
  "@graph": { "@id": "http://people.org/joel" },
  "name": "Joel Gustafson"
}
```

extracts the `"http://people.org/joel"` node from the target document and appends `"name": "Joel Gustafson"` to it. If `"http://people.org/joel"` _also_ had an `@index` with some CID, it'd recursively resolve that link through too, etc.

This approach doesn't quite have the conceptual feng shui I'm gunning for, it's still surprisingly non-intrusive: JSON-LD frames can't match `@index` values and thus presently ignore them (what a waste!). But IDs used within the frame are scoped to the containing graph, so they won't collide and merge with the rest of the document during processing. The approach also comes with a built-in reification strategy: it's easy to link either to a document-as-a-document or to a subject node within a document.

## Inverting the index

> Thoughts from a never-ending BOS->SFO flight 2018-09-05

1. It seems like there are really only two kinds of links - one where you want to use an existing node as a value for a property of a new one, and another where you want to append a property-value (or a few) to an existing node.

2. It's definitely necessary to re-introduce an `"@index": "/"` property at the top level and push the CID index down into `@graph`. This is awkward because it means we almost always need two `@index` properties for each link (bleh!) but otherwise selecting a node by `@id` (by far the most common case) is actually not possible: just `{"@id": "some_id"}` is actually not a valid JSON-LD node, and will get ignore during processing, so trying to reference `{ "@index": "Qm...", "@graph": { "@id": "some_id" } }` won't work. So instead we twis t it into `{ "@index": "/", "@graph": { "@index": "Qm...", "@id": "some_id" } }` so that the all the properties get preserved. This has the side benefit of faster "is-link?" checking during processing, since we don't have to try to parse a CID out of every `@index` we find. _And_, on reflection, this is conceptually cleaner: first have nodes declare that they _are_ links, and _then_ have them declare where they point to.

Suppose we have a CID `Qm...` of the following graph:
```json
{
  "@context": { "@vocab": "http://schema.org/", "@base": "http://example.org/" },
  "@id": "joel",
  "name": "Joel Gustafson",
}
```

Then the two kinds of links look like this:

### Reference value

Let's use the `joel` node as a value in another graph:
```json
{
  "@context": { "@vocab": "http://schema.org/", "@base": "http://example.org/" },
  "@id": "kevin",
  "knows": {
    "@index": "/",
    "@graph": {
      "@index": "Qm...",
      "@id": "joel"
    }
  }
}
```

### Append property
But now suppose you want to describe further properties of the `joel` node - not just using it as a value. In particular, let's append a property `http://schema.org/birthDate` with value `1996-02-02`:

```json
{
  "@context": { "@vocab": "http://schema.org/", "@base": "http://example.org/" },
  "@index": "/",
  "@graph": { "@index": "Qm...", "@id": "joel" },
  "birthDate": "1996-02-02"
}
```

### Wait, those two kinds of links are exactly the same
Yes.
