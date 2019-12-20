# Packages

An _Underlay package_ is a collection of messages, files, and other packages.

- [Resource URIs vs Content URIs](#resource-uris-vs-content-uris)
- [Referent chasing](#referent-chasing)
- [Revisions](#revisions)
- [Members](#members)
  - [Messages](#messages)
  - [Files](#files)
  - [Other packages](#other-packages)
- [Directory representation](#directory-representation)
- [Linked Data Platform Containers](#linked-data-platform-containers)
- [JSON-LD Context Compaction](#json-ld-context-compaction)

They're represented as blank nodes with an `rdf:type` of `http://underlay.mit.edu/ns#Package`, and `prov:hadMember` relations to their members. They're published as RDF Graphs (i.e. RDF Datasets without any named graphs).

Packages are subclasses of both [PROV Collections](https://www.w3.org/TR/prov-o/#Collection) and [Linked Data Platform Direct Containers](https://www.w3.org/TR/ldp/#dfn-linked-data-platform-direct-container).

```
<http://underlay.mit.edu/ns#Package> rdfs:subClassOf prov:Collection .
<http://underlay.mit.edu/ns#Package> rdfs:subClassOf ldp:DirectContainer .
```

Here's an example package:

```
% cat package-a.jsonld
{
  "@context": {
    "@base": "http://registry.example.com/",
    "prov": "http://www.w3.org/ns/prov#",
    "ldp": "http://www.w3.org/ns/ldp#",
    "ldp:membershipResource": { "@type": "@id" }
  },
  "@type": "http://underlay.mit.edu/ns#Package",
  "ldp:membershipResource": "package-a",
  "ldp:hasMemberRelation":  { "@id": "prov:hadMember" },
  "prov:value": {
    "@id": "dweb:/ipfs/bafybeih4wdwetrvaz2ospgebag4rtndhhqebwgmos6hbwxdhfhtw3d2vde"
  },
  "prov:hadMember": [
    {
      "@id": "ul:/ipfs/bafkreib2xgk7gwailskap5ohnz4iua3pno2lm4wemop2bm7opgcun2dtse",
      "ldp:membershipResource": "package-a/jane-doe"
    },
    {
      "@id": "dweb:/ipfs/bafybeiatr6vzozvaxtp5f32ghixj4bvauz6wgl4lbbh6np4yrrsvtep3y4",
      "ldp:membershipResource": "package-a/8-cell-orig.gif"
    }
  ]
}
```

Packages are designed to work with registry namespaces, so it's expected that every package will have a unique URI, managed by its parent registry, with a human-readable package name as the last path element of the URI, with no query or fragment components. In the JSON-LD examples here, the registry "root" URI path will always be given as the [`@base`](https://w3c.github.io/json-ld-syntax/#base-iri) of the JSON-LD context, so that packages in the registry can be referenced simply as `"@id": "package-name"`.

## Resource URIs vs Content URIs

[REST](https://en.wikipedia.org/wiki/Representational_state_transfer) is very explicit about distinguishing between abstract _resources_ and concrete _representations_:

> The key abstraction of information in REST is a resource. Any information that can be named can be a resource: a document or image, a temporal service (e.g. "today's weather in Los Angeles"), a collection of other resources, a non-virtual object (e.g. a person), and so on. In other words, any concept that might be the target of an author's hypertext reference must fit within the definition of a resource. A resource is a conceptual mapping to a set of entities, not the entity that corresponds to the mapping at any particular point in time. - _[5.2.1.1 Resources and Resource Identifiers](https://www.ics.uci.edu/~fielding/pubs/dissertation/rest_arch_style.htm#sec_5_2_1_1)_

> REST components perform actions on a resource by using a representation to capture the current or intended state of that resource and transferring that representation between components. A representation is a sequence of bytes, plus representation metadata to describe those bytes. Other commonly used but less precise names for a representation include: document, file, and HTTP message entity, instance, or variant. - _[5.2.1.2 Representations](https://www.ics.uci.edu/~fielding/pubs/dissertation/rest_arch_style.htm#sec_5_2_1_2)_

Resources are what live in the mind of an author; representations are the bytes that computers operate on. Representations are specific and immutable; resources are what keep their identity across mutations.

The Underlay makes this distiction even more explicit by using two different kinds of URIs, called resource URIs and content URIs.

- Content URIs identify representations by the hash of their bytes.
  - RDF resource representations are canonicalized RDF datasets and their content URIs start with `ul:/ipfs/`.
  - Non-RDF resource representations are files (opaque byte arrays) and their content URIs start with `dweb:/ipfs/`.
  - In both cases, the hash is the base32 CIDv1 of the IPFS file with raw leaves.
    - This means that for small files, the hash is the direct hash of its bytes with a `raw` CID codec.
    - IPFS splits larger files into chunks, in which case the hash is actually the root of a merkle tree, with a `dag-pb` CID codec.
    - The `--raw-leaves` option is not the default in IPFS clients and must be explicitly enabled.
  - The base32 CID is the first and only path element after `/ipfs/` in the URI.
- Resource URIs begin with a registry URL like `http://example.com/registry/` and identify resources as paths, such as `http://example.com/registry/package-a` or `http://example.com/registry/package-a/kitty.png`.

_Version_ and _representation_ are used interchangeably here - a "different version" doesn't imply a unique version number or label or anything other than a different representation of the same underlying abstract resource.

## Referent chasing

It's important to be very clear on exactly what different URI formats refer to. Consider the example package from the introduction:

```
% cat package-a.jsonld | jsonld normalize | ipfs add --raw-leaves -Q | ipfs cid base32
bafkreihqvh4pdolv5ihayngspc2zk6la46dzbqd4eiz5dcoysvnpfojboi
```

```
% ipfs cat bafkreihqvh4pdolv5ihayngspc2zk6la46dzbqd4eiz5dcoysvnpfojboi
<dweb:/ipfs/bafybeiatr6vzozvaxtp5f32ghixj4bvauz6wgl4lbbh6np4yrrsvtep3y4> <http://www.w3.org/ns/ldp#membershipResource> <http://registry.example.com/package-a/8-cell-orig.gif> .
<ul:/ipfs/bafkreib2xgk7gwailskap5ohnz4iua3pno2lm4wemop2bm7opgcun2dtse> <http://www.w3.org/ns/ldp#membershipResource> <http://registry.example.com/package-a/jane-doe> .
_:c14n0 <http://www.w3.org/1999/02/22-rdf-syntax-ns#type> <http://underlay.mit.edu/ns#Package> .
_:c14n0 <http://www.w3.org/ns/ldp#hasMemberRelation> <http://www.w3.org/ns/prov#hadMember> .
_:c14n0 <http://www.w3.org/ns/ldp#membershipResource> <http://registry.example.com/package-a> .
_:c14n0 <http://www.w3.org/ns/prov#hadMember> <dweb:/ipfs/bafybeiatr6vzozvaxtp5f32ghixj4bvauz6wgl4lbbh6np4yrrsvtep3y4> .
_:c14n0 <http://www.w3.org/ns/prov#hadMember> <ul:/ipfs/bafkreib2xgk7gwailskap5ohnz4iua3pno2lm4wemop2bm7opgcun2dtse> .
_:c14n0 <http://www.w3.org/ns/prov#value> <dweb:/ipfs/bafybeih4wdwetrvaz2ospgebag4rtndhhqebwgmos6hbwxdhfhtw3d2vde> .
```

So the file `package-a.jsonld` is a representation of an RDF dataset, and its content URI is:

```
ul:/ipfs/bafkreihqvh4pdolv5ihayngspc2zk6la46dzbqd4eiz5dcoysvnpfojboi
```

But what does this really refer to? _It only refers to the RDF Dataset - the container that has these eight RDF statements as members - and nothing more._ It does _not_ refer to the package described by those statements; it refers to the literal collection of statements themsevles!

If we mean to refer to the package described in the dataset, we need to say so:

```
ul:/ipfs/bafkreihqvh4pdolv5ihayngspc2zk6la46dzbqd4eiz5dcoysvnpfojboi#_:c14n0
```

_This_ is the content URI for this version of the package, and it's why packages representations need to use a blank node (and not the package resource URI) as the subject of all the package properties. Blank nodes, which are strictly scoped to their local dataset, serve as an externally content-addressable identity for specific versions of packages. The blank nodes are linked to their abstract resource URIs with a `ldp:membershipResource` predicate, but it's always the blank node that "defines" a package representation.

Typically, the package blank node will be the only blank node in the dataset, so it will always have the canonical label `_:c14n0`.

## Revisions

In the graph, the package blank node has a `prov:wasRevisionOf` property linking it to the content URI of its previous version, if it exists.

## Members

Packages can contain three distinct classes of members: messages, files, and other packages.

Membership in a package `_:p` of a version `<content-URI>` of an abstract resource `<resource-URI>` is delcared with two triples:

```
_:p <http://www.w3.org/ns/prov#hadMember> <content-URI> .
<content-URI> <http://www.w3.org/ns/ldp#membershipResource> <resource-URI> .
```

The second triple is required for included packages, but optional for messages and files, which may or may not have associated resource URIs.

### Messages

Messages are the most common type of package member, and are described in the [message spec](MESSAGES.md). In this case, we really do want to refer to the message itself as an RDF dataset, so its content URI doesn't have a fragment identifier.

For example, given a message:

```
% cat message.jsonld
{
  "@context": {
    "@vocab": "http://schema.org/",
    "prov": "http://www.w3.org/ns/prov#"
  },
  "prov:wasAttributedTo": { "name": "The Small Town Gazette" },
  "@graph": {
    "@id": "http://example.com/jane-doe",
    "name": "Jane Doe",
    "jobTitle": "Professor",
    "knows": {
      "@id": "http://example.com/john-doe"
    }
  }
}
% cat data.jsonld | jsonld normalize | ipfs add -Q --raw-leaves | ipfs cid base32
bafkreib2xgk7gwailskap5ohnz4iua3pno2lm4wemop2bm7opgcun2dtse
```

...we can include this message in a package `_:p` with the triple

```
_:p <http://www.w3.org/ns/prov#hadMember> <ul:/ipfs/bafkreib2xgk7gwailskap5ohnz4iua3pno2lm4wemop2bm7opgcun2dtse> .
```

Again, note that there is no fragment identifier in this URI - we want to refer to the entire dataset, not to any one of its individual graphs or statements or nodes.

If there is a natural name or identifier for this message in the conceptual organization of the package, such as a UUID for the entity that it describes, then we can identify the abstract resource URI for the message by appending the name as a path element to the package URI. This is a way of naming a message's abstract role in the package, as opposed to justdeclaring a specific message version's presence.

In the example, we might identify `jane-doe` as an appropriate message name. If our package URI is `http://registry.example.com/package-a`, then we would add:

```
<ul:/ipfs/bafkreib2xgk7gwailskap5ohnz4iua3pno2lm4wemop2bm7opgcun2dtse> <http://www.w3.org/ns/ldp#membershipResource> <http://registry.example.com/package-a/jane-doe> .
```

... or in JSON-LD:

```
{
  ...
  "ldp:membershipResource": { "@id": "package-a" },
  "prov:hadMember": {
    "@id": "ul:/ipfs/bafkreib2xgk7gwailskap5ohnz4iua3pno2lm4wemop2bm7opgcun2dtse",
    "ldp:membershipResource": {
      "@id": "package-a/jane-doe"
    }
  }
}
```

This format - appending a single path element to the package resource URI - is the only valid message resource URI format. This means message names are restricted to valid [URI path segments](https://tools.ietf.org/html/rfc3986#section-3.3).

A message should be given a resource URI if it a) describes one coherent entity that has a stable identifier, or b) the message itself corresponds to some coherent named resource (e.g. "the data that was derived from this source / found in this place", even if the data itself is a loose pile of miscellaneous facts). In particular, a message should have a named resource if it is might be replaced (in later versions of the package) by another message that occupies the same place or fulfills the same role. In that case, the new package will have a different content URI as its `prov:hadMember`, but that new content URI will be a `ldp:membershipResource` of the same resource.

No two messages can be a version of the same resource in the same package.

### Files

Packages can also include non-RDF files, which we distinguish with a different URI scheme `dweb:/ipfs/...` instead of `ul:/ipfs/...`. Files should be included in packages if they are a major, focal subject of the data in the package's messages. They can be given resource URIs just like messages (by appending the filename to the package URL), although assertions should only refer to files by their direct content-address.

Using [this image](https://upload.wikimedia.org/wikipedia/commons/d/d6/8-cell-orig.gif) as an example file, we can find its CID:

```
% curl -s https://upload.wikimedia.org/wikipedia/commons/d/d6/8-cell-orig.gif | \
ipfs add -Q --raw-leaves | \
ipfs cid base32
bafybeiatr6vzozvaxtp5f32ghixj4bvauz6wgl4lbbh6np4yrrsvtep3y4
```

Including the file in a package under its original filename `8-cell-orig.gif` would look like:

```
_:package <http://www.w3.org/ns/prov#hadMember> <dweb:/ipfs/bafybeiatr6vzozvaxtp5f32ghixj4bvauz6wgl4lbbh6np4yrrsvtep3y4> .
<dweb:/ipfs/bafybeiatr6vzozvaxtp5f32ghixj4bvauz6wgl4lbbh6np4yrrsvtep3y4> <http://www.w3.org/ns/ldp#membershipResource> <http://registry.example.com/package-a/8-cell-orig.gif> .
```

... or in JSON-LD:

```
{
  ...
  "ldp:membershipResource": { "@id": "package-a" },
  "prov:hadMember": {
    "@id": "dweb:/ipfs/bafybeiatr6vzozvaxtp5f32ghixj4bvauz6wgl4lbbh6np4yrrsvtep3y4",
    "ldp:membershipResource": "package-a/8-cell-orig.gif"
  }
}
```

### Other packages

Packages can include other packages. This might be called "importing" in other contexts, but here we deliberately use the same language we use for other resources. Including a package means the same thing as directly including all of that package's contents - it's just more concise to express and makes it easier to update things when they change. Formally, the previous sentence is equivalent to the statement "`prov:hadMember` is a transitive relation".

Given our example from before of `package-a` with content URI `ul:/ipfs/bafkreifw52aek3l2x44nhsutajpil3c6sc7gsig3bnbigskt6un3tw5pti#_:c14n0`, we could include `package-a` in a version of another package `package-b`:

```
{
  ...
  "ldp:membershipResource": { "@id": "package-b" },
  "prov:hadMember": {
    "@id": "ul:/ipfs/bafkreihqvh4pdolv5ihayngspc2zk6la46dzbqd4eiz5dcoysvnpfojboi#_:c14n0",
    "ldp:membershipResource": { "@id": "package-a" }
  }
}
```

## Directory representation

IPFS can represent entire directory structures, which is very convenient for retrieving large trees of files.

One of the required properties of a package is a [`prov:value`](https://www.w3.org/TR/prov-o/#value) predicate linking to a `dweb:/ipfs/` _directory_ that holds the package's dependency tree. The package itself corresponds to the root directory, and its members are files (messages and files) or subdirectories (packages) named with either their resource name, if it exists, or with their base32 CID.

This means that instead requiring users to manually traverse the pacakge dependency tree and request each message and file individually, an entire package's state can be requested with a single root CID.

### Names and file extensions

This `prov:value` is an opinionated, "direct" representation of a package, and as such it follows some opinionated conventions around naming.

#### Packages

A subpackage `foo` in a package appears twice in its directory representation:

- a file named `foo.nt` that is the subpackage's canonicalized n-quads representation
- a directory named `foo` that is the subpackage's directory representation

For example, the directory representation of a package `package-b` that includes our example package `package-a` would contain:

```
% ipfs ls bafybeib2iuzyhfcyjgoyuoscjxqsfd5kst3hfyyeqhpzxdm622azyoglxe
bafybeih4wdwetrvaz2ospgebag4rtndhhqebwgmos6hbwxdhfhtw3d2vde -   package-a/
bafkreihqvh4pdolv5ihayngspc2zk6la46dzbqd4eiz5dcoysvnpfojboi 988 package-a.nt
```

#### Messages

A message `bar` in a package appears once as a file named `bar.nt`. If a message doesn't have a name (i.e. it doesn't have a resource URI), then its base32 CID is used instead, *still appended with the `.nt` file extension*. For example, if the message `http://example.com/package-a/jane-doe` didn't have a resource URI, it would appear as `package-a/bafkreib2xgk7gwailskap5ohnz4iua3pno2lm4wemop2bm7opgcun2dtse.nt` instead of `package-a/jane-doe.nt`.

#### Files

Files in a package's directory representation have filenames that are just their name (no file extension, unless the file extension is a part of their name), if they have a resource URI, or just their base32 CID (no file extension). For example, if the file `http://example.com/package-a/8-cell-orig.gif` didn't have a resource URI, it would appear as `package-a/bafybeiatr6vzozvaxtp5f32ghixj4bvauz6wgl4lbbh6np4yrrsvtep3y4` instead of `package-a/8-cell-orig.gif`.

### Example

Assembling package directories is straightforward. Continuing our example:

```
% mkdir package-a
% ipfs cat bafkreiel4jhpeqnu6g2cug6j67ho2xn5skyngidgutomsyj5bqjs4nn4ha > package-a/jane-doe.nt
% ipfs cat bafybeiatr6vzozvaxtp5f32ghixj4bvauz6wgl4lbbh6np4yrrsvtep3y4 > package-a/8-cell-orig.gif
% ipfs add package-a -r --raw-leaves -Q | ipfs cid base32
bafybeih4wdwetrvaz2ospgebag4rtndhhqebwgmos6hbwxdhfhtw3d2vde
```

```
% ipfs ls bafybeih4wdwetrvaz2ospgebag4rtndhhqebwgmos6hbwxdhfhtw3d2vde
QmPf1X2Yntp1DiGFPN8JX9WmPdQHsHHYGeU1GfuP2KNpxn              640422 8-cell-orig.gif
bafkreib2xgk7gwailskap5ohnz4iua3pno2lm4wemop2bm7opgcun2dtse 375    jane-doe.nt
```

Incremental changes to an existing package directory are best done with the [`ipfs object patch`](https://docs.ipfs.io/reference/api/cli/#ipfs-object-patch) CLI command:

```
% mkdir package-b
% ipfs add -r -Q package-b | ipfs cid base32
bafybeiczsscdsbs7ffqz55asqdf3smv6klcw3gofszvwlyarci47bgf354
% ipfs object patch bafybeiczsscdsbs7ffqz55asqdf3smv6klcw3gofszvwlyarci47bgf354 add-link package-a.nt bafkreihqvh4pdolv5ihayngspc2zk6la46dzbqd4eiz5dcoysvnpfojboi
bafybeiek322btrjkwer7rc55sdes4f7obrbcs3w3ezo5fwhqghdm6krrr4
% ipfs object patch bafybeiek322btrjkwer7rc55sdes4f7obrbcs3w3ezo5fwhqghdm6krrr4 add-link package-a bafybeih4wdwetrvaz2ospgebag4rtndhhqebwgmos6hbwxdhfhtw3d2vde
bafybeib2iuzyhfcyjgoyuoscjxqsfd5kst3hfyyeqhpzxdm622azyoglxe
```

### Constraints

This directory structure imposes some mild constraints on which names are valid in resource URIs:

- No message or file can be given the same name as a package included in the same directory. For example, even though `http://registry.example.com/package-a` and `http://registry.example.com/package-b/package-a` are different resource URIs, you can't name a something in package B "`http://registry.example.com/package-b/package-a`" if package B also includes a version of `http://registry.example.com/package-a`, since that would induce a name conflict in the directory tree (both would want the name `package-a`).
- Similarly, you can't name a file `bar.nt` if there's either a message named `bar` *or* a subpackage named `bar` in the same package, since that would also induce a name conflict in the directory tree (and you obviously can't name a file just `baz` if there's a message named `baz` since that would give them both the same resource URI, which is even worse).
- No message or file can be given a name that is the CID of a different (named or unnamed) message or file in the same package. Nobody should ever want to do this anyway.

This directory CID has two major uses. It could be literally retrieved as an actual directory, physically materialized on a user's filesystem, or it could be used as a [pinning](https://docs.ipfs.io/guides/concepts/pinning/) mechanism for IPFS, where the current version of a package is always pinned (and unpinned when a new version is found). This means that anything in the dependency tree would always be pinned, and outdated versions would be unpinned and freed for garbage collection.

## Linked Data Platform Containers

The final required properties of a package blank node are two triples

```
_:p <http://www.w3.org/ns/ldp#hasMemberRelation> <http://www.w3.org/ns/prov#hadMember> .
_:p <http://www.w3.org/ns/ldp#membershipResource> <http://registry.example.com/package-a> .
```

... which are required properties of [Linked Data Platform Direct Containers](https://www.w3.org/TR/ldp/#ldpdc). The first triple declares the container's member relation; the second delcares which resource the blank node is a representation of.

## JSON-LD Context Compaction

Applying the [reverse property](https://w3c.github.io/json-ld-syntax/#reverse-properties) and [property index](https://w3c.github.io/json-ld-syntax/#property-based-data-indexing) features of JSON-LD produces a particularly concise package representation:

```
{
  "@context": {
    "@base": "http://registry.example.com/",
    "prov": "http://www.w3.org/ns/prov#",
    "ldp": "http://www.w3.org/ns/ldp#",
    "resource": {
      "@type": "@id",
      "@reverse": "ldp:membershipResource"
    },
    "hadMember": {
      "@container": "@index",
      "@index": "resource"
    }
  },
  "@type": "http://underlay.mit.edu/ns#Package",
  "ldp:hasMemberRelation":  { "@id": "prov:hadMember" },
  "ldp:membershipResource": { "@id": "package-a" },
  "prov:value": {
    "@id": "dweb:/ipfs/bafybeih4wdwetrvaz2ospgebag4rtndhhqebwgmos6hbwxdhfhtw3d2vde"
  },
  "prov:hadMember": {
    "package-a/jane-doe": "ul:/ipfs/bafkreiel4jhpeqnu6g2cug6j67ho2xn5skyngidgutomsyj5bqjs4nn4ha",
    "package-a/8-cell-orig.gif": "dweb:/ipfs/bafybeiatr6vzozvaxtp5f32ghixj4bvauz6wgl4lbbh6np4yrrsvtep3y4"
  }
}
```

... which can be further compacted by caching the context on IPFS:

```
% ipfs cat bafkreihz5jqpso43dctxgun3oi2zbs4l26fko2a3tbd4acdr5kgvq2y2ky
{
  "@context": {
    "@base": "http://registry.example.com/",
    "prov": "http://www.w3.org/ns/prov#",
    "ldp": "http://www.w3.org/ns/ldp#",
    "resource": {
      "@type": "@id",
      "@reverse": "ldp:membershipResource"
    },
    "hadMember": {
      "@container": "@index",
      "@index": "resource"
    }
  }
}
```

... to give us a maximally concise package format:

```
{
  "@context": "ipfs://bafkreihz5jqpso43dctxgun3oi2zbs4l26fko2a3tbd4acdr5kgvq2y2ky",
  "@type": "http://underlay.mit.edu/ns#Package",
  "ldp:hasMemberRelation":  { "@id": "prov:hadMember" },
  "ldp:membershipResource": { "@id": "package-a" },
  "prov:value": {
    "@id": "dweb:/ipfs/bafybeih4wdwetrvaz2ospgebag4rtndhhqebwgmos6hbwxdhfhtw3d2vde"
  },
  "prov:hadMember": {
    "package-a/jane-doe": "ul:/ipfs/bafkreiel4jhpeqnu6g2cug6j67ho2xn5skyngidgutomsyj5bqjs4nn4ha",
    "package-a/8-cell-orig.gif": "dweb:/ipfs/bafybeiatr6vzozvaxtp5f32ghixj4bvauz6wgl4lbbh6np4yrrsvtep3y4"
  }
}
```
