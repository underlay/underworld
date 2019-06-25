# Underlay Roadmap

This roadmap will be re-evaluated and edited **every month**.

## June

The focus for June is building a **framework for simple Underlay deployments** that route messages to external handlers. The deliverable is a docker file that updates and serves backups of PubPub communities.

- [x]  Write Percolate middleware to match and handle specific ShEx shapes
- [x]  Formalize and document ShEx *queries*
- [x]  Write [Percolate](https://github.com/underlay/percolate) middleware to match and handle arbitrary ShEx *queries*
- [ ]  Write a configurable docker file that POSTs messages matching ShEx shapes to URLs
- [ ]  Explore designing a Linked Data Platform Underlay node, document results
    - [https://www.w3.org/TR/ldp/](https://www.w3.org/TR/ldp/)
    - [https://www.w3.org/TR/ldp-bp/](https://www.w3.org/TR/ldp-bp/)
---
- [x]  Refactor [styx](https://github.com/underlay/styx) to parse the new message format
- [ ]  Research past *implementations* of Prolog and Datalog. Understand and document basic concepts and approaches.
- [ ]  Prototype an in-memory RDF query processor that implements simple logical entailment of some of the properties from the [CWM built-in functions](https://www.w3.org/2000/10/swap/doc/CwmBuiltins)
    - [ ]  Easier: `lessThan`, `equalTo`, `memberCount`
    - [ ]  Harder: `quotient`, `sum`

## July

The focus for July is building tools for **visualizing and creating messages**. The deliverables are a stack of re-usable packages that make testing and working with messages easier.

- [ ]  Refactor the [underlay/explore](https://github.com/underlay/explore) repo
    - [ ]  **Survery past graph (especially RDF dataset) visualizations and browsers and document results**
    - [ ]  Redesign the visualization of graphs within datasets
    - [ ]  Redesign the representation of dataset signatures
    - [ ]  Design & implement content-link navigation
- [ ]  Polish and publish the [anagraph](https://github.com/underlay/anagraph) editor
    - [ ]  Implement schema-driven read-only visualization blocks
- [ ]  Explore common provenance patterns and publish a library of sample provenance graphs
- [ ]  Integrate simple logical entailment into the [styx](https://github.com/underlay/styx) query processor

## August

The focus for August is deploying a **reference implementation of a general-purpose graph data Underlay node**. The deliverable is a freebase.com-style dashboard where users can explore and query a sample dataset.

- [ ]  Deploy a KFG styx instance and Underlay node
- [ ]  Find and ingest a large sample dataset
- [ ]  Design and implement a query editor (with templates and examples)
- [ ]  Implement a dashboard integrating [underlay/explore](https://github.com/underlay/explore), [anagraph](https://github.com/underlay/anagraph), and the query editor

## September

The focus for September is **exploring the foundations of routing**.

- [ ]  Research past implementations of federated queries
- [ ]  Explore mechanisms for expressing peer-to-peer coordination in query processing
- [ ]  Research decentralized pub/sub implementations
- [ ]  Prototype mechanisms for subscribing to queries
