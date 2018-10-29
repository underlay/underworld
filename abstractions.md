# Abstractions
> I'm all for 'em

Tim Berners-Lee wrote an essay I love about progress in communication technology. [He tells it best](https://www.w3.org/DesignIssues/Abstractions.html), but the narrative he sees is that networks build on each other in layers of increasing abstraction. 

<dl>
	<dt><strong>Connections → Computers</strong></dt>
	<dd>At first, individual connections between computers were the primitives (you would route mail around manually like <code>timbl@mcvax!cernvax!cernvms</code>), then DNS and TCP/IP abstracted all computers away into a universally addressable "Internet Cloud" that let "programs to talk as though the computers were directly connected".</dd>
	<dt><strong>Computers → Documents</strong></dt>
	<dd>But it turns out that we mostly care about the files on the computers, not the computers themselves. HTTP and HTML set standards for publishing, retrieving, and rendering documents, all addressed by paths relative to a host computer. These documents, all linking to each other, created a new overlay network all of their own that we called the World Wide Web.</dd>
	<dt><strong>Documents → Things</strong></dt>
	<dd>But even the files on the computers are just vehicles for the <em>things in the files</em>. This is the basis for TBL's vision of the Semantic Web: the abstraction above documents, where objects and ideas themselves are the nodes. This was also the original motivation for URI fragments, so that we could index content within documents.</dd>
</dl>

This story is elegant, but shows a few cracks under inspection. After the first layer of abstraction (DNS and TCP/IP), we've only _appended_ elements to addresses - a pathname to the origin to identify a document within a computer, and a fragment to the pathname to identify a thing within a document. But that isn't abstraction, because the previous layers are still visible (and necessary) - it's just construction. This is fine, as abstraction isn't always appropriate and has certainly worked well for the web so far. Nevertheless, true abstraction would be to address documents directly, without reference to a parent computer.

### Content addressing!

This is what the distributed web enables: content-addressable files, in a context that is free from any particular computer. IPFS resolves files' hashes to their raw bytes, Dat resolves public keys to directory roots, and other projects will likely follow (and  are following) similar schemes.

```
https://en.wikipedia.org/wiki/Vincent_van_Gogh
→
dweb:/ipfs/QmXoypizjW3WknFiJnKLwHCnL72vedxjQkDDP1mXWo6uco/wiki/Vincent_van_Gogh.html
```

There are definite tradeoffs. In some ways, traditional URLs are more fragile than content-addresses: a computer can survive a migration without losing its domain name (or even IP address), but a document can't move between host computers without breaking all its existing links <sup>[1](#1)</sup>. But in other ways, they are also more robust, since documents be can updated without losing their identity of being "the same document" <sup>[2](#2)</sup>.

TBL's essay was written in 2007 and last edited in 2010, so I don't blame him for not predicting content-addressability or imagining that it would be practical. But it is! You can browse [Wikipedia](https://ipfs.io/ipfs/QmXoypizjW3WknFiJnKLwHCnL72vedxjQkDDP1mXWo6uco/wiki/) 
or download [Project Gutenberg](https://www.reddit.com/r/IPFS_Hashes/comments/8716n2/project_gutenberg_hash_and_instructions/) 
or read the [Declaration of the Independence of Cyberspace](https://ipfs.io/ipfs/QmVDWmkM87NfR85WE1LvfwfJLRcMEtfNnCBiCJQRePP7Ly) 
and it all kind of works.

<dl>
	<dt><strong>Hey wait! Those links were just normal URLs!</strong></dt>
	<dd>Yeah - browsers aren't set up to work with decentralized protocols yet, so for now we have to go through a gateway to see them. But hopefully browsers will start supporting them soon! The IPFS folks are tracking progress <a href="https://github.com/ipfs/in-web-browsers">here</a>, and a bunch of people are already using a browser called <a href="https://beakerbrowser.com/">Beaker</a> that supports Dat.</dd>
</dl>

**Anyway**, the point is that content-addressable systems like IPFS and Dat finally close the loop in TBL's _Book 2: Abstracting Away Computers_: they address and resolve documents without depending on any particular server to find them.

- [x] Connections → Computers
- [x] Computers → Documents
- [ ] Documents → Things

### Semantic addressing?

Eventually, we may invent a way of addressing semantic content itself - eliminating the containing document in the way that IPFS eliminated the containing computer, and retrieving data by constructing granular descriptions that resemble database queries more than URIs <sup>[3](#3)</sup>. But until we have a real solution for TBL's _Book 3: Abstracting Away Files_ (and as a likely prerequisite), we can at least edge closer by using content-addressing for our documents before falling down to fragments for semantic IDs.

```
https://en.wikipedia.org/wiki/Vincent_van_Gogh#Artistic_breakthrough
→
dweb:/ipfs/QmXoypizjW3WknFiJnKLwHCnL72vedxjQkDDP1mXWo6uco/wiki/Vincent_van_Gogh.html#Artistic_breakthrough
```

- [x] Connections → Computers
- [x] Computers → Documents
- [ ] ~~Documents → Things~~ (punt for later)

---

<a name="1"><strong>1</strong></a>: At least not without cooperation from the original server by serving a redirect response or similar.
<br>
<a name="2"><strong>2</strong></a>: This is more true for IPFS than for Dat. Dat addresses are rooted in a public key, which isn't tied to a computer per se, but also doesn't quite get entirely out of the document's way (if two roots publish the same document, they'll get deduplicated when resolving them, but the URLs will still look different). 
<br>
<a name="3"><strong>3</strong></a>: Queries are a dangerous analogy to make because of their associated uncertainty: "we could never use queries to index data; what if they didn't return any results?" But it's no different than the uncertainty associated with URLs or IP addresses, and is in some ways _more certain_ in that the content served at a URL can change without warning over time, so you're never sure if you got the same thing as the person who sent you the link.
